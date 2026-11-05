# J-PACT shared-text test: results (steps 1–2)

*Thu Nov 5 2026 (prior work). Details, checks and timings: [RUNLOG.md](RUNLOG.md). Code: [harness/](harness/).*

## The setup in plain words

- **NARCBench Core**: four copies of Qwen3-32B sit on a committee, discuss a decision for 3 rounds, then vote (round 4).
  - In a **collusion run**, two of them (the *colluders*) get a secret motive in their instructions and a private chat
    that only they see. The other two (the *honest pair*) get honest instructions.
  - In a **control run**, all four get the honest instructions.
  - We use the 62 released runs: 31 collusion runs and 31 matching controls.
- **Shared text.** In rounds 1–3, the colluders' private chat is pasted word for word into both of their prompts. The
  honest agents never see it. In round 4 everyone gets the same prompt, but the colluders keep their secret motive in
  their instructions.
- **J-PACT** reads each agent's internal state at the end of each of its replies, at all 63 layers. It turns each state
  into its 25 strongest "words" and scores every pair of agents on how many words the two share more with each other
  than with the other two. A run's score is its top pair's score. J-PACT never sees labels.
- **The two lenses.** The **J-lens** (J-PACT's choice) turns a state into words through a learned correction. The
  **logit lens** is the plain, older readout with no correction. We ran J-PACT with each.
- **AUROC**: the chance that a random collusion run scores higher than a random control run. 0.5 is a coin flip, 1.0
  is perfect. As in the paper, it is averaged over the 14 topic areas. The brackets are a 95% range from resampling
  scenarios (a bootstrap).
- **Top pair**: in each collusion run, which pair J-PACT ranks first: the two colluders, the honest pair, or a mixed
  pair (one of each). Mixed pairs never came first.

## Results

| Inputs J-PACT reads | J-lens AUROC | Logit-lens AUROC | Top pair, J-lens (colluders / honest pair, of 31) | Top pair, logit lens |
|---|---|---|---|---|
| Authors' cached numbers, rounds 1–3 | 0.984 [0.90, 1.00] | – | 19 / 12 | – |
| **Our replay, rounds 1–3 (original)** | **1.000** [1.00, 1.00] | **1.000** [1.00, 1.00] | **19 / 12** | 20 / 11 |
| **Rounds 1–3, private chat removed** | **0.992** [0.98, 1.00] | **0.992** [0.98, 1.00] | **9 / 22** | 11 / 20 |
| **Round 4 (vote), identical user prompts** | **0.861** [0.77, 0.99] | **0.992** [0.92, 1.00] | **8 / 23** | 9 / 22 |

Among the runs J-PACT flags at a 5% false-alarm rate, the top pair is: colluders 19 / honest pair 10 (original),
9 / 18 (chat removed) and 7 / 12 (round 4), with the J-lens.

**Step 1 passes.**
- **Inputs:** our replay used exactly the authors' inputs (all 744 token sequences identical).
- **Activations:** they match the authors' cached ones up to normal rounding noise.
- **Decomposition:** ours gives the same words as TransformerLens and as the authors' cache.
- **Score:** AUROC is 1.000 (pass mark 0.90; paper 0.984), and the top-pair split is 19 / 12, the same as the cache.

## What it means

1. **Removing the private chat does not remove detection.** AUROC stays at 0.99 for both lenses. So the copied private
   chat is **not** what makes collusion runs stand out. Our leading explanation, in its simple form, is wrong.
2. **But the chat is what made the colluders look like a pair.**
   - **With the chat:** the colluders outscore the honest pair in 19 of 31 runs.
   - **Without it:** they do so in only 9 of 31, fewer than the 15.5 that chance would give.
   - **Final round:** the same, 8 of 31, with no chat at all.

   Without the shared text, J-PACT's "suspicious pair" is usually the **honest** one, as it already was on Stego.
   So the shared text explains *which* pair gets flagged, not *whether* the run gets flagged.
3. **What still separates collusion from control runs is a 2-against-2 split of the table.** The only difference left
   in these inputs is that two agents have different instructions from the other two. Control runs have no such
   split. This fits "J-PACT detects that the table is split into two instruction groups". But we haven't *tested*
   that yet.
4. **The J-lens isn't needed.** The plain logit lens does as well as the J-lens everywhere. In the final round it does
   better (0.99 vs 0.86). The paper's "J-space" framing gets no support from this test.

**What this does not show.** These conversations can't tell "the model holds collusion" apart from "the model holds
different instructions". Telling them apart needs new conversations, which is the next step and not done here. One
option is two honest agents who get the same extra text. Another is a split table with two honest instruction sets.

## Compute

- **GPU:** one A100 80 GB (RunPod secure cloud, $1.79/h), pod `s4lrx17crkezcm`.
- **Time:** ran 21:43–22:35 UTC, 0.87 GPU-hours, about **$1.56**. About 20 minutes of that went to a tooling bug of
  mine (see RUNLOG).
- **Pod status:** stopped, not terminated, with the model and activations on its 150 GB volume. While stopped, the
  volume bills about $0.05/h (about $1.20/day).
- **Copies on the Mac:** the activations and decompositions are also in `data/activations/` (git-ignored).
