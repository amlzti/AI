# Lab 7 (Week 09) — NLP Foundations: Handwriting OCR Evaluation

Script: `all_experiments/lab06_handwriting_ocr_worked.py` · Data: `all_datasets/lab06-ocr-handwritten-prescription.zip` · Full console output: `run_output.txt`

**OCR mode: live, Tesseract 5.4.0.20240606** (`--oem 1 --psm 7` for every image).

## Q1 — Validate the archive
One label CSV and **89 images**, each present exactly once. They cover **61 unique** medicine names, so some names appear in several handwriting samples (`sample_grid.png`). The images show cursive writing, varied stroke width, uneven lighting and lined paper.

## Q2 — Baseline OCR
Tesseract ran on every raw image with one fixed configuration (LSTM engine, PSM 7 = single text line). Prediction and label were both normalised to lowercase letters and digits. There were **0 engine errors**; every image was kept and its status recorded.

## Q3 — Baseline quality, and Q5 — fair comparison (`metrics.csv`)
| Metric | Raw images | Preprocessed | Change |
|---|---|---|---|
| Exact-match accuracy | 0.000 | 0.011 (1 of 89) | +0.011 |
| Mean normalised edit distance | 0.869 | 0.785 | −0.084 |
| Character error rate | 0.883 | 0.806 | −0.077 |
| Blank predictions | 42 | 15 | −27 |

Both pipelines were scored on the same 89 images with the same normalisation and OCR settings, so the difference comes from the preprocessing alone. My numbers differ slightly from the lecture's reference values (39 → 15 blanks, CER 0.875 → 0.788) because the Tesseract version is different. The direction and size of every change agree with the lecture.

## Q4 — Preprocessing pipeline
Grayscale → 20 px white border → width capped at 1,200 px → 1.5× bicubic enlargement. The 89 processed images are saved in `preprocessed/`. Each step targets a known Tesseract weakness on photos:
- Grayscale removes colour noise.
- The border stops text touching the image edge.
- The width cap limits runtime.
- The enlargement brings stroke height into the range the engine was trained on.

## Q6 — Failure analysis (`error_analysis.csv`, `ocr_failures.png`)
Of the 8 worst preprocessed predictions, **6 are "no text detected"** (azitma, tonoflox, cefiget 40mg, breeky, tab nims 100mg, cap caricef 40mg). The other **2 are "character confusion"**: tab novidat → "i» welll" and tab distalgesic → "wr". There were no engine errors.

## Conclusions (submission checklist)
- **Which stage improved:** segmentation/text detection. Blank predictions fell from 42 to 15, and edit distance and CER both dropped.
- **Which failure remained:** character recognition of cursive. Only 1 of 89 names is read exactly, and the hardest images still produce nothing or garbled text.
- **Why it is not suitable for autonomous clinical transcription:** Tesseract is trained mainly on printed text. A CER of about 0.8 means most characters are wrong, and a misread medicine name or dose could harm a patient. A real system would need:
  - a handwriting-specific recogniser;
  - representative training data and external validation;
  - privacy controls;
  - mandatory human verification.

  It must never decide medication or dosage from uncertain text.
