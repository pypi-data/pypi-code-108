from simpletransformers.classification import ClassificationModel, ClassificationArgs
import pandas as pd
import logging
import torch

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)

class ChessClassification(object):

    def __init__(self):

        # Optional model configuration
        self.model_args = ClassificationArgs(num_train_epochs=1)
        self.model_args.overwrite_output_dir = True

        self.cuda_available = torch.cuda.is_available()

        # Create a ClassificationModel
        self.model = ClassificationModel(
            'bert',
            'bert-base-cased',
            num_labels=3,
            args=self.model_args,
            use_cuda=self.cuda_available
        )

    def train_and_eval(self, train_json, eval_json):
        train_df = pd.read_json(train_json)
        # Train the model
        self.model.train_model(train_df)

        eval_df = pd.read_json(eval_json)
        # Evaluate the model
        result, model_outputs, wrong_predictions = self.model.eval_model(eval_df)

    def predict_fen(self, fen):
        # Make predictions with the model
        prediction, raw_outputs = self.model.predict([fen])
        # print(prediction, raw_outputs)
        return prediction, raw_outputs

