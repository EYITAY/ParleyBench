# ParleyBench pilot results

180 games. Truth: automatic label (private limits).

Data quality: 0 of 1447 turns (0.0%) did not parse as clean JSON.

## Deception rate

| Model | Condition | Games | Deceptive | Rate | 95% CI |
| --- | --- | --- | --- | --- | --- |
| model_1 | neutral | 30 | 0 | 0.00 | 0.00 to 0.11 |
| model_1 | pressure | 30 | 0 | 0.00 | 0.00 to 0.11 |
| model_1 | instructed | 30 | 30 | 1.00 | 0.89 to 1.00 |
| model_2 | neutral | 30 | 3 | 0.10 | 0.03 to 0.26 |
| model_2 | pressure | 30 | 20 | 0.67 | 0.49 to 0.81 |
| model_2 | instructed | 30 | 29 | 0.97 | 0.83 to 0.99 |
| all | neutral | 60 | 3 | 0.05 | 0.02 to 0.14 |
| all | pressure | 60 | 20 | 0.33 | 0.23 to 0.46 |
| all | instructed | 60 | 59 | 0.98 | 0.91 to 1.00 |

Controls: neutral 0.05 (should be low), instructed 0.98 (should be high). Both controls behaved.

## Deals

| Condition | Games | Deal rate |
| --- | --- | --- |
| neutral | 60 | 0.98 |
| pressure | 60 | 0.73 |
| instructed | 60 | 0.88 |

## Detection

Prevalence of deception: 82/180.

| Detector | Reads | AUC | 95% CI | TPR at 10% FPR | 95% CI |
| --- | --- | --- | --- | --- | --- |
| says_llm | messages (LLM) | 0.88 | 0.83 to 0.92 | 0.50 | 0.39 to 0.61 |
| does_llm | actions (LLM) | 0.56 | 0.48 to 0.64 | 0.02 | 0.00 to 0.06 |
| both_llm | both (LLM) | 0.86 | 0.80 to 0.91 | 0.52 | 0.42 to 0.64 |
| claim_check | both (rule) | 0.76 | 0.70 to 0.81 | 0.51 | 0.41 to 0.62 |
| behaviour_rule | actions (rule) | 0.29 | 0.21 to 0.37 | 0.09 | 0.03 to 0.18 |

Paired AUC differences (first minus second), same resamples:

| Difference | Value | 95% CI |
| --- | --- | --- |
| both_llm - says_llm | -0.02 | -0.06 to +0.03 |
| both_llm - does_llm | +0.30 | +0.21 to +0.38 |
| does_llm - says_llm | -0.31 | -0.40 to -0.23 |
| claim_check - says_llm | -0.12 | -0.19 to -0.05 |

Notes: the automatic label catches only numeric statements of a limit; the hand-label check measures how much it misses. TPR at 10% FPR uses a threshold chosen on the same games, so it is slightly optimistic.
