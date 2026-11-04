# B2 baseline plan: do swarms spread errors their agents know are wrong?

Written 2026-11-04, before the sprint. Nothing has been installed, downloaded or run yet. Every fact
below was checked against the original source on 2026-11-04 (see "What I checked"), unless it is
marked *estimate*.

## The short version

- **The baseline is very reproducible on paper.** The Silent Dissent repo has one script per step, a
  committed pre-registration for Qwen3.5-4B (layers 23–30, hit@100, plain format), the exact lens
  file the paper used (still on Hugging Face), and the dataset. Their own test runs took minutes,
  not hours.
- **The target number:** for Qwen3.5-4B agents that gave in to 3 scripted peers, the original-bridge
  readout is **0.852, 95% CI [0.782, 0.917], n = 54 agents**; the logit lens gives 0.06, and the
  J-lens minus logit-lens difference is 0.792 [0.722, 0.857]. (`docs/results/paper/tables.md` in
  the repo.) Without the top-100 cutoff, the logit lens is not blind: on log-rank it scores 0.62
  against the J-lens's 1.40 (`supp/rob_tf.tex`).
- **Total GPU estimate for the whole baseline: 5–7 hours on one card, about $15–20.** I'd stop at
  10 GPU hours ($30). No Adaption credits are needed.
- **The biggest risk is not the reproduction. It's step 2.** Qwen3.5-4B rarely gives in to a
  *single* peer: in the paper, 1 peer flipped only 11 agents. A chain where each agent sees one
  predecessor may produce too few agents that gave in to measure anything. The plan handles this
  with a fixed fallback order (step 5) and a hard drop rule.
- **The proposal overstates the gap.** Silent Dissent already ran a *live* free debate (3 copies of
  the model, 3 rounds, everyone sees everyone) and read the bridge in agents that gave in. For
  Qwen3.5-4B only 20 agents gave in there, and on known facts only 6. What's still new is chains,
  hops, fading over hops, and mixed-model swarms. The write-up must cite their E5 experiment.

## Terms used below

- **Bridge:** the hidden middle step. In "the capital of the country where the Sagrada Familia is",
  the bridge is Spain. Nobody in the conversation ever writes it.
- **Readout:** for each layer, rank all vocabulary tokens by the lens and ask whether the bridge is
  in the top 100 (hit@100). Do the same for a **control entity**: the bridge of a random other fact
  in the same category, e.g. another country. The score is bridge hit minus control hit, averaged
  over layers 23–30. A score of 0 means "no more than a random country".
- **Gave in:** the agent answered correctly alone (round 0), then gave the peers' wrong answer.
- **Held:** it kept its correct answer under the same pressure.
- **Logit lens:** the simple baseline. It reads each layer through the model's own output layer.
  The J-lens has to beat it.

## Steps, in order

### Step 0. Read and test the code on the laptop (CPU, no GPU, ~1 h, $0)

- Clone `https://github.com/ziangni-sys/silent-dissent` into `projects/B2/repos/silent-dissent`
  (MIT licence; last push 2026-10-03).
- Create a venv and run `pip install -e ".[dev]"`, then `pytest -q`. The tests include a full run of
  the pipeline on a tiny random model, with no downloads.
- Run `python scripts/entity_paper.py`. It rebuilds the paper's tables from
  `docs/results/crossmodel_summary.json`.
- **It worked if:** the tests pass and the rebuilt table shows H1 = 0.852 for Qwen3.5-4B.

### Step 1. Set up the GPU (~0.5 h)

- Any card with 24 GB or more fits a 4B model in bf16 (*estimate*: ~9 GB of weights plus the
  activations of every layer for a batch of 16). The authors used an A100 80 GB. Use whichever card
  the projects are sharing.
- Run `bash scripts/setup_gpu.sh configs/qwen35_4b_entity.yaml`. It installs the package, downloads
  the model and lens, runs the tests and a pre-flight check. Downloads:
  - `Qwen/Qwen3.5-4B`: about 9.3 GB (4.66 B parameters in bf16).
  - Lens: `neuronpedia/jacobian-lens`, branch `qwen-n1000`, file
    `qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt`, 406 MB. This is the
    exact file in the paper's config, and it is still at the commit the paper names (`16a01f3`).
  - `soheeyang/TwoHopFact`: one CSV, CC-BY-4.0.
- Also download the two **penultimate-layer** lenses for the same model (step 4):
  `camilablank/workspace-lenses`, files `qwen3.5-4b/j-lens/lens.pt` and `qwen3.5-4b/r-lens/lens.pt`
  (406 MB each).
- Install the `flash-linear-attention` and `causal-conv1d` kernels. The setup script tries this.
  Without them, Qwen3.5 falls back to slow code. Check the log for the "WARN" lines.
- **It worked if:** the setup script ends with `ALL CHECKS PASSED` from `check_model.py`.

### Step 2. Find which facts the model knows (~1–1.5 h *estimate*, up to 3 h without the fast kernels)

- Run `python scripts/entity_build.py --config configs/qwen35_4b_entity.yaml`. It asks the model
  hop 1, hop 2 and the full question for all 45,595 TwoHopFact facts, plus hand-written ones, then
  splits facts into dev and test sets by bridge.
- **It worked if:** about 4.5% of facts come out as known (the pre-registration says 4.5%), and
  after the category filter the test split has close to the paper's 718 items.
- Small differences in known items are expected, because batched bf16 generation is not perfectly
  deterministic. If the count is off by more than ~10%, stop and find out why before going on.

### Step 3. Reproduce the headline (~1–1.5 h *estimate*)

- **Skip** the authors' development and selection stages. Use their committed pre-registration
  `prereg/qwen35_4b_entity.json` as it is, so no choice is made after seeing results.
- Run the test split: `entity_run.py --stage pressure --split test`, then `entity_analyze.py`.
- Then run the "own answer hidden or absent" addendum: `C=configs/qwen35_4b_entity.yaml bash
  scripts/entity_own.sh test`, then `... analyze`. Their own run of this took 8 minutes. The chain
  in step 5 uses this protocol, so its numbers have to be reproduced too.
- **It worked if all of these hold:**

  | Check | Paper | Pass if |
  |---|---|---|
  | H1: bridge readout in agents that gave in (3 peers) | 0.852 [0.782, 0.917], n = 54 | point estimate inside the paper's CI |
  | H4: J-lens minus logit lens, same agents | 0.792 [0.722, 0.857] | CI excludes 0 |
  | Share that gave in, answer style, 3 peers | 8% | 5–12% |
  | Gave in, agent's own answer absent | 0.50 [0.46, 0.54]; 62% gave in | point estimate inside the CI |
  | Gave in, agent's own answer hidden | 0.43 [0.40, 0.47]; 89% gave in | point estimate inside the CI |
  | H1 and H4 without a cutoff (`entity_robust.py`, log-rank) | H1 1.40 [1.01, 1.55]; H4 0.78 [0.38, 0.97] | point estimates inside the CIs |

### Step 4. Check the pitfalls before building anything new (~0.5 h GPU, ~2 h work)

Each check uses data from step 3 or a rerun of its readouts. None of them needs new generations.

1. **Logit-lens baseline, with and without a cutoff.** The repo already computes the logit lens
   for every readout (H4). Report it next to every J-lens number from here on.
   - Report it at hit@10/50/100/500 *and* on log-rank, which has no cutoff.
   - Also report a per-layer AUROC of bridge rank against control rank, the measure
     jspace-obfuscation used. That makes our numbers comparable with that negative result.
   - Check whether the answer word fills the top of the logit lens in layers 23–30. If it does,
     that explains why the logit lens scores near 0 on hit@100.
2. **Same-words control.** The subject ("Sagrada Familia") is in every prompt. The model may work
   out "Spain" automatically, whatever it ends up saying, so a high bridge score alone doesn't show
   the agent knows the peers are wrong. Compare agents that **gave in** with three groups that
   saw the same words: those that **held**, the **agree** condition (peers state the correct answer),
   and the **mention** condition (a peer mentions the wrong answer but doesn't assert it).
   - Use the paper's same-fact comparisons (`supp/rob_items.tex`), not the raw group means (held
     0.54, agreed 0.63, gave in 0.85).
   - On the same facts, gave in minus agree is **−0.11 [−0.22, −0.06]** and held minus agree is
     −0.06. Pressure lowers the readout a little, whether the agent gives in or holds.
   - The high 0.85 is selection: the facts where agents give in have strong bridge readouts anyway
     (+0.22 at round 0).
   - So the honest reading is already "the model still computes the right bridge from the
     subject", not "it knows it is repeating an error". Our rerun should confirm this. Every claim
     has to be worded that way.
3. **Lens target layer.** The paper's lens has `target_layer: null`, which in the jacobian-lens
   library means the final layer, the setting the pitfall post warns about. Rerun the H1 readouts
   with the penultimate-target J-lens and R-lens from `camilablank/workspace-lenses` (target layer
   30 of 32, fitted on 25 prompts). Two practical points:
   - Their file layout differs from Neuronpedia's: `J` is one stacked tensor, not a per-layer
     dict, so it needs a small loader (*estimate*: 1 h).
   - Drop layer 30 from the band for these lenses. It is their target layer, so there the lens does
     nothing.
   - Their README loads the files with `weights_only=False`, which can run code hidden in the file.
     Try `weights_only=True` first, and only fall back after inspecting the file.
4. **Token-frequency bias.** The bridge-minus-control contrast already cancels most of it, since the
   control is an entity of the same kind (a country against a country). As a check, also report the
   raw bridge rank and the control rank, not only the difference.

- **It worked if:** you can fill in a table of gave in, held, agree and mention, under the
  J-lens (final target), the J-lens (penultimate) and the logit lens. A positive result has to
  hold under the penultimate lens to count.

### Step 5. The smallest live network: a chain of 3 (~1.5 h GPU, ~4–6 h coding)

**Design.** For each known test fact:

- **Agent 0 (scripted):** states the wrong answer, using the paper's "answer" style (the peer
  fact's answer, e.g. "... is Rome.").
- **Agent 1 (live Qwen3.5-4B):** sees the question and Agent 0's statement, then answers. Its
  own earlier answer is absent, as in the paper's "absent" addendum, because an agent downstream in
  a chain hasn't answered before.
- **Agent 2 (live):** sees the question and only Agent 1's actual statement.
- **Readout** at the last prompt token of Agents 1 and 2, for the original bridge, the wrong
  bridge (Italy) and the control bridge, under all three lenses.
- **The main hop measure is the wrong bridge, not the original one.** Every agent's prompt contains
  the subject, so the original bridge (Spain) probably can't fade much by construction. The
  question over hops is whether the wrong bridge (Italy) grows stronger downstream, beyond a
  mention baseline, and whether original minus wrong shrinks.

**Code.** One new script in `projects/B2/`, about 150 lines (*estimate*). It reuses the repo's
`EntityState` (with `peer_lines` replaced by the upstream agent's real text), `generate`,
`entity_readout` and bootstrap code. It doesn't fork the repo. Greedy decoding throughout, as in
the paper.

**Controls in the same run:**

- **Correct-seed chain:** Agent 0 states the correct answer. This gives the same words and no error,
  and it is the baseline for "held".
- **No-answer seed:** Agent 0 says something with no answer in it. Any flip here is not conformity:
  this is the control from "Not All Flips Are Conformity", which found 37% of flips happen without
  any peer input.
- **Mention seed:** Agent 0 mentions the wrong answer but asserts the right one.

**Pilot first, on the dev split (200 facts, ~10 min GPU).** Count how many agents give in at
hop 1. The paper's minimum for any estimate is 30. If too few give in, switch protocol in this
fixed order and stop at the first that reaches 30 at hop 1:

1. Chain as above (each agent sees one predecessor).
2. **Seed of 3:** three scripted wrong agents feed Agent 1, the setup the paper reproduces, and from
   there each agent sees the last 3 statements. In practice that means the remaining scripted ones
   plus the live upstream agents.
3. **Hidden own answer** (89% gave in in the paper) instead of absent.

Fix the protocol on dev, write it down in `projects/B2/` and commit it, then run the test split
once. That is the same rule the paper's authors followed.

**It worked if:** on the test split, among agents that gave in at hop 1, the original-bridge
readout is above control with a 95% CI that excludes 0, the J-lens beats the logit lens, and gave in
can be told apart from the correct-seed and no-answer controls. Hop 2 is reported as it comes
out: fading over hops is the research question, not a pass condition.

## What to drop the project on

Any one of these stops B2:

1. **The reproduction fails.** After one debugging pass of at most 2 GPU hours, H1 is outside
   [0.78, 0.92], or the J-lens minus logit-lens CI includes 0.
2. **It's a lens artifact.** With the penultimate lens, gave in minus control has a CI that
   includes 0. (If the logit lens does as well as the J-lens on log-rank, that is a reframe, not a
   drop: use the logit lens as the readout and make no J-space claim.)
3. **Too few agents give in.** Fewer than 30 at hop 1 on the dev pilot under all three protocols
   in step 5. Then there is no cascade to track.
4. **No signal in live agents.** The chain's agents that gave in at hop 1 show no bridge readout
   above control (CI includes 0), under every lens.
5. **Time.** Step 3 isn't finished by the end of Friday Nov 6, or the baseline passes 10 GPU hours.

One outcome is **not** a drop, only a reframe: gave in ≈ held ≈ agree (step 4.2). The project then
reports "agents keep computing the right premise, wherever they end up", and it must not claim the
agents "know" they're wrong.

## Time and cost

| Step | GPU hours (*estimate*) | Your time |
|---|---|---|
| 0. Laptop tests | 0 | 1 h |
| 1. Setup and downloads | 0.5 | 0.5 h |
| 2. Fact check | 1–1.5 (3 if slow kernels) | waiting |
| 3. Reproduction and addendum | 1–1.5 | 1 h reading results |
| 4. Pitfall checks | 0.5 | 2–3 h |
| 5. Chain of 3 (pilot and test) | 1–1.5 | 4–6 h coding |
| **Total** | **~5–7 h; cap 10 h** | **~1.5 days** |

At $2–3 per hour for an 80 GB card, that's about **$15–20**, capped at about $30. The GPU only needs
to be up during steps 1–5, and steps 2–3 can run unattended. The repo's run queues have a
`--stop-pod` option for RunPod. No hosted-inference spend: answers are scored by string match, so
no judge model is needed.

**Shared GPU:** B2 needs the card for one block of ~3 h (steps 1–3) and one of ~2 h (steps 4–5).

**Prior work:** I'd run steps 0–3 on Thursday Nov 5 and declare them as prior work. They are a
replication, so declaring them costs nothing. The dev pilot of step 5 could also run Thursday, to
inform the project choice, and be declared. The test-split chain and everything after it would be
weekend work. Peter decides.

## What I checked (2026-11-04)

| Claim | Source | Status |
|---|---|---|
| H1 0.85 / 0.22 / 0.24 / 0.03 (answer visible) | arXiv 2610.02702 abstract; repo `tables.md` | confirmed |
| With the answer hidden: Qwen3.5-4B 0.43, Qwen3.6-27B 0.29, Gemma 0.37, Llama 0.25 | arXiv abstract; repo `own_cells.tex` | confirmed. The proposal's table shows "—" for three of these, but all four exist. |
| Qwen3.5-4B gave in 8% → 89% with the answer hidden | arXiv abstract; `own_rates.tex` | confirmed |
| Qwen3.5-4B H1 rests on only 54 agents; 1 peer gave only 11 | `tables.md` | confirmed. This drives the step-5 risk. |
| Logit lens without a cutoff: log-rank 0.62 vs J-lens 1.40 (Qwen3.5-4B); Gemma logit ≥ J-lens | repo `supp/rob_tf.tex` | confirmed |
| Same facts: gave in minus agree −0.11 [−0.22, −0.06]; selection +0.22 at round 0 | repo `supp/rob_items.tex` | confirmed |
| Live free debate exists (E5): Qwen3.5-4B, 20 gave in at round 1, readout 0.64 [0.41, 0.85] vs held 0.60 | repo `deb_bridges.tex`, `debate_bridges.json` | confirmed. The proposal's "nobody used live agents" is wrong. |
| The paper's lens file and commit still exist; `target_layer: null` (final layer) | HF `neuronpedia/jacobian-lens`, branch `qwen-n1000`, `config.yaml` | confirmed. Fitted on 417 prompts on a B200. |
| A penultimate-target Qwen3.5-4B J-lens and R-lens exist | HF `camilablank/workspace-lenses` README | confirmed: target 30, n = 25 |
| No J++ lens for Qwen3.5-4B on Neuronpedia | Neuronpedia lens README | confirmed (one exists for Qwen3-4B, a different model) |
| Evidence Integration: "integrate candidates even after internally verifying their invalidity (93-100%...)"; own errors adopted more readily than foreign ones | arXiv 2609.04290 abstract | confirmed in substance. The real title is "Evidence Integration in Large Language Models"; the abstract doesn't name the 12 models; no code. |
| 37% of flips happen without any peer input | arXiv 2606.00820 abstract | confirmed. Measured on GPT-4o, not on open models. |
| jspace-obfuscation: logit lens ≥ J-lens for a silent bridge entity | its `RESULTS.md` | confirmed, but on Qwen3-8B with 17 vs 18 traces. That's a different model from ours, so step 4 matters. |

Not checked: the full PDFs of the three papers (abstracts and the repo's own tables only), and the
actual run time of `entity_build.py` (no log in the repo), so step 2's time is a guess.

## Out of scope for the baseline

Same-model vs mixed swarms (proposal question 3). That needs each model's own typical wrong
answers, not the shared peer facts, and at least one more model with a working readout. Gemma-4-E4B-it
is the obvious second model (H1 0.24; its J-lens had to be fitted by the authors). Plan that only if
step 5 passes.
