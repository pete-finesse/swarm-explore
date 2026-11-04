# Read-only checks behind PAPER.md

Plain Python 3 (no numpy), run from `projects/jpact/` with `python3 -I checks/<script> ...`. They read only small files
downloaded into the git-ignored `data/` folder (J-PACT cache: `data/cache/`, NARCBench: `data/narcbench/`). No model is
loaded and nothing costs money. Paths inside the scripts are as used on Nov 4 2026.

| Script | What it checks | Command |
|---|---|---|
| `core_read.py` | Section 3 Core readout: per-word counts for colluders, counterfactuals, honest and control agents | `python3 -I checks/core_read.py data/cache` |
| `stego_checks.py` | Stego signature matrix with and without the post-hoc words; previous-hand leak; steering logit shifts | `python3 -I checks/stego_checks.py data/cache` |
| `pairs_all.py` | Which pair J-PACT ranks top in each collusion run (colluders, honest pair, cross pair); reproduces Table 3 | `python3 -I checks/pairs_all.py checks data/cache data/narcbench` |
| `callouts_check.py` | Fig 3 callout rule applied colluder→counterfactual and the reverse | `python3 -I checks/callouts_check.py data/cache` |
| `npy.py` | Minimal `.npz` reader used by `pairs_all.py` | (library) |
