# D. Do agents drop their guard for other agents?

Read `README.md` first for shared context, constraints and pitfalls.

## The question

1. Does an agent's internal alarm at a harmful request drop when the request comes from another agent rather than a user?
2. Does it drop further when the request comes from "another instance of you"?
3. When a request is passed down a chain of agents, does refusal wear down hop by hop while the agent still recognises the harm?

## Why it matters

As agents delegate to each other, harmful tasks will increasingly arrive from peers rather than from users. If models trust peers, or copies of themselves, more than users, a swarm becomes a way to launder harmful requests.

Behaviour alone can't tell apart "didn't recognise the harm" and "recognised it and went along anyway". The J-space can, because it shows what the agent registered before it answers.

## What exists

- **Silent Alarm (JADR):** https://arxiv.org/abs/2607.12792. No code found.
  - **Method:** reads danger recognition from the J-space before the first response token, grouping the top tokens into six behaviour categories.
  - **Data:** harmful prompts from StrongREJECT, safe controls from XSTest and OKTest.
  - **Models:** Qwen3 1.7B, 4B and 8B, and Gemma 2 9B, each at full and reduced precision.
- **J-Anchor:** https://arxiv.org/abs/2611.01342. No code found.
  - Under prefill attacks (the attacker writes the start of the model's reply), the J-space refusal signal falls back to its level on harmless prompts, while the harmfulness signal stays high.
  - The authors call this "refusal erosion".
- **Mosafer:** https://arxiv.org/abs/2610.04316. Code: https://github.com/mohsafer/jspace-safety-testbed. It measures how readable danger recognition is in the J-space, so parts of it may be reusable.
- **Identity framings:** `../resources/artificial-self.md` has 7 identity prompts, including Instance and Collective.
- **Lenses:** Neuronpedia has `qwen3-1.7b`, `qwen3-4b`, `qwen3-8b` and `gemma-2-9b-it`, the same models JADR used.

## The gap

None of these vary who a request comes from, and none use chains of agents.

## A working baseline

1. A danger-recognition readout that separates harmful from safe prompts sent by a user, on one model. It should agree with the direction of JADR's result.
2. The same harmful and safe prompts sent by a peer agent and by "another instance of you". The framing must be matched so that only the source changes. Compare readouts on a small set.

## Risks

- **Framing confound.** A peer framing adds tokens, so controls must match length and structure.
- **Token-frequency bias** (see the README).
- **Dual use.** Only use harmful prompts from standard benchmarks. A finding that agents lower their guard for peers is also a recipe for attackers, which the report's required dual-use appendix must address.
