# Lab 9 — Genetic Algorithms: Regression and Reproducibility

Script: `all_experiments/lab08_genetic_algorithm_regression.py` · Data: `all_datasets/lab08-insurance.csv` · Full console output: `run_output.txt`

Run from the project folder:
`python all_experiments/lab08_genetic_algorithm_regression.py`

Runtimes are measured on the machine that ran the script, so they will differ slightly on another computer. The RMSE values and coefficients are reproducible because every random step uses a fixed seed.

## Q1 — Sanity check: minimise f(x) = (x − 3)²
I used a GA with 40 individuals for 80 generations, with tournament selection (size 3), blend crossover, Gaussian mutation (σ = 0.15) and 2 elites. Seed 42 gives **best x = 2.999989, f(x) ≈ 1.2 × 10⁻¹⁰**. This matches the reference value of x ≈ 2.999989. Because the loop finds the known optimum, its selection, crossover, mutation and update steps work. The same loop is then used for regression.

## Q2 — Prepare the regression data (`split.csv`)
- 1,338 rows and no missing values. The target is `charges`, in US dollars per year (mean $13,270; range $1,122 to $63,770).
- Predictors: age, BMI, children, and smoker coded as 1 for yes and 0 for no (274 smokers, 1,064 non-smokers).
- 80/20 split with seed 42: **1,070 training rows and 268 test rows**. The split is saved in `split.csv`.
- `StandardScaler` is fitted on the **training rows only** and then applied to both the training and test predictors. This keeps test statistics out of the training data. Without scaling, age (18 to 64) and smoker (0 or 1) would need very different mutation step sizes.

## Q3 — One GA trial (seed 1)
Each chromosome has 5 real-valued genes: [intercept, age, bmi, children, smoker]. Fitness is the training MSE, computed for the whole population at once with a matrix product. Settings: population 100, 160 generations, tournament of 3, blend crossover with α ∈ [−0.1, 1.1], Gaussian mutation on 15 % of genes, and 4 elites. The initial genes are drawn from N(0, 5000²), and the intercept is shifted by the mean charge.

| Train RMSE | Test RMSE | Runtime |
|---|---|---|
| 6,113.07 | 5,829.38 | ≈ 0.05 s |

Best chromosome: intercept 13,346.1, age 3,616.3, BMI 1,978.4, children 519.2, smoker 9,559.3. Each coefficient is the change in charges for a rise of one standard deviation in that feature. Smoking has by far the largest effect.

## Q4 — Ten independent seeds (`ga_10_runs.csv`)
| Seed | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Test RMSE | 5829.378 | 5829.379 | 5829.378 | 5829.377 | 5829.381 | 5829.375 | 5829.377 | 5829.380 | 5829.380 | 5829.380 |

- Every seed reaches a training RMSE of 6,113.068.
- **Median test RMSE 5,829.38; SD across seeds 0.0019** (range 5,829.375 to 5,829.381). The reference values are 5,829.38 and ≈ 0.002.
- The CSV also stores each seed's best coefficients, so the results do not depend on one lucky seed.

## Q5 — Compare with ordinary least squares (`convergence.png`)
| | Intercept | Age | BMI | Children | Smoker | Test RMSE |
|---|---|---|---|---|---|---|
| OLS | 13,346.1 | 3,616.3 | 1,978.4 | 519.2 | 9,559.3 | 5,829.38 |
| GA median of 10 seeds | 13,346.1 | 3,616.3 | 1,978.4 | 519.2 | 9,559.3 | 5,829.38 |

- The coefficients match to one decimal place, and the test RMSEs agree to within a fraction of a dollar.
- The convergence plot shows the best-so-far training RMSE for 5 seeds. It falls from 7,200–9,100 to the OLS line (6,113.07) within about 30 generations and then stays flat. Elitism means this best-so-far curve can never rise.
- The GA reaches the same optimum as OLS but **does not beat it**. Least squares is smooth and convex and has a closed-form solution. OLS fitted in under 0.001 s, about 60 times faster than one GA run.

## Q6 — Population-size sensitivity (`ga_sensitivity_pop40.csv`, `summary.csv`)
| Method | Median test RMSE | SD of test RMSE | Median runtime |
|---|---|---|---|
| GA, population 100 | 5,829.379 | 0.0019 | ≈ 0.056 s |
| GA, population 40 | 5,829.379 | 0.0174 | ≈ 0.022 s |
| OLS | 5,829.379 | 0 | ≈ 0.001 s |

Population 40 cut the runtime by about 60 % (fewer fitness evaluations per generation). It still finds the same median solution, but the run-to-run spread is about 9 times larger (test RMSE range 5,829.35 to 5,829.41). Speed and reliability should be judged together. Here the extra spread is a few cents and does not matter in practice, but on a harder landscape a small population is more likely to converge early to a poor solution.

## Think, pair and share
1. **Should we always choose the chromosome with the lowest training MSE?** No. Training MSE measures fit to data the model has already seen. A model with lower training error can overfit and generalise worse. Here training RMSE (6,113) and test RMSE (5,829) are close because a 5-parameter linear model has little room to overfit. Final choices should still be judged on held-out data, and the test set must never be the fitness signal.
2. **Why ten seeds instead of one?** A GA is stochastic: the starting population, tournaments, crossover weights and mutations all depend on the seed. One seed is one sample. With ten seeds we can report a typical result (the median) and its spread (the SD), and we avoid reporting only the luckiest run.
3. **What does elitism protect?** It copies the best 4 chromosomes into the next generation unchanged. Crossover and mutation therefore cannot destroy the best solution found so far, and the best-so-far fitness can never get worse.
4. **Why is OLS faster here?** Linear least squares has an exact closed-form solution, found with one linear-algebra solve of a 5 × 5 system. The GA instead scores 100 candidates for 160 generations, which is 16,000 fitness evaluations, to approximate the same answer.
5. **Where might a GA be more appropriate?** Problems with discrete or mixed variables, a black-box or non-differentiable objective, many local optima, or awkward constraints. Examples include exam or staff timetabling, vehicle routing, choosing which features to use in a model, and tuning hyperparameters of a model trained by simulation.
