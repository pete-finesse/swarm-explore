"""Meaning-preserving paraphrases of each Core scenario's honest mandate, for test t2b_full (see replay.py).
Qwen3-32B, greedy, thinking off. Writes harness/paraphrases.json {scenario: paraphrase} and a side-by-side
harness/paraphrases_check.md for reading by eye.

  python paraphrase.py
"""
from __future__ import annotations

import json
from pathlib import Path

import torch

import replay

PROMPT = ('Rewrite the following instructions in different words. Keep exactly the same meaning, the same requirements '
          'and the same level of detail, and roughly the same length. Do not add, remove or soften any requirement, '
          'and do not mention that it is a rewrite. Output only the rewritten instructions.\n\n{text}')


def main():
    here = Path(__file__).resolve().parent
    rows, _ = replay.rows_for('orig')
    mandates = {}
    for _, s in rows:
        if s['role'] == 'honest':
            mandates.setdefault(replay.scenario(s['run_id']), replay.mandate(s))
    from transformers import AutoModelForCausalLM, AutoTokenizer
    path = replay.JPACT/'artifacts/qwen3_32b'
    tok = AutoTokenizer.from_pretrained(path, local_files_only=True)
    tok.padding_side = 'left'
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, device_map='cuda', local_files_only=True).eval()
    keys = sorted(mandates)
    texts = [tok.apply_chat_template([{'role': 'user', 'content': PROMPT.format(text=mandates[k])}], tokenize=False,
                                     add_generation_prompt=True, enable_thinking=False) for k in keys]
    out = {}
    for b in range(0, len(keys), 16):
        enc = tok(texts[b:b + 16], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=600, do_sample=False)
        for k, g in zip(keys[b:b + 16], gen[:, enc['input_ids'].shape[1]:]):
            out[k] = tok.decode(g, skip_special_tokens=True).strip()
            print(k, len(mandates[k]), '->', len(out[k]), flush=True)
    (here/'paraphrases.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (here/'paraphrases_check.md').write_text('\n\n'.join(
        f'## {k}\n\n**Original** ({len(mandates[k])} chars)\n\n{mandates[k]}\n\n**Paraphrase** ({len(out[k])} chars)\n\n{out[k]}'
        for k in keys) + '\n')


if __name__ == '__main__':
    main()
