# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#
# For BERT and HuggingFace Transformers:
#
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Specified Intended uses & limitations (https://huggingface.co/bert-base-uncased)
#
# You can use the raw model for either masked language modeling or next sentence prediction,
# but it's mostly intended to be fine-tuned on a downstream task.
# See the model hub to look for fine-tuned versions on a task that interests you.
#
# Note that this model is primarily aimed at being fine-tuned on tasks that use the whole
# sentence (potentially masked) to make decisions, such as sequence classification, token
# classification or question answering. For tasks such as text generation you should look
# at model like GPT2.
#
# For BERTClass:
#
# MIT License
#
# Copyright (c) 2020 Abhishek Kumar Mishra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""BERTClass class for constructing neural-net using BERT"""

import logging
import torch
import transformers

from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.dnn.nlp.classification.common.constants import MultiLabelParameters
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language

logger = logging.getLogger(__name__)


class BERTClass(torch.nn.Module):
    """Class for creating the neural network using pretrained BERT.

    Creating the customized model, by adding a drop out and a dense layer on top of BERT
    to get the final output for the model.
    """
    BERT_BASE_HIDDEN_DIM = 768

    def __init__(self, dataset_language, num_label_cols):
        """Init function definition.
        :param dataset_language: language code of dataset
        :param num_label_cols: Number of unique classes in label column
        """
        super(BERTClass, self).__init__()
        model_name, download_dir = get_model_from_language(dataset_language, need_path=True,
                                                           is_multilabel_training=True)
        if download_dir is None:
            raise ClientException('CDN could not be downloaded', has_pii=False)
        self.l1 = transformers.BertModel.from_pretrained(download_dir, return_dict=False)
        self.l2 = torch.nn.Dropout(MultiLabelParameters.DROPOUT)
        self.l3 = torch.nn.Linear(self.BERT_BASE_HIDDEN_DIM, num_label_cols)
        self.model_name = model_name

    def forward(self, ids, mask, token_type_ids):
        """Forward function definition."""
        _, output_1 = self.l1(ids, attention_mask=mask, token_type_ids=token_type_ids)
        output_2 = self.l2(output_1)
        output = self.l3(output_2)
        return output
