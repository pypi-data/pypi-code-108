import pandas as pd
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer
from sklearn.feature_extraction import FeatureHasher
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from auger_ml.preprocessors.base import BasePreprocessor
from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas

# Text Datasets:
# 'datasets': [{'path': 'path', 'keys': ['main_key', 'local_key'], 'text_cols': [],'text_metrics': ['separation_score', 'mean_length', 'unique_count']}, {'path': 'path1', 'keys': ['main_key1', 'local_key1']}]
# 'text_metrics': ['separation_score', 'mean_length', 'unique_count']
# Columns to compare
# 'compare_pairs': [{'compare_cols': [{'dataset_idx': 0, 'cols': ['col1']}, {'dataset_idx': 1, 'cols': ['col2']}], 'output_name':'cosine_goals_title', 'params': {}}]

# When no distance will be caclulated
# 'text_cols': ['col1', 'col2']

# Used for generated columns
# 'output_prefix': 'empl_',

# Params: per pair or default
# Text to tokens parameters
# "tokenize": {'max_text_len': 30000, 'tokenizers': ['sent'], 'remove_chars': '○•'}
# Tokens to vector parameters
# see https://github.com/MartinoMensio/spacy-universal-sentence-encoder
# "vectorize": 'en_use_lg'|'hashing'|'en_use_md'|'en_use_cmlm_md'|'en_use_cmlm_lg'
# Calculate distance parameters
#https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.distance_metrics.html#sklearn.metrics.pairwise.distance_metrics
# 'calc_distance': ['none', 'cosine', 'cityblock', 'euclidean', 'haversine', 'l1', 'l2', 'manhattan', 'nan_euclidean'] | 'cosine'
# 'dim_reduction': {'alg_name': 'PCA'|'t-SNE', 'args': {'n_components': 2}}
# For vectorize
#workers_count
#batch_size

class TextPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super().__init__(
            params=params,
            params_keys=['datasets', 'compare_pairs', 'tokenize', 'vectorize', 
                'calc_distance','text_metrics', 'text_cols', 'dim_reduction', 'output_prefix',
                'workers_count', 'batch_size']
        )
        self.params = params
        self.text_metrics = {}

        if self.params.get('text_cols') and self.params.get('calc_distance') and self.params.get('calc_distance') != 'none':
            self.params['compare_pairs'] = []
            for idx, item in enumerate(self.params.get('text_cols')):
                if idx%2 == 0:
                    self.params['compare_pairs'].append(
                        {'compare_cols': [{'dataset_idx': 0, 'cols': [item]}]}
                    )
                else:
                    last_pair = self.params['compare_pairs'][-1]
                    last_pair['compare_cols'].append({'dataset_idx': 0, 'cols': [item]})

        if self.params.get('tokenize') is None:
            self.params['tokenize'] = {'max_text_len': 30000, 'tokenizers': ['sent'], 'remove_chars': '○•'}
            
    def fit(self, df):
        super().fit(df)

    def transform(self, df):
        super().transform(df)

        if not self.params.get('text_cols') and not self.params.get('compare_pairs') and not self.params.get('datasets'):
            return df

        datasets = self._load_datasets(df)
        vector_cols = []
        prefixes = {}
        if self.params.get('vectorize'):
            for idx,dataset in enumerate(datasets):
                text_metrics = self.params.get('text_metrics', [])
                if self.params.get('datasets') and \
                    self.params['datasets'][idx].get('text_metrics') is not None:
                    text_metrics = self.params['datasets'][idx].get('text_metrics')

                cols = self._get_dataset_features(idx, main_key=False)
                self._vectorize(dataset, cols, text_metrics)
                vector_cols.extend(cols)
                for col in cols:
                    prefixes[col] = self.params.get('output_prefix', "")
                    if self.params.get('datasets'):
                        prefixes[col] = self.params['datasets'][idx].get('output_prefix', "")

        df_full = self._prepare_full_dataset(df, datasets)
        if self.params.get('calc_distance') and self.params.get('calc_distance') != 'none':
            field_names, df_full = self._calculate_distance(df_full)
            df_full =  self._make_result_dataset(df, df_full, field_names)
        elif self.params.get('dim_reduction'):
            df_full = self._apply_dim_reduction(df_full, vector_cols, prefixes)
        
        return df_full        

    def _load_datasets(self, df):
        datasets = []
        if self.params.get('datasets'):
            for idx, dataset in enumerate(self.params.get('datasets', [])):
                ds = DataSourceAPIPandas.create_dataframe(data_path=dataset.get('path'), 
                    features=self._get_dataset_features(idx), reset_index=True)
                datasets.append(ds)
        else:
            datasets.append(DataSourceAPIPandas.create_dataframe(data_path=df, reset_index=True))

        return datasets

    def _get_dataset_features(self, dataset_idx, main_key=True):
        if main_key and self.params['datasets'][dataset_idx].get('keys'):
            features = [self.params['datasets'][dataset_idx]['keys'][1]]
        else:
            features = []

        for item in self.params.get('compare_pairs', []):
            for item_cols in item['compare_cols']:
                if item_cols['dataset_idx'] == dataset_idx:
                    features.extend(item_cols['cols'])

        if self.params.get('datasets') and self.params['datasets'][dataset_idx].get('text_cols'):
            features.extend(self.params['datasets'][dataset_idx].get('text_cols'))

        if not self.params.get('compare_pairs') and self.params.get('text_cols'):
            features.extend(self.params.get('text_cols'))

        return list(set(features))
                    
    def _remove_chars(self, text):
        res = text
        if self.params.get('tokenize', {}).get('remove_chars'):
            for c in self.params['tokenize']['remove_chars']:
                res = res.replace(c, '')

        return res
            
    def _tokenize(self, text):
        from nltk import sent_tokenize

        if text is None or pd.isna(text) or text == '':
            return ''
        
        sents = set()
        for sent in sent_tokenize(text):
            new_sent = sent.rstrip().lstrip().replace('\n', ' ')
            new_sent = self._remove_chars(new_sent)
            sents.add(new_sent)
        
        all_sents = ". ".join(list(sents))
        
        max_text_len = self.params.get('tokenize', {}).get('max_text_len')
        if max_text_len and len(all_sents) > max_text_len:
            all_sents = all_sents[0:max_text_len]

        return all_sents

    @staticmethod    
    def install_spacy():
        import site  # pylint: disable=C0415
        from importlib import reload  # pylint: disable=C0415
        import os

        try:
            import spacy_universal_sentence_encoder
        except ModuleNotFoundError:
            req_path = os.path.abspath( os.path.join(os.path.dirname(__file__), '../../requirements.vec.txt'))

            logging.info("Install nltk and spacy from: %s"%req_path)
            os.system(f'pip install -r {req_path}')
            reload(site)
            
            import nltk
            nltk.download('punkt')

    def _create_nlp_model(self):
        nlp_model = None
        if self.params.get('vectorize') and self.params.get('vectorize') != 'hashing':
            #https://tfhub.dev/google/universal-sentence-encoder-large/5
            #https://spacy.io/universe/project/spacy-universal-sentence-encoder
            #Load USE model
            
            self.install_spacy()
            import spacy_universal_sentence_encoder
            
            nlp_model = spacy_universal_sentence_encoder.load_model(self.params.get('vectorize'))

        return nlp_model

    def _run_nlp_model(self, nlp_model, text):
        if nlp_model:
            return nlp_model(text).vector

        return None
            
    def _vectorize(self, dataset, text_features, metrics):
        res_metrics = {}
        for col in text_features:
            self._calc_vector_metrics(dataset.df, col, metrics, self.text_metrics, text_metrics=True)

        if self.params.get('vectorize') == 'hashing': #For testing purposes
            vectorizer = FeatureHasher(n_features=8, input_type='string')
            # vectorizer = TfidfVectorizer(analyzer='word',
            #                 preprocessor= lambda x :x,
            #                 tokenizer= lambda x : x,
            #                 token_pattern=None)            
            #vectorizer = HashingVectorizer()
            for col in text_features:
                res = vectorizer.fit_transform(dataset.df[col])
                dataset.df[col] = pd.Series(res.toarray().tolist())
            
        else:
            #nlp_model = self._create_nlp_model()

            def _do_tokenize(text):
                return self._tokenize(text)

            def _do_vectorize_text(nlp_model, text):
                res_vector = None

                try:
                    res_vector = self._run_nlp_model(nlp_model, text)
                except:
                    pass
                    #errors.append(e)

                if res_vector is None:
                    res_vector = self._run_nlp_model(nlp_model, '')

                return res_vector

            def _do_vectorize_batch(data):
                nlp_model = self._create_nlp_model()

                result = []
                for item in data:
                    result.append(_do_vectorize_text(nlp_model, item))

                return result

            def _flatten(list_of_lists):
                # Flatten a list of lists to a combined list
                return [item for sublist in list_of_lists for item in sublist]


            nlp_model = self._create_nlp_model()

            for col in text_features:
                dataset.df[col] = dataset.df.apply(
                    lambda x : _do_tokenize(x[col]), axis=1)

                
            # for col in text_features:
            #     dataset.df[col] = dataset.df.apply(
            #         lambda x : _do_vectorize_text(nlp_model, x[col]), axis=1)

            for col in text_features:
                dataset.df[col] = [item.vector for item in nlp_model.pipe(dataset.df[col],
                    batch_size=20)]

            # import multiprocess
            # from multiprocess import Pool
            # from tqdm import tqdm
            # import math

            # workers_count = self.params.get('workers_count', multiprocess.cpu_count()-1)
            # batch_size = max( self.params.get('batch_size',0), math.ceil(len(dataset.df)/workers_count))

            # logging.info("Run Bert vectorization. workers_count: %s, batch_size: %s", workers_count, batch_size)
            # with Pool(workers_count) as p:
            #     for col in text_features:
            #         res = list(tqdm(p.imap(_do_vectorize_batch, self._chunker(dataset.df[col], batch_size))))
            #         dataset.df[col] = _flatten(res)

        #print(dataset.df)
        for col in text_features:
            self._calc_vector_metrics(dataset.df, col, metrics, self.text_metrics, text_metrics=False)

    def _chunker(self, seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
            
    def _calc_vector_metrics(self, df, col, metrics, res_metrics, text_metrics):
        if not metrics:
            return

        res = {}
    
        if text_metrics:    
            if 'mean_length' in metrics:
                res['mean_length'] = df[col].str.len().mean()
            if 'unique_count' in metrics:
                res['unique_count'] = df[col].unique().size
        else:        
            if 'separation_score' in metrics:
                s = cosine_similarity([x for x in df[col].values])
                res['separation_score'] = float(1 - s.mean())

        if res:
            if col in res_metrics:
                res_metrics[col].update(res)
            else:    
                res_metrics[col] = res

    def _prepare_full_dataset(self, df, datasets):
        df_full = df
        if self.params.get('datasets'):
            for idx, dataset in enumerate(datasets):
                df_full = pd.merge(df_full, datasets[idx].df, 
                    left_on=self.params['datasets'][idx]['keys'][0], 
                    right_on=self.params['datasets'][idx]['keys'][1])

        return df_full

    def _apply_dim_reduction(self, df_full, vector_cols, prefixes):

        num_components = self.params['dim_reduction'].get('args', {}).get('n_components')
        alg_name = self.params['dim_reduction'].get('alg_name')
        if alg_name == 't-SNE':
            transformer = TSNE(**self.params['dim_reduction'].get('args', {}))
        else:    
            transformer = PCA(**self.params['dim_reduction'].get('args', {}))

        for col in vector_cols:
            vals = np.stack(df_full[col].values)
            res = transformer.fit_transform(vals)

            df_full.drop([col], inplace=True, axis=1)

            for i in range(num_components):
                new_col_name = prefixes[col] if prefixes else ""
                new_col_name += "%s_%d"%(col, i)

                df_full[new_col_name] = res[:,i]
                        
        return df_full

    def _calculate_distance(self, df_full):
        from sklearn.metrics.pairwise import distance_metrics

        field_names = []
        dist_methods = []

        if isinstance(self.params.get('calc_distance'), str):
            dist_methods.append(self.params.get('calc_distance'))
        else:
            dist_methods = self.params.get('calc_distance')    

        for item in self.params.get('compare_pairs', []):
            col1 = item['compare_cols'][0]['cols'][0]
            col2 = item['compare_cols'][1]['cols'][0]

            for dist_method in dist_methods:
                field_name = item.get('output_name')
                if not field_name:
                    field_name = dist_method
                    for item_cols in item['compare_cols']:
                        field_name += '_' + item_cols['cols'][0]
                else:
                    try:
                        field_name = field_name%(dist_method)
                    except:
                        pass    

                def do_calc(record):
                    res = distance_metrics()[dist_method]([record[col1]], [record[col2]])
                    return res[0][0]

                cos_vec = df_full.apply(lambda x: do_calc(x), axis=1)

                df_full[field_name] = cos_vec
                field_names.append(field_name)

        return field_names, df_full

    def _make_result_dataset(self, df, df_full, field_names):
        if field_names:
            exclude_features = self._get_dataset_features(0, main_key=False)
            fields = []
            for item in df.columns.tolist():
                if item in exclude_features or item in field_names:
                    continue
                fields.append(item)
                    
            fields.extend(field_names)
            df_full = df_full[fields]

        return df_full
