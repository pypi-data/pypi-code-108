# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
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

torch_present = False
try:
    import torch
    from torch.utils.data import (DataLoader, RandomSampler,
                                  SequentialSampler,
                                  TensorDataset)

    from torch.nn import CrossEntropyLoss, MSELoss
    from torch import nn

    from .modeling_bert_no_apex import (BertConfig,
                                        BertModel,
                                        BertForSequenceClassification,
                                        BertPreTrainedModel,
                                        gelu as bert_gelu
                                        )

    from pytorch_transformers import (BertTokenizer,
                                      XLNetModel,
                                      XLNetConfig,
                                      XLNetForSequenceClassification,
                                      XLNetTokenizer)

    from pytorch_transformers.modeling_xlnet import (XLNetPreTrainedModel,
                                                     SequenceSummary,
                                                     gelu as xlnet_gelu)

    MODEL_CLASSES = {
        'bert': (BertConfig, BertForSequenceClassification, BertTokenizer),
        'xlnet': (XLNetConfig, XLNetForSequenceClassification, XLNetTokenizer),
    }
    torch_present = True
except ImportError:
    torch_present = False


if torch_present:
    class BertTransformerLowerDim(BertPreTrainedModel):
        def __init__(self, config):
            super(BertTransformerLowerDim, self).__init__(config)

            self.num_labels = config.num_labels
            self.bert = BertModel(config)
            self.dropout = nn.Dropout(config.hidden_dropout_prob)

            hdim = 150
            self.hidden_layer = nn.Linear(config.hidden_size, hdim)
            self.classifier = nn.Linear(hdim, self.config.num_labels)
            self.apply(self.init_weights)

        def set_transform_type(self, transform_type):
            self.transform_type = transform_type

        def get_transform_type(self):
            try:
                ret = self.transform_type
            except AttributeError:
                ret = "probabilities"
            return ret

        def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                    labels=None, position_ids=None, head_mask=None):
            outputs = self.bert(input_ids, position_ids=position_ids,
                                token_type_ids=token_type_ids,
                                attention_mask=attention_mask,
                                head_mask=head_mask)
            pooled_output = outputs[1]
            pooled_output = self.dropout(pooled_output)
            hidden_output = bert_gelu(
                self.dropout(self.hidden_layer(pooled_output)))
            clf_out = self.classifier(hidden_output)
            if self.get_transform_type() == "embedding":
                clf_out = hidden_output

            # add hidden states and attention if they are here
            outputs = (clf_out,) + outputs[2:]

            if labels is not None and\
                    self.get_transform_type() not in ["embedding", "prediction"]:
                if self.num_labels == 1:
                    #  We are doing regression
                    loss_fct = MSELoss()
                    loss = loss_fct(clf_out.view(-1), labels.view(-1))
                else:
                    loss_fct = CrossEntropyLoss()
                    loss = loss_fct(clf_out.view(-1, self.num_labels),
                                    labels.view(-1))
            else:
                loss = None
            outputs = (loss,) + outputs
            return outputs  # (loss), logits, (hidden_states), (attentions)

    class BertTransformerLinear(BertPreTrainedModel):
        def __init__(self, config):
            super(BertTransformerLinear, self).__init__(config)
            self.num_labels = config.num_labels
            self.bert = BertModel(config)
            self.dropout = nn.Dropout(config.hidden_dropout_prob)
            self.classifier = nn.Linear(config.hidden_size, self.config.num_labels)
            self.apply(self.init_weights)

        def set_transform_type(self, transform_type):
            self.transform_type = transform_type

        def get_transform_type(self):
            try:
                ret = self.transform_type
            except AttributeError:
                ret = "probabilities"
            return ret

        def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                    labels=None, position_ids=None, head_mask=None):
            outputs = self.bert(input_ids, position_ids=position_ids,
                                token_type_ids=token_type_ids,
                                attention_mask=attention_mask,
                                head_mask=head_mask)
            pooled_output = outputs[1]

            pooled_output = self.dropout(pooled_output)
            clf_out = self.classifier(pooled_output)
            if self.get_transform_type() == "embedding":
                clf_out = pooled_output

            # add hidden states and attention if they are here
            outputs = (clf_out,) + outputs[2:]

            if labels is not None and\
                    self.get_transform_type() not in ["embedding", "prediction"]:
                if self.num_labels == 1:
                    #  We are doing regression
                    loss_fct = MSELoss()
                    loss = loss_fct(clf_out.view(-1), labels.view(-1))
                else:
                    loss_fct = CrossEntropyLoss()
                    loss = loss_fct(clf_out.view(-1, self.num_labels),
                                    labels.view(-1))
            else:
                loss = None
            outputs = (loss,) + outputs
            return outputs  # (loss), logits, (hidden_states), (attentions)

    class XLNetTransformerLinear(XLNetPreTrainedModel):
        def __init__(self, config):
            super(XLNetTransformerLinear, self).__init__(config)
            self.num_labels = config.num_labels

            self.transformer = XLNetModel(config)
            self.sequence_summary = SequenceSummary(config)
            self.logits_proj = nn.Linear(config.d_model, config.num_labels)

            self.apply(self.init_weights)

        def set_transform_type(self, transform_type):
            self.transform_type = transform_type

        def get_transform_type(self):
            try:
                ret = self.transform_type
            except AttributeError:
                ret = "probabilities"
            return ret

        def forward(self, input_ids, token_type_ids=None, input_mask=None,
                    attention_mask=None, mems=None, perm_mask=None,
                    target_mapping=None, labels=None, head_mask=None):
            transformer_outputs = self.transformer(input_ids,
                                                   token_type_ids=token_type_ids,
                                                   input_mask=input_mask,
                                                   attention_mask=attention_mask,
                                                   mems=mems, perm_mask=perm_mask,
                                                   target_mapping=target_mapping,
                                                   head_mask=head_mask)
            output = transformer_outputs[0]

            output = self.sequence_summary(output)
            clf_out = self.logits_proj(output)
            if self.get_transform_type() == "embedding":
                clf_out = output
            # Keep mems, hidden states, attentions if there are in it
            outputs = (clf_out,) + transformer_outputs[1:]

            if labels is not None and\
                    self.get_transform_type() not in ["embedding", "prediction"]:
                if self.num_labels == 1:
                    #  We are doing regression
                    loss_fct = MSELoss()
                    loss = loss_fct(clf_out.view(-1), labels.view(-1))
                else:
                    loss_fct = CrossEntropyLoss()
                    loss = loss_fct(clf_out.view(-1, self.num_labels),
                                    labels.view(-1))
            else:
                loss = None
            outputs = (loss,) + outputs

            return outputs

    class XLNetTransformerLowerDim(XLNetPreTrainedModel):
        def __init__(self, config):
            super(XLNetTransformerLowerDim, self).__init__(config)
            self.num_labels = config.num_labels

            self.transformer = XLNetModel(config)
            self.sequence_summary = SequenceSummary(config)

            hdim = 150
            # TODO: xlnet doesn't use dropout,
            # so we need to check whether it's needed for the hidden layer here
            self.dropout = nn.Dropout(config.summary_last_dropout)
            self.hidden_layer = nn.Linear(config.d_model, hdim)
            self.logits_proj = nn.Linear(hdim, self.config.num_labels)

            self.apply(self.init_weights)

        def set_transform_type(self, transform_type):
            self.transform_type = transform_type

        def get_transform_type(self):
            try:
                ret = self.transform_type
            except AttributeError:
                ret = "probabilities"
            return ret

        def forward(self, input_ids, token_type_ids=None, input_mask=None,
                    attention_mask=None, mems=None, perm_mask=None,
                    target_mapping=None, labels=None, head_mask=None):
            transformer_outputs = self.transformer(input_ids,
                                                   token_type_ids=token_type_ids,
                                                   input_mask=input_mask,
                                                   attention_mask=attention_mask,
                                                   mems=mems, perm_mask=perm_mask,
                                                   target_mapping=target_mapping,
                                                   head_mask=head_mask)
            output = transformer_outputs[0]

            output = self.sequence_summary(output)
            hidden_output = xlnet_gelu(self.dropout(self.hidden_layer(output)))
            clf_out = self.logits_proj(hidden_output)
            if self.get_transform_type() == "embedding":
                clf_out = hidden_output

            # Keep mems, hidden states, attentions if there are in it
            outputs = (clf_out,) + transformer_outputs[1:]

            if labels is not None and\
                    self.get_transform_type() not in ["embedding", "prediction"]:
                if self.num_labels == 1:
                    #  We are doing regression
                    loss_fct = MSELoss()
                    loss = loss_fct(clf_out.view(-1), labels.view(-1))
                else:
                    loss_fct = CrossEntropyLoss()
                    loss = loss_fct(clf_out.view(-1, self.num_labels),
                                    labels.view(-1))
            else:
                loss = None
            outputs = (loss,) + outputs

            return outputs
