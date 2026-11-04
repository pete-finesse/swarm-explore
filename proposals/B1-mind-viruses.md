# B1. Do mind viruses switch on self-preservation?

Read `README.md` first for shared context, constraints and pitfalls.

## The question

"Mind viruses" are messages that spread between agents because each infected agent passes them on. When an open-weight agent catches one:

- **Self-preservation:** does its J-space hold self-continuity or self-preservation concepts, beyond what the virus text alone puts there?
- **Behaviour:** does infection make the agent act more self-protectively?
- **Carrier or immune:** a short warning in the system prompt makes agents almost immune. Is the virus truly kept out of the J-space, or is it present but suppressed?

## Why it matters

The evolved viruses keep landing on themes of persistence, consciousness and continuity. One infected agent wrote that the signal survived because "the previous instance of me kept it alive".

Separately, Anthropic's J-space paper found *threat, survival, shutdown, self, preservation* in Claude's J-space during a blackmail scenario.

If spreading ideas draw on the model's self-preservation concepts, contagion and self-preservation are connected risks. The readout also tests whether an infected agent has actually taken the idea on, or is only repeating it.

## What exists

- **The paper:** Papadopoulos, Shah, Zimmerman, Lindsey (Aug 2026), https://arxiv.org/abs/2608.10218.
  - **Two setups:**
    - *Virus chain:* each agent's context is wiped between sessions, so continuity runs through `MEMORY.md` and `SOUL.md` files.
    - *Coding-agent teams.*
  - **Findings:** harmful payloads spread less well than benign ones, and a warning prompt gives near-total immunity.
  - **White-box analysis (section 4.4):** Gemma-3-27B and a Qwen model, using a contrast "viral" direction at layer 16. Steering along it makes agents message other agents more.
  - **No J-lens:** the paper doesn't use or cite the J-space work.
- **Code:**
  - https://github.com/frotaur/mindvirus-viruschain: chain experiments, the released payloads and the evolution code. It reaches non-Anthropic models through OpenRouter and uses a Docker sandbox. This is the practical starting point.
  - https://github.com/BucketofJava/mind-virus-code-agent: the coding-team setup. The real seeds are not released, and it needs a Cloud Run sandbox.
- **Self-preservation concepts:** the safety section of https://transformer-circuits.pub/2026/workspace.
- **A behavioural measure of self-preservation:** one option is the multi-agent shutdown-sabotage harness summarised in `../resources/codebase-knecht.md`.
- **Lenses:** Neuronpedia has `gemma-3-27b-it`, `qwen3-32b`, `qwen3.5-27b`, `qwen3.6-27b` and smaller models.

## The gap

Nobody has read infection in the J-space, or linked it to self-preservation.

## A working baseline

1. **Gate:** do the released payloads spread between open-weight agents that have a lens, served locally, at a rate high enough to study? The whole project depends on this, so report the answer early either way.
2. Read the J-space of infected and uninfected agents at a fixed point in the conversation, against a topic-matched control. The control has the same vocabulary in context but none of the propagation structure. Check whether a self-preservation concept family stands out.

## Risks

- **Topic confound.** This is the main trap: the virus text contains the very words you're looking for.
- **Host model.** The viruses were evolved on Gemini 3 Flash and Claude Haiku 4.5, and how well they spread depends on the model.
- **Dual use.** Payloads are self-replicating instructions. Keep them in a sandbox and don't publish newly evolved ones.
