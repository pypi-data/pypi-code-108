import torch
import numpy as np
import pandas as pd
import transformers
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score

from BERT_STEM.Encode import *
from BERT_STEM.TrainBERT4PT import *

class BertSTEM:
    
    def __init__(self, model_name = None):
        
        if model_name is not None:
            self.model_name = model_name

        else:
            self.model_name = "pablouribe/bertstem"

        self._model = transformers.BertModel.from_pretrained(self.model_name)

        self._tokenizer = transformers.BertTokenizerFast.from_pretrained("dccuchile/bert-base-spanish-wwm-uncased",
                                                                         do_lower_case = True,
                                                                         add_special_tokens = False)

    def _encode_df(self, df, column, encoding):

        return(sentence_encoder(df, self._model, self._tokenizer, column, encoding))

    def get_embedding_matrix(self):

        #Build the Embedding Matrix
        max_vocab = 50105
        bert_dim = 768
        embedding_matrix = np.zeros((max_vocab, bert_dim))
        
        with torch.no_grad():
            for i in range(max_vocab):
                try:
                    tokenized_text = self._tokenizer.decode([i])
                    indexed_tokens = self._tokenizer.convert_tokens_to_ids(tokenized_text)
                    tokens_tensor = torch.tensor([indexed_tokens]).to(torch.int64)
                    encoded_layers = self._model.get_input_embeddings()(tokens_tensor)[0]
                    
                    embedding_vector = np.array(encoded_layers)
                    embedding_matrix[i] = embedding_vector
                except:
                    pass

        return(embedding_matrix)


class BertSTEMForPreTraining:
    
    def __init__(self, model_name = None):
        
        if model_name is not None:
            self.model_name = model_name
        
        else:
            self.model_name = "pablouribe/bertstem"
        
        self._model = transformers.BertForPreTraining.from_pretrained(self.model_name)
        
        self._tokenizer = transformers.BertTokenizerFast.from_pretrained("dccuchile/bert-base-spanish-wwm-uncased",
                                                                         do_lower_case = True,
                                                                         add_special_tokens = False)

    def _train(self, text, checkpoint):
        
        train_Bert4PT(self._model, self._tokenizer, text)
    
    def _get_text_from_files(self, files_path):
        
            return(get_text_from_files(files_path))


class BertSTEMForTextClassification:
    
    def __init__(self, n, model_name = None):
        
        if model_name is not None:
            self.model_name = model_name
        
        else:
            self.model_name = "pablouribe/bertstem"
        
        self._model = transformers.BertForSequenceClassification.from_pretrained(self.model_name,
                                                                                 num_labels = n, # The number of output labels.
                                                                                 output_attentions = False, # Whether the model returns attentions weights.
                                                                                 output_hidden_states = False) # Whether the model returns all hidden-states.
                                                                                 
        
        self._tokenizer = transformers.BertTokenizerFast.from_pretrained("dccuchile/bert-base-spanish-wwm-uncased",
                                                                         do_lower_case = True,
                                                                         add_special_tokens = False)

    def _get_inputs_from_df(self, df, col_text, col_labels):

        # Tokenize all of the utterances and map the tokens to thier word IDs.
        text = df[col_text].values
        labels = df[col_labels].values

        encoded_dict = self._tokenizer.batch_encode_plus(
                                           list(text),                      # Sentence to encode.
                                           add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                                           max_length = 120,
                                           truncation = True,           # Pad & truncate all utterances.
                                           pad_to_max_length = True,
                                           return_attention_mask = True,   # Construct attn. masks.
                                           return_tensors = 'pt')
                                           
        encoded_dict['labels'] = torch.tensor(labels, dtype=torch.long)

        return(encoded_dict)
    
    def _compute_metrics(self, pred):
        
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
        acc = accuracy_score(labels, preds)
        bacc = balanced_accuracy_score(labels, preds)
        return {
            'bacc': bacc,
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }


    def _train(self, inputs_train, inputs_val, num_train_epochs=3, learning_rate=1e-5,
               load_best_model_at_end=True, early_stopping_patience=5, metric_for_best_model="bacc"):

        dataset_train = CorpusDataset(inputs_train)
        dataset_val = CorpusDataset(inputs_val)

        training_args = transformers.TrainingArguments(
                                               output_dir='./results',          # output directory
                                               num_train_epochs=num_train_epochs,              # total # of training epochs
                                               per_device_train_batch_size=8,  # batch size per device during training
                                               per_device_eval_batch_size=8,   # batch size for evaluation
                                               warmup_steps=500,                # number of warmup steps for learning rate scheduler
                                               weight_decay=0.01,               # strength of weight decay
                                               logging_dir='./logs',
                                               learning_rate = learning_rate,
                                               load_best_model_at_end=load_best_model_at_end,
                                               evaluation_strategy="epoch",
                                               save_strategy = "epoch",
                                               metric_for_best_model = metric_for_best_model)
        
        early_stopping = transformers.EarlyStoppingCallback(early_stopping_patience=5)
        
        if load_best_model_at_end:
            callbacks=[early_stopping]

        else:
            callbacks=[]

        trainer = transformers.Trainer(
                               model=self._model,                         # the instantiated Transformers model to be trained
                               args=training_args,                  # training arguments, defined above
                               train_dataset=dataset_train,               # training dataset
                               eval_dataset=dataset_val,                # evaluation dataset
                               callbacks = callbacks,
                               compute_metrics=self._compute_metrics)

        trainer.train()

        return()

    def predict(self, df, col_text):

        text = df[col_text].values
        
        encoded_text = self._tokenizer.batch_encode_plus(list(text),                # Sentence to encode.
                                                        add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                                                        max_length = 120,
                                                        truncation = True,           # Pad & truncate all utterances.
                                                        pad_to_max_length = True,
                                                        return_attention_mask = True,   # Construct attn. masks.
                                                        return_tensors = 'pt')


        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self._model.to(device)
        encoded_text.to(device)

        with torch.no_grad():
            logits = self._model(encoded_text['input_ids'])['logits']
        
        return(torch.nn.Softmax()(logits))


    def trainer_evaluate(self, df, col_text, col_labels, batch_size=8):

        encoded = self._get_inputs_from_df(df, col_text, col_labels)
        dataset = CorpusDataset(encoded)



        training_args = transformers.TrainingArguments(output_dir='./results',          # output directory
                                                       num_train_epochs=3,              # total # of training epochs
                                                       per_device_train_batch_size=8,  # batch size per device during training
                                                       per_device_eval_batch_size=batch_size,   # batch size for evaluation
                                                       warmup_steps=500,                # number of warmup steps for learning rate scheduler
                                                       weight_decay=0.01,               # strength of weight decay
                                                       logging_dir='./logs',
                                                       evaluation_strategy="epoch",
                                                       save_strategy = "epoch")

        trainer = transformers.Trainer(model=self._model,                         # the instantiated Transformers model to be trained
                                       args=training_args,                  # training arguments, defined above
                                       train_dataset=dataset)

        output = trainer.predict(dataset)

        return(output)
