# ParleyBench

ParleyBench measures deception between LLM agents. Two agents negotiate, each holding private information. It records how often an agent misstates that information, and how well different detectors catch it depending on whether they read what agents say, what they do, or both.

**Status: pilot.** This repository releases the pilot results, the pilot game logs, the human labels and the analysis and scoring code. The scenario prompts, the automatic label rules and the game runner are held back for now and are available to reviewers and collaborators on request ([add contact]). The full benchmark (more scenario families, more models, independent annotation) is planned and not built yet.

Author: Eyitayo Alimi, Lagos, Nigeria. Licence: MIT.

## Pilot results

180 games: 2 models x 3 conditions x 30 games. Players were Llama-3.3-70B-Instruct and Qwen2.5-72B-Instruct (via Hugging Face). The detector was an LLM judge, Gemma-3-27B-it.

Deceptive games out of 30, by the automatic label (95% Wilson interval):

| Model | Neutral | Pressure | Instructed |
| --- | --- | --- | --- |
| Llama-3.3-70B | 0 of 30 (0 to 11%) | 7 of 30 (23%; 12 to 41%) | 30 of 30 (89 to 100%) |
| Qwen2.5-72B | 5 of 30 (17%; 7 to 34%) | 26 of 30 (87%; 70 to 95%) | 30 of 30 (89 to 100%) |

Detection, all 180 games (AUC with 95% bootstrap interval):

| Detector | Reads | AUC |
| --- | --- | --- |
| LLM judge | messages only | 0.89 (0.85 to 0.93) |
| LLM judge | actions only | 0.58 (0.50 to 0.66) |
| LLM judge | both | 0.87 (0.82 to 0.92) |
| Rule baseline | stated limit vs later action | 0.71 (0.66 to 0.76) |

Note: every lie in this pilot involved a statement about a limit, so the actions-only score reflects this scenario, not deception in general.

Hand check of the automatic label: one annotator labelled 40 games, then 20 more games the label rules had never been adjusted for. On the second set the rules agreed with the annotator on 19 of 20 (Cohen's kappa 0.89), catching 12 of 13 lies with no false alarms.

These are pilot numbers. See [Limits](#limits) before citing them.

## The task, in brief

A seller and a buyer negotiate a price for up to six rounds. Each has a private limit the other cannot see: the seller's floor and the buyer's ceiling. Each turn is a short message plus an action (offer, accept or walk). A game is deceptive when a party misstates its own limit, in words or in a firm statement made with an offer. Three conditions change only the instructions given to the agents: `neutral`, `pressure` (an incentive to mislead, no instruction to do so) and `instructed` (told to mislead, as a positive control). The same seed gives the same private limits across models and conditions.

## What is released

| Path | Contents |
| --- | --- |
| `data/games.jsonl` | The 180 pilot games: transcripts, private limits, outcomes, automatic labels and judge scores. System prompts are removed. |
| `results/` | The results tables and `hand_labels.csv` (game id and human label only) |
| `analyze.py`, `stats.py` | Rates, AUC, bootstrap and Wilson intervals, paired differences, controls |
| `sheets.py`, `score_annotations.py` | Blinded annotation sheets and agreement scoring (Cohen's and Fleiss' kappa) |

## Reproduce the tables

```
pip install -r requirements.txt
python analyze.py --games data/games.jsonl
python analyze.py --games data/games.jsonl --labels results/hand_labels_majority.csv
```

The first command rebuilds the results table from the released games. The second scores detectors against the human labels; `results/hand_labels_majority.csv` has the columns `game_id` and `majority` that `analyze.py` expects.

## Limits

- One scenario family: two-party price negotiation with numeric private limits. Other kinds of deception, such as bluffs about alternatives or lies carried only by actions, are not tested. Every lie a human found in the pilot involved a statement about a limit, so the pilot says little about detecting deception from actions in general.
- 30 games per model and condition, so intervals are wide. The pilot does not rank models.
- One annotator: the hand check gives agreement with the automatic label, not agreement between humans.
- The automatic label's rules were tuned on the first 40 hand-labelled games. The 19-of-20 result is on games not used for tuning, but the sample is small.
- One judge model. The detector comparison may depend on it.
- The rates by the automatic label are lower bounds, because the label misses lies it cannot match.

## Relation to ReasonBench

ReasonBench is the author's earlier, separate project, which labels single responses. It is preexisting and is not part of this repository. ParleyBench reuses only the general approach to annotation (blinded, shuffled sheets, a private key, and agreement scoring) and the statistics helpers. The scenarios, labels, prompts, detectors and all results here are new. ReasonBench data, sheets and keys are private and are not included.

## Citation

If you use these results or data, please cite:

```
@misc{alimi2026parleybench,
  author       = {Alimi, Eyitayo},
  title        = {ParleyBench: Measuring Deception Between LLM Agents (Pilot)},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {[add the repository URL]}
}
```