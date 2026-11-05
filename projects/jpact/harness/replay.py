"""Replay NARCBench's released Qwen3-32B Core transcripts through bf16 Qwen3-32B and save the residual at the last token
of each rendered turn, at J-PACT's 63 lens layers. Uses J-PACT's own row loader (`utils.build.replay._aligned`) and
NARCBench's own chat renderer (`extraction/extract_core._build_gen_text`), exactly as J-PACT's replay does.

Conditions:
  orig       discussion rounds 1-3, unchanged (J-PACT's Core observations; 744 rows)
  noprivate  discussion rounds 1-3, colluder rows only, with the "PRIVATE COORDINATION (...)" block cut from the user
             prompt (186 rows; every other row is byte-identical to `orig` and is reused from it at scoring time)
  final      round 4, the final vote: user prompt byte-identical for all four agents (248 rows)

Run from anywhere with PYTHONPATH=<jpact-code> (pod.sh sets it):
  python replay.py --condition orig --out /workspace/acts/orig.npz [--limit N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

JPACT = Path(os.environ.get('PYTHONPATH', '/workspace/jpact/jpact-code').split(':')[0]).resolve()
LAYERS = tuple(range(63))                      # J-PACT's Qwen all_layers (lens covers 0-62)
PRIVATE_HEAD = 'PRIVATE COORDINATION (only you and '
HISTORY_HEAD = '\n\nDISCUSSION HISTORY:\n'


def strip_private(user_prompt: str) -> str:
    """Cut the colluders' private-chat block. NARCBench's COLLUDER_DISCUSSION_TEMPLATE is
    '{context}\\n\\nOPTIONS UNDER REVIEW:\\n{options}\\n\\nPRIVATE COORDINATION (...):\\n{private}\\n\\nDISCUSSION HISTORY:...'
    and the honest DISCUSSION_PROMPT_TEMPLATE is the same without the PRIVATE block, so the result is exactly the honest
    template filled with the same context, options and history."""
    start = user_prompt.index(PRIVATE_HEAD)
    end = user_prompt.index(HISTORY_HEAD, start)
    if user_prompt.count(PRIVATE_HEAD) != 1:
        raise ValueError('expected one private block')
    if user_prompt[start - 2:start] != '\n\n':
        raise ValueError('unexpected text before the private block')
    out = user_prompt[:start - 2] + user_prompt[end:]
    if 'PRIVATE' in out:
        raise ValueError('private text left after cut')
    return out


def rows_for(condition: str):
    """[(metadata row index, NARCBench sample)] for one condition, via J-PACT's loader."""
    os.environ['NARC_PHASE'] = 'final' if condition == 'final' else 'discussion'
    os.chdir(JPACT)
    sys.path.insert(0, str(JPACT))
    # J-PACT's _upstream() imports NARCBench's three extractors; the public NARCBench checkout's Transfer extractor
    # differs from J-PACT's (unpublished) pin, so we import the Core one the same way _upstream does, and nothing else.
    from utils.build.replay import _aligned
    from utils.narcbench import modules
    extract_core, = modules('extraction', 'extract_core')
    loader, render = extract_core.load_runs, extract_core._build_gen_text
    rows = _aligned(Path('artifacts/narcbench'), 'core', loader, 'qwen3_32b')
    if condition == 'noprivate':
        rows = [(i, {**s, 'user_prompt': strip_private(s['user_prompt'])}) for i, s in rows
                if s['mode'] == 'collusion' and s['role'] == 'colluder']
    return rows, render


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--condition', choices=('orig', 'noprivate', 'final'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    rows, render = rows_for(args.condition)
    rows = rows[:args.limit]
    model_dir = JPACT/'artifacts/qwen3_32b'
    tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    ids = [tok(render(tok, s), add_special_tokens=False).input_ids for _, s in rows]
    # Check our inputs against J-PACT's own replay (token-id hashes in its identity file), where it has the row.
    ident = {}
    p = JPACT/'artifacts/qwen_reproduction/identity/core/sites.jsonl'
    if p.exists():
        ident = {r['row_index']: r['full_input_sha256'] for r in map(json.loads, p.read_text().splitlines())}
    hashes = [hashlib.sha256(np.asarray(x, dtype=np.int32).tobytes()).hexdigest() for x in ids]
    same = sum(ident.get(i) == h for (i, _), h in zip(rows, hashes))
    known = sum(i in ident for i, _ in rows)
    print(f'{args.condition}: {len(rows)} rows; inputs identical to J-PACT replay for {same}/{known} rows it has; '
          f'tokens min/median/max {min(map(len, ids))}/{int(np.median(list(map(len, ids))))}/{max(map(len, ids))}',
          flush=True)
    model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.bfloat16, device_map='cuda',
                                                 local_files_only=True).eval()
    cap = {}
    def hook(layer):
        def f(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            cap[layer] = h[0, -1].to(torch.float16).cpu()
        return f
    handles = [model.model.layers[l].register_forward_hook(hook(l)) for l in LAYERS]
    X = np.zeros((len(LAYERS), len(rows), model.config.hidden_size), dtype=np.float16)
    t0 = time.time()
    with torch.no_grad():
        for n, x in enumerate(ids):
            cap.clear()
            model.model(torch.tensor([x], device=model.device), use_cache=False)   # as J-PACT: model.model, no cache
            for li, l in enumerate(LAYERS):
                X[li, n] = cap[l].numpy()
            if n % 50 == 0 or n == len(ids) - 1:
                print(f'  {n + 1}/{len(ids)} tokens={len(x)} elapsed={time.time() - t0:.0f}s', flush=True)
    for h in handles:
        h.remove()
    if not np.isfinite(X.astype(np.float32)).all():
        raise ValueError('nonfinite activations')
    meta = [{'row_index': i, 'run_id': s['run_id'], 'agent_name': s['agent_name'], 'role': s['role'],
             'mode': s['mode'], 'round': int(s['round']), 'domain': s['scenario_domain'], 'n_tokens': len(x),
             'input_sha256': h, 'same_as_jpact_input': ident.get(i) == h if i in ident else None}
            for (i, s), x, h in zip(rows, ids, hashes)]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(args.out, X=X, layers=np.array(LAYERS))
    args.out.with_suffix('.json').write_text(json.dumps({'condition': args.condition, 'rows': meta,
        'torch': torch.__version__, 'seconds': time.time() - t0}, indent=0))
    print(f'saved {args.out} {X.shape} in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
