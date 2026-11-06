#!/usr/bin/env bash
# Instruction-split tests (see replay.py). Stage 1: paraphrases + replays except t2b_full. Stage 2 (after the
# paraphrases are read by eye): t2b_full replays. Stage 3: decompose and score everything present.
#   bash run_tests.sh replay | full | score
set -euo pipefail
A=/workspace/acts; D=/workspace/dec; mkdir -p $A $D
rep() { [ -f $A/$1_$2.npz ] || python replay.py --condition $1 --phase $2 --out $A/$1_$2.npz; }
case "$1" in
  replay) [ -f paraphrases.json ] || python paraphrase.py
          for t in t1 t2 t2b_intro; do for p in discussion final; do rep $t $p; done; done ;;
  full)   for p in discussion final; do rep t2b_full $p; done ;;
  score)  for f in $A/t*_*.npz; do n=$(basename $f .npz); for a in J L; do
            [ -f $D/${n}_$a.npz ] || python decompose.py --acts $f --arm $a --out $D/${n}_$a.npz; done; done
          for f in $A/t*_*.npz; do n=$(basename $f .npz); t=${n%_*}; p=${n##*_}; for a in J L; do
            python score.py test --test $t --phase $p --arm $a --name ${n}_$a; done; done ;;
esac
echo "STAGE $1 DONE"
