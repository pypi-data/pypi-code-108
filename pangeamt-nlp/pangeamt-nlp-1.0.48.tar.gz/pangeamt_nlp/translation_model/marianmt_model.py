
from pangeamt_nlp.translation_model.translation_model_base import (
    TranslationModelBase,
)
from typing import List, Tuple, Dict
# pip install websocket_client  
from websocket import create_connection
import subprocess
import os
import sys
import tempfile

class ONMT_model(TranslationModelBase):
    NAME = "marianmt"
    INITIALIZED = False
    DEFAULT = (
        "--type transformer \
        --max-length 300 \
        --mini-batch-fit -w 10000 --maxi-batch 1000 \
        --early-stopping 10 --cost-type=ce-mean-words \
        --valid-freq 5000 --save-freq 5000 --disp-freq 500 \
        --valid-metrics ce-mean-words perplexity \
        --valid-mini-batch 64 \
        --beam-size 6 --normalize 1 \
        --enc-depth 6 --dec-depth 6 \
        --transformer-heads 8 --transformer-dim-ffn 2048 --dim-emb 512 \
        --transformer-postprocess-emb d \
        --transformer-postprocess dan \
        --transformer-dropout 0.1 --label-smoothing 0.1 \
        --learn-rate 0.0003 --lr-warmup 8000 --lr-decay-inv-sqrt 8000 --lr-report \
        --optimizer-params 0.9 0.998 1e-09 --clip-norm 0 \
        --tied-embeddings-all \
        --sync-sgd --seed 1111 \
        --exponential-smoothing \
        -a 1000Ku"

    )

    DEFAULT_DECODING = {
        "gpu": -1, "n_best": 5, "min_length": 0, "max_length": 300,
        "ratio": 0.0, "beam_size": 6, "seed": 1111, "in_training_servers": True,
        "marian_path": "/home/pangeanic/marian/build"
    }

    def __init__(self, path: str, **kwargs) -> None:
        super().__init__()
        self._args = kwargs
        if not kwargs["in_training_servers"]:
            self._load(path, **kwargs)
        self._trainer = None
    

    @staticmethod
    def extract_vocab(
        data_path: str, model_path: str, marian_path: str, **kwargs
    ):

        command = (
              f"cat {data_path}/train_src.txt  {data_path}/train_tgt.txt | " 
            + f"{marian_path}/marian-vocab --max-size 36000 > {model_path}/vocab.yml"
        )
        print(command)
        os.system(f'{command} | tee -a workflow.log')

    @staticmethod
    def train(
            data_path: str, model_path: str, marian_path: str, *args, gpu: str = None, **kwargs
    ):

        prepend_args = (
              f"--model {model_path}/model.npz "
            + f"--train-sets {data_path}/train_src.txt {data_path}/train_tgt.txt "
            + f"--vocabs {model_path}/vocab.yml {model_path}/vocab.yml "
            + f"--valid-sets {data_path}/dev_src.txt {data_path}/dev_tgt.txt "
            + f"--valid-translation-output {data_path}/dev.output "
            + f"--quiet-translation --log {model_path}/train.log --valid-log "
            + f"{model_path}/valid.log --overwrite --keep-best "
        )
        if gpu:
            apend_args = f" --devices {gpu} "
        else:
            apend_args = f" --cpu-threads 15 "
        args = (prepend_args + (" ").join(list(args)) + " " + apend_args).split(" ")
        args = " ".join(args)
        command = (f"{marian_path}/marian {args}")
        os.system(f'{command} | tee -a workflow.log')

    def _load(self, path: str, **kwargs) -> None:
            if kwargs["gpu"] >= 0:
                device_args = f' --devices {kwargs["gpu"]} '
            else:
                device_args = f' --cpu-threads 6 '
            command = f'{kwargs["marian_path"]}/marian-server --port 8080 -c {path} {device_args} '
            subprocess.Popen(f"{command}", shell=True)

        
    def translate(self, srcs, n_best=1):
        #open connection
        ws = create_connection("ws://localhost:8080/translate")
        batch = ""
        translations = []
        for src in srcs:
            src = src.strip() + "\n"
            batch += src.decode('utf-8') if sys.version_info < (3, 0) else src
                # translate the batch
        ws.send(batch)
        result = ws.recv()
        translations.extend(result.split("\n"))
        ws.close()
        return translations

    def translate_training_servers(self, srcs, model_path, marian_path, gpu: str = None):
        with tempfile.NamedTemporaryFile('w+') as to_translate_file,\
             tempfile.NamedTemporaryFile('w+') as translated_file:
            for src in srcs:
                to_translate_file.write(src.strip() + "\n")
            if gpu:
                apend_args = f"--devices {gpu} "
            else:
                apend_args = f"--cpu-threads 6 "
            
            os.system(f' cat {to_translate_file.name} | {marian_path}/marian-decoder'
                    + f' -c {model_path} {apend_args} --seed 1111 > {translated_file.name}')
                   
            results = list(translated_file)        
        return results

    def online_train(self, tus: List[Tuple[str, str]], num_steps: int = 1):
        raise Exception("Online learning not activated for this model.")
