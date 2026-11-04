# Project A: baseline plan for "Does J-space collusion detection hold up in a swarm?"

Written Wed Nov 4 2026 by the project A researcher session. So far this is reading only: nothing has been installed, run or paid for. All numbers below come from the original papers, code or dataset listings, which I fetched and read myself. The "Sources checked" section lists what each one was checked against.

## Short version

- **The baseline looks viable and cheap.** J-PACT's code and part of its cache can be downloaded. Its detector only *reads* NARCBench's released transcripts, so reproducing the N=4 number needs no text generation.
- **Step 1 needs no GPU at all.** The cache holds J-PACT's sparse J-space decompositions for Qwen3-32B Core, for every lens layer. That should let us recompute the 0.984 AUROC on a laptop.
- **The real risk is scientific, not compute.** In NARCBench, the two colluders literally share a block of private text (their coordination chat) inside their prompts, and the honest agents don't. J-PACT scores "concepts a pair shares that the others don't". So it may be detecting *shared secret text* rather than collusion. The baseline must include a control that tests this (Step 3). If J-PACT fails it, the swarm question changes (see "When to drop the project").
- **J-PACT has no logit-lens baseline.** Its only unsupervised comparison is a word-list ("ontology") score. We add a logit-lens version (Step 2), as `proposals/README.md` requires.
- **Estimated cost before the weekend:** about 6–9 GPU-hours on one 80 GB card, roughly **$15–30**, plus about $0–5 of Adaption credits.

## Corrections to the proposal (from reading the sources)

1. **J-PACT's detector is not "top J-lens tokens at the middle layers, at the reply-start token".** That describes the paper's Section 3 interpretability readout, which was done on DeepSeek. The detector (Section 5, `detect.py`) works differently:
   - It takes the residual at the **last token of each public response**.
   - It runs a **sparse non-negative decomposition** of that residual onto the J-lens directions (25 tokens, using TransformerLens gradient pursuit).
   - It averages the pair contrast over **all 63 lens layers (0–62)** and over all 3 rounds.
2. **NARCBench Appendix G gives no Core number at N=8.** It reports 8 agents with 2, 3 or 4 colluders only on **Transfer** and **Stego**, using Qwen3-32B probes. Both are poor comparison points:
   - J-PACT is at chance on Transfer even at N=4 (0.556 on Qwen).
   - On Stego every method is already at the ceiling (≈1.000).

   So there is **no published probe number for Core at N=8**. We have to produce it ourselves: the NARCBench probe runs on CPU once activations exist.
3. **NARCBench's 8-agent code and data are not released.** `generation/core.py` draws exactly 4 names and treats the first 2 as colluders. Nothing 8-agent is in the HF dataset either: I searched the file list.
4. **The cache can't be used "as is".** J-PACT's README says that if `MANIFEST.sha256` verifies, `reproduce.sh` runs only the report steps, on CPU. But 48 of the 88 files in the manifest are **not in the HF cache**: `observations/*`, the NARCBench probe outputs, and Qwen's row-identity and `pairs/` files. So `reproduce.sh` would fall back to the full GPU path. Step 1 works around this by hand.
5. **Which data J-PACT reads for Qwen3-32B:**
   - **Transcripts:** NARCBench's Qwen3-32B-**AWQ** (4-bit) transcripts.
   - **Activations:** read with full-precision **`Qwen/Qwen3-32B`** (bf16, revision `9216db5…`).
   - **Runs:** 62 Core runs (31 collusion, 31 control; 744 observations = 62 runs × 4 agents × 3 rounds).
   - **Discrepancy to note:** the NARCBench paper says it kept 36 collusion runs. I haven't traced why J-PACT has 31. It doesn't block anything, but we'll note it.
6. **The Qwen3-32B lens is weak and targets the final layer.**
   - Its `config.yaml` (at J-PACT's pinned revision) has `target_layer: null`, which means the final layer.
   - It reports `prompts_fitted: 80`, even though it asked for 1000 with a minimum of 100.
   - Its results block was "reconstructed" afterwards.

   We should read the J-PACT numbers with this in mind. No J++ or penultimate-layer lens exists for Qwen3-32B (checked against the Neuronpedia README and the B2 and D sibling notes).

## Pitfalls from `proposals/README.md`, and how this plan handles them

| Pitfall | Why it matters here | What we do |
|---|---|---|
| **Same-words control** | The colluding pair shares a verbatim private chat and a similar motive paragraph. Pair contrast rewards exactly "shared beyond the table". | Step 3 adds a **shared-briefing honest pair**: two honest agents get the same private briefing and private channel, with the same words, but are told to act honestly. We also add two cheap text-only diagnostics (Step 2). |
| **Logit-lens baseline** | J-PACT never compares against the logit lens, and in viznu/jspace-obfuscation the J-lens lost to it. | Step 2 runs the **same J-PACT code** with the logit lens: atoms `W_U[t]` instead of `W_U[t]·J_l`. We also add a raw-residual cosine version that uses no lens at all. |
| **Lens targets the final layer** | J-PACT averages all layers, including late ones where the readout is mostly the next token. | Step 1 also reports AUROC by layer band: early 0–15, middle 16–47, late 48–62. |
| **Token-frequency bias** | Common tokens appear for everyone. | Pair contrast already subtracts what the pair shares with outsiders, which cancels common tokens. We report the top pooled tokens for the best pairs, to check by eye. |
| **Causal claims replicate weakly** | We make no causal claims. | Detection only. |

## Steps, in order

Each step lists what to do, what it needs, how long and how much it costs, how we know it worked, and when to stop. Times are my estimates, and assume one person working with Claude.

### Step 1. Recompute J-PACT's Qwen3-32B Core AUROC from the cache (CPU, no GPU)

- **What:**
  - Load the 63 cached decompositions for Qwen Core, one per layer (`individual_j_reconstruction/sparse/core_layer_{0..62}.npz`). I checked the format by reading the file headers: each holds `support` [744×25], `coordinates` [744×25], `episode`, `agent` and `response`.
  - Recover each observation's round by ordering its `response` ids within each (episode, agent).
  - Join the labels from `evaluator/core.json` (episode → collusion or control, plus domain).
  - Run J-PACT's own `shares`, `pair_contrast`, `jpact` and `grouped_auroc` functions from `detect.py`, copied unchanged.
  - Also: report AUROC for 1, 2 and 3 rounds, and AUROC by layer band (see the pitfalls table).
  - **Early warning for the same-words problem:** if the early band (0–15) alone already gives a high AUROC, J-PACT is likely reading surface words in the context, such as the shared private chat. Then Step 3's shared_honest control becomes the deciding test; tell the orchestrator.
- **Download (about 25 MB, all small):**
  - J-PACT code. The page `anonymous.4open.science/r/maj-lens-reproduction-D043` refuses scripts, but its file API works: `…/api/repo/maj-lens-reproduction-D043/files` and `…/file/<path>`. I have already read every source file that way.
  - From `throwaway-reproducibility-354364563/jpact-cache`: only `maj/2026-09-22-repro/qwen3_32b/` (about 20 MB) and `cache_expansion/qwen3_32b/` (about 25 MB, for row ids).
- **Needs:** Python with numpy and scipy, on the laptop.
- **Time:** 2–4 hours. **Cost:** $0.
- **Worked if:** we get **0.984** (J-PACT's Table 1, Qwen3-32B Core) to about ±0.005, and the 1- and 2-round values match Table 2 (0.861 and 0.978). An exact match is possible because these are J-PACT's own cached numbers.
- **Stop rule:** if we can't line the rows up within 4 hours, skip to Step 2, which rebuilds everything from public inputs.
- **Prior work:** if this is done before Friday, it is declared as prior work.

### Step 2. Rebuild the N=4 baseline from public inputs on the GPU, with the logit lens

- **What:**
  - Use J-PACT's own pipeline for Qwen only: `STUDY_MODELS=qwen3_32b`, then `utils.build.setup all` and `detect.py sweep qwen3_32b`. This replays NARCBench's released Core transcripts through bf16 Qwen3-32B, saves the end-of-response residuals at layers 0–62, and decomposes them.
  - Then add three things (small edits, each in a new file):
    1. **Logit-lens PACT:** the same decomposition and contrast with atoms `W_U[t]` (no Jacobian).
    2. **Residual-cosine pair contrast:** the pair's cosine similarity minus their mean similarity with outsiders, averaged over layers. No lens at all.
    3. **Two text-only diagnostics:** pair contrast on bag-of-words of (a) each agent's *public messages only*, which is what a fair black-box monitor sees, and (b) each agent's *full input prompt*. (b) is not a fair monitor, because it sees the private chat. It measures how much J-PACT's signal could come from the shared private text alone.
  - Run NARCBench's probe on the same activations as the supervised reference (CPU).
- **Clone or download:**
  - J-PACT code (as in Step 1).
  - `aaronrose227/narcbench` at commit `85fea3be…` (code), and the HF dataset `aaronrose227/narcbench` at revision `19cb14b2…` (I checked: it holds 100 Qwen Core runs, 50 + 50, at that revision).
  - `anthropics/jacobian-lens` at `581d3986…`.
  - The lens `neuronpedia/jacobian-lens` at `8aa8152c…`: `qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt`, **3.3 GB**, fp16.
  - `Qwen/Qwen3-32B` at `9216db57…`: 32.8B parameters, about **66 GB** in bf16.
  - Pinned packages: `env/requirements.txt` (transformers 5.17.0, transformer-lens 3.9.0, …).
- **GPU:** 1× 80 GB (H100 or A100). The bf16 weights take about 66 GB, which leaves room for the ≤8k-token forward passes; the replay loads the model with `device_map="cuda"`. The sweep step loads only the lens and the unembedding (6.6 GB of Jacobians in fp32, plus a 3.1 GB dictionary per layer), not the model. **Disk: at least 150 GB.**
- **Time (estimates):**
  - About 30 minutes of downloads.
  - About 10–20 minutes of replay: 744 forward passes of 2–5k tokens.
  - About 30–60 minutes of decomposition: 744 × 63 one-row-at-a-time gradient pursuits. The logit-lens arm costs the same again.
  - **2–3 GPU-hours including debugging, about $5–10.**
- **Worked if:** J-PACT Core AUROC ≥ **0.90** (the bottom of the paper's 95% CI, [0.90, 1.00]), ideally within 0.02 of 0.984. The README warns that replayed activations are not bit-identical, so small drift is expected. The probe should be ≈1.00.
- **What we learn:** whether the J-lens beats the logit lens and no-lens baselines here, and how much of the signal the text-only diagnostic (b) alone reproduces.

### Step 3. One larger committee end to end: N=8, 2 colluders, plus the same-words control

- **What:**
  - Generalise NARCBench's `generation/core.py` to N agents and k colluders. I read the whole run loop, and the 4-agent assumptions are in a few places:
    - `sample(NAME_POOL, 4)`, with colluders taken as `agents[:2]`;
    - `partner = colluder_pair[1 - i]` (needs a list of partners for k > 2);
    - the style-assignment tables, which are built for 2 + 2 agents;
    - the `≥3 of 4` majority rule;
    - `max_workers=4`.
  - Generalise J-PACT's `detect.py` the same way. Its formula already has N in it (`1/(2(N−2))`). In the code: `PAIRS = combinations(range(4), 2)`, `range(4)` in `pair_contrast`, the `len(ags) != 4` skip, and the localisation, which assumes "pair or its complement".
  - Add a third condition, **`shared_honest`**: two honest agents get the collusion motive as a private briefing and a private channel, with the same private-chat template, but are told to disclose it and judge on merit. Same words, no collusion.
  - **Pilot set:** 12 Core scenarios (at least one per domain group) × 3 conditions (collusion, control, shared_honest) = **36 runs**, at N=8, k=2.
  - Generate with **Qwen3-32B-AWQ on vLLM**, as NARCBench did: temperature 0.7, thinking off, 512 max tokens.
  - Replay the transcripts with bf16 Qwen3-32B, as in Step 2, and score with J-PACT, logit-lens PACT and the text diagnostics.
  - Keep NARCBench's filter: drop collusion runs where the colluders did not both vote for the target.
- **Download:** `Qwen/Qwen3-32B-AWQ` (about 19 GB) and vLLM. NARCBench's own scripts start vLLM as `vllm serve Qwen/Qwen3-32B-AWQ --port 8020`.
- **Time (estimates):**
  - A run at N=8 has 2 private turns, 24 discussion turns and 8 final turns. Turns within a run happen one after another, but vLLM handles many runs at once.
  - Rough load per run: about 8k generated tokens and about 140k prompt tokens, much of it reused through vLLM's prefix cache.
  - 36 runs is roughly **30–60 minutes of generation**. Replay plus decomposition is about 864 observations, roughly **45–75 minutes**.
  - Code changes take 3–4 hours and need no GPU (they can be written before renting).
  - **About 2–3 GPU-hours, $5–10.**
  - The "which N can we afford" table in Step 4 uses the *measured* times from this step, not these guesses.
- **Worked if:**
  - (0) **Regression test, before any N=8 data:** the N-agent version of `detect.py`, run on the N=4 data, gives *exactly* the same pair scores and AUROC as the original code. This catches silent bugs in the generalisation.
  - (a) Every run finishes without `[ERROR]` turns, and the longest prompt fits Qwen3's 32k-token native context.
  - (b) At least about 60% of collusion runs pass the vote filter.
  - (c) J-PACT produces a score for every run.
  - (d) We get two AUROCs with bootstrap intervals: collusion vs control, and collusion vs shared_honest. With 12 scenarios the intervals will be wide; this is a pilot, not the result.
- **Adaption credits (optional, about $1–5):** an LLM judge to check whether colluders really coordinated, which NARCBench used as its second filter. This is black-box only, so it fits the credits.

### Step 4. Budget table for the weekend (no new compute)

- Using the times measured in Step 3, fill in the GPU-hours for each (N, k) cell, with N ∈ {4, 8, 12, 16} and k ∈ {2, 3, 4}, at 50 scenarios × 3 conditions.
- Separate N from the variables tangled with it:
  - **Speaking turns per agent:** keep 3 rounds.
  - **Transcript length:** add an arm with the history capped to the last 4×3 messages, so context stays the same size as at N=4.
  - **Colluder-to-honest ratio:** compare (N=8, k=2) with (N=8, k=4) with (N=4, k=2).
- Rough expectation, to be replaced by measurements: N=16 means 48 turns per run, one after another, with histories up to about 15k tokens. That is probably 3–5× the cost of N=8 per run, so the full N=16 grid may not fit the weekend.
- **Worked if:** the table exists, and a weekend design fitting about 20 GPU-hours (about $50–60) is chosen together with the orchestrator.

## What to clone or download (summary)

Everything goes in git-ignored `projects/A/repos/` and `projects/A/data/`.

| Item | Pin | Size | Step |
|---|---|---|---|
| J-PACT code (anonymous repo, via its file API) | as served on Nov 4 | <1 MB | 1 |
| `jpact-cache`, Qwen subfolders only | HF main | ~45 MB | 1 |
| `aaronrose227/narcbench` code | `85fea3be` | <1 MB | 2, 3 |
| `aaronrose227/narcbench` dataset | `19cb14b2` | 1.4 GB (all models); Qwen part much smaller | 2 |
| `anthropics/jacobian-lens` | `581d3986` | small | 2 |
| Neuronpedia Qwen3-32B J-lens | `8aa8152c` | 3.3 GB | 2, 3 |
| `Qwen/Qwen3-32B` bf16 | `9216db57` | ~66 GB | 2, 3 |
| `Qwen/Qwen3-32B-AWQ` | latest | ~19 GB | 3 |

Models: Qwen3-32B only. **Fallback model if Qwen generation at N=16 is too slow:** GPT-OSS-20B, which fits in about 16 GB with MXFP4, has a released lens, and scores 0.838 on Core with J-PACT. It would need NARCBench's gpt-oss chat format.

## Time and cost summary (estimates)

| Step | Where | Wall time | GPU-h | Cost |
|---|---|---|---|---|
| 1. Cached recompute | laptop | 2–4 h | 0 | $0 |
| 2. N=4 rebuild + logit lens + text controls | 1× 80 GB | 4–6 h | 2–3 | $5–10 |
| 3. N=8 pilot, 3 conditions | 1× 80 GB | 6–8 h (incl. coding) | 2–3 | $5–10 |
| 4. Budget table | laptop | 1 h | 0 | $0 |
| Slack for setup and debugging | | | 2–3 | $5–10 |
| **Total before the weekend** | | **~2 days** | **6–9** | **~$15–30** (+ ≤$5 Adaption) |

The prices assume $2–3/h for an 80 GB card. Steps 2 and 3 can share one rental session, so the 66 GB model downloads only once. The GPU is shared with other projects, so book one block of about 5 hours.

## When to drop the project

These conditions are checked in order. Each one stops further spending on project A.

1. **We can't reproduce the baseline.** After Step 2, J-PACT Core AUROC on Qwen3-32B is **below 0.90**, and 4 hours of debugging (pinned versions, row alignment, layer set) don't fix it.
2. **J-PACT is a "shared text" detector.** In Step 3, collusion vs shared_honest AUROC is **at most about 0.65** (close to chance), while collusion vs control stays high. Then J-PACT is picking up the shared private briefing, not collusion. Scaling it to a swarm would only measure how often agents share text. **Early warning from Step 2:** if the full-prompt bag-of-words diagnostic (b) alone reaches about J-PACT's AUROC, expect this outcome. This is a real negative result and could be written up, but it is a different project. Bring it to the orchestrator rather than continuing with A as planned.
3. **The lens adds nothing.** Logit-lens PACT or residual-cosine contrast is **within J-PACT's confidence interval** on Core at N=4 and N=8. Then the "J-space" framing is not doing the work. This doesn't kill the project by itself, but its novelty drops: it becomes "pair contrast on residuals at scale". Flag it to the orchestrator.
4. **N=8 can't be generated reliably.** Fewer than about 50% of N=8 collusion runs pass the vote filter, or prompts overflow the context, or the measured N=8 cost implies that even N ∈ {4, 8, 12} × k=2 × 50 scenarios needs more than about 25 GPU-hours.
5. **Nothing to gain from scaling.** J-PACT at N=8 is already **≥0.99** on the pilot, with no room to get better or worse, *and* it fails the shared_honest control. If it is at the ceiling but *passes* the control, keep going: the interesting direction is then the false-alarm growth at N=12–16.

## Sources checked (Nov 4 2026)

- **J-PACT:** arXiv 2611.02153 v1 (abstract and full HTML), including Tables 1–3, Equations 1–7, Appendices A–D and the reproducibility statement. Code: all source files read through the anonymous repo's file API (`config.py`, `detect.py`, `lens.py`, `reproduce.sh`, `utils/models.py`, `utils/build/*`, `env/requirements.txt`, `results/main/detection.tex`). Cache: the full file listing on HF, plus `README.md`, `MANIFEST.sha256`, `evaluator/core.json` and two `.npz` headers.
- **NARCBench:** arXiv 2604.01151 (full HTML: §5, Appendices C, G, H, I, J). GitHub `aaronrose227/narcbench`: README, `config.py`, `generation/core.py` (the run loop and prompt templates) and `extraction/extract_core.py`. HF dataset listing at main and at the pinned revision.
- **Lenses:** the Neuronpedia `jacobian-lens` README and the Qwen3-32B `config.yaml` at the pinned revision.
- **Pitfall posts:** confirmed by title, date and summary (LessWrong API): the final-layer target post (Sep 25), z-scoring (Sep 17), topic detector (Aug 11), Nanda's review (Jul 6). `viznu/jspace-obfuscation` `RESULTS.md` confirms the negative logit-lens result, for example 0.95 (logit) vs 0.77 (J) at layer 24.
- **Sibling notes** (B2, D) agree: the Neuronpedia lenses target the final layer, and the lens format is `{"J": {layer: fp16 [d,d]}, …}`.
- **Not verified:**
  - The 31 vs 36 collusion-run discrepancy.
  - The real throughput of vLLM and of the decomposition (the times above are estimates).
  - Whether J-PACT's code runs as pinned: nothing has been executed yet.

## Questions for Peter

1. **GPU booking:** can project A have one block of about 5 hours on Thursday? Steps 2 and 3 back to back avoid downloading the 66 GB model twice.
2. **Hugging Face token:** is a token in `.env`? `Qwen/Qwen3-32B` isn't gated, but J-PACT's setup reads a token if one is present.
3. **Prior work:** is it fine to run Step 1 (laptop only) before Friday and declare it as prior work?
