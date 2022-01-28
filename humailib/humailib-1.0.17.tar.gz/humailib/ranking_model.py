import pandas as pd
import numpy as np

from pathlib import Path

# Classifier models
import sklearn
import joblib

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score

from sklearn.pipeline import FeatureUnion, Pipeline

from humailib.cloud_tools import GoogleCloudStorage

class HumaiRankingModel:

    def __init__(self):

        self.models = {
            'rf':RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
            #'svc':SVC(),  -> slow to train
            #'sgd':SGDClassifier(),
            'mlp':MLPClassifier(),
            #'nb':MultinomialNB(),
            #'log':LogisticRegression(solver='lbfgs', random_state=0),
        }

        self.clf = None

        return

    def select_best_model(self, df, covariate_columns, observed_column = 'observed', scoring='accuracy', folds=5):

        cv_df = pd.DataFrame(index=range(folds * len(self.models)))
        entries = []
        for name, model in self.models.items():
            print("Evaluating {}...".format(name))
            accuracies = cross_val_score(model, df[covariate_columns], df[observed_column], scoring=scoring, cv=folds)
            for fold_idx, accuracy in enumerate(accuracies):
                entries.append((name, fold_idx, accuracy))

        cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])

        accs = cv_df.groupby('model_name')['accuracy'].mean()
        print("Best model: {} (mean accuracy: {:.2f})".format(accs.idxmax(), accs.max()))

        return accs.idxmax(), cv_df
    

    def train_model(self, df, covariate_columns, model, observed_column = 'observed'):
        
        self.clf = self.models[model].fit(df[covariate_columns], df[observed_column])
        
        return self.clf
    

    def predict(self, df, covariate_columns, pred_threshold = 0.5, ranking_output = 'pred_ranking', pred_output = 'pred_observed'):

        if self.clf is None:
            return

        df.loc[:,ranking_output] = self.clf.predict_proba(df[covariate_columns])[:,1]
        df.loc[:,pred_output] = df[ranking_output].apply(lambda x: 1 if x > pred_threshold else 0)
        

    def predict_and_rank(self, df, covariate_columns, pred_threshold = 0.5, ranking_output = 'pred_ranking', pred_output = 'pred_observed'):

        if self.clf is None:
            return

        self.predict(df, covariate_columns, pred_threshold=pred_threshold, ranking_output=ranking_output, pred_output=pred_output)
        df.sort_values(by=[ranking_output], ascending=False, inplace=True)
        

    def save(self, filename, gcs=None, cache_dir='./cache'):

        if self.clf is None:
            return

        # Create the model as a single-step pipeline
        pipeline = Pipeline([
            ('classifier', self.clf)
        ])

        if 'gs://' in filename:
            if gcs is None:
                gcs = GoogleCloudStorage()
            cache_file = cache_dir + '/' + filename.split('/')[-1]
            joblib.dump(pipeline, cache_file)
            gcs.upload_file(cache_file, filename)
        else:
            joblib.dump(pipeline, filename)
            

    def load(self, filename, gcs=None, cache_dir='./cache'):

        if 'gs://' in filename:
            if gcs is None:
                gcs = GoogleCloudStorage()
            cache_file = Path(cache_dir + '/' + filename.split('/')[-1])
            gcs.download_file(filename, cache_file)
            pipeline = joblib.load(cache_file)
        else:
            pipeline = joblib.load(filename)
    
        self.clf = pipeline.named_steps['classifier']


    def __test__(self):

        hyper_param_opt = False

        if hyper_param_opt:
            #Hyper parameter optimisation
            # Evaluate different models
            models = {
                'rf1':RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
                'rf2':RandomForestClassifier(n_estimators=200, max_depth=2, random_state=0),
                'rf3':RandomForestClassifier(n_estimators=200, max_depth=1, random_state=0),
                'rf4':RandomForestClassifier(n_estimators=200, max_depth=None, random_state=0),
                'rf5':RandomForestClassifier(n_estimators=300, max_depth=None, random_state=0),
                'rf6':RandomForestClassifier(n_estimators=400, max_depth=None, random_state=0),
            }

            folds = 5
            cv_df = pd.DataFrame(index=range(folds * len(models)))
            entries = []
            for name, model in models.items():
                model_name = name#model.__class__.__name__
                accuracies = cross_val_score(model, model_train_feat[covariate_columns], model_labels, scoring='accuracy', cv=folds)
                for fold_idx, accuracy in enumerate(accuracies):
                    entries.append((model_name, fold_idx, accuracy))

            cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])

            accs = cv_df.groupby('model_name')['accuracy'].mean()
            best_model = accs.idxmax()
            print(best_model)
            print(cv_df[cv_df.model_name == best_model])
    

