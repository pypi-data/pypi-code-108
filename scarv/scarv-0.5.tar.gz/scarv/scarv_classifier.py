# scarv_classifier

def query_matching_variants(patho_SNVs, benign_SNVs, ratio, genome_segmentation, splice_sites):
    from scarv import scarv_queries
    import pyranges as pr
    import pandas as pd
    import numpy as np
    import collections
    import os

    patho_SNVs.Annot = "Intergenic"
    benign_SNVs.Annot = "Intergenic"

    for feature in genome_segmentation.keys():
        hits_benign = benign_SNVs.join(genome_segmentation[feature], how='left')
        benign_SNVs.Annot = [x if y=='-1' else y for x, y, in zip(hits_benign.Annot, hits_benign.Name)]

        hits_patho = patho_SNVs.join(genome_segmentation[feature], how='left')
        patho_SNVs.Annot = [x if y=='-1' else y for x, y, in zip(hits_patho.Annot, hits_patho.Name)]

    # annotate with distance to splice
    benign_SNVs = benign_SNVs.k_nearest(splice_sites, ties='first')[['Chromosome', 'Start', 'End', 'Annot', 'Distance']]
    benign_SNVs.Distance = benign_SNVs.Distance.abs()

    patho_SNVs = patho_SNVs.k_nearest(splice_sites, ties='first')[['Chromosome', 'Start', 'End', 'Annot', 'Distance']]
    patho_SNVs.Distance = patho_SNVs.Distance.abs()

    matched_benign_SNVs = pr.PyRanges()
    for SNV in patho_SNVs.as_df().iterrows():
        element = SNV[1].Annot
        distToSplice = SNV[1].Distance
        matched_benign_SNVs = sample_variants(element, distToSplice, matched_benign_SNVs, benign_SNVs, ratio)

    # remove duplicates and ensure distance of > 500 bp between benign variants
    matched_benign_SNVs_no_dups = matched_benign_SNVs.merge().tile(1)
    matched_benign_SNVs_no_dups_extd = matched_benign_SNVs_no_dups.slack(250).merge()

    while(len(matched_benign_SNVs_no_dups_extd) != len(matched_benign_SNVs_no_dups)):
        first_overlap = np.where(matched_benign_SNVs_no_dups_extd.lengths() > 501)[0][0]
        matched_benign_SNVs_no_dups = pr.PyRanges(matched_benign_SNVs_no_dups.as_df().drop(first_overlap))
        matched_benign_SNVs_no_dups_extd = matched_benign_SNVs_no_dups.slack(250).merge()

    return matched_benign_SNVs_no_dups



def sample_variants(element, distToSplice, sampled_variants, control_variants, ratio):
    import pyranges as pr
    import pandas as pd
    import numpy as np  

    correct_annotation = control_variants[control_variants.Annot==element].as_df()
    correct_annotation['distDiff'] = np.abs([x - distToSplice for x in correct_annotation.Distance])
    correct_annotation_std_by_distDiff = correct_annotation.sort_values('distDiff')

    new_samples = pr.PyRanges(correct_annotation_std_by_distDiff.iloc[:ratio])[['Chromosome', 'Start', 'End']]
    sampled_variants = pr.PyRanges(pd.concat([sampled_variants.as_df(), new_samples.as_df()]))

    return sampled_variants



def load_data (gr, fn, score_annotation_fns = {}, gene_annotation_fns = {}, pLI_association_annotation_fns = {}, superenhancer_annotation_fns = {}):
    import pyranges as pr
    import pandas as pd
    import numpy as np  

    for feature in score_annotation_fns.keys():
        print("Annotating with " + feature)
        gr = query_annotation(gr, fn, score_annotation_fns[feature], feature)
        print("Done")

    for feature in gene_annotation_fns.keys():
        print("Annotating with " + feature)
        gr = query_nearest_gene_feature(gr, gene_annotation_fns[feature], feature)
        print("Done")

    for feature in pLI_association_annotation_fns.keys():
        print("Annotating with " + feature)
        gr = annotate_pLI_associations(gr, pLI_association_annotation_fns[feature], [feature, feature + "_ind"])
        print("Done")

    for feature in superenhancer_annotation_fns.keys():
        print("Annotating with " + feature)
        gr = annotate_superenhancer(gr, superenhancer_annotation_fns[feature], feature)
        print("Done")

    return gr



def query_annotation (gr, gr_fn, annot_fn, name):
    import os
    import pyranges as pr
    import numpy as np

    query = os.popen("tabix " + annot_fn + " -R " + gr_fn).read().split()

    x = np.where(["chr" in x for x in query])[0]
    ncols = x[1] - x[0]

    gr_annot = pr.from_dict({'Chromosome': query[::ncols], 'Start': list(map(int, query[1::ncols])), 'End': list(map(int, query[2::ncols])), name: list(map(float, query[3::ncols]))})
    
    df_annot = gr_annot.as_df()
    df_annot['Chromosome'] = df_annot['Chromosome'].astype("object")

    gr_annot_max = pr.PyRanges(df_annot.groupby(['Chromosome','Start','End'])[name].max().dropna().reset_index())
    gr = annotate(gr, gr_annot_max, name)

    return gr



def annotate (gr, gr_annot, name):
    import numpy as np
    import pyranges as pr

    cols = list(gr.columns)
    new_cols = cols + [name]

    hits = gr.join(gr_annot, how='left').as_df()
    hits_no_dups = hits[~hits[['Chromosome', 'Start', 'End']].duplicated()].copy()
    hits_no_dups.loc[hits_no_dups.End_b == -1, name] = np.nan

    gr = pr.PyRanges(hits_no_dups)[new_cols]

    return gr



def query_nearest_gene_feature(gr, annot_fn, name):
    import pyranges as pr

    annot = pr.read_bed(annot_fn)
    annot.columns = ['Chromosome', 'Start', 'End', name]

    gr_annot = gr.k_nearest(annot, ties='first')[[name]]
    gr = annotate(gr, gr_annot, name)

    return gr



def annotate_pLI_associations (gr, pLI_annotation_fn, names):
    import numpy as np
    import pyranges as pr
    import pandas as pd

    cols = list(gr.columns)
    new_cols = cols + names

    pLI_annotation = pr.read_bed(pLI_annotation_fn)
    pLI_annotation.columns = ['Chromosome', 'Start', 'End', names[0]]

    hits = gr.join(pLI_annotation, how='left').as_df()
    hits.loc[hits['End_b'] == -1, names[0]] = np.nan
    hits[names[1]] = 1 - np.isnan(hits[names[0]]).astype(int)
    hits_no_dups = hits[~hits[['Chromosome', 'Start', 'End']].duplicated()].copy()

    gr = pr.PyRanges(hits_no_dups)[new_cols]

    return gr



def annotate_superenhancer (gr, superenhancer_annotation_fn, name):
    import numpy as np
    import pyranges as pr

    cols = list(gr.columns)
    new_cols = cols + [name]

    superenhancer_annotation = pr.read_bed(superenhancer_annotation_fn)
    superenhancer_annotation.columns = ['Chromosome', 'Start', 'End', name]

    hits = gr.join(superenhancer_annotation, how='left').as_df()
    hits_no_dups = hits[~hits[['Chromosome', 'Start', 'End']].duplicated()].copy()
    hits_no_dups.loc[hits_no_dups.End_b == -1, name] = 0

    gr = pr.PyRanges(hits_no_dups)[new_cols]

    return gr



def get_AUC(train_data, test_data):
    from xgboost import XGBClassifier
    from sklearn.metrics import roc_auc_score

    clf = XGBClassifier(eval_metric='logloss', use_label_encoder=False)
    clf.fit(train_data['X'], train_data['y'])

    preds_prob = clf.predict_proba(test_data['X'])[:,1]
    auc = roc_auc_score(test_data['y'], preds_prob)

    return auc



def cross_validation_k_fold(X, Y, k):
    from xgboost import XGBClassifier
    import numpy as np

    folds = np.random.choice(np.arange(k), size=X.shape[0], replace=True)
    preds = np.empty(X.shape[0])

    for i in range(k):
        X_train, X_test = X[folds!=i], X[folds==i]
        Y_train, Y_test = Y[folds!=i], Y[folds==i]

        clf = XGBClassifier(eval_metric='logloss', use_label_encoder=False)
        clf.fit(X_train, Y_train)

        preds[folds==i] = clf.predict_proba(X_test)[:,1]

    return preds

