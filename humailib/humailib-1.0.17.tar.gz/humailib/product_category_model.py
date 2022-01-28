import pandas as pd
import numpy as np
from scipy import stats
import datetime
import os
import math
import pickle
import matplotlib.pyplot as plt 

import sklearn.metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.utils import resample
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score

class HumaiProdCategoryFeatureGen:

    def __init__(self):
        self.vectorizer = None
        return
    
    def init(self, df_prod, item_name='item_name', category='category', verbose=True):

        # Generate Term Frequency-Inverse Document Frequency vectors from all item names
        self.vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', 
                             ngram_range=(1, 2))
        self.vectorizer = self.vectorizer.fit(df_prod[item_name].tolist())

    def generate(self, item_names):
        if self.vectorizer is None:
            return None

        features = self.vectorizer.transform(item_names)
        print("Words in vocabulary: {0}".format(len(self.vectorizer.vocabulary_)))

        return features

    def save(self, filename):
        pickle.dump( self.vectorizer, open(filename, "wb") )
        return
    
    def load(self, filename):
        self.vectorizer = pickle.load(open(filename, "rb"))
        return


class HumaiProdCategoryModel:

    def __init__(self):
        self.best_model = None
        self.clf = None
        return
    
    def learn(self, df_train, feature_gen, 
              item_name = 'item_name', category = 'category', 
              k_folds=5, 
              balancing=True, balance_thresholds = [5, 300], 
              verbose=True,
              show_plots=False):

        dfg_train = df_train.groupby(category)

        # Balance the data by undersampling classes that exceed a certain size,
        # and oversampling classes that are not big enough.
        item_names = []
        item_categories = []
        if balancing:
            for _, df_group in dfg_train:
                #print(cat)
                if len(df_group) > balance_thresholds[1]:
                    names, categories = resample(df_group[item_name].tolist(), df_group[category].tolist(), 
                                                replace=False, n_samples=balance_thresholds[1], random_state=0)
                elif len(df_group) < balance_thresholds[0]:
                    names, categories = resample(df_group[item_name].tolist(), df_group[category].tolist(), 
                                                replace=True, n_samples=balance_thresholds[0], random_state=0)

                else:
                    names = df_group[item_name].tolist()
                    categories = df_group[category].tolist()

                item_names.extend(names)
                item_categories.extend(categories)
        else:
            item_names = df_train[item_name]
            item_categories = df_train[category]

        if show_plots:
            # Plot balanced classes
            df_balanced = pd.DataFrame()
            df_balanced[item_name] = item_names
            df_balanced[category] = item_categories
            fig = plt.figure(figsize=(20,6))
            df_balanced.groupby(category)[item_name].count().plot.bar(ylim=0)
            plt.show()

        # Create training data
        features = feature_gen.generate(item_names)
        labels = item_categories

        if verbose:
            print("Features shape {0}".format(features.shape))

        # Evaluate different models
        models = {
            'rf':RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
            'svc':LinearSVC(),
            'nb':MultinomialNB(),
            'log':LogisticRegression(random_state=0),
        }

        folds = k_folds
        cv_df = pd.DataFrame(index=range(folds * len(models)))
        entries = []
        for name, model in models.items():
            model_name = name#model.__class__.__name__
            accuracies = cross_val_score(model, features, labels, scoring='accuracy', cv=folds)
            for fold_idx, accuracy in enumerate(accuracies):
                entries.append((model_name, fold_idx, accuracy))

        cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])

        accs = cv_df.groupby('model_name')['accuracy'].mean()
        self.best_model = accs.idxmax()

        weights = sklearn.utils.class_weight.compute_sample_weight(class_weight='balanced', y=labels, indices=None)
        self.clf = models[self.best_model].fit(features, labels, sample_weight=weights)

        if verbose:
            print("Best model: {0} (accuracy={1})".format(self.best_model, accs.max()))

        return self.best_model, cv_df

    def predict(self, features):
        if self.clf is None:
            return None

        pred = self.clf.predict(features)

        return pred

    def save(self, filename):
        pickle.dump( [self.best_model, self.clf], open(filename, "wb") )
        return
    
    def load(self, filename):
        self.best_model, self.clf = pickle.load(open(filename, "rb"))
        return