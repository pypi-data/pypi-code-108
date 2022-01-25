'''
All the ML Solutions are written here
'''
import pandas as pd
from sklearn import linear_model
from sklearn import ensemble
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import datasets
import numpy as np
from tensorflow.keras import datasets as tensordatasets
from tensorflow.keras import layers, models
import cv2

class SpamMessageDetector():
    def __init__(self):
        self.training_data = pd.read_csv('https://raw.githubusercontent.com/CoderKid12344/Spam-Message-Detector-Machine-Learning/main/Train.csv')
        self.Model = linear_model.LogisticRegression(max_iter=5000000000)
        self.X_train = list(self.training_data['msg'].values)
        self.Y_train = self.training_data['value'].values
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(self.X_train)
        self.X_train = self.vectorizer.transform(self.X_train)
    
    def train(self):
        self.Model.fit(self.X_train, self.Y_train)
    
    def detect_spam(self, msg):
        '''
        Detects if the message is spam or not
        returns True if its spam
        or returns False if its not spam
        '''
        X_test = self.vectorizer.transform([str(msg)])
        Y_Pred = self.Model.predict(X_test)
        if Y_Pred[0] == 'spam':
            return True
        elif Y_Pred[0] == 'ham':
            return False
        else:
            return None

class HousePricePrediction():
    def __init__(self):
        self.training_data = pd.read_csv('https://raw.githubusercontent.com/CoderKid12344/House-Price-Prediction/main/House%20Pricing.csv')
        self.training_data.dropna(axis=0)
        self.Model = linear_model.LinearRegression()
        self.Data_Features = ['Rooms', 'Bathroom', 'Landsize', 'Lattitude', 'Longtitude']
        self.X_train = self.training_data[self.Data_Features].values
        self.Y_train = self.training_data['Price'].values
    
    def train(self):
        '''
        Trains the House Price Prediction Model
        '''
        self.Model.fit(self.X_train, self.Y_train)

    def get_price(self, rooms, bathrooms, landsize, lattidute, longtitude):
        X_test = [rooms, bathrooms, landsize, lattidute, longtitude]
        X_test = np.array(X_test)
        X_test = X_test.reshape(1, -1)
        Y_Pred = self.Model.predict(X_test)
        return Y_Pred[0]

class WineQualityPrediction():
    def __init__(self):
        self.dataset = datasets.load_wine()
        self.wine_X = self.dataset.data[:, np.newaxis, 2]
        self.X_train = self.wine_X[:-60]
        self.Y_train = self.dataset.target[:-60]
        self.Model = ensemble.RandomForestClassifier()
    
    def train(self):
        self.Model.fit(self.X_train, self.Y_train)
    
    def get_wine_quality(self, alcohol):
        X_test = [alcohol]
        X_test = np.array(X_test)
        X_test = X_test.reshape(1, -1)
        Y_Pred = self.Model.predict(X_test)
        return Y_Pred[0]

class IrisVirginicaPrediction():
    def __init__(self):
        self.dataset = datasets.load_iris()
        self.X_train = self.dataset["data"][:, 3:]
        self.Y_train = (self.dataset["target"] == 2).astype(np.int)
        self.Model = linear_model.LogisticRegression(max_iter=5000000000)

    def train(self):
        self.Model.fit(self.X_train, self.Y_train)
    
    def detect_iris_virginica(self, petal_width_in_cm):
        X_test = [petal_width_in_cm]
        X_test = np.array(X_test)
        X_test = X_test.reshape(1, -1)
        Y_Pred = self.Model.predict(X_test)

        if Y_Pred[0] == 0:
            return False
        elif Y_Pred[0] == 1:
            return True
        else:
            return None

class ImageClassification():
    def __init__(self):
        (training_images, self.training_labels), (_, __) = tensordatasets.cifar10.load_data()
        self.training_images = training_images / 255
        self.class_names = ['Plane', 'Car', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']
        self.training_images = self.training_images[:20000]
        self.training_labels = self.training_labels[:20000]
    
    def train(self):
        self.Model = models.Sequential()
        self.Model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
        self.Model.add(layers.MaxPooling2D((2, 2)))
        self.Model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.Model.add(layers.MaxPooling2D((2, 2)))
        self.Model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.Model.add(layers.Flatten())
        self.Model.add(layers.Dense(64, activation='relu'))
        self.Model.add(layers.Dense(10, activation='softmax'))
        self.Model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self.Model.fit(self.training_images, self.training_labels, epochs=10)

    def save_model(self, model_name):
        self.Model.save(f"{model_name}.model")
    
    def load_model(self, model_name):
        self.Model = models.load_model(f"{model_name}.model")

    def recognize_image(self, image_path):
        '''
        Recognizes The Image,
        First Of All, Convert your image into 32*32 px on https://www.privatedaddy.com/resize-to-32x32
        Then, Put the 32*32 image file path in the image_path argument
        '''
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        Y_Pred = self.Model.predict(np.array([img])/255)
        index = np.argmax(Y_Pred)
        name = self.class_names[index]
        return name

class SurvivalPrediction():
    def __init__(self):
        self.training_data = pd.read_csv('https://raw.githubusercontent.com/CoderKid12344/ml-solutions-python-module-resources/main/train.csv').dropna(axis=0).dropna(axis=1)
        self.Data_Features = ['Age', 'Fare']
        self.X = self.training_data[self.Data_Features]
        self.Y = self.training_data["Sex"]
        self.Model = linear_model.LogisticRegression(max_iter=500000000000)

    def train(self):
        self.Model.fit(self.X, self.Y)

    def get_result(self, fare, age):
        X_test = [fare, age]
        X_test = np.array(X_test)
        X_test = X_test.reshape(1, -1)
        Y_Pred = self.Model.predict(X_test)
        return Y_Pred