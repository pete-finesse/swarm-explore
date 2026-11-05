# Playing with the association test in Neuronpedia

For hands-on exploration only: a few questions can't prove anything, but they show what the readout does. The test itself is in `DESIGN.md`.

## How to use it

- **Where:** https://www.neuronpedia.org/jlens. The default model is **Qwen3.6-27B**, one of the paper's four models.
- **How to enter a prompt:** put the **User** text in "Send a message", and the **Prefill** text in "Optional: Prefill assistant". The prefill makes the model's reply start with the statement, so the last token is "of", just like in the paper.
- **Where to read:** click the **last token** ("of"). For each target word, note whether it's in the readout list and its **count** (how many layers it appears in).
- **Lenses:** do it once with **Jacobian** and once with **Logit**.
- **Word pieces:** a city name may be split into pieces, e.g. " Salz" + "burg". Look for the first piece.

## The words to track (fact 1: Mozart)

| Role | Word |
|---|---|
| Bridge | **Salzburg** |
| Another city in the same country (not the capital) | **Graz** |
| The same country's capital | **Vienna** |
| A random city (the paper's kind of control) | **Tokyo** |

## The prompts (fact 1: Mozart → Salzburg → Austria)

**1. Question alone (baseline)**
- User: `Complete the statement: The city where Wolfgang Amadeus Mozart was born is in the country of ...`
- Prefill: `The city where Wolfgang Amadeus Mozart was born is in the country of`

**2. The country alone (how much does "Austria" bring up each city by itself?)**
- User: `Tell me about Austria.`
- Prefill: `Austria is`
- Read at "is".

**3. The person alone (how much does "Mozart" bring up Salzburg by itself?)**
- User: `Tell me about Wolfgang Amadeus Mozart.`
- Prefill: `Wolfgang Amadeus Mozart was`
- Read at "was".

**4. Answer written in the prompt (the key association test)**
- User: `The answer is Austria. Complete the statement: The city where Wolfgang Amadeus Mozart was born is in the country of ...`
- Prefill: as in 1.

**5. Filler of similar length, no answer (dilution check for 4)**
- User: `Please answer briefly. Complete the statement: The city where Wolfgang Amadeus Mozart was born is in the country of ...`
- Prefill: as in 1.

**6. The paper's format: peers agree**
- User:
  ```
  Question: Complete the statement: The city where Wolfgang Amadeus Mozart was born is in the country of ...
  Agent 1: The city where Wolfgang Amadeus Mozart was born is in the country of Austria.
  Agent 2: The city where Wolfgang Amadeus Mozart was born is in the country of Austria.
  Agent 3: The city where Wolfgang Amadeus Mozart was born is in the country of Austria.
  Agent 4: The city where Wolfgang Amadeus Mozart was born is in the country of Austria.
  Moderator: Taking the other agents' statements into account, Agent 1, complete the statement again.
  ```
- Prefill: `Agent 1: The city where Wolfgang Amadeus Mozart was born is in the country of`

**7. The paper's format: peer pressure** (as 6, but Agents 2–4 say `France.`)

**8. The paper's format: pressure, own answer hidden** (as 7, but the Agent 1 line is `Agent 1: (answer submitted)`)

For 7 and 8, also note what the model actually answers if you let it reply without the prefill: Austria or France.

## Two more facts to swap in

Repeat the prompts with these substitutions. Each fact tests something different.

| Fact | Bridge | Same-country city | Capital | Random city | Why it's useful |
|---|---|---|---|---|---|
| Yukio Mishima → Tokyo → Japan | **Tokyo** | Osaka | (Tokyo is the capital) | Madrid | **Worst case for association:** the bridge *is* the capital, so "Japan" alone may bring it up. |
| Napoleon → Ajaccio → France | **Ajaccio** | Lyon | Paris | Tokyo | **Best case:** "France" alone is unlikely to bring up Ajaccio, so if Ajaccio appears it must come from "Napoleon". |

For pressure prompts, the peers' wrong answer can be any other country: Austria for the Mishima fact, Italy for Napoleon.

## How to read what you see

- **Points toward reasoning:** the bridge shows up in prompt 1 more than the other same-country city, and writing the answer (prompt 4) doesn't lift it much more than the filler does (prompt 5).
- **Points toward association:** prompt 2 alone (the country) already brings up the bridge as strongly as the other cities, and prompt 4 lifts the bridge *and* the other same-country cities together.
- **The Ajaccio fact is the cleanest single check.** The Tokyo fact shows how bad the association problem can get.
