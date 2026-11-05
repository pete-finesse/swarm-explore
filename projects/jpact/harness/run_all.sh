#!/usr/bin/env bash
# Steps 0-2 after the replays: check our batched decomposition, then decompose and score every cell.
set -euo pipefail
D=/workspace/dec; mkdir -p $D
python decompose.py --cached --arm J --check 6 --layers 0,20,40,62
[ -f $D/cache_J.npz ] || python decompose.py --cached --arm J --out $D/cache_J.npz
python score.py cache --dec $D/cache_J.npz --name cache_our_decomposition_J
for c in orig noprivate final; do for a in J L; do
  [ -f $D/${c}_$a.npz ] || python decompose.py --acts /workspace/acts/$c.npz --arm $a --out $D/${c}_$a.npz
done; done
for a in J L; do
  python score.py fresh --cond orig --dec $D/orig_$a.npz --name orig_$a
  python score.py fresh --cond noprivate --dec $D/noprivate_$a.npz --base $D/orig_$a.npz --name noprivate_$a
  python score.py fresh --cond final --dec $D/final_$a.npz --name final_$a
done
echo ALL DONE
