import numpy as np
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
        self.model= load_model('SA_Model_Final_v8')

        # Initialize Tokenizer
        with open('tokenizer.pickle', 'rb') as handle:
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
        