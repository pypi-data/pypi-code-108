import os
import json
from autoclass import autoclass
from pangeamt_tea.project.workflow.stage.init_stage import InitStage
from pangeamt_tea.project.workflow.stage.clean_stage import CleanStage
from pangeamt_tea.project.workflow.stage.prepare_stage import PrepareStage
from pangeamt_tea.project.workflow.stage.train_stage import TrainStage
from pangeamt_tea.project.workflow.stage.eval_stage import EvalStage
from pangeamt_tea.project.workflow.stage.publish_stage import PublishStage
from pangeamt_tea.project.workflow.stage.stage_factory import StageFactory


@autoclass
class Config:
    STAGES = [
        InitStage.NAME,
        CleanStage.NAME,
        PrepareStage.NAME,
        TrainStage.NAME,
        EvalStage.NAME,
        PublishStage.NAME,
    ]

    def __init__(
        self, workflow_dir, init, clean, prepare, train, eval, publish
    ):
        pass

    def get_runable_stage(self):
        i = 0
        for i, stage in enumerate(Config.STAGES):
            info = getattr(self, stage)
            if info is None:
                break
            if stage != "train" and info["end"] is None:
                return None
        return Config.STAGES[i]

    @staticmethod
    def new(workflow_dir):
        config = Config(workflow_dir, None, None, None, None, None, None)
        config.save()
        return config

    @staticmethod
    def load(workflow_dir):
        config_file = Config.get_file(workflow_dir)
        with open(config_file, "r") as f:
            data = json.load(f)
        return Config(
            workflow_dir,
            data["init"],
            data["clean"],
            data["prepare"],
            data["train"],
            data["eval"],
            data["publish"],
        )

    def set_stage(self, stage, value):
        setattr(self, stage, value)

    @staticmethod
    def get_file(worflow_dir):
        return os.path.join(worflow_dir, "config.json")

    def save(self):
        config_file = Config.get_file(self.workflow_dir)
        data = {}
        data["init"] = self.init
        data["clean"] = self.clean
        data["prepare"] = self.prepare
        data["train"] = self.train
        data["eval"] = self.eval
        data["publish"] = self.publish
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            f.write("\n")  # Add newline cause Py JSON does not

    def reset_stage(
        self, target_stage: str, project_dir: str, workflow
    ) -> None:
        found = False
        for stage_name in self.STAGES:
            if found:
                if getattr(self, stage_name) is not None:
                    stage = StageFactory.new(stage_name, workflow)
                    stage.reset(project_dir)
                    setattr(self, stage_name, None)
            else:
                if stage_name == target_stage:
                    if getattr(self, stage_name) is not None:
                        stage = StageFactory.new(stage_name, workflow)
                        stage.reset(project_dir)
                        setattr(self, stage_name, None)
                    found = True
        self.save()

    def show(self):
        config_file = Config.get_file(self.workflow_dir)
        with open(config_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        total_lines = 0
        for resource in data["init"]["report"]["resources"]:
            total_lines += resource["num_trans_units"]

        print(
            f"\n\nWorkflow initialized on {data['init']['start']} and found {total_lines} "
            "segments.\n"
        )

        if data["clean"]:
            print(
                f"Data cleanning started on {data['clean']['start']} and ended on "
                f"{data['clean']['end']} dropping {data['clean']['report']['dropped']} "
                f"and leaving {data['clean']['report']['useful']} useful lines.\n"
            )
        else:
            print(
                "Cleanning is the next stage to run; "
                "(tea workflow clean -n <number of workers> -d <flag to debug>)\n\n"
            )
            return

        if data["prepare"]:
            print(
                f"Data preparing started on {data['prepare']['start']} and ended on "
                f"{data['prepare']['end']}.\n"
            )
        else:
            print(
                "Preparing is the next stage to run; "
                "(tea workflow prepare -n <number of workers> -s <seed for shuffle>)\n\n"
            )
            return

        if data["train"]:
            print(
                f"Model training started on {data['train']['start']} and ended on "
                f"{data['train']['end']}.\n"
            )
        else:
            print(
                "Training is the next stage to run; "
                "(tea workflow train <--gpu (optional)>)\n\n"
            )
            return

        if data["eval"]:
            print(
                f"Model evaluation started on {data['eval']['start']} and "
                f"ended on {data['eval']['end']} with a score of "
                f"{data['eval']['report']['Score']}.\n"
            )
        else:
            print(
                "Evaluation is the next stage to run; "
                "(tea workflow eval <--gpu (optional)><--step (optional)>)\n\n"
            )
            return

        if data["publish"]:
            print(
                f"Model publishing started on {data['publish']['start']} and ended on "
                f"{data['publish']['end']}.\n\n"
            )
        else:
            print(
                "Publishing is the next stage to run; (tea workflow publish)\n\n"
            )
            return
