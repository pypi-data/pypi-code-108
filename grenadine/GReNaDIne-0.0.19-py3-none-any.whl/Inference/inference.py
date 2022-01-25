# -*- coding: utf-8 -*-
"""
This module allows to infer co-expression  Gene Regulatory Networks using
gene expression data (RNAseq or Microarray).
"""
from tqdm.autonotebook import tqdm
from grenadine.Preprocessing.standard_preprocessing import z_score
import pandas as pd
import numpy as np

__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2019, The GReNaDIne Project"
__credits__ = ["Pauline Schmitt"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"


def score_links(gene_expression_matrix,
                score_predictor,
                tf_list = None,
                tg_list = None,
                normalize = False,
                discr_method=None,
                progress_bar=False,
                **predictor_parameters):
    """
    Scores transcription factors-target gene co-expressions using a predictor.

    Args:
        gene_expression_matrix (pandas.DataFrame):  gene expression matrix where
            rows are genes and  columns ares samples (conditions).
            The value at row i and column j represents the expression of gene i
            in condition j.
        score_predictor (function): function that receives a pandas.DataFrame X
            containing the transcriptor factor expressions and a pandas.Series
            y containing the expression of a target gene, and scores the
            co-expression level between each transcription factor and the target
            gene.
        tf_list (list or numpy.array): list of transcription factors ids.
        tg_list (list or numpy.array): list of target genes ids.
        normalize (boolean): If True the gene expression of genes is z-scored
        discr_method : discretization method to use, if discretization of target
            gene expression is desired
        progress_bar: bool, if true include progress bar
        **predictor_parameters: Named parameters for the score predictor

    Returns:
        pandas.DataFrame: co-regulation score matrix.

        Rows are target genes and columns are transcription factors.
        The value at row i and column j represents the score assigned by the
        score_predictor to the regulatory relationship between target gene i
        and transcription factor j.

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> np.random.seed(0)
        >>> data = pd.DataFrame(np.random.randn(5, 5),
                            index=["gene1", "gene2", "gene3", "gene4", "gene5"],
                            columns=["c1", "c2", "c3", "c4", "c5"])
        >>> tf_list = ["gene1", "gene2", "gene5"]

        >>> # Example with a regression method
        >>> from grenadine.Inference.regression_predictors import GENIE3
        >>> scores1 = score_links(gene_expression_matrix=data,
                                  score_predictor=GENIE3,
                                  tf_list=tf_list)
        >>> scores1
                  gene2     gene5     gene1
        gene1  0.484081  0.515919       NaN
        gene2       NaN  0.653471  0.346529
        gene3  0.245136  0.301229  0.453634
        gene4  0.309982  0.306964  0.383054
        gene5  0.529839       NaN  0.470161

        >>> # Example with a classification method
        >>> from grenadine.Inference.classification_predictors import RF_classifier_score
        >>> from grenadine.Preprocessing.discretization import discretize_genexp
        >>> discr_method = lambda X: discretize_genexp (X, "efd", 5, axis=1)
        >>> scores2 = score_links(gene_expression_matrix=data,
                                        score_predictor=RF_classifier_score,
                                        tf_list=tf_list,
                                        discr_method=discr_method)
        >>> scores2
                  gene2     gene5     gene1
        gene1  0.512659  0.487341       NaN
        gene2       NaN  0.463122  0.536878
        gene3  0.368175  0.317341  0.314484
        gene4  0.302738  0.346799  0.350463
        gene5  0.524815       NaN  0.475185

    """
    gene_expression_matrix = gene_expression_matrix.T
    # Set the list of TFs and TGs if necessary
    if tg_list is None:
        tg_list = gene_expression_matrix.columns
    if tf_list is None:
        tf_list = gene_expression_matrix.columns
    tf_list_present = set(gene_expression_matrix.columns).intersection(tf_list)
    tg_list_present = list(set(gene_expression_matrix.columns).intersection(tg_list))
    if not len(tf_list_present):
        Exception('None of the tfs in '+str(tf_list)+\
        " is present in the gene_expression_matrix genes list"+\
        str(gene_expression_matrix.columns))
    if not len(tg_list_present):
        Exception('None of the tgs in '+str(tg_list)+\
        " is present in the gene_expression_matrix genes list"+\
        str(gene_expression_matrix.columns))
    tg_list_present.sort()
    #  Normalize expression data for each gene
    if normalize:
        gene_expression_matrix = z_score(gene_expression_matrix,axis=0)
    # compute tf scores for each gene
    scores_tf_per_gene = []
    for gene in tqdm(tg_list_present,disable=not progress_bar):
        # Exclude the current gene from the tfs list
        tfs2test = list(tf_list_present.difference(set([gene])))
        tfs2test.sort()
        X = gene_expression_matrix[tfs2test].values
        y = gene_expression_matrix[gene].values
        if discr_method is not None :
            y = discr_method(y)
        if len(np.unique(y)) <= 1:
            # handle the case when only one class was detected in y
            score = np.zeros(len(tfs2test))
        else:
            score = score_predictor(X, y, **predictor_parameters)
        # Get the features importance (score for each TF -> Gene)
        scores = pd.Series(score)
        scores.index = tfs2test
        scores_tf_per_gene.append(scores)
    df_results = pd.DataFrame(scores_tf_per_gene, index=tg_list_present)
    return(df_results)

def clean_nan_inf_scores(scores):
    """
    Replaces nan and -inf scores by the (minimum_score - 1), and inf scores by
    (maximum_score + 1)

    Args:
        scores (pandas.DataFrame): co-regulation score matrix.
        Rows are target genes and columns are transcription factors.
        The value at row i and column j represents the score assigned by the
        score_predictor to the regulatory relationship between target gene i
        and transcription factor j.

    Returns:
        pandas.DataFrame: co-regulation score matrix.

        Rows are target genes and columns are transcription factors.
        The value at row i and column j represents the score assigned by the
        score_predictor to the regulatory relationship between target gene i
        and transcription factor j.

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> np.random.seed(0)
        >>> data = pd.DataFrame(np.random.randn(5, 5),
                            index=["gene1", "gene2", "gene3", "gene4", "gene5"],
                            columns=["c1", "c2", "c3", "c4", "c5"])
        >>> tf_list = ["gene1", "gene2", "gene5"]

        >>> # Example with a regression method
        >>> from grenadine.Inference.regression_predictors import GENIE3
        >>> scores1 = score_links(gene_expression_matrix=data,
                                  score_predictor=GENIE3,
                                  tf_list=tf_list)
        >>> scores1
                  gene2     gene5     gene1
        gene1  0.484081  0.515919       NaN
        gene2       NaN  0.653471  0.346529
        gene3  0.245136  0.301229  0.453634
        gene4  0.309982  0.306964  0.383054
        gene5  0.529839       NaN  0.470161
        >>> clean_nan_inf_scores(scores1)
                  gene2     gene5     gene1
        gene1  0.484081  0.515919  0.245126
        gene2  0.245126  0.653471  0.346529
        gene3  0.245136  0.301229  0.453634
        gene4  0.309982  0.306964  0.383054
        gene5  0.529839  0.245126  0.470161

    """
    # replacing NaN scores with minimum score - epsilon
    epsilon = 1e-5
    nan_scores = np.isnan(scores)
    min_score =  scores[np.logical_not(nan_scores)].min().min()
    scores[nan_scores] = min_score-epsilon
    # replacing infinite scores with maximum score + epsilon
    finite_scores = np.isfinite(scores)
    max_score =  scores[finite_scores].max().max()
    positive_inf = np.logical_and(np.logical_not(finite_scores),finite_scores>0)
    negative_inf = np.logical_and(np.logical_not(finite_scores),finite_scores<0)
    scores[positive_inf] = max_score+epsilon
    scores[positive_inf] = min_score-epsilon
    return scores


def rank_GRN(coexpression_scores_matrix, take_abs_score=False, clean_scores=True):
    """
    Ranks the co-regulation scores between transcription factors and target genes.

    Args:
        coexpression_scores_matrix (pandas.DataFrame):co-expression score matrix
            where rows are target genes and columns are transcription factors.
            The value at row i and column j represents the score assigned by a
            score_predictor to the regulatory relationship between target gene i
            and transcription factor j.
        take_abs_score (bool): take the absolute value of the score instead of
            taking scores themselves
    Returns:
        pandas.DataFrame: ranking matrix.

        A ranking matrix contains a row for each possible regulatory link, it
        also contains 4 columns, namely the rank, the score, the transcription
        factor id, and the target gene id.

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> np.random.seed(0)
        >>> data = pd.DataFrame(np.random.randn(3, 2),
                            index=["gene1", "gene2", "gene3"],
                            columns=["gene1", "gene3"])
        >>> # scores associated to self loops are set to nan
        >>> data.iloc[0,0]=np.nan
        >>> data.iloc[2,1]=np.nan
        >>> ranking_matrix = rank_GRN(data)
        >>> ranking_matrix
                     rank     score     TF     TG
        gene3_gene2   1.0  2.240893  gene3  gene2
        gene1_gene3   2.0  1.867558  gene1  gene3
        gene1_gene2   3.0  0.978738  gene1  gene2
        gene3_gene1   4.0  0.400157  gene3  gene1

    """
    epsilon = 1e-10
    rand_values = np.random.rand(*coexpression_scores_matrix.shape)*epsilon
    coexpression_scores_matrix += rand_values
    if clean_scores:
        coexpression_scores_matrix = clean_nan_inf_scores(coexpression_scores_matrix)
    if take_abs_score:
        coexpression_scores_matrix = np.abs(coexpression_scores_matrix)
    coexpression_unstack = coexpression_scores_matrix.unstack(level=0)
    ranking = pd.DataFrame()
    ranking["rank"] = coexpression_unstack.rank(method="dense",
                                                ascending=False,
                                                na_option="bottom")
    ranking["score"] = coexpression_unstack
    ranking["TF"] = list(ranking.index.get_level_values(level=0))
    ranking["TG"] = list(ranking.index.get_level_values(level=1))
    ranking = ranking.sort_values("score",ascending=False)
    ranking.index = ranking["TF"].astype(str)+"_"+ranking["TG"].astype(str)
    ranking = ranking.dropna()
    return(ranking)

def join_rankings_scores_df(**rank_scores):
    """
    Join rankings and scores data frames generated by different methods.

    Args:
        **rank_scores: Named parameters, where arguments names should be the
            methods names and arguments values correspond to pandas.DataFrame
            output of rank_GRN

    Returns:
        (pandas.DataFrame, pandas.DataFrame): joined ranks and joined scores
            where rows represent possible regulatory links and columns represent
            each method.
            Values at row i and column j represent resp. the rank or the score
            of edge i computed by method j.

    Examples:
        >>> import pandas as pd
        >>> method1_rank = pd.DataFrame([[1,1.3, "gene1", "gene2"],
                                         [2,1.1, "gene1", "gene3"],
                                         [3,0.9, "gene3", "gene2"]],
                                         columns=['rank', 'score', 'TF', 'TG'])
        >>> method1_rank.index = method1_rank['TF']+'_'+method1_rank['TG']
        >>> method2_rank = pd.DataFrame([[1,1.4, "gene1", "gene3"],
                                         [2,1.0, "gene1", "gene2"],
                                         [3,0.9, "gene3", "gene2"]],
                                         columns=['rank', 'score', 'TF', 'TG'])
        >>> method2_rank.index = method2_rank['TF']+'_'+method2_rank['TG']
        >>> ranks, scores = join_rankings_scores_df(method1=method1_rank, method2=method2_rank)
        >>> ranks
                     method1  method2
        gene1_gene2        1        2
        gene1_gene3        2        1
        gene3_gene2        3        3
        >>> scores
                     method1  method2
        gene1_gene2      1.3      1.0
        gene1_gene3      1.1      1.4
        gene3_gene2      0.9      0.9

    """
    ranks_df = {method:rank_scores[method]["rank"] for method in rank_scores}
    ranks_df = pd.DataFrame(ranks_df)
    scores_df = {method:rank_scores[method]["score"] for method in rank_scores}
    scores_df = pd.DataFrame(scores_df)
    return(ranks_df,scores_df)
