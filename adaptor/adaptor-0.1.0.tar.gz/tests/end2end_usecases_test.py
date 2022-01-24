from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from adaptor.adapter import Adapter
from adaptor.evaluators.generative import BLEU
from adaptor.lang_module import LangModule
from adaptor.objectives.MLM import MaskedLanguageModeling
from adaptor.objectives.classification import TokenClassification
from adaptor.objectives.denoising import DenoisingObjective
from adaptor.objectives.seq2seq import Sequence2Sequence
from adaptor.schedules import ParallelSchedule
from utils import training_arguments, paths, test_base_models

unsup_target_domain_texts = paths["texts"]["target_domain"]["unsup"]
sup_target_domain_texts = paths["texts"]["target_domain"]["ner"]
sup_target_domain_labels = paths["labels"]["target_domain"]["ner"]


def test_adaptation_ner():
    # 1. pick the models - randomly pre-initialize the appropriate heads
    lang_module = LangModule(test_base_models["token_classification"])

    # 2. pick objectives
    # for datasets, pass in pre-loaded List[str] for in-memory iteration, or str of file path for online retrieval
    objectives = [MaskedLanguageModeling(lang_module,
                                         batch_size=1,
                                         texts_or_path=paths["texts"]["target_domain"]["unsup"]),
                  TokenClassification(lang_module,
                                      batch_size=1,
                                      texts_or_path=paths["texts"]["target_domain"]["ner"],
                                      labels_or_path=paths["labels"]["target_domain"]["ner"])]

    # 4. pick a schedule of the selected objectives
    schedule = ParallelSchedule(objectives, training_arguments)

    # 5. train using Adapter
    adapter = Adapter(lang_module, schedule, training_arguments)
    adapter.train()

    # 6. save the trained lang_module (with all heads)
    adapter.save_model("entity_detector_model")


def test_adaptation_translation():
    # 1. pick the models - randomly pre-initialize the appropriate heads
    lang_module = LangModule(test_base_models["translation"])

    # (optional) pick train and validation evaluators for the objectives
    seq2seq_evaluators = [BLEU(use_generate=True, decides_convergence=True)]

    # 2. pick objectives - we use BART's objective for adaptation and mBART's seq2seq objective for fine-tuning
    objectives = [DenoisingObjective(lang_module,
                                     batch_size=1,
                                     texts_or_path=paths["texts"]["target_domain"]["unsup"]),
                  Sequence2Sequence(lang_module, batch_size=1,
                                    texts_or_path=paths["texts"]["target_domain"]["translation"],
                                    val_evaluators=seq2seq_evaluators,
                                    labels_or_path=paths["labels"]["target_domain"]["translation"],
                                    source_lang_id="en", target_lang_id="cs")]
    # 3. pick a schedule of the selected objectives
    # this one will shuffle the batches of both objectives
    schedule = ParallelSchedule(objectives, training_arguments)

    # 4. train using Adapter
    adapter = Adapter(lang_module, schedule, training_arguments)
    adapter.train()

    # 5. save the trained (multi-headed) lang_module
    adapter.save_model("translator_model")

    # 6. reload and use it like any other Hugging Face model
    translator_model = AutoModelForSeq2SeqLM.from_pretrained("translator_model/Sequence2Sequence")
    tokenizer = AutoTokenizer.from_pretrained("translator_model/Sequence2Sequence")

    # 7. use the model anyhow you like, e.g. as a translator with iterative generation
    tokenizer.src_lang, tokenizer.tgt_lang = "en", "cs"

    inputs = tokenizer("A piece of text to translate.", return_tensors="pt")
    output_ids = translator_model.generate(**inputs)
    output_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    print(output_text)

# test_adaptation_translation()
