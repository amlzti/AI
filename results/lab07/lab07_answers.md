# Lab 8 — NLP: Airline Tweet Sentiment Classification

Script: `all_experiments/lab07_airline_sentiment.py` · Data: `all_datasets/lab07-Tweets.csv` · Full console output: `run_output.txt`

Run from the project folder:
`python all_experiments/lab07_airline_sentiment.py --data all_datasets/lab07-Tweets.csv --out results/lab07`

## Q1 — Inspect, clean and deduplicate
- 14,640 raw tweets. Kept tweet_id, text, airline_sentiment and airline. URLs became `URL`, @handles became `USER`, and text was lowercased with whitespace collapsed.
- **213 exact duplicate texts; 355 duplicates after normalisation.** Both were removed before splitting, leaving **14,285 tweets**.
- Class balance: negative 9,069 (63.5 %), neutral 2,981 (20.9 %), positive 2,235 (15.6 %).

## Q2 — Fixed stratified split (`split.csv`)
70/15/15, seed 42, stratified by sentiment: **9,999 train, 2,143 validation, 2,143 test**. Each subset keeps the same class mix (test: 1,361 negative / 447 neutral / 335 positive).

## Q3 — Text features fitted on training data only
CountVectorizer (English stopwords removed, min_df = 2, max 20,000 features), fitted on training tweets only: **4,671 unigram features; 11,850 unigram + bigram features.**

## Q4 — Majority-class baseline
Always predict "negative". On validation: accuracy 0.635, macro precision 0.212, macro recall 0.333, **macro F1 0.259**.

## Q5 — Tune Naive Bayes on validation (`validation_results.csv`)
| n-grams | α = 0.3 | α = 0.5 | α = 1.0 | α = 2.0 |
|---|---|---|---|---|
| (1, 1) | 0.676 | 0.674 | 0.671 | 0.644 |
| (1, 2) | **0.697** | 0.690 | 0.687 | 0.652 |

Selected: **unigrams + bigrams, α = 0.3** (validation macro F1 0.697). For α ≤ 1, the n-gram choice mattered more than the smoothing value. The test set was not used for this choice.

## Q6 — Final test results (`metrics.csv`, `confusion_matrix.png`, `test_predictions.csv`)
| Model | Accuracy | Macro precision | Macro recall | Macro F1 |
|---|---|---|---|---|
| Majority baseline | 0.635 | 0.212 | 0.333 | 0.259 |
| Multinomial NB | **0.770** | **0.704** | **0.693** | **0.698** |

Confusion matrix (rows = true, columns = predicted):

| | negative | neutral | positive |
|---|---|---|---|
| negative | 1,185 | 115 | 61 |
| neutral | 158 | 239 | 50 |
| positive | 63 | 46 | 226 |

## Q7 — Read the evidence (`per_class_metrics.csv`, `per_airline_f1.csv`, `error_analysis.csv`)
- **Per-class F1:** negative 0.857, positive 0.673, neutral 0.564. Neutral is the weakest class: 158 neutral tweets were predicted negative.
- **Per airline:** macro F1 ranges from 0.659 (Delta) to 0.782 (Virgin America), with test-group sizes from 63 to 594. The groups differ in size, class mix and topics, so this is a diagnostic, not a ranking of airlines.
- **Error sample:** the 4 most confident mistakes for each true class give 12 tweets. They were tagged as:
  - 3 negation;
  - 2 question or request;
  - 7 ambiguous or other.

  Every one had a confidence of 0.9999 or higher.
- **Label quality:** the retweeted joke "Our fleet's on fleek" appears with negative and with positive labels. The model calls it neutral, so not every error is a model failure.

## Think, pair and share
1. **Why 63 % accuracy by predicting only negative?** 63.5 % of tweets are negative, so the majority guess is right that often. It never finds a neutral or positive tweet, which is why its macro F1 is only 0.259.
2. **Why might "not good" look like "good"?** "not" is in the English stopword list, so it is removed. Both tweets then become just "good". Bigrams can only keep "not good" if "not" survives preprocessing.
3. **Why is neutral the hardest class?** It has few distinctive words. Neutral tweets are often questions or requests about delays, holds and bookings, and those words overlap heavily with complaints. It is also a minority class (21 %).
4. **Why use the test set only once?** If we looked at test scores while choosing settings, the test set would become part of model selection. The reported score would then be optimistic rather than a fair estimate of performance on new tweets.
5. **Would you trust a prediction with confidence 0.999?** Not on its own. Naive Bayes multiplies many word likelihoods as if they were independent, which pushes probabilities toward 0 or 1. All 12 sampled mistakes scored ≥ 0.9999. Confidence is not correctness.

## Limitations
Bag-of-words Naive Bayes ignores word order, so it struggles with negation, sarcasm and jokes. Next steps could be TF-IDF weighting, keeping negation words, embeddings or a contextual language model, all using the same leakage-safe protocol.
