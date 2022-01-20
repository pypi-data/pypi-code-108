import os
from pangeamt_tea.project.workflow.stage.base_stage import BaseStage
from pangeamt_tea.project.workflow.stage.stage_factory import StageFactory
from pangeamt_nlp.translation_model.translation_model_factory import (
    TranslationModelFactory,
)


class TrainStage(BaseStage):
    NAME = "train"
    DIR = "03_trained"

    def __init__(self, workflow):
        super().__init__(workflow, self.NAME)

    async def run(self, gpu: int = None, continue_from: str = None):
        project = self.workflow.project
        config = project.config
        project_dir = config.project_dir
        workflow_dir = self.workflow.get_dir(project_dir)
        model_dir = os.path.join(workflow_dir, TrainStage.DIR)
        try:
            os.mkdir(model_dir)
        except Exception:
            pass

        name = config.translation_model["name"]
        translation_model = TranslationModelFactory.get_class(name)
        if continue_from is not None:
            if name == "onmt":
                args = (
                    config.translation_model["args"]
                    + " -train_from "
                    + os.path.join(model_dir, continue_from)
                )
                args = args.split(" ")
            elif name == "marianmt":
                args = config.translation_model["args"].split(" ")
            else:
                raise Exception("Continue not implemented for " + name)
        else:
            args = config.translation_model["args"].split(" ")

        prepare_stage = StageFactory.new("prepare", self.workflow)
        prepared_dir = os.path.join(workflow_dir, prepare_stage.DIR)

        if gpu is not None:
            gpu = str(gpu)

        if name == "onmt":
            data_dir = os.path.join(prepared_dir, "05_batched")
            translation_model.train(data_dir, model_dir, *args, gpu=gpu)
        elif name == "marianmt":
            data_dir = os.path.join(prepared_dir, "04_bpe")
            marian_path = config.translation_model["marian_path"]
            translation_model.extract_vocab(data_dir, model_dir, marian_path)
            translation_model.train(data_dir, model_dir, marian_path, *args, gpu=gpu)

        return {}
