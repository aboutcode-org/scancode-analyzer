---
language: en
tags:
  - license
  - sentence-classification
  - scancode
  - license-compliance
license: apache-2.0
datasets:
  - bookcorpus
  - wikipedia
  - scancode-rules
version: 1.0
---

# `false-positives-scancode-bert-base-uncased-L8-1`

## Intended Use

This model is intended to be used for Sentence Classification which is used for
results analysis in
[`scancode-results-analyzer`](https://github.com/aboutcode-org/scancode-results-analyzer).

`scancode-results-analyzer` helps detect faulty scans in
[`scancode-toolkit`](https://github.com/aboutcode-org/scancode-results-analyzer)
by using statistics and nlp modeling, among other tools, to make Scancode
better.

#### How to use

Refer
[quickstart](https://github.com/aboutcode-org/scancode-results-analyzer#quickstart---local-machine)
section in `scancode-results-analyzer` documentation, for installing and getting
started.

- [Link to Code](https://github.com/aboutcode-org/scancode-results-analyzer/blob/master/src/results_analyze/nlp_models.py)

Then in `NLPModelsPredict` class, function `predict_basic_false_positive` uses
this classifier to predict sentances as either valid license tags or false
positives.

#### Limitations and bias

As this model is a fine-tuned version of the
[`bert-base-uncased`](https://huggingface.co/bert-base-uncased) model, it has
the same biases, but as the task it is fine-tuned to is a very specific field
(license tags vs false positives) without those intended biases, it's safe to
assume those don't apply at all here.

## Training and Fine-Tuning Data

The BERT model was pretrained on BookCorpus, a dataset consisting of 11,038
unpublished books and English Wikipedia (excluding lists, tables and headers).

Then this `bert-base-uncased` model was fine-tuned on Scancode Rule texts,
specifically trained in the context of sentence classification, where the two
classes are

    - License Tags
    - False Positives of License Tags

## Training procedure

For fine-tuning procedure and training, refer `scancode-results-analyzer` code.

- [Link to Code](https://github.com/aboutcode-org/scancode-results-analyzer/blob/master/src/results_analyze/nlp_models.py)

In `NLPModelsTrain` class, function `prepare_input_data_false_positive` prepares
the training data.

In `NLPModelsTrain` class, function `train_basic_false_positive_classifier`
fine-tunes this classifier.

1. Model - [BertBaseUncased](https://huggingface.co/bert-base-uncased) (Weights
   0.5 GB)
2. Sentence Length - 8
3. Labels - 2 (False Positive/License Tag)
4. After 4-6 Epochs of Fine-Tuning with learning rate 2e-5 (6 secs each on an
   RTX 2060)

Note: The classes aren't balanced.

## Eval results

- Accuracy on the training data (90%) : 0.99 (+- 0.005)
- Accuracy on the validation data (10%) : 0.96 (+- 0.015)

The errors have lower confidence scores using thresholds on confidence scores
almost makes it a perfect classifier as the classification task is comparatively
easier.

Results are stable, in the sence fine-tuning accuracy is very easily achieved
every time, though more learning epochs makes the data overfit, i.e. the
training loss decreases, but the validation loss increases, even though
accuracies are very stable even on overfitting.
