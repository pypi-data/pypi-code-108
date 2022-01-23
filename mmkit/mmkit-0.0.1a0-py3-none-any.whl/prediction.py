import pandas as pd
import torch
import torch.nn as nn
from mmk.models.tabular_dataset import TabularDataset,FeedForwardNN
from torch.utils.data import DataLoader
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import random_split


# Using only a subset of the variables.

class MultimodalPredictionModel:
    def __init__(self,data_path, all_features,categorical_features,output_feature,output_error):
        self.all_features=all_features
        self.categorical_features=categorical_features
        self.output_feature=output_feature
        self.output_error=output_error
        self.n_cont=n_cont=len(all_features)-len(categorical_features)-1
        print("------Start Configure-----------")
        print(self.all_features)
        print(self.categorical_features)
        print(self.output_feature)
        print(self.output_error)
        print("-------End Configure-----------")
        self.data = pd.read_csv(data_path, encoding='gbk', usecols=all_features).dropna()
        self.last_acc=0

    def get_last_accuracy(self):
        return self.last_acc

    # prepare the dataset
    def prepare_data(self,dataset):
        # load the dataset
        # dataset = CSVDataset(path)
        # calculate split
        train, test = self.get_splits(dataset)
        # prepare data loaders
        train_dl = DataLoader(train, batch_size=64, shuffle=True)
        test_dl = DataLoader(test, batch_size=64, shuffle=False)
        return train_dl, test_dl

    # get indexes for train and test rows
    def get_splits(self,dataset, n_test=0.33):
        # determine sizes
        test_size = round(n_test * len(dataset))
        train_size = len(dataset) - test_size
        # calculate the split
        return random_split(dataset, [train_size, test_size])

    def is_acceptable(self,a, b):
        if abs(a - b) <= self.output_error:
            return True
        else:
            return False

    def train(self):
        # categorical variables
        label_encoders = {}
        for cat_col in self.categorical_features:
            label_encoders[cat_col] = LabelEncoder()
            self.data[cat_col] = label_encoders[cat_col].fit_transform(self.data[cat_col])

        # load dataset
        dataset = TabularDataset(data=self.data, cat_cols=self.categorical_features,
                                 output_col=self.output_feature)

        train_dl, test_dl = self.prepare_data(dataset)

        # model
        batchsize = 64
        # dataloader = DataLoader(dataset, batchsize, shuffle=True, num_workers=1)

        cat_dims = [int(self.data[col].nunique()) for col in self.categorical_features]

        emb_dims = [(x, min(50, (x + 1) // 2)) for x in cat_dims]

        # print(cat_dims)
        # print(emb_dims)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # print(device)

        model = FeedForwardNN(emb_dims, no_of_cont=self.n_cont, lin_layer_sizes=[50, 100],
                              output_size=1, emb_dropout=0.04,
                              lin_layer_dropouts=[0.001, 0.01]).to(device)

        # start training
        no_of_epochs = 10
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(no_of_epochs):
            running_train_loss = 0.0
            running_train_accuracy = 0.0

            total = 0
            correct = 0
            for y, cont_x, cat_x in train_dl:
                cat_x = cat_x.to(device)
                # print(cat_x)
                cont_x = cont_x.to(device)

                y = y.to(device)
                # Forward Pass
                preds = model(cont_x, cat_x)
                loss = criterion(preds, y)

                # Backward Pass and Optimization
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                running_train_loss += loss.item()

                n_correct = 0
                y = y.tolist()
                preds = preds.tolist()
                for idx, y_pred in enumerate(preds):
                    # print(y)
                    if self.is_acceptable(preds[idx][0], y[idx][0]):
                        n_correct += 1
                acc = n_correct * 1.0 / len(y)
                running_train_accuracy += acc

            avg_acc = running_train_accuracy / len(train_dl)
            avg_loss = running_train_loss / len(train_dl)

            # print(f"Epoch: {epoch} | Train Loss: {avg_loss} | Accuracy: {avg_acc}")
            running_val_loss = 0.0
            running_val_accuracy = 0
            total = 0
            correct = 0
            for y, cont_x, cat_x in test_dl:
                cat_x = cat_x.to(device)
                # print(cat_x)
                cont_x = cont_x.to(device)

                y = y.to(device)
                # Forward Pass
                preds = model(cont_x, cat_x)
                loss = criterion(preds, y)

                running_val_loss += loss.item()

                n_correct = 0
                y = y.tolist()
                preds = preds.tolist()
                for idx, y_pred in enumerate(preds):
                    # print(y)
                    if self.is_acceptable(preds[idx][0], y[idx][0]):
                        n_correct += 1

                acc = n_correct * 1.0 / len(y)
                running_val_accuracy += acc

            avg_acc = running_val_accuracy / len(test_dl)
            avg_loss = running_val_loss / len(test_dl)
            self.last_acc = avg_acc
            # print(f"Epoch: {epoch} | Validation Loss: {avg_loss} | Accuracy: {avg_acc}")
            # print()
        print("Final Accuracy: ", self.last_acc)
        return self.last_acc




