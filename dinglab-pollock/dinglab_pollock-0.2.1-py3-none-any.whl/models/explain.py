import logging
import os
import pathlib
import subprocess
import uuid

import anndata
import pandas as pd
import numpy as np
import scanpy as sc
import shap

from pollock.models.model import embed_from_anndata, predict_from_anndata, load_from_directory

ENCODER_SHAPS_SCRIPT = os.path.join(pathlib.Path(__file__).parent.absolute(),
        '..', 'wrappers', 'encoder_shaps.py')


def explain_predictions(explain_adata, background_adata,
        module_filepath, prediction_key='cell_type', n_background_cells=100,
        temp_dir=None, abs_transform=True):
    """Explain the predictions of the given module.

    Arguments
    ---------
    explain_adata : anndata.AnnData
        AnnData object holding cells to be explained.
    background_adata : anndata.AnnData
        AnnData object holding cells to be used as background for shap value
        prediction. This object will be downsampled to n_background_cells.
    module_filepath : str
        Filepath of module used for prediction.
    prediction_key : str
        Column in explain.obs that cell type predictions are stored.
    n_background_cells : int
        Number of cells to sample from background_adata. A larger number
        means more accurate results, but a longer runtime.
    temp_dir : str, None
        Directory to write temporary files. Defaults to current working
        directory.

    Returns
    -------
    pd.DataFrame
        Dataframe where columns are genes, rows are cells, and the values correspond to
        How much each gene contributed to a given cells classification. High values
        mean that gene pushed that cell towards the predicted cell type
    """
    if temp_dir is None: temp_dir = os.getcwd()

    # make sure module_filepath is absolute filepath
    if not os.path.isabs(module_filepath):
        module_filepath = os.path.abspath(module_filepath)

    sampled_background = background_adata[np.random.choice(
        background_adata.obs.index, size=n_background_cells)]

    # save files so we can call external shap embedding values script
    a, b, c = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    explain_adata_fp = os.path.join(temp_dir, f'{a}.h5ad')
    background_adata_fp = os.path.join(temp_dir, f'{b}.h5ad')
    output_fp = os.path.join(temp_dir, f'{c}.npy')

    explain_adata.write_h5ad(explain_adata_fp)
    sampled_background.write_h5ad(background_adata_fp)

    subprocess.check_output(('python', ENCODER_SHAPS_SCRIPT, explain_adata_fp, background_adata_fp,
                                module_filepath, output_fp))

    # should be of shape (n_cells, n_embeddings, n_features)
    embedding_shaps = np.load(output_fp)

    # clean up
    os.remove(explain_adata_fp)
    os.remove(background_adata_fp)
    os.remove(output_fp)

    # get shap values for random forest classifier
    embeddings = embed_from_anndata(explain_adata.copy(), module_filepath)
    pds, pm = load_from_directory(explain_adata.copy(), module_filepath)
    logging.info(f'{pds.prediction_adata.shape}')
    explainer = shap.TreeExplainer(pm.clf)
    clf_shaps = explainer.shap_values(embeddings)
    clf_shaps = np.swapaxes(np.asarray(clf_shaps), 0, 1)


    # get feature values
    totals = None
    for i in range(explain_adata.shape[0]):
        cell_emb_shaps = clf_shaps[i, list(pm.class_names).index(explain_adata.obs[prediction_key][i]), :].flatten()
        # expected shape is (n_embeddings,)
        combined = cell_emb_shaps.reshape(-1, 1) * embedding_shaps[i]
        # expected shape is (n_embeddings, n_features)
        total = np.sum(combined, axis=0).flatten()

        if abs_transform: total = np.abs(total) # take abs value since directionality for emb is meaningless
        # expected shape is (n_features,)
        if totals is None:
            totals = total.reshape(1, len(total))
        else:
            totals = np.concatenate((totals, total.reshape(1, len(total))), axis=0)
    totals.shape

    df = pd.DataFrame(data=totals, index=pds.prediction_adata.obs.index,
            columns=pds.prediction_adata.var.index)

    return df
