from transformers import AutoTokenizer, AutoModelForTokenClassification

from adaptor.lang_module import LangModule
from adaptor.objectives.MLM import MaskedLanguageModeling
from adaptor.objectives.classification import TokenClassification
from adaptor.schedules import SequentialSchedule, StoppingStrategy
from adaptor.adapter import Adapter, AdaptationArguments

import torch

training_arguments = AdaptationArguments(output_dir="adaptation_output_dir",
                                         stopping_strategy=StoppingStrategy.FIRST_OBJECTIVE_NUM_EPOCHS,
                                         do_train=True,
                                         do_eval=True,
                                         gradient_accumulation_steps=2,
                                         log_level="critical",
                                         logging_steps=1,
                                         num_train_epochs=1)


# 1. pick the models - randomly pre-initialize the appropriate heads
lang_module = LangModule("bert-base-multilingual-cased")

# 2. pick objectives
# Objectives take either List[str] for in-memory iteration, or a source file path for streamed iteration
objectives = [MaskedLanguageModeling(lang_module,
                                     batch_size=1,
                                     texts_or_path="tests/mock_data/domain_unsup.txt"),
              TokenClassification(lang_module,
                                  batch_size=1,
                                  texts_or_path="tests/mock_data/ner_texts_sup.txt",
                                  labels_or_path="tests/mock_data/ner_texts_sup_labels.txt")]

# 3. pick a schedule of the selected objectives
# This one will initially fit the first objective to the convergence on its eval set, fit the second 
schedule = SequentialSchedule(objectives, training_arguments)

# 4. Run the training using Adapter, similarly to running HF.Trainer, only adding `schedule`
adapter = Adapter(lang_module, schedule, training_arguments)
adapter.train()

# 5. save the trained lang_module (with all heads)
adapter.save_model("entity_detector_model")


# 6. reload and use it like any other Hugging Face model
ner_model = AutoModelForTokenClassification.from_pretrained("entity_detector_model/TokenClassification/")
tokenizer = AutoTokenizer.from_pretrained("entity_detector_model/TokenClassification/")

inputs = tokenizer("Is there any Abraham Lincoln here?", return_tensors="pt")
outputs = ner_model(**inputs)
token_ids = torch.argmax(outputs.logits, dim=-1)[0].tolist()
print([ner_model.config.id2label[i] for i in token_ids])
