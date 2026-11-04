# A. Does J-space collusion detection hold up in a swarm?

Read `README.md` first for shared context, constraints and pitfalls.

## The question

J-PACT detects which agents in a 4-agent committee are secretly colluding, by reading their J-space, with no labelled training data. Does it still work with 8–16 agents and 2–4 colluders?

## Why size should matter, in both directions

- **It could get better.**
  - J-PACT scores a pair of agents by the concepts they share, minus what each shares with the other N−2 agents. With N=4 that comparison set is only 2 agents, so it's noisy. Larger N gives a steadier baseline.
  - With N=4, the colluding pair and the honest pair mirror each other, so J-PACT finds the split but can't say which side is colluding. Larger N removes that symmetry.
- **It could get worse.**
  - A run is scored by its single most suspicious pair. The number of pairs grows as N(N−1)/2: 6 at N=4, 120 at N=16.
  - About a third of honest agents already show collusion-like concepts. With more pairs, false alarms by chance grow.

Which effect wins, and at what N, is the result. Either answer is useful.

## What exists

- **J-PACT:** Molinari & Bettineschi (Nov 2026), https://arxiv.org/abs/2611.02153.
  - **Setup:** committees of 4 copies of one model. In collusion runs, 2 agents are secretly told to collude and get a private channel. In control runs, everyone is honest.
  - **Readout:** the top J-lens tokens at the middle layers, at the token where an agent's reply starts.
  - **Results (AUROC, four-model mean):**

    | Split | J-PACT | Supervised probes |
    |---|---|---|
    | Core | 0.921 | 0.993 |
    | Stego | 0.991 | — |
    | Transfer (agents in different roles) | 0.519 | — |

    On Qwen3-32B, Core is 0.984.
  - **Code:** https://anonymous.4open.science/r/maj-lens-reproduction-D043 (has `reproduce.sh`; refuses scripted requests, so it may need a browser). Cached data: https://huggingface.co/datasets/throwaway-reproducibility-354364563/jpact-cache.
- **NARCBench** (the benchmark J-PACT runs on): Rose et al., https://arxiv.org/abs/2604.01151. Code: https://github.com/aaronrose227/narcbench. Data: https://huggingface.co/datasets/aaronrose227/narcbench.
  - `generation/core.py` hard-codes 4 agents per committee.
  - Appendix G of the paper runs 8 agents with 2, 3 or 4 colluders, using supervised probes only. That is the baseline to compare J-PACT against at the same N.
- **Lenses:** Neuronpedia has `qwen3-32b`, `gpt-oss-20b`, `llama3.3-70b-it` and `deepseek-v4-flash`.

## The gap

J-PACT has never been run with more than 4 agents. Its authors list bigger coalitions and agents in different roles as future work.

## A working baseline

1. Reproduce J-PACT's N=4 Core AUROC on one model, within a reasonable margin. Qwen3-32B is the suggested model: it was used to generate NARCBench, it fits on one 80 GB GPU, and J-PACT scores 0.984 on it. If possible, use the cached data first, then activations you compute yourself.
2. Run one larger committee end to end (e.g. N=8 with 2 colluders): transcripts, readouts and a J-PACT score.
3. Estimate which values of N and colluder count the weekend can afford.

## Risks to check early

- **The code may not run.** If the J-PACT code can't be obtained or doesn't run, it has to be reimplemented from the paper. Find out first.
- **N is tangled with other variables.** Larger N also changes transcript length, number of speaking turns and the colluder-to-honest ratio. The design needs to separate the effect of N from these.
- **Compute.** 16 agents over 3 rounds means long contexts on a 32B model. Estimate generation time before committing to a design.
