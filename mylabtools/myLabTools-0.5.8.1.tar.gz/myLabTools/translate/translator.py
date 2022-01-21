from transformers import MarianTokenizer, MarianMTModel
import os
from typing import List
import torch

class Translator():
    def __init__(self, models_dir):
        self.models = {}
        self.models_dir = models_dir

    def get_supported_langs(self):
        routes = [x.split('-')[-2:] for x in os.listdir(self.models_dir)]
        return routes

    def load_model(self, route):
        model = f'opus-mt-{route}'
        path = os.path.join(self.models_dir,model)
        try:
            print(path)
            model = MarianMTModel.from_pretrained(path)
            tok = MarianTokenizer.from_pretrained(path)
        except Exception as e:
            print(e)
            return 0,f"Make sure you have downloaded model for {route} translation"
        self.models[route] = (model,tok)
        return 1,f"Successfully loaded model for {route} transation"

    def translate(self, source, target, text):
        route = f'{source}-{target}'
        if not self.models.get(route):
            success_code, message = self.load_model(route)
            if not success_code:
                return message
        batch = self.models[route][1].prepare_seq2seq_batch(src_texts=[text])
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        batch = {
            "input_ids":torch.tensor(input_ids, dtype=torch.long),
            "attention_mask":torch.tensor(attention_mask, dtype=torch.long),
        }
        gen = self.models[route][0].generate(**batch)
        words: List[str] = self.models[route][1].batch_decode(gen, skip_special_tokens=True) 
        return words

if __name__ == "__main__":
    translator = Translator("/media/mayq/文档/PycharmProjects/en_zh_trans/saved_model")
    print(translator.translate("en","zh","RIP, F-22 and F-35: Are Stealth Weapons Going To Soon Be Obsolete? DARPA has called for “reduced reliance on increasingly complex, monolithic platforms.”"))

    translator = Translator("/media/mayq/文档/PycharmProjects/en_zh_trans/data")
    print(translator.translate("en","zh","The predatory resource exploitation featured the traditional economical mode, which damaged very seriously the environment on which the human-kind relies to maintain existence. Along with the thought of sustainable development coming into consensus in the world, many nations begin to set up a new mode of circular economy that the resource exploitation shall be reduced with friendly environment kept on. As a nation of which the economy develops at high speed, China's environment has been severely wrecked. So, it is an inevitable and urgent choice for China to set up and develop a sound mode of circular economy for its sustainable development. In this respect, perfecting the finance-taxation policy is necessary to support and develop circular economy. Started from the concept of circular economy, some policy problems are discussed, such as purchasing expenditures, financial subsidy, tax revenue and credits. In view of the international practice, some measures are proposed to take to implement the policy."))