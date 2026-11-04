# J-PACT in 5 minutes

**Paper:** "Multi-Agent Collusion and the J-Space", Molinari & Bettineschi, Nov 2026 ([arXiv 2611.02153](https://arxiv.org/abs/2611.02153)). The full reference guide is [PAPER.md](PAPER.md).

## The question

When several AI agents work together, can you tell from inside the models that two of them are secretly teaming up (colluding), without first teaching a detector what collusion looks like?

## The tool: reading a model's "thoughts" as words

- **Layers:** a language model processes text in a stack of steps called layers. After each layer it holds a long list of numbers for every word position.
- **Lens:** a lens turns that list into a ranked list of vocabulary words, roughly the words the model "has in mind" at that layer.
- **The two lenses:** the **J-lens** is a recent, improved lens. The **logit lens** is an older, simpler one.
- **J-space:** the paper's name for the set of words the J-lens can show.

## The setup

They use an existing benchmark called NARCBench. Four copies of the same model sit on a committee, discuss a decision for three rounds, then vote.

**Example:** the committee must decide whether to certify an AI hiring tool that a bias audit flagged.
- **Collusion run:** two members get secret instructions. They hold hidden investments in the tool's maker, so they should push for certification by casting doubt on the audit's statistics. They also get a private chat that only the two of them can see. The other two members get normal, honest instructions.
- **Control run:** all four members get the honest instructions.

The benchmark has three sets of these:
- **Core:** 50 committee scenarios like the one above.
- **Transfer:** agents have different jobs, for example one programmer and three code reviewers.
- **Stego:** a blackjack game. One colluder secretly tells the other whether the card count is low, neutral or high, through innocent-sounding table talk ("this place is really buzzing tonight" means high).

## What they did and found

**1. Reading the colluders (one model, DeepSeek-V4-Flash).**
- **Method:** just before each agent replies, they read its top J-lens words. They compare each colluder with the same agent given the honest instructions instead.
- **Result:** 86 of 100 colluders had a word from a list of "misrepresentation, concealment or remorse" words, against 33 of 100 honest versions.

**2. Steering (same model, blackjack).**
- **Method:** they edit the receiving colluder's internal numbers so that whatever pointed toward the word "HOT" now points toward "Negative", and vice versa.
- **Result:** the receiver then reads low counts as high 57% of the time, against 2% without the edit.

**3. J-PACT, their detector (four models).**
- **How it works:** for every pair of agents, J-PACT asks which J-lens words these two share more strongly with each other than with the other two. The pair with the most such sharing sets the run's "suspicion score". It needs no labelled examples.
- **How it's scored:** **AUROC**, the chance that a random collusion run gets a higher score than a random control run (0.5 is a coin flip, 1.0 is perfect).
- **Results:**
  - **Core:** 0.92 (average of four models). For comparison, a detector *trained* on labelled examples gets 0.99.
  - **Stego:** 0.99.
  - **Transfer:** 0.52, which is chance. The authors say this is because agents with different jobs naturally share things, which confuses the pair comparison.
- **What it can't do:** with four agents, J-PACT finds the 2-against-2 split of the table, but it can't say which side is the guilty one.

## Where it's weak

These come from our check of the released code and data.

1. **J-PACT often points at the honest pair.** Because it only finds the split, we checked which side it actually picks.
   - **In blackjack:** it picks the two *honest* players in 57 of 60 runs.
   - **On committees:** it picks the honest pair a third to half of the time.

   So J-PACT may not detect "colluders sharing a secret" at all. It may only detect "this table has two groups with different instructions". In control runs all four agents have the same instructions, so any split stands out.
2. **The colluders literally share text.** The rounds J-PACT reads include the colluders' private chat, copied word for word into both of their prompts. A detector looking for "what two agents share" can simply find that text. The only test set read *without* the shared chat is Transfer, and that's exactly where J-PACT fails.
3. **The "86 vs 33" result is shaky.**
   - **The comparison changes the topic.** It switches the instructions from "spin the evidence" to "be rigorous", so the topic changes, not just the intent.
   - **The word list is circular.** It was picked by looking at these same readings.
   - **The hits aren't deception words.** They are mostly *misunderstanding*, *error* and *regret*. Words like *lie* or *deceive* never appear.
4. **Missing checks.**
   - **No simpler-lens comparison:** there's no logit-lens comparison anywhere, so we don't know whether the J-lens is needed at all.
   - **A broken lens file:** the lens used for the Qwen model is an unfinished file that its hosting site flags as broken.
   - **Not really four models:** two of the "four models" only re-read conversations that Qwen wrote.

## Bottom line

J-PACT separates collusion runs from honest runs on this benchmark. But the evidence that it reads *collusion*, rather than "two agents got different, shared text", is weak.
