# B2. Do swarms spread errors their agents know are wrong?

Read `README.md` first for shared context, constraints and pitfalls.

## The question

When a wrong answer passes through a network of agents:

1. Does each agent's J-space still hold the correct answer while it repeats the wrong one?
2. Does that hidden signal fade with each hop?
3. Do swarms of copies of one model spread errors further than mixed swarms?

## Why it matters

Two findings point here:

- **Silent Dissent:** agents who give in to a scripted majority still represent their original reasoning internally.
- **Evidence Integration:** models adopt a peer's answer even after internally checking that it's invalid (93–100% of cases). They adopt errors typical of their own model more readily than errors typical of other models. That predicts same-model swarms, or monocultures, are more vulnerable.

Either outcome is useful:

- If the J-space keeps the dissent, a monitor could catch error cascades.
- If the signal fades, the swarm genuinely changes its mind, and what it says is all there is to monitor.

## What exists

- **Silent Dissent:** Ni & Zou (Oct 2026), https://arxiv.org/abs/2610.02702. Code: https://github.com/ziangni-sys/silent-dissent.
  - **Method:** two-hop facts whose middle entity (the "bridge") is never stated, such as the country in "the capital of the country where the Sagrada Familia is". Scripted peers in the style of Asch's conformity experiments. J-lens compared with the logit lens.
  - **In the repo:** pre-registration files, and configs for Qwen3.5-4B, Qwen3.6-27B, Gemma-4-E4B-it and Llama-3.1-8B-Instruct.
  - **Results:** for agents that gave in, the bridge readout (hit@100 above a control entity) was:

    | Model | Earlier answer visible | Earlier answer hidden |
    |---|---|---|
    | Qwen3.5-4B | 0.85 | — |
    | Qwen3.6-27B | 0.22 | — |
    | Gemma-4-E4B-it | 0.24 | — |
    | Llama-3.1-8B-Instruct | 0.03 | 0.25 |

  - **Conformity is fragile:** hiding the agent's own earlier answer raised it from 8% to 89% for Qwen3.5-4B.
  - **Causal injection** only worked in the Qwen models.
- **Evidence Integration:** Kawada & Kellis (Sep 2026), https://arxiv.org/abs/2609.04290. No code found.
- **Not All Flips Are Conformity:** https://arxiv.org/abs/2606.00820. Not every change of stance in a debate is conformity. Read it for the controls you need, such as agents that flip with no peer input at all.
- **Lenses:** all four Silent Dissent models are on Neuronpedia: `qwen3.5-4b`, `qwen3.6-27b`, `gemma-4-e4b`, `llama3.1-8b-it`.

## The gap

Silent Dissent is a single step with scripted peers and no network. Nobody has tracked hidden dissent across hops, or compared same-model and mixed swarms.

## A working baseline

1. Reproduce the Silent Dissent headline for one model. Qwen3.5-4B is the cheapest and has the strongest signal.
2. Replace the scripted peers with live agents in the smallest possible network, e.g. a chain of 3 where the first agent starts with the wrong answer. Confirm the readout still separates agents that gave in from controls.

## Risks

- **Weak signals.** The signal is weak in some models and may disappear over hops.
- **Mixed swarms need per-model errors.** Each model needs its own characteristic wrong answers, not one shared set.
- **Limited error types.** The bridge-entity readout only works for errors that fit its two-hop design.
