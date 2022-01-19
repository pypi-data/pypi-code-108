import torch
import random
import transformers
import pandas as pd

def generate_next_sentence(text):
    
    sentence_a = []
    sentence_b = []
    label = []
    n_lines = len(text['sentence'])
    for i, line in enumerate(text['sentence']):
        # 50/50 whether is IsNextSentence or NotNextSentence
        if random.random() >= 0.5:
            # this is IsNextSentence
            sentence_a.append(line)
            sentence_b.append(text['next_sentence'][i])
            label.append(0)
        else:
            index = random.randint(0, n_lines-1)
            # this is NotNextSentence
            sentence_a.append(line)
            sentence_b.append(text['next_sentence'][index])
            label.append(1)
    
    return sentence_a, sentence_b, label


def mask_for_mlm(inputs):
    
    # create random array of floats with equal dimensions to input_ids tensor
    rand = torch.rand(inputs.input_ids.shape)
    # create mask array
    mask_arr = (rand < 0.15) * (inputs.input_ids != 4) * \
               (inputs.input_ids != 5) * (inputs.input_ids != 1)
    selection = []

    for i in range(inputs.input_ids.shape[0]):
        selection.append(
            torch.flatten(mask_arr[i].nonzero()).tolist()
        )

    for i in range(inputs.input_ids.shape[0]):
        inputs.input_ids[i, selection[i]] = 0
    
    return(inputs)

def generate_inputs_from_text(tokenizer, text):
    
    sentence_a, sentence_b, label = generate_next_sentence(text)
    
    inputs = tokenizer(sentence_a, sentence_b, return_tensors='pt',
                   max_length=512, truncation=True, padding='max_length')
    
    inputs['next_sentence_label'] = torch.LongTensor([label]).T
    inputs['labels'] = inputs.input_ids.detach().clone()
    inputs = mask_for_mlm(inputs)
    
    return(inputs)


class CorpusDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings
    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
    def __len__(self):
        return len(self.encodings.input_ids)
    

def train_Bert4PT(model, tokenizer, text, batch_size=4):
    
    inputs = generate_inputs_from_text(tokenizer, text)
    dataset = CorpusDataset(inputs)
    early_stopping = transformers.EarlyStoppingCallback(early_stopping_patience= 5)
    
    
    
    training_args = transformers.TrainingArguments(output_dir='./results',          # output directory
                                                   num_train_epochs=3,              # total # of training epochs
                                                   per_device_train_batch_size=8,  # batch size per device during training
                                                   per_device_eval_batch_size=8,   # batch size for evaluation
                                                   warmup_steps=500,                # number of warmup steps for learning rate scheduler
                                                   weight_decay=0.01,               # strength of weight decay
                                                   logging_dir='./logs',
                                                   load_best_model_at_end=True,
                                                   evaluation_strategy="epoch",
                                                   save_strategy = "epoch")

    trainer = transformers.Trainer(model=model,                         # the instantiated Transformers model to be trained
                                   args=training_args,                  # training arguments, defined above
                                   train_dataset=dataset,               # training dataset
                                   eval_dataset=dataset,                # evaluation dataset
                                   callbacks = [early_stopping])
    
    trainer.place_model_on_device = True
    
    trainer.train()
    trainer.push_to_hub("pablouribe/bertstem")
    
    
    return(model)


def get_text_from_files(files_path):
    
    list_dfs = []
    for file in files_path:
        with open(file) as f:
            lines = f.readlines()

        lines = [line.rstrip('\n') for line in lines]
        lines = [line for line in lines if line != '']

        df_transcription = pd.DataFrame()
        df_transcription['line'] = lines
        df_transcription['next_line'] = df_transcription['line'].shift(-1).fillna(df_transcription['line'])
        list_dfs.append(df_transcription)

    df_transcriptions = pd.concat(list_dfs).dropna()

    text = {}
    text['sentence'] = df_transcriptions['line'].astype(str).values
    text['next_sentence'] = df_transcriptions['next_line'].astype(str).values

    return(text)
