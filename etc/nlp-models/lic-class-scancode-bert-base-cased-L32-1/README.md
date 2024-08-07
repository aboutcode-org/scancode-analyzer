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

# `lic-class-scancode-bert-base-cased-L32-1`

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

Then in `NLPModelsPredict` class, function `predict_basic_lic_class` uses this
classifier to predict sentances as either valid license tags or false positives.

#### Limitations and bias

As this model is a fine-tuned version of the
[`bert-base-cased`](https://huggingface.co/bert-base-cased) model, it has the
same biases, but as the task it is fine-tuned to is a very specific task
(license text/notice/tag/referance) without those intended biases, it's safe to
assume those don't apply at all here.

## Training and Fine-Tuning Data

The BERT model was pretrained on BookCorpus, a dataset consisting of 11,038
unpublished books and English Wikipedia (excluding lists, tables and headers).

Then this `bert-base-cased` model was fine-tuned on Scancode Rule texts,
specifically trained in the context of sentence classification, where the four
classes are

    - License Text
    - License Notice
    - License Tag
    - License Referance

## Training procedure

For fine-tuning procedure and training, refer `scancode-results-analyzer` code.

- [Link to Code](https://github.com/aboutcode-org/scancode-results-analyzer/blob/master/src/results_analyze/nlp_models.py)

In `NLPModelsTrain` class, function `prepare_input_data_false_positive` prepares
the training data.

In `NLPModelsTrain` class, function `train_basic_false_positive_classifier`
fine-tunes this classifier.

1. Model - [BertBaseCased](https://huggingface.co/bert-base-cased) (Weights 0.5
   GB)
2. Sentence Length - 32
3. Labels - 4 (License Text/Notice/Tag/Referance)
4. After 4 Epochs of Fine-Tuning with learning rate 2e-5 (60 secs each on an
   RTX 2060)

Note: The classes aren't balanced.

## Eval results

- Accuracy on the training data (90%) : 0.98 (+- 0.01)
- Accuracy on the validation data (10%) : 0.84 (+- 0.01)

## Further Work

1. Apllying Splitting/Aggregation Strategies
2. Data Augmentation according to Vaalidation Errors
3. Bigger/Better Suited Models
