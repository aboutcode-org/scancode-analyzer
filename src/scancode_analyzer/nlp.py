#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

# Refer https://github.com/labteral/ernie for usage docs
from ernie import SentenceClassifier, Models
# Imports for Upload Download using the Huggingface Transformers Library
# Docs - https://huggingface.co/transformers/model_sharing.html
from transformers import AutoTokenizer, TFAutoModel, AutoConfig

import pandas as pd
import numpy as np
import torch
import os

from analyzer_nlp.load_scancode_data import LicenseRulesInfo

# Device has a NVIDIA GPU with CUDA Compute Score > 2.
HAS_CUDA_GPU = True
# Save all iterations of the models
SAVE_ALL_MODEL_VERSIONS = True

# Link - https://huggingface.co/ayansinha
HFACE_ACCOUNT = 'ayansinha/'

# Refer Model Cards for More Information
# Cards are also locally present for each `model-name` at
# `src/results_analyze/data/nlp-models/model-name/README.md`
HFACE_MODEL_NAME_FALSE_POS = 'false-positives-scancode-bert-base-uncased-L8-1'
HFACE_MODEL_NAME_LIC_CLASS = 'lic-class-scancode-bert-base-cased-L32-1'


# Is CUDA libraries and a CUDA capable GPU available
def is_cuda_gpu_available():
    assert (torch.cuda.is_available())
    assert (torch.cuda.device_count() > 0)


# ToDo: Inherit from ernie `SentenceClassifier`.
class SentenceClassifierTransformer:

    def __init__(self, hface_model_name, max_len, labels_no, classifier=None):
        """
        Constructor for a SentenceClassifierTransformer object.
        This extends the ernie `SentenceClassifier` object with local/online backup options.
        """

        # An ernie `SentenceClassifier` object at
        # https://github.com/labteral/ernie/blob/master/ernie/ernie.py#L29
        self.classifier = classifier

        # Model name at huggingface for local/online backup
        self.hface_model_name = hface_model_name
        self.local_model_dir = os.path.join(os.path.dirname(__file__), 'data/nlp-models/' + hface_model_name)

        # naming support for backing up different versions locally
        self.version = 1
        self.local_model_dir_new = os.path.join(self.local_model_dir, '-v' + str(self.version))

        # Main Model Parameters
        self.max_length_sentence = max_len
        self.labels_no = labels_no

        self._model = None
        self._tokenizer = None
        self._config = None

    @property
    def model(self):
        return self._model

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def config(self):
        return self._config

    def save_classifier(self, classifier_path):
        """
        Saves classifier data to Local Storage.
        From self.classifier if new/local model, or from self.model if online downloaded model.
        Data Format - https://huggingface.co/transformers/model_sharing.html#check-the-directory-before-uploading
        Only has Tensorflow support for now, i.e. there will be a tf_model.h5 file.

        :param classifier_path : os.path
            Local Directory where model is to be saved.
        """

        # Case 1: Local/New Model, where self.classifier is an ernie `SentenceClassifier` object
        if self.config is None:
            try:
                self.classifier.dump(classifier_path)
            except FileExistsError:
                self.version += 1
                self.local_model_dir_new = os.path.join(self.local_model_dir, 'v' + str(self.version))
                self.classifier.dump(self.local_model_dir_new)
        # Case 2: Where self.classifier has to be initialized as an ernie `SentenceClassifier` object
        else:
            try:
                os.makedirs(self.local_model_dir_new)
            except FileExistsError:
                self.version += 1
                self.local_model_dir_new = os.path.join(self.local_model_dir, 'v' + str(self.version))
                os.makedirs(self.local_model_dir_new)

            self.model.save_pretrained(self.local_model_dir_new)
            self.tokenizer.save_pretrained(self.local_model_dir_new)
            self.config.save_pretrained(self.local_model_dir_new)

    def load_classifier_new(self):
        """
        Loads a pre-trained model, whose model identifier is `model_name`, from `ernie.AUTOSAVE_PATH` if
        downloaded before, or downloads the pre-trained model from huggingface website, and saves it locally,
        before loading it into a `ernie.SentenceClassifier` class, with the model parameters.
        Used parameters:
            - self.max_length_sentence:
                Max Sentence length for model input. Sentences are to be broken down into smaller sentences
                and the output aggregated, for bigger sentences.
            - self.labels_no:
                Number of classes in the classifier.
        """
        self.classifier = SentenceClassifier(model_name=Models.BertBaseUncased, max_length=self.max_length_sentence,
                                             labels_no=self.labels_no)

    def load_classifier_from_local_backup(self, classifier_path):
        """
        Loads a locally saved model, and then initializes a `ernie.SentenceClassifier` object, with the parameters.
        Used parameters:
            - model_path: os.path
                Local directory where the model is stored.
            - self.max_length_sentence:
                Max Sentence length for model input. Sentences are to be broken down into smaller sentences
                and the output aggregated, for bigger sentences.
            - self.labels_no:
                Number of classes in the classifier.
        """
        self.classifier = SentenceClassifier(model_path=classifier_path, max_length=self.max_length_sentence,
                                             labels_no=self.labels_no)

    def load_classifier_from_online_backup(self, hface_model_name):
        """
        Loads a pre-trained model, whose huggingface model identifier is `hface_model_name`, from `ernie.AUTOSAVE_PATH`
        if downloaded before, or downloads the fine-tuned sentence classifier model  from huggingface website,
        and saves it locally, before loading it into a `ernie.SentenceClassifier` object, with the model parameters.
        Used parameters:
            - hface_model_name and HFACE_ACCOUNT:
                Combines account name and model identifier for a full huggingface model identifier.
                Example - https://huggingface.co/ayansinha/false-positives-scancode-bert-base-uncased-L8-1
        """
        # huggingface model identifier
        hface_model_path = HFACE_ACCOUNT + hface_model_name

        # Load the model, tokenizer and config files required
        self._tokenizer = AutoTokenizer.from_pretrained(hface_model_path)
        self._model = TFAutoModel.from_pretrained(hface_model_path)
        self._config = AutoConfig.from_pretrained(hface_model_path)

        # Save locally in the `ernie` model format so a `ernie.SentenceClassifier` can be loaded and initialized
        # from this local copy.
        self.save_classifier(self.local_model_dir_new)

        # Initialize an `ernie.SentenceClassifier` object and load the model into the object from the saved
        # local copy.
        self.load_classifier_from_local_backup(self.local_model_dir_new)

    def load_classifier(self, classifier_type='new'):
        """
        Initializes a 'ernie.SentenceClassifier` object at self.classifier.

        :param classifier_type: string
            Options:
                - 'new': Initialize a new 'ernie.SentenceClassifier` object with a pre-trained BERT classifier.
                - 'offline_backup': Initialize a locally saved 'ernie.SentenceClassifier` object.
                - 'online_backup': Initialize an online-saved 'ernie.SentenceClassifier` object.
        """
        if classifier_type == 'new':
            self.load_classifier_new()
        elif classifier_type == 'offline_backup':
            self.load_classifier_from_local_backup(classifier_path=self.local_model_dir)
        elif classifier_type == 'online_backup':
            self.load_classifier_from_online_backup(hface_model_name=self.hface_model_name)


class NLPModelsTrain:

    def __init__(self):
        """
        Constructor for NLPModelsTrain.
        Initialize ernie `SentenceClassifier` objects and fine-tune them from scratch from a pretrained BERT model
        or re fine-tune an existing model.
        """

        # Checks for CUDA and CUDA capable GPUs
        if HAS_CUDA_GPU:
            is_cuda_gpu_available()

        # Loads Scancode Rules and Licenses to be used as training data.
        self.lic_rule_info = LicenseRulesInfo()

        # Initialize a False Positive Sentence Classifier
        self.false_positive_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_FALSE_POS,
                                                                       max_len=8, labels_no=2)

        # Initialize a License Class Sentence Classifier
        self.license_class_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_LIC_CLASS,
                                                                      max_len=32, labels_no=4)

    def prepare_input_data_false_positive(self):
        """
        Constructor for NLPModelsErnie.
        Initialize ernie `SentenceClassifier` objects and fine-tune them from scratch from a pretrained BERT model
        or re fine-tune an existing model.

        :returns input_data_false_pos: pd.DataFrame
            One Column with the sentences and one column with the labels
            (i.e. with a numerical value 0/1 depending on whether it is a False Positive or a License Tag)
        """

        # Queries all License Tag Rules
        lic_tags_positive = self.lic_rule_info.rule_df.query("is_license_tag == True")
        # Queries all the False Positive Rules
        lic_tags_negative = self.lic_rule_info.rule_df.query("is_negative == True")

        # Label the License Tags to belong in class 1
        rule_texts_pos = lic_tags_positive[["Rule_text"]].copy()
        rule_texts_pos.loc[:, [1]] = 1
        rule_texts_pos.rename(columns={"Rule_text": 0}, inplace=True)

        # Label the False Positives to belong in class 0
        rule_texts_neg = lic_tags_negative[["Rule_text"]].copy()
        rule_texts_neg.loc[:, [1]] = 0
        rule_texts_neg.rename(columns={"Rule_text": 0}, inplace=True)

        # Concatenate the Two DataFrames into a single DataFrame
        rule_texts_df = pd.concat([rule_texts_pos, rule_texts_neg])

        # Initialize a RangeIndex and randomly Re-Order the Rows to mix the two labels
        # Note: the classes are still unbalanced, i.e. one class has more examples than the other.
        rule_texts_df.index = pd.RangeIndex(start=0, stop=rule_texts_df.shape[0])
        input_data_false_pos = rule_texts_df.sample(frac=1).reset_index(drop=True)

        return input_data_false_pos

    @staticmethod
    def divide_rules_into_classes(df):
        """
        Assign each rule to a distinct class.

        :param df: pd.DataFrame
            A DataFrame with all the scancode rules, and an extra `class` column.
        """
        # As Scancode License Rules might have multiple classes, only take the dominant class (in this order)
        # This prepares row wise masks, to facilitate selection of all entries of that class, to assign their class.
        mask_text = df["is_license_text"]
        mask_notice = np.bitwise_and(np.bitwise_not(mask_text), df["is_license_notice"])
        mask_tag = np.bitwise_and(np.bitwise_not(mask_notice), df["is_license_tag"])
        mask_reference = np.bitwise_and(np.bitwise_not(mask_tag), df["is_license_reference"])

        # Label them as Classes 0-3, using the masks
        df.loc[mask_text, "class"] = 0
        df.loc[mask_notice, "class"] = 1
        df.loc[mask_tag, "class"] = 2
        df.loc[mask_reference, "class"] = 3

    def prepare_input_data_lic_class(self):

        # Load all the scancode rules, and make a new `class` column.
        lic_rules = self.lic_rule_info.rule_df.copy()
        lic_rules["class"] = 0

        # Assign each rule to a distinct class using the `divide_rules_into_classes` function.
        self.divide_rules_into_classes(lic_rules)

        # Only select two columns, the Rule Text, and the class.
        all_rules_input = lic_rules.loc[(lic_rules["class"] >= 0), ["Rule_text", "class"]]
        all_rules_input.rename(columns={"Rule_text": 0, "class": 1}, inplace=True)

        # Initialize a RangeIndex and randomly Re-Order the Rows to mix the two labels
        # Note: the classes are still unbalanced, i.e. one class has more examples than the other.
        all_rules_input.index = pd.RangeIndex(start=0, stop=all_rules_input.shape[0])
        input_data_lic_class = all_rules_input.sample(frac=1).reset_index(drop=True)

        return input_data_lic_class

    @staticmethod
    def fine_tune_bert_on_data(classifier, input_data, epochs_num=4, validation_split=0.1):
        """
        Fine-tine a pretrained BERT Transformer model to perform Multi-class Sentence Classification tasks on
        a specific input dataset.

        :param classifier: ernie.SentenceClassifier Object
            The Ernie SentenceClassifier Object which holds the Model and Training/Validation Data.
        :param input_data: pd.DataFrame
            Two column DataFrame, with the Text as Sentences and their Class Label as Integers.
        :param epochs_num: int
            How many cycles of Training to be performed on the Training Data
        :param validation_split: float
            What fraction of the Data will be kept for Model Validation (i.e. To Validate the model,
            To Validate how the model performs classification on previously unseen data)
            Value Range 0-1
        """

        # Load DataSet to Memory for Training, with a 90/10 Validation Split
        classifier.load_dataset(input_data, validation_split=validation_split)

        classifier.fine_tune(epochs=epochs_num, learning_rate=2e-5, training_batch_size=32, validation_batch_size=64)

    def train_basic_false_positive_classifier(self, classifier_type='new'):
        """
        Fine-tine a pretrained BERT Transformer model on the Scancode Rules to classify False Positives from Valid
        License Tags, using Binary (2-class) Sentence Classification.

        :param classifier_type: ernie.SentenceClassifier Object
            Options:
                - 'new': Initialize a new 'ernie.SentenceClassifier` object with a pre-trained BERT classifier.
                        (Default)
                - 'offline_backup': Initialize a locally saved 'ernie.SentenceClassifier` object.
                - 'online_backup': Initialize an online-saved 'ernie.SentenceClassifier` object.
        """
        # Load Training Data
        input_data = self.prepare_input_data_false_positive()

        # Load a transformer model by initializing a `ernie.SentenceClassifier` Object
        self.false_positive_classifier.load_classifier(classifier_type)

        # Fine-tune the pre-trained Transformer Model on `input_data`
        self.fine_tune_bert_on_data(classifier=self.false_positive_classifier.classifier, input_data=input_data)

        # Backup Classifier Weights/Parameters Locally
        self.false_positive_classifier.save_classifier(self.false_positive_classifier.local_model_dir_new)

    def train_basic_lic_class_classifier(self, classifier_type='new'):
        """
        Fine-tine a pretrained BERT Transformer model on the Scancode Rules to classify
        License Texts/Notices/Tags/References, using Multi-class Sentence Classification.

        :param classifier_type: ernie.SentenceClassifier Object
            Options:
                - 'new': Initialize a new 'ernie.SentenceClassifier` object with a pre-trained BERT classifier.
                        (Default)
                - 'offline_backup': Initialize a locally saved 'ernie.SentenceClassifier` object.
                - 'online_backup': Initialize an online-saved 'ernie.SentenceClassifier` object.
        """
        # Load Training Data
        input_data = self.prepare_input_data_lic_class()

        # Load a transformer model by initializing a `ernie.SentenceClassifier` Object
        self.license_class_classifier.load_classifier(classifier_type)

        # Fine-tune the pre-trained Transformer Model on `input_data`
        self.fine_tune_bert_on_data(classifier=self.license_class_classifier.classifier, input_data=input_data)

        # Backup Classifier Weights/Parameters Locally
        self.license_class_classifier.save_classifier(self.license_class_classifier.local_model_dir_new)


class NLPModelsPredict:

    def __init__(self):
        """
        Constructor for NLPModelsPredict.
        Initialize ernie `SentenceClassifier` objects by loading fine-tuned sentence classifiers for
        prediction of a batch of sentences.
        """

        # Checks for CUDA and CUDA capable GPUs
        if HAS_CUDA_GPU:
            is_cuda_gpu_available()

        # Loads Scancode Rules and Licenses to be used as training data.
        self.lic_rule_info = LicenseRulesInfo()

        # Initialize a False Positive Sentence Classifier
        self.false_positive_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_FALSE_POS,
                                                                       max_len=8, labels_no=2)
        # Initialize a License Class Sentence Classifier
        self.license_class_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_LIC_CLASS,
                                                                      max_len=32, labels_no=4)

    def predict_basic_false_positive(self, sen_list, classifier_type='online'):
        """
        Load a Fine-tined a BERT Transformer Model to predict False Positives from Valid License Tags,
        using Binary (2-class) Sentence Classification.

        :param sen_list: list
            List of sentences to Predict
        :param classifier_type: ernie.SentenceClassifier Object
            Options:
                - 'new': Initialize a new 'ernie.SentenceClassifier` object with a pre-trained BERT classifier.
                - 'offline_backup': Initialize a locally saved 'ernie.SentenceClassifier` object.
                - 'online_backup': Initialize an online-saved 'ernie.SentenceClassifier` object.  (Default)
        :returns predictions: pd.DataFrame
            A DataFrame with each column having confidence scores for a license class, and in each row
            confidence scores for all classes for that sentence.
        """
        # Load Training Data
        self.false_positive_classifier.load_classifier(classifier_type)

        # Generate Predictions using the Model
        predictions = self.false_positive_classifier.classifier.predict(sen_list)

        return predictions

    def predict_basic_lic_class(self, sen_list, classifier_type='online'):
        """
        Load a Fine-tined a BERT Transformer Model to predict False Positives from Valid License Tags,
        using Binary (2-class) Sentence Classification.

        :param sen_list: list
            List of sentences to Predict
        :param classifier_type: ernie.SentenceClassifier Object
            Options:
                - 'new': Initialize a new 'ernie.SentenceClassifier` object with a pre-trained BERT classifier.
                - 'offline_backup': Initialize a locally saved 'ernie.SentenceClassifier` object.
                - 'online_backup': Initialize an online-saved 'ernie.SentenceClassifier` object. (Default)
        :returns predictions: pd.DataFrame
            A DataFrame with each column having confidence scores for a license class, and in each row
            confidence scores for all classes for that sentence.
        """
        # Load Training Data
        self.license_class_classifier.load_classifier(classifier_type)

        # Generate Predictions using the Model
        predictions = self.license_class_classifier.classifier.predict(sen_list)

        return predictions
