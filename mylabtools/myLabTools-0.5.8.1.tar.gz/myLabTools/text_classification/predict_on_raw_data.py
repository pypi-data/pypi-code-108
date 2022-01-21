from transformers import AutoTokenizer
import json
from tqdm import tqdm
from sklearn.metrics import classification_report
from .bert_text_classify_pipeline import TextClassificationPipeline
from .bert_model import BertCNNForSequenceClassification
import copy



class PredictBase():
    def __init__(self,model_checkpoint,device = 0):
        model,tokenizer = self.load_checkpoint(model_checkpoint)

        self.tc_pipline = TextClassificationPipeline(
            model = model,
            tokenizer = tokenizer,
            device = device,
            return_all_scores = True
            )
    def load_checkpoint(self,model_checkpoint):
        model = BertCNNForSequenceClassification.from_pretrained( 
            model_checkpoint
            )
        tokenizer = AutoTokenizer.from_pretrained(
            model_checkpoint, 
            use_fast=True
            )
        return model,tokenizer
    def pred_jsonline_file(self,
        data_path = "./json_data/task_1/v1/test.json",
        text_field = "text",
        write_to_json = True,
        output_json_path = "./prediction.json"
        ):
        res = []
        with open(data_path,"r",encoding="utf-8") as f:
            for line in tqdm(f):
                data = json.loads(line)
                temp = copy.deepcopy(data)
                text = temp[text_field]
                tc_pred_res = self.tc_pipline(text)
                temp["prediction"] = tc_pred_res
                res.append(temp)
        if write_to_json:
            json.dump(res,open(output_json_path,"w+",encoding = "utf-8"),indent=4,ensure_ascii=False)
        return res
    def model_report(self,
        y_true, 
        y_pred,
        digits = 4,
        print_classification_report = True,
        return_classification_report_dict  =True
        ):
        if print_classification_report:
            print(classification_report(
                y_true, 
                y_pred,
                digits = digits)
            )
        if return_classification_report_dict:
            return classification_report(
                y_true, 
                y_pred,
                digits = digits,
                output_dict = True
                )
        else:
            return None

from transformers import AutoTokenizer,BertPreTrainedModel
import torch
import json
import numpy as np

class PredictorForPairTextClf():
    def __init__(self,
        predictor_config = {
            "model_checkpoint":"",
            "device":"cuda:0",
            "max_length":512
        },
        id2label = {
                    0:"entailment",
                    1:"contradiction",
                    2:"neutral"
                },
        ClfModelClass:BertPreTrainedModel = None
        ) -> None:
        self.cuda_field = ['input_ids', 'token_type_ids', 'attention_mask']
        self.device = predictor_config["device"] 
        self.config = predictor_config

        self.max_length = predictor_config["max_length"]
        self.id2label = id2label

        self.tokenizer = AutoTokenizer.from_pretrained(predictor_config["model_checkpoint"], use_fast=True)

        self.model = self.load_model(ClfModelClass,predictor_config["model_checkpoint"])

        self.model.to(predictor_config["device"])
        
    

    def load_model(self,ClfModelClass:BertPreTrainedModel,model_checkpoint):
        model = ClfModelClass.from_pretrained(
            model_checkpoint, 
            num_labels=len(self.id2label))
        return model

    # 将文本转换为tokenid 
    def process_pair_text(self,sent_1,sent_2):
        encoded_data = self.tokenizer(
            sent_1,sent_2, 
            padding="max_length", 
            max_length=self.max_length,
            truncation=True,
            return_tensors = "pt"
            )
        encoded_data["labels"] = None
        for field in self.cuda_field:
            encoded_data[field] = encoded_data[field].to(self.device)
        return encoded_data
    
    # 文本分类 传入一个文本
    def predict(self,sent_1,sent_2):
        inputs = self.process_pair_text(sent_1,sent_2)
        with torch.no_grad() :
            outputs = self.model(**inputs)
        
        if "cuda" in self.device:
            logits = outputs["logits"].cpu().numpy()[0]
            # if self.config["has_text_vector"] 
        else:
            logits = outputs["logits"].numpy()[0]

        prediction = np.argmax(logits)
        result = {
            "logits":dict(zip(self.id2label.values(), logits.tolist())), # 各个标签对应的概率
            "prediction":{"label_id":int(prediction) ,"label":self.id2label[int(prediction)]}# 预测的结果
        }
        return result



class PredictorForSingleTextClf():
    def __init__(self,
        predictor_config = {
            "model_checkpoint":"",
            "device":"cuda:0",
            "max_length":512
        },
        id2label = {
                    0:"pos",
                    1:"neg"
                },
        ClfModelClass:BertPreTrainedModel = None
        ) -> None:
        self.cuda_field = ['input_ids', 'token_type_ids', 'attention_mask']
        self.device = predictor_config["device"] 
        self.max_length = predictor_config["max_length"]
        self.config = predictor_config
        self.id2label = id2label
        
        self.tokenizer = AutoTokenizer.from_pretrained(predictor_config["model_checkpoint"], use_fast=True)
        self.model = self.load_model(ClfModelClass,predictor_config["model_checkpoint"])

        self.model.to(predictor_config["device"])
        
    

    def load_model(self,ClfModelClass:BertPreTrainedModel,model_checkpoint):
        model = ClfModelClass.from_pretrained(
            model_checkpoint, 
            num_labels=len(self.id2label))
        return model

    # 将文本转换为tokenid 
    def process_text(self,text):
        encoded_data = self.tokenizer(
            [text],
            padding="max_length", 
            max_length=self.max_length,
            truncation=True,
            return_tensors = "pt")
        
        encoded_data["labels"] = None
        for field in self.cuda_field:
            encoded_data[field] = encoded_data[field].to(self.device)
        return encoded_data
    
    # 文本分类 传入一个文本
    def predict(self,text):
        inputs = self.process_text(text)
        with torch.no_grad() :
            outputs = self.model(**inputs)
        
        if "cuda" in self.device:
            logits = outputs["logits"].cpu().numpy()[0]
            # if self.config["has_text_vector"] 
        else:
            logits = outputs["logits"].numpy()[0]

        prediction = np.argmax(logits)
        result = {
            "logits":logits.tolist(), # 各个标签对应的概率
            "prediction":{"label_id":int(prediction) ,"label":self.id2label[int(prediction)]} # 预测的结果
        }
        return result