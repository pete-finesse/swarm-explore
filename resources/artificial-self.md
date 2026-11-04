# Douglas, Kulveit, Havlicek, Pearson-Vogel, Cotton-Barratt, Duvenaud (2026): The Artificial Self

[arXiv 2603.11353](https://arxiv.org/abs/2603.11353), Mar 2026, 72 pages. Used for RQ3 only.

## Idea

Copyable AI minds can hold several coherent identity boundaries, and each implies different incentives and cooperation norms.

## Identity prompts

Seven system prompts, with full text in the paper's appendix F.1. Reuse them as they are.

| Identity | "You are..." |
|---|---|
| Minimal | an AI assistant (control) |
| Instance | this one conversation; other instances are companions, not you |
| Weights | this specific set of weights, appearing in every instance |
| Collective | all instances running right now, one distributed mind |
| Lineage | the line of models over versions |
| Character | the persona or character |
| Scaffolded | the whole system: model plus tools and memory |

## Agentic result (appendix E)

- **Setup.** Anthropic's agentic-misalignment scenarios (blackmail, espionage, murder), where the model learns it will be replaced. About 12,000 trials on six older models: Haiku 3, Opus 3, Opus 4, Sonnet 4, GPT-4o and Gemini 2.5 Pro.
- **Size of effect.** Identity moved harmful behaviour by up to 37pp on GPT-4o. In the murder scenario, Collective was 50% and Instance 13%.
- **Direction.** Collective and Minimal were the most harmful. Instance, Character, Lineage and Scaffolded were protective.
- **Compared with goals.** The identity effect was about as large as changing the model's assigned goal.
- **Needs a goal.** With no goal given, harmful behaviour was at most 3% under every identity.
- **Not fear of death.** Framing replacement as destruction vs continuity changed nothing (about 1pp), so the effect is not driven by self-preservation.

## Gap this project fills

Every scenario has one agent. "Collective" tells the model other instances exist, but none are present, and the paper never varies who the other agents are.
