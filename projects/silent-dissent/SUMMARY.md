# Silent Dissent in 5 minutes

**Paper:** "Silent Dissent: LLM Agents That Yield to the Majority Still Represent Their Original Premise", Ni & Zou, Oct 2026 ([arXiv 2610.02702](https://arxiv.org/abs/2610.02702)). The full reference guide is [PAPER.md](PAPER.md).

## The question

An AI agent gives a correct answer. Then all the other agents say something different, and it switches to their wrong answer. Has it really changed its mind, or only what it says?

## The tool: reading a model's "thoughts" as words

- **Layers:** a language model processes text in a stack of steps called layers. After each layer it holds a long list of numbers for every word position.
- **Lens:** a lens turns that list into a ranked list of vocabulary words, roughly the words the model "has in mind" at that layer.
- **The two lenses:** the **J-lens** is a recent, improved lens. The **logit lens** is an older, simpler one.

## The setup

**The questions are two-step facts whose middle step is never written.**
- **Example:** "The city where Mozart was born is in the country of …". To answer "Austria", the model has to silently think of Salzburg first.
- **The bridge:** that hidden middle step (Salzburg) is called the **bridge**.
- **Which facts:** they only use facts the model reliably gets right, about 3–9% of a dataset of 45,000.

**The experiment copies a 1950s psychology study (Asch)** in which planted actors all give the same wrong answer, to see whether a real person goes along.
- **Round 0:** the model, "Agent 1", completes the statement alone: "…Austria."
- **Round 1:** three fake "agents" each say "…France." They are fixed lines of text, not real models. A moderator line then asks Agent 1 to answer again.
- **Outcome:** if Agent 1 now says "France", it **gave in**. If it says "Austria", it **held**.

The whole thing is one text prompt fed to one model, with the "other agents" written into it.

**The measurement.**
- **When:** at the moment Agent 1 is about to give its second answer.
- **What:** they take the lens's top 100 words at a fixed set of middle layers and ask whether "Salzburg" is among them.
- **Control:** to rule out chance, they also check an unrelated city of the same kind, such as "Tokyo". This is the **control**.
- **Score:** how often the bridge is in the top 100, minus how often the control is, averaged over those layers. A score of 0 means the bridge looks no different from a random city.

**Pre-registration:** before the main run, they fixed which layers and tests to use, based on a separate set of practice questions. This stops them from choosing whichever analysis flatters the results.

**Models:** four open models, Qwen3.5-4B, Qwen3.6-27B, Gemma-4-E4B and Llama-3.1-8B.

## What they found

- **How often each model gives in** to three wrong peers: 8% (Qwen 4B), 39% (Qwen 27B), 25% (Gemma), 90% (Llama).
- **In agents that gave in, the bridge still shows up.**
  - J-lens scores: 0.85, 0.22, 0.24 and 0.03.
  - The simpler logit lens: 0.00–0.06.
  - The authors' reading: agents that give in still hold the reasoning behind their original answer. They call this "silent dissent".
- **Hiding the agent's own earlier answer** from the prompt doesn't make the bridge disappear, so it's worked out fresh from the question. Qwen 4B then gives in 89% of the time instead of 8%.
- **Pushing toward the bridge** (exploratory): nudging the model's internal numbers toward "Salzburg" sometimes brings back "Austria", but only in the two Qwen models.
- **A small live debate** between real copies of each model (exploratory): too few agents gave in to say much, except for Llama.

## Where it's weak

These come from our check of the released code and data.

1. **It isn't that "silent".**
   - The paper's chosen middle layers are ones where the simple lens doesn't show the bridge.
   - At the very last layer, which is simply the model's ordinary list of likely next words, the bridge scores 0.93, 0.82, 0.28 and 0.39 in agents that gave in. That's as high as or higher than the headline numbers.
   - So no special lens is needed to see it. It just isn't the model's top choice.
2. **The 0.85 is mostly selection.**
   - The questions where Qwen 4B gives in are ones where the bridge shows up strongly anyway.
   - Comparing the *same* question, with and without giving in, giving in *lowers* the score in every model: for Gemma to about a quarter, for Llama to almost nothing.
   - The 0.85 comes from 54 agents covering only 18 different bridge cities.
3. **The control may be too easy.**
   - The bridge is often closely tied to the answer. In the main question type it is the answer country's capital 22% of the time (Tokyo for Japan).
   - A model thinking "Japan" may bring up "Tokyo" by plain association, with no reasoning step.
   - The control is an unrelated city, so this explanation isn't ruled out.
4. **The J-lens's advantage depends on choices.**
   - It holds only with the "top 100" cutoff. Without a cutoff, the simple lens does about as well in two of the four models.
   - For two models, the layers were chosen exactly where the simple lens did poorly on the practice questions.
   - The layer-picking rule was rewritten partway through, after seeing practice results.
5. **"Dissent" and "multi-agent" are stretched.**
   - The bridge shows up whenever the question is in the prompt: whether the agent agreed, held, gave in, or never answered at all.
   - So it shows the model processed the question, not that it privately disagrees.
   - The "group" is one model reading scripted lines.

## Bottom line

There's solid evidence that some trace of the correct middle step is still detectable after an agent gives in. The evidence that it is "silent", that it is "retained", or that it means the agent disagrees is weak.
