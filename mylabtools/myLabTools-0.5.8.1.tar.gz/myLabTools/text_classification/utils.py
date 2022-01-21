import json
import os


class TextClassificationConfigBase:
    def __init__(self):
        self.required_field = [
            "model_checkpoint",
            "sentence1_key",
            "sentence2_key",
            "json_files",
            "train_args",
            "num_labels"
            ]
        
        self.template = {
            "model_checkpoint":"./bert_model",
            "sentence1_key":"text",
            "sentence2_key":"",
            "json_files":{
                            "train":"./json_data/task_1/v1/dev.json",
                            "valid":"./json_data/task_1/v1/train.json",
                            "test":"./json_data/task_1/v1/test.json"
                        },
            "max_length" : 512,
            "num_labels":2,
            "train_args" :{
                "output_dir":"saved_model/task_1/bert_attact",
                "evaluation_strategy" : "steps",
                "eval_steps" : 200,
                "logging_steps" : 10,
                "learning_rate":2e-5,
                "per_device_train_batch_size":8,
                "per_device_eval_batch_size":8,
                "num_train_epochs":10,
                "warmup_ratio" : 0.05,
                "save_total_limit":3,
                "load_best_model_at_end":True,
                "metric_for_best_model":"eval_loss",
                "report_to":["wandb"],
                "run_name" : "explitcit_prop_task1"
            }
        }
    def load_from_config_file(self,config_path):
        missing_fields = []
        
        params = json.load(open(config_path,"r",encoding="utf-8"))
        for k in self.required_field:
            if k not in params.keys():
                missing_fields.append(k)
        if len(missing_fields) > 0:
            print(" ".join(missing_fields), "is required")
        return params


    def gen_config_template(self,config_path):
        if os.path.exists(config_path):
            print(config_path,"exists!!,please change file path")
            return False
        else:
            json.dump(self.template,
                        open(config_path,"w+",encoding = "utf-8"),
                        indent=4,
                        ensure_ascii=False
                        )
            return True
