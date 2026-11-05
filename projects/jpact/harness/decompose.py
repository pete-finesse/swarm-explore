"""J-PACT's sparse nonnegative decomposition (K = 25 atoms), for all rows of a layer at once on the GPU.

This is TransformerLens 3.9.0's `get_sparse_decomposition(x, atoms, 25, algorithm='gradient_pursuit')`
(transformer_lens/tools/analysis/jacobian_lens_decomposition.py), which J-PACT's `lens.decompose` calls one row at a
time, rewritten line for line with a batch dimension. Same selection rule, stopping rule, projected-gradient step with
backtracking, and active-support pruning. `--check` compares it with TransformerLens itself on a few rows.

Arms (atoms are rows of a [vocab, d_model] matrix):
  J  W_U[t] J_l   J-PACT's atoms: lens.dictionary(readout, layer) = head[:vocab].float() @ J_l.float()
  L  W_U[t]       logit-lens atoms: the same without the Jacobian

  python decompose.py --acts X.npz --arm J --out D.npz                  fresh activations (replay.py output)
  python decompose.py --cached --arm J --out D.npz                      J-PACT's cached Core activations
  python decompose.py --cached --arm J --check 8                        compare with TransformerLens on 8 rows
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

JPACT = Path(os.environ.get('PYTHONPATH', '/workspace/jpact/jpact-code').split(':')[0]).resolve()
K = 25
CORR_TOL = math.sqrt(torch.finfo(torch.float32).eps)      # _CORRELATION_RELATIVE_TOLERANCE
ACTIVE_TOL = math.sqrt(torch.finfo(torch.float64).eps)    # _ACTIVE_RELATIVE_TOLERANCE
BACKTRACK = 20                                            # _GRADIENT_BACKTRACK_STEPS


def batched_gradient_pursuit(X: torch.Tensor, atoms: torch.Tensor, k: int = K):
    """X [B, d] fp32, atoms [V, d] fp32 -> support [B, k] (token ids, -1 unused), coordinates [B, k]."""
    B, d = X.shape
    norms = torch.linalg.vector_norm(atoms, dim=1)
    xnorm = torch.linalg.vector_norm(X, dim=1)                       # [B]
    tol = CORR_TOL * xnorm
    selected = torch.full((B, k), -1, dtype=torch.long, device=X.device)
    coef = torch.zeros((B, k), device=X.device)
    nsel = torch.zeros(B, dtype=torch.long, device=X.device)
    live = torch.ones(B, dtype=torch.bool, device=X.device)
    residual = X.clone()
    ar = torch.arange(B, device=X.device)
    for step in range(k):
        corr = (residual @ atoms.T) / norms                         # [B, V]
        if step:
            corr.scatter_(1, selected[:, :step].clamp_min(0), float('-inf'))   # -1 only in rows already stopped
        val, cand = corr.max(dim=1)
        del corr
        live &= val > tol                                           # TL: break once no atom is materially positive
        if not live.any():
            break
        selected[live, step] = cand[live]
        nsel[live] += 1
        # Gradient-pursuit step on rows still live; selected atoms as [B, d, step+1] (TL: atoms[selected].T)
        idx = selected[:, :step + 1].clamp_min(0)
        A = atoms[idx].transpose(1, 2)                              # [B, d, s]
        c = coef[:, :step + 1].clone()                              # new atom starts at 0
        r = X - torch.einsum('bds,bs->bd', A, c)
        feasible = c.clamp_min(0.0)
        direction = torch.einsum('bds,bd->bs', A, r)
        projected = torch.einsum('bds,bs->bd', A, direction)
        den = (projected * projected).sum(1)
        stepsize = torch.where(den > 0, (projected * r).sum(1) / den.clamp_min(1e-30), torch.zeros_like(den))
        cur = (r * r).sum(1)
        new = feasible.clone()
        pending = den > 0
        for _ in range(BACKTRACK + 1):
            cand_c = (c + stepsize[:, None] * direction).clamp_min(0.0)
            cr = X - torch.einsum('bds,bs->bd', A, cand_c)
            ok = pending & ((cr * cr).sum(1) <= cur)
            new[ok] = cand_c[ok]
            pending &= ~ok
            if not pending.any():
                break
            stepsize = torch.where(pending, stepsize * 0.5, stepsize)
        coef[live, :step + 1] = new[live]
        residual[live] = (X - torch.einsum('bds,bs->bd', A, coef[:, :step + 1]))[live]
        del A
    # Active support: contribution coef * ||atom|| > ACTIVE_TOL * ||x||
    contrib = coef * norms[selected.clamp_min(0)] * (selected >= 0)
    active = contrib > ACTIVE_TOL * xnorm[:, None]
    support = torch.where(active, selected, torch.full_like(selected, -1))
    coords = torch.where(active, coef, torch.zeros_like(coef))
    # TL returns the active atoms in selection order, packed; pack ours the same way
    order = torch.argsort((~active).to(torch.int8), dim=1, stable=True)
    return support.gather(1, order).cpu().numpy().astype(np.int32), coords.gather(1, order).cpu().numpy().astype(np.float32)


def load_readout():
    os.chdir(JPACT)
    sys.path.insert(0, str(JPACT))
    from utils.models import get_model
    spec = get_model('qwen3_32b')
    return spec.readout(tuple(spec.all_layers), device='cuda'), spec


def atoms_for(readout, layer, arm):
    import lens
    if arm == 'J':
        return lens.dictionary(readout, layer)                      # J-PACT's own function
    return readout.head[:readout.vocab_size].float()


def cached_rows(layer):
    """J-PACT's cached Core activations at one layer (744 rows, float32), and their cached decomposition."""
    base = JPACT/'artifacts/maj/2026-09-22-repro/qwen3_32b/end_of_response'
    v = np.load(base/f'raw/input/core_layer_{layer}.npz')['vectors'].astype(np.float32)
    v = v[:, 0] if v.ndim == 3 else v
    z = np.load(base/f'individual_j_reconstruction/sparse/core_layer_{layer}.npz')
    return v, z['support'], z['coordinates']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--acts', type=Path)
    ap.add_argument('--cached', action='store_true')
    ap.add_argument('--arm', choices=('J', 'L'), required=True)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--check', type=int, help='compare with TransformerLens on this many rows per layer (layers 0, 31, 62)')
    ap.add_argument('--layers', default='all')
    args = ap.parse_args()
    torch.set_float32_matmul_precision('highest')                  # no TF32: TransformerLens runs in full fp32
    out_path = args.out.resolve() if args.out else None
    acts = None
    if args.acts:                                                  # read once (npz members are re-read on every access)
        z = np.load(args.acts.resolve())
        acts = {'X': z['X'], 'layers': z['layers']}
    readout, spec = load_readout()
    layers = list(spec.all_layers) if args.layers == 'all' else [int(x) for x in args.layers.split(',')]
    if args.check:
        from transformer_lens.tools.analysis import get_sparse_decomposition
        for layer in layers:
            v, s_cache, c_cache = cached_rows(layer)
            atoms = atoms_for(readout, layer, args.arm)
            X = torch.tensor(v[:args.check], device='cuda')
            s_ours, c_ours = batched_gradient_pursuit(X, atoms)
            for i in range(args.check):
                tl = get_sparse_decomposition(X[i], atoms, K, algorithm='gradient_pursuit')
                tl_s = tl.support.numpy()
                ours = s_ours[i][s_ours[i] >= 0]
                cache = s_cache[i][s_cache[i] >= 0] if args.arm == 'J' else None
                print(f'layer {layer} row {i}: ours==TL support {np.array_equal(ours, tl_s)}, '
                      f'max|coef diff| {np.abs(c_ours[i][:len(ours)] - tl.coordinates.cpu().numpy()).max() if len(ours) == len(tl_s) else "n/a"}'
                      + (f', TL==cache {np.array_equal(tl_s, cache)}, ours==cache {np.array_equal(ours, cache)}' if cache is not None else ''),
                      flush=True)
        return
    S, C, t0 = [], [], time.time()
    for layer in layers:
        if args.cached:
            v, _, _ = cached_rows(layer)
        else:
            li = list(acts['layers']).index(layer)
            v = acts['X'][li].astype(np.float32)
        atoms = atoms_for(readout, layer, args.arm)
        s, c = batched_gradient_pursuit(torch.tensor(v, device='cuda'), atoms)
        S.append(s); C.append(c)
        del atoms; torch.cuda.empty_cache()
        print(f'layer {layer}: {len(v)} rows, mean active atoms {(s >= 0).sum(1).mean():.1f}, {time.time() - t0:.0f}s', flush=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_path, support=np.stack(S), coordinates=np.stack(C), layers=np.array(layers))
    print(f'saved {out_path}', flush=True)


if __name__ == '__main__':
    main()
