import pandas as pd

class Sklearn_API:
    def housing(self, download=False):
        from sklearn.datasets import fetch_california_housing
        loaded_dataset = fetch_california_housing(return_X_y=False)
        df = pd.DataFrame(data=loaded_dataset['data'], columns=loaded_dataset['feature_names'])
        df['target'] = loaded_dataset['target']
        if download:
            df.to_csv('boston.csv')
        return df

    def breast_cancer(self, download=False):
        from sklearn.datasets import load_breast_cancer
        loaded_dataset = load_breast_cancer(return_X_y=False)
        df = pd.DataFrame(data=loaded_dataset['data'], columns=loaded_dataset['feature_names'])
        df['target'] = loaded_dataset['target']
        if download:
            df.to_csv('breast_cancer.csv')
        return df

    def diabetes(self, download=False):
        from sklearn.datasets import load_diabetes
        loaded_dataset = load_diabetes(return_X_y=False)
        df = pd.DataFrame(data=loaded_dataset['data'], columns=loaded_dataset['feature_names'])
        df['target'] = loaded_dataset['target']
        if download:
            df.to_csv('diabetes.csv')
        return df

    def digits(self, download=False):
        from sklearn.datasets import load_digits
        loaded_dataset = load_digits(return_X_y=False)
        df = pd.DataFrame(data=loaded_dataset['data'], columns=[ 'X_0' + str(i) if i < 10 else 'X_' + str(i) for i in range(1, 65) ])
        df['target'] = loaded_dataset['target']
        if download:
            df.to_csv('digits.csv')
        return df

    def iris(self, download=False):
        from sklearn.datasets import load_iris
        loaded_dataset = load_iris(return_X_y=False)
        df = pd.DataFrame(data=loaded_dataset['data'], columns=loaded_dataset['feature_names'])
        df['target'] = loaded_dataset['target']
        if download:
            df.to_csv('iris.csv')
        return df

    def wine(self, download=False):
        from sklearn.datasets import load_wine
        loaded_dataset = load_wine(return_X_y=False)
        df = pd.DataFrame(data=loaded_dataset['data'], columns=loaded_dataset['feature_names'])
        df['target'] = loaded_dataset['target']
        if download:
            df.to_csv('wine.csv')
        return df
