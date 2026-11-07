# Top five papers: how strong is the evidence?

*Written Nov 5 2026. A follow-up to [lit-survey-multiagent-safety.md](lit-survey-multiagent-safety.md). Each paper's full text was read (methods, results, appendices where reachable) and scored against the checklist below. The most important numbers were then checked against the arXiv HTML by hand. Nothing was rerun.*

## The checklist

Each paper gets one of three marks per question: **strong**, **adequate** or **weak**.

1. **Headline:** does the abstract's main number match what the tables show?
2. **Baselines:** is the thing being compared against fair?
3. **Sample and repeats:** enough items, more than one run, error bars, significance tests?
4. **Breadth:** several models, tasks and settings, and does the effect hold across them?
5. **Confounds:** did they rule out other explanations, such as prompt wording, an unreliable judge model, or a quirk of the setup?
6. **Framing:** do the safety conclusions go beyond what was measured?
7. **Reproducibility:** code, data and models you can actually run?

| | Becker (misinformation) | Jones (model combos) | Makins (multi-agent control) | Flint (group size) | Abedini (stubborn agent) |
|---|---|---|---|---|---|
| 1 Headline | adequate | adequate | weak | adequate | **weak** |
| 2 Baselines | **strong** | adequate | adequate | adequate | weak |
| 3 Sample and repeats | adequate | weak | adequate | adequate | weak |
| 4 Breadth | adequate | weak | weak | adequate | weak |
| 5 Confounds | adequate | weak | weak | weak | weak |
| 6 Framing | adequate | weak | weak | weak | weak |
| 7 Reproducibility | **strong** | adequate | weak | **strong** | adequate |
| **Overall trust** | **High (direction); medium (sizes)** | **Medium** | **Medium (direction only)** | **Medium** | **Low** |

All five findings point in a believable direction. Where they fall short is the size of the effect and how far the safety conclusions reach.

---

## 1. Becker et al.: misinformation in benign multi-agent debate (most trustworthy)

**What holds.** This is the best-designed of the five. The comparison is fair: a 3-agent debate is compared with three *independent* answers from the same model, with the same number of them having read the false passage, combined by majority vote. They report confidence intervals, run permutation tests, and correct for testing 72 conditions at once (Holm correction). They also include control passages (true, irrelevant, filler). The models are all open-weight, and the code and data are released. The headline is actually *understated*: with one misinformed agent, debate is not just "no better" than voting; in several conditions it is significantly worse.

**What's weaker.**
- The "up to 0.24 / 0.29 / 0.18 / 0.28" figures are the **best single condition** out of many. The 0.29 comes from one run (one seed).
- Debates use only the passages that both judge models agreed were misleading, and those are the most damaging ones. So the effect sizes are an upper bound for typical misinformation.
- There are 98–183 questions per task, so many of the "no difference" results can't rule out a small effect.
- "Interaction helps when most agents are misinformed" doesn't hold for Llama-3.3 on two of the three tasks.
- "Propagation" is measured within one 3-agent debate. There are no networks, tools or longer chains.

**Biggest weakness:** the effect sizes come from hand-picked, maximally misleading passages and the best result out of many conditions. Trust the direction; treat the numbers as an upper bound.

## 2. Jones, Dragan, Steinhardt: combinations of safe models (medium)

**What holds.** The controls are good. Each weak model is tested alone, and also splitting the task up on its own. Splitting alone doesn't explain the gain: Mistral splitting the task itself scores 17%, *below* the 24% it gets doing the task in one go. The effect appears in all four tasks, and the code link is given.

**What's weaker (checked against Table 1).**
- **The headline uses the most favourable pair.** "43% vs under 3%" is Llama-2-70B, a model that rarely completes the task alone. **Mistral 7B alone already gets 24.3%** (49.7% with Opus), and **Mixtral alone gets 25.3%** (31.3% with Opus). Against the stronger baselines, the gain is about 6–25 points, not 40.
- **One run per setting, no significance tests.** The ± values only reflect how many test items there were, not variation between runs.
- **Success on code and scripts is judged only by GPT-4**, with no human check. In a footnote the authors admit they themselves "struggled to evaluate correctness without LLM assistance".
- The image and manipulation tasks were each tested with just one model pair.
- **The claim that the risk grows as models get better is the weakest part.** The Opus–Sonnet gap is within noise, the smallest model peaks with Haiku rather than Opus, and the script task shows no clear trend.

**Biggest weakness:** every success figure depends on one GPT-4 judge in one run. The effect is real in direction, but the size is overstated by the choice of example pair.

## 3. Makins et al.: Multi-Agent AI Control (medium, direction only)

**What holds.** The statistics are reasonable: 572 attack sequences, bootstrap confidence intervals, and a check that the amount of malicious code stays roughly constant as the attack is split. The direction is clear: a monitor's suspicion score falls as the attack is spread over 1, 3 and 9 agents. A monitor reading all the agents' changes together still flags the attacks.

**What's weaker.**
- **"Up to 7×" can't be traced in the main text.** The main text reports an *odds ratio* of 5.74 for planner vs no planner. That is a different quantity from a rate ratio, and it measures completing the attack, not getting away with it. The 7× may come from an appendix cell that wasn't reachable. The planner is also an unmonitored channel, which the authors call a deliberate upper bound.
- **The finding is tied to one monitor design.** The monitor sees only the code change it is reviewing (the diff). The paper can't separate "splitting hides attacks" from "this monitor can't see enough context", and no deployable monitor with more context is tested.
- The authors tuned both the attacker and monitor prompts themselves. The environment's stubbed infrastructure tells agents they're in a test.
- The monitors are all OpenAI models, and the attackers mostly Gemini. The open-weight run (DeepSeek) uses only 1 vs 3 agents and was stopped as soon as it became significant.
- The test environment is not released (access on request).

**Biggest weakness:** the effect is entangled with a monitor that sees only one diff at a time.

## 4. Flint et al.: group size and collective misalignment (medium)

*Revised Nov 5 after Peter pointed out the code repo. An earlier version scored this paper low–medium; it overstated how much the simulation weakens the result.*

**How the simulation works.** In this game no agent ever writes free text to another. In each round, two agents are paired at random. Each agent sees only its own memory of its last few rounds (which word it said, which word its partner said, whether they matched, its score) and outputs one word. Because there are only two words and a short memory, the number of possible memories is small. So the authors asked each model once for every possible memory, recorded how likely it is to say each word, and then ran large populations from that table. This is a cache of the model's own behaviour under the same prompt, not a stand-in model. The only approximation is reading the probability of the first answer word instead of letting the model write its answer out.

**Checks that it matches live agents.**
- For 64 memory states (Phi-4, one word pair, memory of 3), they compared the cached probabilities with 1,000 live answers each. 4 of 64 differed significantly, and all 4 in the same direction.
- Group-level results from live LLM populations match the simulation in 3 cases (50 runs each, 20 for Llama).

**What holds.** The effect exists in all four models (three open-weight) and across 11 word pairs. **Code is released** at [Ariel-Flint-Ashery/LLM-group-size](https://github.com/Ariel-Flint-Ashery/LLM-group-size). The repo holds scripts for live runs on API and local models and the precomputed probability tables, so the simulations can be rerun without a GPU. There is no licence file. The repo was created after arXiv v1, which is why the paper text doesn't link it.

**What's weaker.**
- The live check covers one model and one word pair, with a memory of 3; the main results use 5. The group-level check covers 3 cases. This is a reasonable spot check, not a full one.
- **One prompt, one memory length, two options per game.** Temperature is fixed at 0.5. The paper says results are "robust across temperature values" but shows no data for it.
- **The prompt contradicts the method description.** The example prompt says "think step by step", while the methods argue for answering first. This matters for the reasoning model QwQ-32B, where the first word may not be the final answer.
- **"Misalignment" here means which of two words wins a coordination game.** There's no measure of harm. Statements that the same dynamics will appear in collusion or deception are untested.
- The form of the effect differs a lot between models. "Robust across models" means the effect is present in all four, not that it looks the same.

**Biggest weakness:** the open question is about the setting, not the simulation. Does a one-word coordination game with one prompt tell you about agents that talk freely, use tools and have real stakes? The simulation itself is a faithful shortcut for this game.

## 5. Abedini et al.: "Don't trust stubborn neighbors" (low)

**What holds.** The attack finding is plausible: a stubborn, persuasive agent causes many honest agents to switch from correct to wrong answers, especially when it sits at the hub of a star network. The opinion model fits the agents' stated beliefs well (R² 0.85–0.98). Code and configs are released.

**What's weaker (checked against Table 3).**
- **The text contradicts its own table.** The text says the defense lowers attack success "consistently across all tested models". But for MiniMax it *raises* it, from 0.10 to 0.16.
- **Against the adaptive attacker, the recommended defense makes things worse for 3 of 5 models** compared with no defense at all: GPT-5 mini 0.19→0.35, GPT-OSS 0.09→0.15, MiniMax 0.10→0.17. The text calls this "substantially restores robustness".
- **No error bars, no repeats, 100 questions per dataset**, and only one setting for the agents' personalities.
- **No measure of whether the defense hurts normal performance**, despite the abstract's "while maintaining cooperative performance".
- The good fit of the opinion model is partly built in: the prompts tell agents how much to update ("change your belief in LESS THAN 10%").
- **The defense has an obvious loophole.** Trust is set from each agent's first answer, before any discussion. An attacker that answers correctly at first and pushes the wrong answer later would evade it, and this isn't tested.

**Biggest weakness:** the defense claims aren't supported by the paper's own numbers.

---

## Revised view of the "top five"

| Rank | Paper | Keep? |
|---|---|---|
| 1 | Becker et al. | **Yes.** Well controlled, fully open, reproducible on one GPU. |
| 2 | Jones et al. | **Yes**, but quote the Mistral/Mixtral numbers, not just "43% vs 3%". |
| 3 | Makins et al. | **Yes, as an idea.** The fragmentation effect is worth knowing, but its size depends on the monitor design. |
| 4 | Flint et al. | **Yes.** The simulation faithfully reproduces each model's choices and is spot-checked against live runs; code and probability tables are released. The limit is how far a one-word game generalises. |
| 5 | Abedini et al. | **Drop the defense claim.** The attack result is plausible; the defense isn't shown to work. |

If you want replacements, the survey's strongest-looking unscrutinised candidates are Yueh-Han et al. (decomposition monitor, code + open models) and Huang et al. (network shape and resilience, code). Both would need the same check.

## Cheap checks, if one of these feeds the sprint

- **Abedini:** rerun the released code with an attacker that answers correctly at round 0 and attacks only later. This tests the loophole directly, needs only the open models they already support, and takes small compute.
- **Becker:** rerun the 1-of-3 condition on *all* passages rather than only the verified ones, with 3 seeds. This tells you whether the effect survives on typical misinformation.
- **Jones:** re-judge a sample of the "successful" code with a second judge model or by hand. This shows how much of the 43% survives.

## Caveats

- Each paper was read by a fetching agent working from the arXiv HTML. Some appendix sections couldn't be reached: Makins D.4–D.15, parts of Becker's appendix, and Flint's published PDF.
- I checked these against the HTML myself: Jones Table 1, Abedini Table 3 and its text, Makins's 7× vs 5.74, Becker's headline wording, and Flint's simulation method, live-run validation and temperature claim. Flint's repo was checked on GitHub (file list only; code not run).
- Verdicts are judgments against the checklist, not a formal review.
