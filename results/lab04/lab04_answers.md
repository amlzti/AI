# Lab 4 (Week 07) — Fuzzy Logic and ANFIS with Air-Quality Data

Script: `all_experiments/lab04_fuzzy_anfis.py` · Data: `all_datasets/lab04-AirQuality.csv` · Full console output: `run_output.txt`

## Q1 — Clean the data
- Read with `sep=";"` and `decimal=","`, dropped empty columns/rows, replaced `-200` with NaN.
- **9,357 rows.** Usable: T 8,991, RH 8,991, CO(GT) 7,674, PT08.S1(CO) 8,991, PT08.S2(NMHC) 8,991.
- T spans about 0–45 °C and RH about 10–90 %, which set the controller ranges (`temperature_humidity.png`).

## Q2 — Build the fuzzy controller (Mamdani)
- Three triangular sets per variable, outer ones as shoulders (`fuzzy_memberships.png`).
- Rules: low = cold∧dry or cold∧comfortable; medium = mild∧dry, mild∧comfortable or cold∧humid; high = hot or humid.
- Worked example: 15 °C, 45 % RH → **40.4 %** ventilation. Try-it: 28 °C, 60 % RH → **55.5 %**.

## Q3 — Validate the rule base
| T (°C) | RH (%) | Expected | Ventilation (%) |
|---|---|---|---|
| 10 | 30 | low | 18.9 |
| 20 | 50 | medium | 50.0 |
| 35 | 50 | high | 82.3 |
| 25 | 80 | high | 83.8 |
| 40 | 80 | high | 84.2 |

All five match their expected level. The control surface (`fuzzy_control_surface.png`) rises smoothly toward hot and humid, with no cliffs or flat patches.

## Q4 — Prepare the ANFIS task
- Predict CO(GT) from PT08.S1(CO) and PT08.S2(NMHC), complete rows only: **7,344 rows = 5,140 train + 1,102 validation + 1,102 test** (70/15/15, seed 42, `split.csv`).
- `StandardScaler` fitted on the training rows only, then applied to all rows (no leakage).

## Q5 — Fit two model classes (`metrics.csv`)
| Model | Val RMSE | Val MAE | Test RMSE | Test MAE |
|---|---|---|---|---|
| Linear regression | 0.5103 | 0.3722 | 0.5365 | 0.3821 |
| ANFIS-2MF (4 rules) | 0.4550 | 0.3195 | 0.4715 | 0.3264 |
| ANFIS-3MF (9 rules) | 0.4489 | 0.3144 | 0.4672 | 0.3246 |

**ANFIS-3MF** has the lowest validation RMSE and is selected. The test columns played no part in this choice.

## Q6 — Evaluate once on the test data
- Linear regression: RMSE 0.5365, MAE 0.3821. ANFIS-3MF: RMSE 0.4672, MAE 0.3246.
- Test RMSE improves by **12.9 %**. In `predicted_vs_actual.png` the linear model under-predicts at high CO, while ANFIS follows the curve.
- **Verdict:** the extra complexity is justified here. ANFIS beats the baseline on both validation and test, by a clear margin.
- Limits: the random split ignores time order and sensor drift, so a time-based split would be a stricter test.

## Check your understanding
1. **At 28 °C, which temperature sets are non-zero?** Mild = (32 − 28)/(32 − 22) = 0.4; hot = (28 − 26)/(45 − 26) ≈ 0.11; cold = 0 because 28 > 18.
2. **Why AND = min and joining rules = max?** A conjunction can be no truer than its weakest part, so AND is min. A conclusion supported by several rules is as true as its strongest reason, so alternatives combine with max.
3. **Which change turns Mamdani into Sugeno?** Replace each rule's fuzzy output set with a linear function of the inputs. The output is then linear in the coefficients, so least squares solves them in one step.
4. **ANFIS with 3 sets per input and 2 inputs?** 3² = 9 rules, each with 3 coefficients (1, x1, x2) = 27 consequent coefficients.
5. **Why fit the scaler on training rows only?** Otherwise the test rows' mean and spread leak into the model, and the test RMSE becomes optimistic rather than a fair estimate.
