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

from ernie import SentenceClassifier, Models
from transformers import AutoTokenizer, TFAutoModel, AutoConfig
import pandas as pd
import numpy as np
import torch

import os

from results_analyze.rules_analyze import LicenseRulesInfo

# Device has a NVIDIA GPU with CUDA Compute Score > 2.
HAS_CUDA_GPU = True
# Save all iterations of the models
SAVE_ALL_MODEL_VERSIONS = True

# Link - https://huggingface.co/ayansinha
HFACE_ACCOUNT = 'ayansinha/'

# Refer Model Cards for More Information
# Cards are also locally present at `src/results_analyze/data/nlp-models/model-name/README.md`
HFACE_MODEL_NAME_FALSE_POS = 'false-positives-scancode-bert-base-uncased-L8-1'
HFACE_MODEL_NAME_LIC_CLASS = 'lic-class-scancode-bert-base-cased-L32-1'


# Is CUDA libraries and a CUDA capable GPU available
def is_cuda_gpu_available():
    assert (torch.cuda.is_available())
    assert (torch.cuda.device_count() > 0)


class SentenceClassifierTransformer:

    def __init__(self, hface_model_name, max_len, labels_no, classifier=None):

        self.classifier = classifier

        self.hface_model_name = hface_model_name
        self.local_model_dir = os.path.join(os.path.dirname(__file__), 'data/nlp-models/' + hface_model_name)
        self.version = 1
        self.local_model_dir_new = os.path.join(self.local_model_dir, '-v' + str(self.version))

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

        if self.config is None:
            try:
                self.classifier.dump(classifier_path)
            except FileExistsError:
                self.version += 1
                self.local_model_dir_new = os.path.join(self.local_model_dir, 'v' + str(self.version))
                self.classifier.dump(self.local_model_dir_new)
        else:
            try:
                os.makedirs(self.local_model_dir_new)
            except FileExistsError:
                self.version += 1
                self.local_model_dir_new = os.path.join(self.local_model_dir, 'v' + str(self.version))
                os.makedirs(self.local_model_dir_new)

            self._model.save_pretrained(self.local_model_dir_new)
            self._tokenizer.save_pretrained(self.local_model_dir_new)
            self._config.save_pretrained(self.local_model_dir_new)

    def load_classifier_new(self):

        self.classifier = SentenceClassifier(model_name=Models.BertBaseUncased, max_length=self.max_length_sentence,
                                             labels_no=self.labels_no)

    def load_classifier_from_local_backup(self, classifier_path):

        self.classifier = SentenceClassifier(model_path=classifier_path, max_length=self.max_length_sentence,
                                             labels_no=self.labels_no)

    def load_classifier_from_online_backup(self, hface_model_name):

        hface_model_path = HFACE_ACCOUNT + hface_model_name

        self._tokenizer = AutoTokenizer.from_pretrained(hface_model_path)
        self._model = TFAutoModel.from_pretrained(hface_model_path)
        self._config = AutoConfig.from_pretrained(hface_model_path)

        self.save_classifier(self.local_model_dir_new)

        self.load_classifier_from_local_backup(self.local_model_dir_new)

    def load_classifier(self, classifier_type='new'):

        if classifier_type == 'new':
            self.load_classifier_new()
        elif classifier_type == 'offline_backup':
            self.load_classifier_from_local_backup(classifier_path=self.local_model_dir)
        elif classifier_type == 'online_backup':
            self.load_classifier_from_online_backup(hface_model_name=self.hface_model_name)


class NLPModelsTrain:

    def __init__(self):
        """
        Constructor for NLPModelsErnie.
        """

        if HAS_CUDA_GPU:
            is_cuda_gpu_available()

        self.lic_rule_info = LicenseRulesInfo()

        self.false_positive_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_FALSE_POS,
                                                                       max_len=8, labels_no=2)
        self.license_class_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_LIC_CLASS,
                                                                      max_len=32, labels_no=4)

    def prepare_input_data_false_positive(self):
        lic_tags_positive = self.lic_rule_info.rule_df.query("is_license_tag == True")
        lic_tags_negative = self.lic_rule_info.rule_df.query("is_negative == True")

        rule_texts_pos = lic_tags_positive[["Rule_text"]].copy()
        rule_texts_pos.loc[:, [1]] = 1
        rule_texts_pos.rename(columns={"Rule_text": 0}, inplace=True)

        rule_texts_neg = lic_tags_negative[["Rule_text"]].copy()
        rule_texts_neg.loc[:, [1]] = 0
        rule_texts_neg.rename(columns={"Rule_text": 0}, inplace=True)

        rule_texts_df = pd.concat([rule_texts_pos, rule_texts_neg])

        rule_texts_df.index = pd.RangeIndex(start=0, stop=rule_texts_df.shape[0])

        input_data_false_pos = rule_texts_df.sample(frac=1).reset_index(drop=True)

        return input_data_false_pos

    @staticmethod
    def divide_rules_into_classes(df):
        mask_text = df["is_license_text"]
        mask_notice = np.bitwise_and(np.bitwise_not(mask_text), df["is_license_notice"])
        mask_tag = np.bitwise_and(np.bitwise_not(mask_notice), df["is_license_tag"])
        mask_reference = np.bitwise_and(np.bitwise_not(mask_tag), df["is_license_reference"])

        df.loc[mask_text, "class"] = 0
        df.loc[mask_notice, "class"] = 1
        df.loc[mask_tag, "class"] = 2
        df.loc[mask_reference, "class"] = 3

    def prepare_input_data_lic_class(self):
        lic_rules = self.lic_rule_info.rule_df.copy()
        lic_rules["class"] = 0

        self.divide_rules_into_classes(lic_rules)

        all_rules_input = lic_rules.loc[(lic_rules["class"] >= 0), ["Rule_text", "class"]]
        all_rules_input.rename(columns={"Rule_text": 0, "class": 1}, inplace=True)

        all_rules_input.index = pd.RangeIndex(start=0, stop=all_rules_input.shape[0])

        input_data_lic_class = all_rules_input.sample(frac=1).reset_index(drop=True)

        return input_data_lic_class

    @staticmethod
    def fine_tune_bert_on_data(classifier, input_data, epochs_num=4, validation_split=0.1):
        classifier.load_dataset(input_data, validation_split=validation_split)

        classifier.fine_tune(epochs=epochs_num, learning_rate=2e-5, training_batch_size=32, validation_batch_size=64)

    def train_basic_false_positive_classifier(self, classifier_type='new'):
        input_data = self.prepare_input_data_false_positive()

        self.false_positive_classifier.load_classifier(classifier_type)

        self.fine_tune_bert_on_data(classifier=self.false_positive_classifier.classifier, input_data=input_data)

        self.false_positive_classifier.save_classifier(self.false_positive_classifier.local_model_dir_new)

    def train_basic_lic_class_classifier(self, classifier_type='new'):
        input_data = self.prepare_input_data_lic_class()

        self.license_class_classifier.load_classifier(classifier_type)

        self.fine_tune_bert_on_data(classifier=self.license_class_classifier.classifier, input_data=input_data)

        self.license_class_classifier.save_classifier(self.license_class_classifier.local_model_dir_new)


class NLPModelsPredict:

    def __init__(self):
        """
        Constructor for NLPModelsErnie.
        """

        if HAS_CUDA_GPU:
            is_cuda_gpu_available()

        self.lic_rule_info = LicenseRulesInfo()

        self.classifier_dir_path_local = self.hdf_dir = os.path.join(os.path.dirname(__file__), 'data/nlp-models/')

        self.false_positive_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_FALSE_POS,
                                                                       max_len=8, labels_no=2)
        self.license_class_classifier = SentenceClassifierTransformer(hface_model_name=HFACE_MODEL_NAME_LIC_CLASS,
                                                                      max_len=32, labels_no=4)

    def predict_basic_false_positive(self, sen_list, classifier_type='online'):
        self.false_positive_classifier.load_classifier(classifier_type)

        predictions = self.false_positive_classifier.classifier.predict(sen_list)

        return predictions

    def predict_basic_lic_class(self, sen_list, classifier_type='online'):
        self.license_class_classifier.load_classifier(classifier_type)

        predictions = self.license_class_classifier.classifier.predict(sen_list)

        return predictions
