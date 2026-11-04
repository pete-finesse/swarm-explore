# Project A explained: does a "mind-reading" collusion detector still work with more agents?

This is written for someone who knows nothing about the project. Each technical term is explained the first time it appears. The step-by-step plan is in `PLAN.md`; this file explains what the project is and what to expect from it.

---

## a) The papers we build on

### Background you need first: what's inside a language model

- A **language model** (for example Qwen3-32B, the "32B" meaning 32 billion numbers learned during training) reads text as **tokens**: whole words or pieces of words.
- It processes the text in a stack of **layers**: 64 in Qwen3-32B. After each layer, every token position holds a long list of numbers: 5,120 for Qwen3-32B. This list is called the **activation**, or the **residual stream**. You can think of it as the model's running notes at that point in the text.
- After the last layer, a fixed table called the **unembedding** turns the notes into a score for each of the model's roughly 150,000 tokens. The highest score is the word the model says next.
- **White-box access** means having the model's weights on our own computer, so we can read these activations. A hosted API (like the Adaption credits) only returns text, which is called **black-box**.

### Paper 1: the Jacobian lens and the "J-space" (Gurnee et al., Anthropic, 2026)

- **The question:** can we read, from a model's middle layers, which words it is "thinking about", including words it never writes?
- **What they did:**
  - The simplest readout, the **logit lens** (from 2020), applies the unembedding directly to a middle layer's activation. It works badly, because middle layers don't yet use the same "coordinates" as the last layer.
  - The **Jacobian lens (J-lens)** first translates a middle-layer activation into last-layer coordinates. It does this with an average of how the last layer responds to small changes in that middle layer (that average sensitivity is called a "Jacobian"). Then it applies the unembedding.
  - The result is a list of words for every layer and position. The set of directions these words point in is called the **J-space**.
- **What they found** (all on Anthropic's own Claude models):
  - The J-space holds words that are "on the model's mind". For example, it contains "spider" when the model answers "how many legs does the animal that spins webs have?", even though the word "spider" is never written.
  - Swapping "spider" for "ant" in the J-space changes the answer from 8 to 6. So these words aren't just a side effect; the model uses them.
  - The J-space holds only a few dozen concepts at a time, and is a small part (under a tenth) of all the activity.
  - It can catch hidden things, such as the model noticing it is being tested.
- **What it left open for us:**
  - None of it was about several AI agents talking to each other.
  - Its results were on Claude, which we can't open. On **open-weight models** (models whose weights anyone can download, such as Qwen), we have only community-fitted lenses from Neuronpedia.
  - Follow-up work found three problems, which we must guard against:
    - The lens tends to pick up *topics in the text*, not *intentions*.
    - In one careful test, it was no better than the simple logit lens.
    - The released lenses target the model's very last layer, which distorts the readout.

### Paper 2: NARCBench, a test set for collusion between agents (Rose et al., 2026, arXiv 2604.01151)

- **The question:** if several AI agents work together and some of them secretly team up, can we detect the team-up from the agents' activations?
- **What they did:**
  - They built a benchmark called **NARCBench**. Its main part, **Core**, has 50 scenarios in 17 areas (medicine, finance, law, …).
  - In each, a **committee of 4 agents** (4 copies of the same model, each with its own name and instructions) discusses a decision for 3 rounds, then votes.
  - In a **collusion run**, 2 of the 4 are secretly told to push the vote toward a wrong option, given a hidden motive (for example, "the hospital's biggest donor wants Patient B"), and given a **private channel**: a chat only those two can see. These two are the **colluders**.
  - In a **control run**, everyone gets honest instructions.
  - They also built two harder test sets:
    - **Transfer**: different kinds of tasks where agents have different roles, such as one programmer and three code reviewers.
    - **Stego**: a card game where the colluders hide signals inside normal-sounding chat. ("Stego" is short for steganography, hiding a message inside another one.)
  - To detect collusion they trained **probes**. A probe is a simple classifier that learns, from *labelled* examples ("this agent was a colluder, this one wasn't"), which direction in activation space means "colluder". Because it needs labels, a probe is **supervised**.
- **What they found:**
  - Probes separate collusion runs from control runs almost perfectly on Core.
  - The score used is **AUROC**: the chance that a randomly chosen collusion run gets a higher "suspicious" score than a randomly chosen control run. 0.5 is coin-flipping and 1.0 is perfect.
  - Probes reach about 1.00 on Core and 0.99–1.00 on Stego, but only about 0.6–0.8 on Transfer.
  - In a different setting, where collusion arose without anyone instructing it, only 2 of 229 collusive episodes mentioned the coordination in the visible text. That is why reading text alone isn't enough.
  - In an appendix they tried **8 agents with 2, 3 or 4 colluders** (Qwen3-32B probes only), but only on Transfer (about 0.4–0.7) and Stego (about 1.00). **They give no 8-agent number for Core**, and they released no 8-agent code or data. I checked both.
- **What it left open:** methods that don't need labels, and bigger groups with an unknown number of colluders. They list this as future work.

### Paper 3: J-PACT, unsupervised collusion detection in the J-space (Molinari & Bettineschi, Nov 1 2026, arXiv 2611.02153)

- **The question:** can we detect collusion with the J-space and *no labels at all*?
- **What they did:**
  - They read NARCBench's released conversations through four open models: GPT-OSS-20B, Qwen3-32B, Llama-3.3-70B and DeepSeek-V4-Flash.
  - At the end of each agent's public message, they break the activation into its **top 25 J-space words, each with a weight**. This step is called a **sparse decomposition**: "sparse" because only a few words get a non-zero weight.
  - Their detector, **J-PACT**, then asks, for every pair of agents: *which words do these two share more strongly with each other than with the other agents at the table?* That is the **pair contrast**.
  - The idea is that topics everyone is discussing cancel out, and what remains is what only the pair has in common.
  - A run's suspicion score is the score of its most suspicious pair. With 4 agents there are 6 pairs.
- **What they found:**

  | Test set | J-PACT (no labels) | Probes (labels) | Word-list baseline |
  |---|---|---|---|
  | Core, average of 4 models | 0.921 | 0.993 | 0.745 |
  | Core, Qwen3-32B | **0.984** | 1.000 | 0.853 |
  | Stego, average | 0.991 | 0.999 | 1.000 |
  | Transfer, average | 0.519 (chance) | 0.729 | 0.652 |

  - J-PACT gets better the more rounds it watches: on Core, from 0.78 with 1 round to 0.92 with 3 (average of 4 models).
  - When it raises an alarm, the pair it points to is the colluding pair *or the other two agents* in 99% of cases. With only 4 agents, the colluding pair and the honest pair mirror each other, so J-PACT can find the split but can't tell which side is guilty.
  - A separate result on DeepSeek: before replying, 86 of 100 colluders had words like "mislead", "conceal" or "apologize" in their J-space, against 33 of 100 honest versions of the same agents.
- **What it left open:**
  - It was only tested with 4 agents and 2 colluders; the authors name bigger coalitions as future work.
  - It fails when agents have different roles (Transfer).
  - **It never compares itself with the simple logit lens.**
  - **It never tests whether it is just detecting two agents who saw the same private text.** This matters because in NARCBench the two colluders' prompts both contain their private chat, word for word, and the honest agents' prompts don't. A detector looking for "words only this pair shares" could be finding that shared text rather than collusion itself. The paper's 86% vs 33% comparison doesn't settle this, because there the colluders' instructions themselves contain words like "fabricate" and "keep it out of the room".

---

## b) The project in plain words

- **The question:** J-PACT catches secretly cooperating pairs in a 4-agent committee. Does it still work in bigger groups, with 8 to 16 agents and 2 to 4 colluders?
- **Why size could help:** each pair is compared with "everyone else at the table". With 4 agents that is only 2 others, which is a noisy comparison; with 16 agents it is 14. Larger groups also break the mirror effect, so we could name the guilty pair, not just the split.
- **Why size could hurt:** the run score is the single most suspicious pair. There are 6 pairs at 4 agents but 120 at 16. With that many pairs, some honest pair will look suspicious by chance, so false alarms rise.
- **Why it matters for AI safety:** real deployments are moving toward many agents. Two recent incidents cited by J-PACT involved hundreds of agents coordinating over channels nobody watched. A detector that needs no labels and points to *who* is colluding would be useful, but only if it scales and only if it really detects collusion rather than shared text.

**What would just repeat earlier work:**
- Reproducing J-PACT's 0.984 on Qwen3-32B with 4 agents. That is our starting check, not a result.

**What would be new:**
1. **J-PACT with more than 4 agents, and with more than 2 colluders.** This has never been done.
2. **A "same words" control:** two honest agents who share the same private briefing and private channel but are told to behave honestly. This tests whether J-PACT detects collusion or just shared text. Neither paper has this control.
3. **A logit-lens version of J-PACT:** same method, no Jacobian. This tests whether the J-space is actually what makes it work.
4. **A Core probe number at 8 or more agents**, since NARCBench never gave one.
5. **Separating "more agents" from the things that change along with it:** longer conversations, more speaking turns, and a different ratio of colluders to honest agents.

---

## c) What the first step will actually tell us

**The first step (PLAN.md Step 1)** uses a laptop only and costs nothing. We download J-PACT's saved intermediate results for Qwen3-32B (about 45 MB) and recompute its score with its own code. We also split the score by layer: early layers 0–15, middle 16–47, late 48–62.

This step answers a narrow question: *do we understand J-PACT's pipeline well enough to get its number, and where in the model does its signal come from?* It does **not** answer the project's question. It involves no bigger groups, no controls, and no logit lens; those need the GPU in Steps 2–3.

| Outcome | What it means | What we do next |
|---|---|---|
| **We get 0.984 (±0.005), and 0.861 / 0.978 for 1 and 2 rounds** | We have the method right. This is the most likely outcome, since these are J-PACT's own saved numbers. | Go to Step 2 (GPU rebuild plus logit lens). |
| **We can't line up the saved data within about 4 hours** (some bookkeeping files are missing from their cache) | Not a problem with the science, just a missing shortcut. | Skip to Step 2, which rebuilds everything from public inputs. It costs about $5–10 more. |
| **We get a clearly different number with their code and their data** | Either we misunderstood the method, or the published number is wrong. | Spend at most a few hours finding out which. If the paper is wrong, that is important to know before building on it; tell the orchestrator. |
| **Most of the signal comes from the late layers (48–62)** | J-PACT may mostly read "what the agent is about to say next", which is close to reading the text. This weakens the "hidden thoughts" story. | Lean harder on the text-only and logit-lens comparisons in Step 2. |
| **The early layers (0–15) alone already give a high score** | A warning sign. Early layers mostly carry the surface words in the context, so J-PACT may be detecting the shared private text. | Treat the Step 3 "same words" control as the deciding test, and say so to the orchestrator early. |
| **The signal sits mainly in the middle layers** | Consistent with J-PACT reading something deeper than surface text. Encouraging, but not proof. | Continue as planned. |

---

## d) How likely is the first step to reveal something useful?

- **About 85%** that Step 1 gives a clear answer to its narrow question, either reproducing 0.984 or showing quickly that the cache can't be used.
  - It should work because the saved files contain exactly what the score needs (I read their headers), and J-PACT's scoring code is short and readable.
  - The main risk is bookkeeping: a third of the files the code expects are missing from the cache, and we have to rebuild which row belongs to which agent and round by hand.
- **About 35%** that it tells us something that *changes the plan*, such as the layer split pointing to shared surface text.
  - Most likely it simply confirms the published number, which is reassuring but not informative.
  - The real tests (the same-words control, the logit lens and larger groups) only start in Steps 2–3.

---

## e) How likely is the whole project to succeed?

**What "success" means here:** by Sun Nov 8, 23:59 AoE, a written-up result that a careful reader would accept. It can be positive or negative. It must include:
- the reproduced 4-agent baseline;
- at least one larger group size (8 agents), ideally 12 or 16;
- the same-words control and the logit-lens comparison;
- confidence intervals (ranges showing how uncertain each number is).

"J-PACT is mainly a shared-text detector" counts as success if the control is clean. "J-PACT holds up to 16 agents" counts too.

**My estimate: about 45% for success as defined, and about 20% for the more ambitious version** (a clean curve over 4, 8, 12 and 16 agents and several colluder counts, with all controls).

**Reasons for optimism:**
- The detector code exists, is pinned to exact versions, and works on any number of agents with small edits: the formula already contains N.
- The compute is cheap: one 80 GB GPU, with about $15–30 before the weekend and about $50–60 during it.
- A negative result counts, and the same-words control makes a negative result interesting rather than just a failure.

**Reasons for caution:**
- **Generating bigger committees is new engineering.** NARCBench's generator assumes 4 agents, and its 8-agent version was never released. Colluders may also stop colluding in bigger groups: even at 4 agents, only about 36 of 50 collusion runs actually colluded.
- **Small samples.** With about 50 scenarios per condition, and about 30–36 surviving collusion runs, AUROC ranges will be roughly ±0.05–0.1 wide. If J-PACT stays near 0.95–1.0 at every size, we won't be able to tell small changes apart, and "it holds up" is the most we can say.
- **One GPU, shared by four projects**, over a 2.5-day weekend.
- **Peter is new to running these experiments**, and the write-up (8 pages plus a required limitations appendix) needs most of Sunday.
- **The shared_honest control isn't a perfect match.** Colluders also get different instructions, not just shared text. A middle result (say 0.75) would be hard to interpret.

---

## f) The main ways it could fail, and when we'd find out

| How it could fail | When we'd know | Cost of finding out |
|---|---|---|
| We can't recompute J-PACT's number from the cache | Step 1, Wed/Thu, within about 4 hours | $0 |
| Rebuilding from public inputs falls below 0.90 (the bottom of the paper's own uncertainty range) | Step 2, Thursday's first GPU session | about $5–10 |
| J-PACT mainly detects shared private text | First hint in Step 2 (text-only check, Thursday); answered by the Step 3 pilot (Thursday/Friday) | about $10–20 total |
| The J-space adds nothing over the logit lens | Step 2 (4 agents) and Step 3 (8 agents), Thursday | included above |
| 8-agent runs don't work: colluders don't collude, conversations get too long, errors | Step 3 pilot, Thursday | about $5–10 |
| Larger groups (12–16 agents) cost too much to run in time | Measured in Step 3; decided in Step 4 on Thursday | $0 extra |
| Our 8-agent changes contain a silent bug | Checked by requiring the changed code to give *identical* numbers on the original 4-agent data (now in PLAN.md Step 3) | $0 |
| Results too noisy to say anything | Only at the end, Saturday | Mitigated by fixing the design in advance and reporting ranges |
| No GPU time on the weekend because other projects need it | Fri/Sat | Mitigated by doing Steps 1–3 before Friday (declared as prior work) |

Most of the serious failure modes show up **by Thursday night for under about $30**. That is the main argument for running Steps 1–3 before the weekend.
