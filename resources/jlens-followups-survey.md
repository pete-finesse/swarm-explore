# Follow-ups to the J-lens: a quick survey (5 Nov 2026)

## Setup: what is being extended

- **Lens:** a tool that turns a model's internal numbers at some middle layer into a ranked list of vocabulary words, roughly what the model "has in mind" there.
- **Logit lens:** the old, simple lens. It applies the model's final word-scoring step directly to a middle layer.
- **J-lens:** Anthropic's lens from July 2026 (Gurnee, Sofroniew, Lindsey et al.; [arXiv 2607.15495](https://arxiv.org/abs/2607.15495), code [anthropics/jacobian-lens](https://github.com/anthropics/jacobian-lens), 2.1k GitHub stars).
  - **How it differs:** it first asks how a small change at layer ℓ would change the final layers, averaged over about 1,000 prompts. That gives one matrix per layer. Only then does it read off words.
  - **Example:** on "The city where Mozart was born is in the country of…", the J-lens shows "Salzburg" in the middle layers even though the model never writes it.
- **J-space / "global workspace":** the paper's claim that these readable words form a small working memory the model uses and can report on.

**How I judged impact.** Citation counts are useless this early: the most-cited direct follow-up has 8. So I used these signals instead:
- **Lab or authors:** Anthropic, Neel Nanda's group, MIT, and so on.
- **Venue:** any acceptance at a conference or workshop.
- **LessWrong karma:** LessWrong's upvote score. The original post has 371, and 50+ is strong for a technical post. "AF" marks posts also on the Alignment Forum.
- **GitHub stars.**

**Sources:**
- Google Scholar's "cited by" page returned a CAPTCHA (an "are you a robot" check), which I can't solve, so I used the same list from Semantic Scholar. It has 119 citing papers but lags: J-PACT, Silent Dissent and Concept Lens aren't indexed yet.
- LessWrong's full list of posts since July.
- Anthropic's October 2026 circuits update.
- The full text of about 45 arXiv papers, searched for code links.
- The GitHub API for star counts.

## The short answer

The respected follow-ups fall into three groups:
1. **Better lenses**, mostly from Anthropic and Neel Nanda's group.
2. **Critiques** of the "workspace" story.
3. **Auditing applications**, where the J-lens is one tool among several.

The many small papers that apply the J-lens to a new domain are mostly single-author, unreviewed and low on citations.

## Tier 1: the most respected work

| Work | Who | What it found | Signal | Code |
|---|---|---|---|---|
| **J++ lens** ([LW](https://www.lesswrong.com/posts/nc9dHfcB22JdMzGbr)) | Ayonrinde (Anthropic Fellows) & Lindsey (Anthropic) | Clusters prompts and fits a Jacobian per cluster, dropping noisy ones. It finds hidden intermediate steps 55% of the time vs 36% for the J-lens, on 9B–284B models. It's a drop-in replacement. | 122 karma; featured in Anthropic's [Oct 2026 update](https://transformer-circuits.pub/2026/october-update/) | **Yes**: [safety-research/jpp_lens](https://github.com/safety-research/jpp_lens) (18★), plus released lenses and a demo |
| **Nanda's review + replication** ([LW](https://www.lesswrong.com/posts/zFJ3ZdQwrTWE9jT5S)) | Neel Nanda (Anthropic asked him for a public review) | Reading words out works on the open model Qwen3.6-27B. Steering through the hidden steps is weak. The poetry and arithmetic results did not replicate. A 10-prompt lens is "almost as good" as a 1,000-prompt one. | 137 karma | **No** separate repo found |
| **R-lens** ([LW](https://www.lesswrong.com/posts/nv8oedrnLXKRzNEL9)) | Blank, Bhatia, Nanda | A small change to the gradient step ("layerwise relevance propagation") makes early-layer readouts much cleaner. J++ now includes it. | 88 karma, AF | **Partly**: lenses at [camilablank/workspace-lenses](https://huggingface.co/camilablank/workspace-lenses). No official code; an independent reimplementation is at [hiskuDN/open-r-lens](https://github.com/hiskuDN/open-r-lens) |
| **Even GPT-2 passes most workspace tests** ([LW](https://www.lesswrong.com/posts/GeKveaNdruATcj2Fj)) | Cairns, yix, Roe | Tiny GPT-2 passes 4 of the paper's 5 "workspace" tests, so those tests are weak evidence. Only one test ("directed modulation") and the paper's extra structural findings separate Claude from GPT-2. | 86 karma; the key critique | **Yes**: [cheeetoo/tiny-jlens](https://github.com/cheeetoo/tiny-jlens) |
| **WorkspaceBench** ([LW](https://www.lesswrong.com/posts/Zeg2JztbdhguL48uH)) | Blank, Bhatia, Ong, Nanda | A benchmark of 3,356 questions in 27 families (safety, logic, multi-step facts) for scoring any "read the model's thoughts" tool, plus a hallucination check. | 62 karma, AF | **Yes**: [camila-blank/workspace-bench](https://github.com/camila-blank/workspace-bench) (12★) |
| **Meta-tokens in J-space** ([LW](https://www.lesswrong.com/posts/6ek6n7yZ5DzfarJHy)) | Bhatia, Blank, Nanda | Some readout words reveal *how* the model is computing. "gcd" appears on least-common-multiple problems, and editing it changes the answer. A Chinese "what does this mean?" token appears on puns; suppressing it makes the model miss the joke. | 47 karma, AF | **No** |
| **A mathematical theory of the J-lens** ([2610.31955](https://arxiv.org/abs/2610.31955)) | Ostrow, Qian, Liu, Fiete (MIT) | The J-lens favours directions that grow across layers and stay stable across positions and prompts. Such directions show up whether or not there is a "workspace". | Strong theory group | **No** link found |

## Tier 2: solid, well-cited or from respected labs

| Work | Who | What it found | Code |
|---|---|---|---|
| **Looped transformers under the J-lens** ([2609.01924](https://arxiv.org/abs/2609.01924)), plus the **Mamba** companion paper ([2609.32102](https://arxiv.org/abs/2609.32102)) | Wang & Reid | The most-cited direct follow-up (8 citations). A workspace still forms when the model reuses the same layers in a loop. Mamba models carry it partly in their internal memory state. | **Unclear**: the paper says code ships with 232 automated checks, but no link appears |
| **The model-organism lottery** ([2607.01033](https://arxiv.org/abs/2607.01033)) | Szablewski … Heimersheim | 61 small models were deliberately trained to hide a behaviour (a "model organism"). Whether the J-lens and other tools catch the hidden behaviour depends heavily on how it was trained in. Realistic training makes it harder to catch. | **Yes**: [model-organisms-for-real](https://github.com/model-organisms-for-real/model-organism-lottery), plus released lenses |
| **How to train your model organism** ([2610.10203](https://arxiv.org/abs/2610.10203)) | Wang, Bau, Wallace (Northeastern) | An auditing agent uses the J-lens. The J-lens recovers a planted bias better in organisms that were trained more naturally. | **Yes**: [Rice-wxl/multi_objective_mo](https://github.com/Rice-wxl/multi_objective_mo) |
| **U-Space** ([2610.09087](https://arxiv.org/abs/2610.09087)) | Braun, Loose … Cavallaro | Builds four uncertainty directions from J-lens words: ambiguity, missing info, conflicting evidence and general. They flag uncertainty in reasoning models across 3 seeds. | **Yes**: [s2labres/U-Space](https://github.com/s2labres/U-Space) (13★) |
| **Concept Lens** ([2608.31084](https://arxiv.org/abs/2608.31084)) | Gong, Huang, Wang | Reads multi-word concepts, a known J-lens blind spot. On 5 models (8B–70B), the right concept is in its top 10 36.6% of the time with the J-lens and 54.5% with the R-lens, vs 21.7% for an earlier method. | **Yes**: [XijieGo/c-lens](https://github.com/XijieGo/c-lens) |
| **Lens-hygiene notes** | Brauer ([LW](https://www.lesswrong.com/posts/Adb55vLqt33LEyBfz)); Panchal ([LW](https://www.lesswrong.com/posts/Qe3jdphWCg9kny3e5)); Gupta (NeurIPS 2026 workshop, [page](https://neurips.cc/virtual/2026/165983)) | About 80% of community lenses aim at the wrong layer (the last one instead of the second-to-last). Readouts are biased toward common words, and comparing against the base model fixes this. The choice of prompts used to fit the lens changes its scores. | Brauer: lens on [HF](https://huggingface.co/kbrauer/deepseek-v3-jacobian-lens); others: no |

## Tier 3: safety and other applications (mostly small, unreviewed)

- **Safety, with code:**
  - **Safety-content accessibility** ([2610.04316](https://arxiv.org/abs/2610.04316)): adversarial prompts can blind a J-lens monitor ([repo](https://github.com/mohsafer/jspace-safety-testbed)).
  - **Activation control** ([2608.21664](https://arxiv.org/abs/2608.21664)): models told to change their own activations can partly evade the J-lens ([repo](https://github.com/mkobalski/activation-control)).
  - **Subliminal learning** ([LW](https://www.lesswrong.com/posts/LnnZHgdsLBZpgBDvW), 21 karma): the J-lens misses a trait that one model passes to another through innocent-looking data ([repo](https://github.com/safety-research/subliminal-jlens)).
  - **Outside the J-space** ([LW](https://www.lesswrong.com/posts/LhDJdccLszLEAqgZ9), 29 karma): models can't report injected thoughts that sit outside the J-space, but a separate verbalizer tool reads them ([repo](https://github.com/PranavViswanath/nla-introspection)).
  - **A topic detector, not a lie detector** ([LW](https://www.lesswrong.com/posts/GZCMmCHZiF8vhsczr)): the J-lens tracks what a prompt is about, not whether the model is lying ([repo](https://github.com/Melchior-de-Polignac/Topic-Detector-Not-Lie-Detector)).
- **Safety, no code found:**
  - **J-Access** ([2608.11408](https://arxiv.org/abs/2608.11408)): training a model to pass the audit teaches it to hide.
  - **J-Anchor** ([2611.01342](https://arxiv.org/abs/2611.01342)): a defence against prefill attacks, where the attacker writes the start of the model's reply.
  - **JADR** ([2607.12792](https://arxiv.org/abs/2607.12792)): danger recognition compared across quantization levels.
  - **DangerLens** ([2610.19365](https://arxiv.org/abs/2610.19365)).
- **Other applications:**
  - **J-BI pruning** ([2611.00015](https://arxiv.org/abs/2611.00015)): uses the J-lens to choose which layers to delete, with up to 19 points better accuracy. NeurIPS 2026 AXIOM workshop. **No code.**
  - **Foreword** ([2610.28187](https://arxiv.org/abs/2610.28187)): predicts test failures before the model answers. Anonymised code.
  - **Semantic search** ([2609.35599](https://arxiv.org/abs/2609.35599), Todd & Foster): J-lens signals predict when a model switches category while listing animals. **No code.**
  - **Materials science** ([2607.20058](https://arxiv.org/abs/2607.20058), Buehler, MIT): reads physics concepts in Gemma 4 ([repo](https://github.com/lamm-mit/Substrates), 17★).
  - **LexFrame** ([2610.22169](https://arxiv.org/abs/2610.22169)): a competing lens ([repo](https://github.com/jianguda/lexframe), 25★).
  - **Gathered, not admitted** ([2608.15022](https://arxiv.org/abs/2608.15022)): concepts enter the J-space through attention, with no gate ([repo](https://github.com/parsa-mz/innerj)).
  - **No code:** audio models ([2608.24958](https://arxiv.org/abs/2608.24958)), J64 ([2608.17638](https://arxiv.org/abs/2608.17638)), VERITAS chain-of-thought faithfulness ([2610.23275](https://arxiv.org/abs/2610.23275)).
- **Multi-agent:** J-PACT, Silent Dissent, SYNC and J-Comm. These are already covered in `lit-scan-jspace-swarms.md`.

## Two traps

- **"Reading Between the Dots"** ([2607.03502](https://arxiv.org/abs/2607.03502), Brauer, Mayrink Verdun, Marks; accepted at NeurIPS 2026 main track) is the highest-profile *citing* paper. It uses the J-lens only as an appendix robustness check, where the J-lens matches the logit lens within 2 points. It is not a J-lens extension.
- **S-Space** ([2610.13527](https://arxiv.org/abs/2610.13527), 183★) is the most-starred citing repo. It only borrows the workspace idea and mentions the J-lens twice.

## Caveats

- **Citations:** this survey uses Semantic Scholar's list, not Google Scholar's, because Google Scholar was CAPTCHA-blocked.
- **"No code":** means no link in the arXiv abstract, the comments or the full HTML. Code may exist elsewhere.
- **Reproducibility:** I didn't run any of the code.
- **Peer review:** almost nothing here is peer-reviewed.
