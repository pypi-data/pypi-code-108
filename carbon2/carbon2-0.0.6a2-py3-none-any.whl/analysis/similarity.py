import itertools
import collections

import jieba
import numpy as np
from strsimpy.metric_lcs import MetricLCS

def analyze_similar_document_pairs(csv_path="../examples_simple/downloaded_datasets/list_news_india.csv",
                          stopwords_path='datasets/hit_stopwords.txt',analyze_field='Title',method="fast_lsh_pairs",
                          save_similar_result_path="",need_similarity=False,minimum_similarity=0.8
                          ):
    metric_lcs = MetricLCS()
    documents = []

    from quickcsv.file import qc_read,qc_write
    list_doc = qc_read(csv_path)
    # list_doc = list_doc[:1000]
    for model in list_doc:
        title = model[analyze_field]
        documents.append(title)

    stopwords = []
    if stopwords_path!="":
        with open(stopwords_path, 'r', encoding='utf-8') as file:
            for line in file:
                stopwords.append(line.strip())

    print("Using stopwords:", stopwords)

    print()
    for i, doc in enumerate(documents):
        list_word = []
        list_word_raw = jieba.cut(doc, cut_all=False)
        for word in list_word_raw:
            if word not in stopwords:
                list_word.append(word)
        documents[i] = ''.join(list_word)
        if documents[i] == "":
            documents[i] = "【空】"
        if i<20:
            print(i, documents[i])
    print("...")
    print(f"获得文档共{len(documents)}个!")


    print(f"Average char-length: {np.mean(np.array([len(x) for x in documents]))}")
    print(f"Min char-length: {min(len(x) for x in documents)}")
    print(f"Max char-length: {max(len(x) for x in documents)}")

    # create K-shingles by sliding window approach
    def getShingles(str1, K=5):
        d1 = set()
        for i in range(len(str1) - K):
            d1.add(str1[i:i + K])
        # print(f"Found {len(d1)} unique shingles, out of {len(str1)} possible.")
        return d1

    doc_shingles = [getShingles(s, 5) for s in documents]

    def jaccardSim(d1, d2):
        NNN = len(d1.union(d2))
        if NNN == 0:
            NNN = 0.000001
        return len(d1.intersection(d2)) / NNN

    # itertools.combinations finds all (,n) n-pairs
    # then we use a map op on the tuples with jaccardSim

    # Take union of all sets. Convert to an array and assign
    # each element an integer based on position in array
    fullset = set.union(*doc_shingles)
    shingle_dict = dict(zip(list(fullset), range(len(fullset))))
    print(f"There are {len(shingle_dict)} shingles")

    # Create a hash function
    # define as a callable class, so that we only
    # intialize random functions once
    class HashManager():
        def __init__(self, shingle_dict):
            self.shingle_dict = shingle_dict
            self.N = len(shingle_dict)
            self.params = None

        def _initParams(self, n_sig):
            self.params = np.random.randint(self.N, size=[n_sig, 2])

        def _permuteRow(self, row):
            return (self.params @ np.array([1, row])) % self.N

        def __call__(self, docs, n_sig, init=True):
            # Initialize if we change signature matrix length
            # or if we request to re-initialize
            if self.params is None or len(self.params) != n_sig or init:
                self._initParams(n_sig)

            # initialize signature matrix
            sig = np.full((n_sig, len(docs)), np.inf)

            # each doc in docs is assumed to be an iterable object
            for j, doc in enumerate(docs):
                for shingle in doc:
                    orig_row = shingle_dict[shingle]
                    curr_col = self._permuteRow(orig_row)
                    sig[:, j] = np.minimum(sig[:, j], curr_col)
            return sig.astype(int)

    # run some tests:
    try:
        print("Initialization test: ", end="")
        hm = HashManager(shingle_dict)
        print("passed")

        print("Set parameters to right size: ", end="")
        hm._initParams(n_sig=4)
        assert (hm.params.shape == (4, 2))
        print("passed")

        print("Permuting a row integer returns array: ", end="")
        curr_col = hm._permuteRow(3)
        assert (curr_col.shape == (4,))
        print("passed")

        print("Compute minhashed signature matrix: ", end="")
        hm(doc_shingles, 4)
        print("passed")
    except Exception as e:
        print("failure")
        print(e.args)

    hm = HashManager(shingle_dict)

    def trueSimScores(doc_shingles):
        pair_labels = []
        pair_sims = []
        idxs = range(len(doc_shingles))
        for x1, x2 in itertools.combinations(zip(idxs, doc_shingles), 2):
            pair_labels.append((x1[0], x2[0]))
            pair_sims.append(jaccardSim(x1[1], x2[1]))
        return dict(zip(pair_labels, pair_sims))

    def sigSimScores(sig_mat):
        #     cols = [sig_mat[:,i] for i in range(sig_mat.shape[1])]
        cols = sig_mat.T
        idxs = range(sig_mat.shape[1])

        pair_labels = []
        pair_sims = []
        for (i, col1), (j, col2) in itertools.combinations(zip(idxs, cols), 2):
            pair_labels.append((i, j))
            pair_sims.append(np.mean(col1 == col2))

        return dict(zip(pair_labels, pair_sims))

    def printScoreComparison(true_dict, approx_dict):
        print(f"**~~~~~~ Similarity score comparison ~~~~~~**")
        print("Pair\t\tApprox\t\tTrue\t\t%Error")
        for pair, true_value in true_dict.items():
            approx_value = approx_dict[pair]
            err = 100 * abs(true_value - approx_value) / true_value
            print(f"{pair}\t\t{approx_value:.3f}\t\t{true_value:.3f}\t\t{err:.2f}")

    def candidatePairs(score_dict, threshold):
        return set(pair for pair, scr in score_dict.items() if scr >= threshold)

    def accMatrix(true_dict, approx_dict, threshold):
        true_pairs = candidatePairs(true_dict, threshold)
        approx_pairs = candidatePairs(approx_dict, threshold)
        false_negatives = len(true_pairs - approx_pairs)
        false_positives = len(approx_pairs - true_pairs)
        print(f"False negatives: {false_negatives}")
        print(f"Potential false positives: {false_positives}")

    # Brute force banded candidate pair function, for checking hash method later
    def bandedCandidatePair(col1, col2, b, r):
        """Returns a boolean if the two columns are a candidate pair
        inputs must obey n=len(col1)=len(col2)=b*r"""
        n = len(col1)
        assert (n == b * r)
        assert (n == len(col2))
        truth_array = (col1 == col2)
        return any(all(band) for band in np.array_split(truth_array, b))

    def bandedCandidatePairs(sig_mat, b, r):
        d = sig_mat.shape[1]
        idxs = range(d)
        cols = [sig_mat[:, i] for i in range(d)]
        pairs = set()
        for (i, col1), (j, col2) in itertools.combinations(zip(idxs, cols), 2):
            if bandedCandidatePair(col1, col2, b, r):
                pairs.add((i, j))
        return pairs

    '''

    sig_mat = hm(doc_shingles, 10)
    true_score_dict = trueSimScores(doc_shingles)
    approx_score_dict = sigSimScores(sig_mat)
    printScoreComparison(true_score_dict, approx_score_dict)

    print("True pairs:", candidatePairs(true_score_dict, 0.25))
    print("Candidate pairs:", candidatePairs(approx_score_dict, 0.25))
    accMatrix(true_score_dict, approx_score_dict, 0.4)

    print('=============================================================')



    # set p = 0.3 arbitrarily
    p = 0.3
    n = 120
    b = 30
    r = 4

    # see how many candidate pairs we got right!

    sig_mat = hm(doc_shingles, n)
    true_score_dict = trueSimScores(doc_shingles)
    approx_score_dict = sigSimScores(sig_mat)
    print("True pairs:",candidatePairs(true_score_dict, p))
    # print("LSH pairs:",bandedCandidatePairs(sig_mat, b, r))
    print("Vanilla MinHash pairs:",candidatePairs(approx_score_dict, p))
    # accMatrix(true_score_dict, approx_score_dict, 0.4)

    # sig_mat = hm(doc_shingles, n)
    # true_score_dict = trueSimScores(doc_shingles)
    printScoreComparison(true_score_dict, approx_score_dict)
    '''
    print('===========================正在生成结果==================================')

    # Finally, we perform the fast candidate pair search, using a hash table of band and column id's
    def fastCandidatePairs(sig_mat, b, r):
        n, d = sig_mat.shape
        assert (n == b * r)
        hashbuckets = collections.defaultdict(set)
        bands = np.array_split(sig_mat, b, axis=0)
        for i, band in enumerate(bands):
            for j in range(d):
                # The last value must be made a string, to prevent accidental
                # key collisions of r+1 integers when we really only want
                # keys of r integers plus a band index
                band_id = tuple(list(band[:, j]) + [str(i)])
                hashbuckets[band_id].add(j)
        candidate_pairs = set()
        for bucket in hashbuckets.values():
            if len(bucket) > 1:
                for pair in itertools.combinations(bucket, 2):
                    candidate_pairs.add(pair)
        return candidate_pairs

    # to make sure it works,
    # compare with the brute force method on a few trials

    # set p = 0.3 arbitrarily
    p = 0.8
    n = 120
    b = 30
    r = 4

    def show_dict(list_pairs):
        print("====相似的标题ID及标题对比====")
        list_model=[]
        for (id1, id2) in list_pairs:
            print(f'{id1} <--> {id2}')
            print(documents[id1])
            print(documents[id2])
            print()
            model = {
                "Id1": list_doc[id1]["Id"],
                "Id2": list_doc[id2]["Id"],
                "Id1_Text": list_doc[id1][analyze_field],
                "Id2_Text": list_doc[id2][analyze_field]
            }
            if need_similarity:
                dist=metric_lcs.distance(documents[id1], documents[id2])
                sim = 1 - dist
                if sim<minimum_similarity:
                    continue
                model['similarity']=sim
                list_model.append(model)
            else:
                list_model.append(model)
        return list_model

    # see how many candidate pairs we got right!
    sig_mat = hm(doc_shingles, n)
    true_score_dict = trueSimScores(doc_shingles)

    list_final_result=None
    if method=="true_pairs":
        list_final_result = candidatePairs(true_score_dict, p)
        # print('True pairs:\t', list_final_result)

    if method=="true_lsh_pairs":
        list_final_result = bandedCandidatePairs(sig_mat, b, r)
        # print("True LSH pairs:\t", list_final_result)

    if method=="fast_lsh_pairs":
        list_final_result = fastCandidatePairs(sig_mat, b, r)
        # print("Fast LSH pairs:\t", list_final_result)

    if method=="true_minshash_pairs":
        approx_score_dict = sigSimScores(sig_mat)
        list_final_result = candidatePairs(approx_score_dict, p)
        # print("MinHash pairs:\t", list_final_result)

    if save_similar_result_path!="":
        list_result=show_dict(list_final_result)
        print("Saving to ",save_similar_result_path)
        qc_write(save_similar_result_path,list_result)
        print("Finished")

    return list_final_result
