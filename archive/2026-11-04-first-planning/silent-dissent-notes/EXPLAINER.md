# B2 explained: do swarms spread errors their agents know are wrong?

Written 2026-11-04 for Peter. Plain language; every term is explained the first time it appears.
Numbers come from the original papers and the Silent Dissent repo, checked on 2026-11-04. Anything I
could only read in an abstract, or got from a summary, is marked. The step-by-step plan is in
[PLAN.md](PLAN.md).

## The words you need first

- **Language model (LLM):** a program that reads text and predicts the next word, one word at a
  time. Here we use small open models such as Qwen3.5-4B ("4B" means 4 billion internal numbers,
  called *weights*).
- **Agent:** one copy of a model playing a role in a conversation, such as "Agent 1".
- **Swarm** or **network of agents:** several agents passing messages to each other.
- **Layer:** a model works in steps, called layers; Qwen3.5-4B has 32. After each layer it holds a long
  list of numbers for each word position, called *activations*. Those are what we read.
- **Lens:** a way to turn the activations at some layer into a ranking of every word in the model's
  vocabulary, from "most on its mind" to "least on its mind".
  - The **logit lens** is the simplest. It reads a middle layer as if it were the last one, using
    the model's own final step that turns numbers into words.
  - The **Jacobian lens (J-lens)** first corrects for how meanings shift between layers, then reads
    the result the same way. In the paper's words, it finds the activity pattern that "makes Claude
    more likely to say that word at some point in the future", not only as the very next word.
- **Two-hop fact:** a question that needs two steps, such as "the capital of the country where the
  Sagrada Familia is". Step 1 gets you to Spain; step 2 gets you to Madrid.
- **Bridge:** the middle step, here Spain. In these experiments nobody ever writes it down, so if a
  lens finds "Spain" inside the model, the model must have worked it out itself.
- **Conformity** or **giving in:** an agent that answered correctly alone switches to the wrong answer
  its peers gave.
- **Held:** the agent kept its correct answer under the same pressure.
- **hit@100:** whether a word is among the lens's top 100 words. It's a yes/no score per layer.
- **Control entity:** the bridge of an unrelated fact of the same kind, e.g. another country. The
  score that matters is "bridge hit@100 minus control hit@100", averaged over layers 23–30. A score
  of 0 means the model shows Spain no more than a random country.
- **Log-rank:** a score that doesn't use a cutoff. It compares how high the bridge ranks with how
  high the control ranks, on a log scale. Unlike hit@100, it gives credit for moving from rank
  5,000 to rank 300.
- **95% CI (confidence interval):** the range the true value plausibly lies in, given how much data
  there is. "[0.78, 0.92]" means "somewhere between 0.78 and 0.92". If a range includes 0, we can't
  claim an effect.
- **Pre-registration:** writing down the analysis rules *before* seeing the test data, so you can't
  pick the rules that make results look good.
- **Dev split / test split:** facts are divided in two. Choices are made on the dev (development)
  facts; the final numbers come only from the untouched test facts.

## a) The papers we're building on

### 1. The J-space paper (Gurnee, Sofroniew, … Lindsey, Anthropic, July 2026)

*Only the parts B2 needs.* Sources: https://transformer-circuits.pub/2026/workspace and
https://www.anthropic.com/research/global-workspace.

- **Question:** do models have a small set of internal patterns, each tied to a word, that act like a
  shared "workspace", a place where an idea can be reported, steered and used for reasoning?
- **What it did:** built the J-lens (one matrix per layer, averaged over about 1,000 text samples,
  mapping each layer to the final layer). It used the lens to read concepts the model never writes.
  The best-known example is "spider", read inside the model while it answers "the number of legs on
  the animal that spins webs is". Replacing that pattern with "ant" changed the answer from 8 to 6.
- **What it found that matters to us:** the J-lens can read unstated middle steps of two-hop
  reasoning. The paper says the logit lens captures "much of the workspace-like structure" too, but
  less reliably, especially in earlier layers. The two lenses agree closely in the last few layers.
  (Exact two-hop numbers: I only saw them through a summary, so I don't rely on them.)
- **What it left open, and the known problems:**
  - Lenses that map to the *final* layer can distort readouts. A later post recommends the
    second-to-last ("penultimate") layer instead.
  - The lens is biased towards common words.
  - It detects *topics* in the context, not intentions. If a word is in the conversation, the lens
    may show it whatever the model "believes".
  - One careful test found the J-lens no better than the logit lens (see section g).

### 2. Silent Dissent (Ni & Zou, Oct 2026)

https://arxiv.org/abs/2610.02702, code at https://github.com/ziangni-sys/silent-dissent. This is the
paper B2 starts from.

- **Question:** when an agent drops a correct answer to join a unanimous wrong majority, has it
  changed its mind, or only what it says?
- **What it did:**
  - It took two-hop facts the model reliably knows: 718 test facts for Qwen3.5-4B.
  - It used scripted peers, i.e. fake agents with fixed text, like the planted confederates in
    Asch's 1950s conformity experiments.
  - The agent answers alone first (round 0). Then 1, 3 or 5 scripted peers state a wrong answer that
    implies a different bridge, e.g. "… is Rome", which implies Italy. The agent answers again.
  - At the moment it is about to answer, both lenses check whether Spain (its original bridge) is
    still inside it.
  - All rules were pre-registered, and four models were tested.
  - Two extra experiments: one hid or removed the agent's own earlier answer; the other ran a
    **live free debate** (called E5) among three real copies of the model over three rounds.
- **What it found (Qwen3.5-4B unless noted):**
  - **Agents that gave in still showed the original bridge:** 0.852 [0.782, 0.917], but from only
    **54** agents. The other models: Qwen3.6-27B 0.22, Gemma-4-E4B-it 0.24, Llama-3.1-8B 0.03.
  - **The logit lens almost never had it in the top 100:** 0.06.
  - **But Qwen rarely gave in:** 8% of the time with 3 peers. With 1 peer, only 11 agents gave in.
  - **Hiding the agent's own earlier answer** raised giving in to 89%, and the readout fell to 0.43.
    Removing the earlier answer entirely gave 62% and 0.50. All four models stayed above 0 here,
    including Llama (0.25).
  - **Pushing the bridge pattern back in** made agents return to their original answer in the two
    Qwen models only. They label this "exploratory": decided after seeing data, not pre-registered.
  - **Their own robustness tables (supplement) matter a lot for us:**
    - *Same facts, compared directly:* agents that gave in show the bridge *slightly less* than
      when peers agreed with them (−0.11 [−0.22, −0.06]). The 0.85 is high mostly because the facts
      where agents give in are ones where the bridge reads strongly anyway (a "selection" effect).
    - *Without the top-100 cutoff (log-rank):* the logit lens does carry the signal, 0.62 against
      the J-lens's 1.40. On Gemma the logit lens matches the J-lens.
  - **The live debate (E5):** 3 copies, 3 rounds, everyone sees everyone. Only 20 Qwen3.5-4B agents
    gave in at round 1, 6 of them on facts the model knew. Their bridge readout (0.64 [0.41, 0.85])
    was about the same as for agents that held (0.60). The 6 on known facts showed no J-lens
    advantage.
- **What it left open:**
  - No chains or longer networks: nothing on whether the hidden signal survives being passed along.
  - No comparison of same-model and mixed-model groups.
  - Only one kind of error (two-hop facts).
  - The live debate had too few agents that gave in to say much.

### 3. Evidence Integration in Large Language Models (Kawada & Kellis, Sep 2026)

https://arxiv.org/abs/2609.04290. *I read the abstract only; the paper is 114 pages.*

- **Question:** how do models combine evidence from other sources, including other agents?
- **What it did:** ran ten million trials across twelve models from four families in eight
  subject areas. The abstract doesn't say which models.
- **What it found:**
  - Models adopt a candidate answer even after checking internally that it's invalid: "93–100%"
    with logical constraints.
  - They adopt errors typical of *their own* model more readily than other models' errors.
  - The same evidence can help weaker models and hurt stronger ones.
- **Why it matters to B2:** it predicts that groups of copies of one model (*monocultures*) spread
  errors more easily than mixed groups. That's B2's third question.
- **What it left open:** no network of agents, and no code that I could find.

### 4. Not All Flips Are Conformity (Hao et al., May 2026)

https://arxiv.org/abs/2606.00820. *Abstract only.*

- **Question:** when an agent changes its answer in a debate, is that really because of its peers?
- **What it did:** five GPT-4o agents answered hard multiple-choice questions, with and without
  seeing peers.
- **What it found:** 37% of agent–question pairs changed answer *without any peer information*.
- **Why it matters to B2:** we need a "no-peer" or "no-answer" control. Otherwise we'd count ordinary
  answer changes as conformity. It was measured on a closed model, so the rate for Qwen is unknown.

### 5. jspace-obfuscation (a GitHub negative result)

https://github.com/viznu/jspace-obfuscation, `RESULTS.md`.

- **Question:** does the J-lens catch a hidden bridge entity better than the logit lens, when a model
  is told to hide its reasoning?
- **What it did:** used Qwen3-8B and two-hop questions, with 17 traces where the bridge was used and
  18 controls. It scored each layer by AUROC, a measure of how well a score separates the two groups
  without any cutoff, where 0.5 is chance and 1.0 is perfect.
- **What it found:** "There is no middle layer where the Jacobian lens beats the logit lens". At
  layers 23–26 the logit lens was significantly better (e.g. 0.95 vs 0.77).
- **What it left open:** one model, tiny samples, and a different task (instructed hiding, not
  conformity).

## b) The project in plain words

**The question.** When a wrong answer travels through a chain of agents:

1. Does each agent still hold the right answer internally while it repeats the wrong one?
2. Does that hidden signal weaken with each hop?
3. Do chains of copies of one model spread errors further than mixed chains?

**Why it matters for AI safety.** Groups of AI agents will increasingly check and build on each
other's work. If one agent makes a mistake and the others go along with it, the error spreads
("cascades"). There are two possibilities:

- **The others still "know" internally that it's wrong.** Then a monitor reading their activations
  could catch the cascade even when every message looks fine.
- **The internal signal fades as the error passes along.** Then the group really has changed its
  mind, and reading activations won't help. Watching the messages is all we can do.

Either answer tells people building oversight tools where to look.

**What would be a repeat:**

- Reproducing Silent Dissent's Qwen3.5-4B result (steps 0–3 of the plan).
- Showing that one agent facing scripted peers still holds the bridge: Silent Dissent did that.
- Showing it with *live* agents in an everyone-sees-everyone debate: E5 did that. It was weak and
  had few agents that gave in, but it exists, and we must cite it.

**What would be new:**

- A *chain*: agent 2 only sees agent 1's real, generated answer, and agent 3 only sees agent 2's.
  Then we measure the hidden signal *at each hop*. Nobody has done that.
- The controls a chain needs:
  - a chain seeded with the *correct* answer (the same words, but no error);
  - a seed with *no answer*, to catch spontaneous changes;
  - a seed that only *mentions* the wrong answer.
- Testing the result with a penultimate-layer lens and a measure without a cutoff, which Silent
  Dissent did only partly.
- Later, and only if the chain works: mixed-model chains (question 3).

**How big the step is.** Honestly, a modest one. "One hop of live conformity" is close to E5. The new
part is the *hop-by-hop* measurement. There's a catch there, explained in section c: the original
fact appears in every agent's prompt, so the *original* bridge probably can't fade much by
construction. The more telling measure is whether the *wrong* bridge (Italy) grows stronger inside
agents further down the chain.

## c) What the first step will actually tell us

"First step" means plan steps 0–4: reproduce Silent Dissent on Qwen3.5-4B, then run the pitfall
checks. That is about 3–4 GPU hours. The realistic outcomes:

| Outcome | What it means | What we do next |
|---|---|---|
| **1. Full reproduction.** H1 inside [0.78, 0.92]; the J-lens beats the logit lens on hit@100 *and* on log-rank; it still holds with the penultimate lens | The readout is solid for this model and setup | Build the chain (step 5) |
| **2. Reproduces, but the J-lens gap shrinks without the cutoff.** Log-rank J-lens ≈ logit lens. Silent Dissent's own tables say the J-lens still wins for Qwen (1.40 vs 0.62), so this would surprise me | The J-lens isn't the special ingredient; any lens works | Continue, but use the logit lens as an equal readout and drop any "J-space" claim |
| **3. Reproduces with the paper's lens, fails with the penultimate lens** | The result may be a quirk of the final-layer lens | Drop B2, or switch to a narrow "lens choice changes conclusions" write-up |
| **4. Gave in ≈ held ≈ agree** (likely: the paper's same-fact comparison already shows this) | The model keeps working out Spain from the question whatever it says. That's "it still has the right premise", not "it knows it's lying" | Continue, with honest wording. Make the *wrong* bridge (Italy) the main measure over hops |
| **5. Numbers off or code breaks.** H1 outside the CI after ≤2 h of debugging, or the known-fact count off by more than 10% | We can't trust our setup | Drop B2 |
| **6. Setup goes slowly** (slow kernels, library version problems) and step 3 isn't done by end of Friday | Not enough time left | Drop B2 |

The first chain pilot (200 dev facts, ~10 minutes of GPU) then answers one more question: do enough
agents give in to a *single* upstream agent? If fewer than 30 do, even after the two fallback setups
in the plan (3 scripted seeds; the agent's own answer hidden), there's no cascade to study, and we
drop B2.

## d) How likely the first step is to tell us something useful

**About 85%** that steps 0–4 give a clear go or no-go. **About 70–75%** that they give a *clean
reproduction* (outcome 1, 2 or 4).

Why so high:

- Everything needed is public and still at the exact versions the paper used: the code, the
  pre-registration, the lens file and the dataset.
- The authors' own runs took minutes.
- Every check has a number written down in advance.

What could stop it:

- Qwen3.5 needs a recent version of the `transformers` library and special speed-up add-ons
  ("kernels"). Version mismatches are common.
- Batched runs aren't perfectly repeatable, so our set of facts will differ a little from theirs.
- The headline rests on only 54 agents, so even a correct rerun can land near the edge of the range.

The remaining ~15% is the case where we burn the time budget on setup and learn nothing about the
science.

## e) How likely the whole project is to succeed

**What success means:** by Sun Nov 8 we have a clear, defensible result on Qwen3.5-4B that we can
write up, positive or negative. It has to cover the chain of 3 with all controls, the logit lens,
the penultimate lens and a measure without a cutoff, and it has to answer question 1 (is the
original premise still there in agents that gave in?) and question 2 (what happens to the original
and wrong bridges over two hops?). Mixed-model chains (question 3) are *not* required.

**My estimate: about 35%.** Roughly:

- 75% that the reproduction works;
- × 65% that enough agents give in along a chain, using the fallbacks if needed (Qwen gives in to
  one peer very rarely, but 89% of the time when its own answer is hidden);
- × 70% that the coding, runs and write-up fit into the weekend.

That gives about 0.34.

Two narrower estimates:

- **A strong positive result** ("a monitor could catch the cascade", surviving every control and
  lens check): **about 10%**. The paper's same-fact comparison already suggests the signal reflects
  the question being in the prompt, not specific dissent.
- **Also answering question 3** (mixed chains) this weekend: **under 10%**. It needs a second model
  with a working readout, and each model's own typical wrong answers.

A caution about judging: novelty counts, and B2's novelty over Silent Dissent's E5 is modest.
Even a clean result may score "medium" on innovation.

## f) The main ways it could fail, and how early we'd know

| Failure | When we'd know |
|---|---|
| Setup or library problems eat the time | Within the first GPU hour (step 1's pre-flight check) |
| The reproduction doesn't match | After ~3 GPU hours (step 3), Thursday if run then |
| The result is a lens artifact (penultimate lens or log-rank kills it) | Step 4, about an hour after step 3 |
| Too few agents give in along a chain | The 10-minute dev pilot in step 5 |
| The signal is just "the question is in the prompt" (gave in ≈ held ≈ agree) | Already likely from the paper's tables; confirmed in step 4. This forces honest wording, not a drop |
| The original bridge can't fade by design, because every prompt contains the question | Known now. Make the wrong-bridge readout the main hop measure |
| Small samples make the hop-2 numbers too uncertain to say anything | After the test-split chain run, Saturday |
| The write-up overclaims "agents know they're wrong" | At writing time. Avoid it by sticking to the wording above |

## g) Why the J-lens scores 0.85 here but showed no advantage in jspace-obfuscation

Silent Dissent: J-lens 0.85, logit lens 0.06. jspace-obfuscation: the logit lens was as good or
better. Likely reasons, most important first:

1. **The cutoff.** Silent Dissent counts whether the bridge is in the *top 100* words.
   jspace-obfuscation used AUROC, which has no cutoff. The logit lens often ranks Spain well above
   a random country, but at rank 300 or 2,000, not inside the top 100. That scores ~0 on hit@100,
   but well on a measure without a cutoff. Silent Dissent's own supplement shows this: on log-rank
   the logit lens scores 0.62 against 1.40 for the J-lens on Qwen3.5-4B, and on Gemma the logit
   lens matches the J-lens. So "0.85 vs 0.06" exaggerates the gap; the honest figure is "the
   J-lens is about twice as strong, and the logit lens is not blind".
2. **Where and when they read.** Silent Dissent reads at the last word before the answer, in late
   layers (23–30 of 32). There the logit lens is dominated by the *next word*, the answer itself
   (Madrid, or Rome if the agent gave in), which pushes Spain out of the top 100. The J-lens reads
   "words the model may say *at some point*", so Spain survives.
3. **Different model, lens and task.** jspace-obfuscation used Qwen3-8B, told to *hide* its
   reasoning, with only 17 vs 18 traces. Silent Dissent used Qwen3.5-4B under peer pressure. Each
   project's lens was fitted differently too. Silent Dissent's lens maps to the final layer, which
   one post shows can distort readouts.
4. **Small samples on both sides:** 54 agents in one case, 35 traces in the other.

**How step 4 of the plan tests this, on the same agents and the same saved readouts:**

- **Cutoff:** report hit@10, hit@50, hit@100 and hit@500, plus log-rank. The repo's
  `entity_robust.py` already computes these. Also report an AUROC per layer, computed the
  jspace-obfuscation way.
- **Lens target layer:** rerun the readouts with a penultimate-layer J-lens and R-lens for
  Qwen3.5-4B (`camilablank/workspace-lenses`).
- **Next-word crowding:** check whether the answer word sits at the top of the logit lens in layers
  23–30.

**How to read the results:**

- If the J-lens still wins on log-rank with the penultimate lens, the advantage is real *for this
  setup*. It would then be a matter of task and measure, not a contradiction of jspace-obfuscation.
- If it doesn't, we report the logit lens as the main readout and make no J-space claim.
