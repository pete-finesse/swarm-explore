"""Ablate, steer and swap a word's lens direction, and read the model's answer probabilities.

A word's direction at layer l is the lens direction of its first piece(s): for the J-lens
J_l^T (gain * unembedding row), for the logit lens the unembedding row itself
(silent_dissent.lenses.*.direction). Each edit acts on the residual stream after block l, at
chosen prompt positions, for every layer listed. Definitions (h = residual at one position):

  ablate  h <- h - P h         P projects onto the span of the word(s)' piece directions.
                               Adds nothing back: the lens's logit for the word goes to ~0.
  steer   h <- h + alpha * |h| * d          d = unit direction (the authors' convention:
                               alpha is a fraction of the residual norm; negative pushes away).
  swap    the coefficients of h on the two directions (a, b) are exchanged:
          c_a' = (1-s) c_a + s c_b,  c_b' = (1-s) c_b + s c_a      s = strength, 1 = exact swap.

Neuronpedia's own ablate / swap may be defined differently; these are written out so they
can be checked. Positions are prompt positions (absolute), so the same edit applies when
candidate answers are appended for scoring, and during generation (which runs without a cache).
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import torch

from silent_dissent.model import get_layers, layer_output, replace_layer_output

from .text import resolve_positions, word_tokens


@dataclass
class Edit:
    kind: str                      # ablate | steer | swap
    words: list[str]               # ablate: 1+ words; steer: 1; swap: 2 (a, b)
    layers: list[int]
    positions: object = "last"     # see text.resolve_positions
    alpha: float = 0.0             # steer strength (fraction of |h|)
    strength: float = 1.0          # swap strength (1 = exact swap)
    lens: str = "jlens"            # whose directions to use
    label: str = ""

    def __post_init__(self):
        if self.kind not in ("ablate", "steer", "swap"):
            raise ValueError(f"unknown edit {self.kind!r}")
        if self.kind == "swap" and len(self.words) != 2:
            raise ValueError("swap needs exactly two words")
        if self.kind == "steer" and len(self.words) != 1:
            raise ValueError("steer takes one word")
        if not self.label:
            w = "+".join(self.words) if self.kind != "swap" else "->".join(self.words)
            extra = f" a={self.alpha:g}" if self.kind == "steer" else f" s={self.strength:g}" if self.kind == "swap" else ""
            self.label = f"{self.kind} {w}{extra} L{_layers_str(self.layers)}"


def _layers_str(layers):
    layers = sorted(layers)
    if len(layers) > 2 and layers == list(range(layers[0], layers[-1] + 1)):
        return f"{layers[0]}-{layers[-1]}"
    return ",".join(map(str, layers))


def directions(h, edit: Edit, layer: int) -> list[torch.Tensor]:
    """Per word: [k, d] unit piece directions at `layer` (k = number of pieces kept)."""
    lens = h.lenses[edit.lens]
    toks = word_tokens(h, edit.words, dedupe=edit.kind != "ablate")
    out = []
    for w in edit.words:
        if not toks[w]:
            raise ValueError(f"{w!r} has no usable token")
        D = torch.stack([lens.direction(t, layer).float() for t in toks[w]])
        out.append(D / D.norm(dim=-1, keepdim=True))
    return out


def _apply(H: torch.Tensor, edit: Edit, dirs: list[torch.Tensor]) -> torch.Tensor:
    """H [n, d] float32 -> edited H."""
    if edit.kind == "ablate":
        Q, _ = torch.linalg.qr(torch.cat(dirs).T)          # [d, k] orthonormal basis of the span
        return H - (H @ Q) @ Q.T
    if edit.kind == "steer":
        d = dirs[0].mean(0)
        d = d / d.norm()
        return H + edit.alpha * H.norm(dim=-1, keepdim=True) * d
    a = dirs[0].mean(0); a = a / a.norm()
    b = dirs[1].mean(0); b = b / b.norm()
    A = torch.stack([a, b], 1)                              # [d, 2]
    C = torch.linalg.lstsq(A, H.T).solution.T               # [n, 2] coefficients on (a, b)
    s = edit.strength
    M = torch.tensor([[1 - s, s], [s, 1 - s]], dtype=H.dtype, device=H.device)
    return H - C @ A.T + (C @ M) @ A.T


@contextmanager
def applied(h, text: str, edits: list[Edit]):
    """Register forward hooks that apply `edits` while the prompt `text` (possibly with tokens
    appended) runs. Register before any capture hooks so captures see the edited residual."""
    edits = edits or []
    n = len(h.encode(text))
    blocks = get_layers(h.model)
    with ExitStack() as stack:
        for e in edits:
            pos = resolve_positions(h, text, e.positions, n)
            for layer in e.layers:
                dirs = [D.to(h.device) for D in directions(h, e, layer)]

                def hook(_m, _i, out, e=e, dirs=dirs, pos=pos):
                    x = layer_output(out)
                    x = x.clone()
                    idx = [p for p in pos if p < x.shape[1]]
                    if idx:
                        sel = x[:, idx, :].float()
                        B, P, d = sel.shape
                        x[:, idx, :] = _apply(sel.reshape(-1, d), e, dirs).reshape(B, P, d).to(x.dtype)
                    return replace_layer_output(out, x)

                handle = blocks[layer].register_forward_hook(hook)
                stack.callback(handle.remove)
        yield


#: Ways an answer can start after the prompt. Chat models often bold it: after the prefill
#: "...in the country of", Qwen3.5-4B writes " **" with p=0.96 and " Austria" with p=0.001.
FORMATS = (" {}", " **{}")


@torch.no_grad()
def answer_probs(h, text: str, candidates: list[str], edits: list[Edit] | None = None, top: int = 5,
                 formats: tuple[str, ...] = FORMATS) -> dict:
    """Probability that the model's next words are each candidate answer.
    p_full:   P(" Austria") + P(" **Austria"): every piece teacher-forced, summed over `formats`
    p_plain / p_bold: the two terms;  p_first, rank_first: the first piece of " Austria" alone
    p_share:  p_full / the sum of p_full over the candidates (which candidate wins, among these)
    Also the model's top next tokens. Edits apply at prompt positions only."""
    prompt = h.encode(text)
    n = len(prompt)
    seqs = [(c, f, h.encode(f.format(c.strip()))) for c in candidates for f in formats]
    rows = [prompt + t for _, _, t in seqs] or [prompt]
    L = max(len(r) for r in rows)
    pad = h.tok.pad_token_id or 0
    ids = torch.tensor([r + [pad] * (L - len(r)) for r in rows], device=h.device)   # right padding
    mask = torch.tensor([[1] * len(r) + [0] * (L - len(r)) for r in rows], device=h.device)
    with applied(h, text, edits):
        logp = h.model(input_ids=ids, attention_mask=mask).logits.float().log_softmax(-1)
    first = logp[0, n - 1]
    out = {"top": [(h.tok.decode([int(t)]), float(first[t].exp())) for t in first.topk(top).indices]}
    probs = {c: {} for c in candidates}
    for i, (c, f, toks) in enumerate(seqs):
        lp = sum(float(logp[i, n - 1 + j, t]) for j, t in enumerate(toks))
        key = "p_plain" if f == " {}" else "p_bold" if f == " **{}" else f"p[{f}]"
        probs[c][key] = float(np.exp(lp))
        if f == formats[0]:
            probs[c]["p_first"] = float(logp[i, n - 1, toks[0]].exp())
            probs[c]["rank_first"] = int((logp[i, n - 1] > logp[i, n - 1, toks[0]]).sum())
    for c in candidates:
        probs[c]["p_full"] = sum(v for k, v in probs[c].items() if k.startswith("p_") and k not in ("p_first",))
    tot = sum(v["p_full"] for v in probs.values()) or 1.0
    for c in candidates:
        probs[c]["p_share"] = probs[c]["p_full"] / tot
    out["cands"] = probs
    return out


def compare(h, text: str, candidates: list[str], runs: dict[str, list[Edit]], top: int = 3) -> pd.DataFrame:
    """One row per (run, candidate): probabilities, change vs the unedited prompt, top tokens.
    `runs` maps a label to a list of edits; "baseline" (no edits) is always added first."""
    runs = {"baseline": [], **runs}
    base = None
    rows = []
    for label, edits in runs.items():
        r = answer_probs(h, text, candidates, edits, top)
        base = base or r
        top_str = ", ".join(f"{t!r} {p:.3g}" for t, p in r["top"])
        for c, v in r["cands"].items():
            rows.append({"run": label, "candidate": c, **v,
                         "d_p_full": v["p_full"] - base["cands"][c]["p_full"], "top_tokens": top_str})
    return pd.DataFrame(rows)


@torch.no_grad()
def generate(h, text: str, edits: list[Edit] | None = None, max_new_tokens: int = 8) -> str:
    """Greedy continuation, recomputed from scratch each step so prompt positions stay fixed."""
    ids = h.encode(text)
    new = []
    with applied(h, text, edits):
        for _ in range(max_new_tokens):
            x = torch.tensor([ids + new], device=h.device)
            t = int(h.model(input_ids=x).logits[0, -1].argmax())
            new.append(t)
            if t == h.tok.eos_token_id or "\n" in h.tok.decode([t]):
                break
    return h.tok.decode(new)
