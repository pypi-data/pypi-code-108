import numpy as np
import pkg_resources
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

class IRIS():
    def __init__(self):
        # Initialise emotion classes and index
        self.classes = ['joy', 'fear', 'anger', 'sadness', 'love', 'surprise']
        self.class_to_index = dict((c,i) for i, c in enumerate(self.classes))
        self.index_to_class = dict((v, k) for k, v in self.class_to_index.items())

        # Initialize SA-Model-Final-v8
        self.model_path = pkg_resources.resource_filename('iris_emotion', 'SA_Model_Final_v8/')
        self.model= load_model(self.model_path)

        # Initialize Tokenizer
        self.tk_path = pkg_resources.resource_filename('iris_emotion', 'tokenizer.pickle')
        with open(self.tk_path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    def get_sequences(self, msg):
        # Preprocess message
        maxlen = 50
        sequences = self.tokenizer.texts_to_sequences([msg])
        padded = pad_sequences(sequences, truncating='post' , padding='post', maxlen = maxlen)

        # Return tokenized message
        return padded

    def get_emotion(self, msg):
        # Tokenize message
        msg_seq = self.get_sequences(msg)

        # Predict emotion
        p = self.model.predict(msg_seq)[0]
        pred_class = self.index_to_class[np.argmax(p).astype('uint8')]

        # Return predicted emotion
        return pred_class
        