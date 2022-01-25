class Config(object):
    n_classes = 2
    batch_size = 32
    split_ratio = 0.8
    n_epochs = 2
    seed_val = 42

    # optimizer conf
    lr = 2e-5
    eps = 1e-8

    # bert specific
    add_special_tokens = True     # Add '[CLS]' and '[SEP]'
    return_attention_mask = True  # Construct attn. masks.
    return_tensors = "pt"         # Return pytorch tensors.
    max_length = 32               # Max length of tokenized sequence
    padding = "max_length"        # Padding strategy
    truncation = True             # Truncate sequences?

    output_attention_weights = False
    output_hidden_states = False


    bert_model = "bert-base-multilingual-cased"
    label_reverse_index = {}
    label_index = {}
    pos_label = ""

    use_state_dict = False

    classes = []

    def to_dict(self):
        d = {"n_classes": self.n_classes,
             "batch_size": self.batch_size,
             "split_ratio": self.split_ratio,
             "n_epochs": self.n_epochs,
             "seed_val": self.seed_val,
             "lr": self.lr,
             "eps": self.eps,
             "add_special_tokens": self.add_special_tokens,
             "padding": self.padding,
             "truncation": self.truncation,
             "return_attention_mask": self.return_attention_mask,
             "return_tensors": self.return_tensors,
             "max_length": self.max_length,
             "bert_model": self.bert_model,
             "label_index": self.label_index,
             "label_reverse_index": self.label_reverse_index,
             "classes": self.classes,
             "pos_label": self.pos_label,
             "use_state_dict": self.use_state_dict
            }
        return d

    def update(self, kw, value):
        if kw == "n_classes":
            self.n_classes = value
        elif kw == "batch_size":
            self.batch_size = value
        elif kw == "split_ratio":
            self.split_ratio = value
        elif kw == "n_epochs":
            self.n_epochs = value
        elif kw == "seed_val":
            self.seed_val = value
        elif kw == "lr":
            self.lr = value
        elif kw == "eps":
            self.eps = value
        elif kw == "add_special_tokens":
            self.add_special_tokens = value
        elif kw == "padding":
            self.padding = value
        elif kw == "truncation":
            self.truncation = value
        elif kw == "return_attentioon_mask":
            self.return_attention_mask = value
        elif kw == "return_tensors":
            self.return_tensors = value
        elif kw == "max_length":
            self.max_length = value
        elif kw == "bert_model":
            self.bert_model = value
        elif kw == "label_reverse_index":
            self.label_reverse_index = value
        elif kw == "label_index":
            self.label_index = value
        elif kw == "output_attention_weights":
            self.output_attention_weights = value
        elif kw == "output_hidden_states":
            self.output_hidden_states = value
        elif kw == "classes":
            self.classes = value
        elif kw == "pos_label":
            self.pos_label = value
        elif kw == "use_state_dict":
            self.use_state_dict = value

    def update_bulk(self, kwargs):
        for kw, val in list(kwargs.items()):
            self.update(kw, val)
