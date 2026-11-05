# J-PACT shared-text test: plan

*Written Thu Nov 5 2026 (prior work). Scope: steps 1–2 only, no new conversations.*

**Question.** J-PACT flags a run when one pair of agents shares more J-lens words with each other than with the rest
of the table. In NARCBench Core the two colluders' prompts both contain their private chat, word for word. Does J-PACT
detect that shared text rather than collusion?

**Terms.** *Observation*: one agent's internal state (residual) at the last token of one of its replies, at each of
Qwen3-32B's 63 lens layers. *Arm*: which word directions the state is decomposed into, J-lens atoms `W_U[t]·J_l`
(J-PACT) or plain logit-lens atoms `W_U[t]` (our baseline). *AUROC*: chance a random collusion run outscores a random
control run (0.5 = coin flip), averaged over Core domains as in the paper, with a 95% bootstrap over scenarios.
*Top-pair split*: in each collusion run, is J-PACT's top pair the colluders, the honest pair, or a mixed pair?

## Steps

| # | What | Rows replayed | Pass / report |
|---|---|---|---|
| 0 | **Check our scorer and decomposition on the authors' cache** (no model needed). Score their cached decompositions with J-PACT's own `detect.py` functions; then decompose their cached activations with our GPU-batched copy of TransformerLens's gradient pursuit and compare atom by atom. | 0 | 0.984 and 19 colluder / 12 honest top pairs from the cache; our decomposition matches theirs |
| 1 | **Baseline.** Replay the 62 released Qwen Core runs (31 collusion + 31 control) through bf16 Qwen3-32B with NARCBench's own chat renderer, discussion rounds 1–3. J arm and logit-lens arm. | 744 | J AUROC ≥ 0.90; top-pair split matches the cache; fresh activations close to the cached ones |
| 2a | **Private chat removed.** Same rows, but in each colluder prompt the `PRIVATE COORDINATION (...)` block is cut. The result is exactly the honest prompt template. Replies, history and system prompts unchanged. | 186 (colluder rows; the other 558 rows are identical to step 1 and reused) | AUROC and split, both arms |
| 2b | **Final round.** Round 4 (the vote): the user prompt is byte-identical for all four agents. | 248 | AUROC and split, both arms |

Both 2a and 2b still leave the colluders' shared *system prompt* (secret motive paragraph). A drop to ~0.5 means the
private chat drove the signal; a score that stays high could still be the system-prompt split, which only the later
"same words, honest" control can separate.

## How

- **Code**: `projects/jpact/harness/`. `pod.sh` (from the Silent Dissent driver) pushes code and runs jobs; `replay.py`
  imports J-PACT's `_aligned` loader and NARCBench's `extract_core._build_gen_text` renderer and saves fp16 residuals
  at the last token, all 63 layers, as J-PACT does; `decompose.py` runs the K = 25 nonnegative gradient pursuit for all
  rows at once (TransformerLens does one row at a time, which would take hours); `score.py` imports `shares`,
  `pair_contrast`, `jpact`, `grouped_auroc` and `scenario_draws` from J-PACT's `detect.py` unchanged.
  We don't run J-PACT's `setup.py all`: it pins a NARCBench commit that isn't public, and it replays all three test
  sets.
- **Pins** (from J-PACT's `config.py`): Qwen/Qwen3-32B `9216db57`, NARCBench dataset `19cb14b2`, lens
  `neuronpedia/jacobian-lens@8aa8152c` (`qwen3-32b/jlens/Salesforce-wikitext`, the 80-prompt partial checkpoint the
  paper used, divided by 80 as J-PACT does), transformers 5.17.0, transformer-lens 3.9.0.
- **Activations** are kept on the pod volume and copied to `projects/jpact/data/activations/` (about 1 GB, git-ignored).

## GPU, time, cost

- **GPU**: 1× A100 80 GB, secure cloud ($1.79/h at the time of writing), 150 GB volume. H100 ($3.99/h) only if no
  A100 is available.
- **Estimates**: setup and downloads (66 GB model, 3.3 GB lens, 1 GB cache) about 45 min; step 0 about 15 min; replay
  of 1,178 rows about 30 min; decompositions (3 conditions × 2 arms, batched) about 30 min; debugging slack 1–2 h.
  **About 3–5 GPU-hours, $6–9.** Cap: $25; I stop and ask Peter before going over it.
- The pod is stopped (not terminated) between steps if there is a gap of more than ~20 min, and after step 2.
  Each start, stop and running cost goes in `RUNLOG.md`.
