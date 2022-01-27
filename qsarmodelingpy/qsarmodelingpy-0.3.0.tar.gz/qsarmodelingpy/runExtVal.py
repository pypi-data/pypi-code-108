import pandas as pd
from qsarmodelingpy import Utils
from qsarmodelingpy.external_validation import ExternalValidation
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.kennardstonealgorithm import kennardstonealgorithm
from qsarmodelingpy.Interfaces import ConfigExtValInterface, ExtValResult
import qsarmodelingpy.lj_cut as lj
import logging


def run(config: ConfigExtValInterface) -> ExtValResult:
    """Run External Validation with configuration given by `config`.

    `config` is a Dictionary that follows the same interface as `qsarmodelingpy.Interfaces.ConfigExtValInterface`.

    Args:
        config (qsarmodelingpy.Interfaces.ConfigExtValInterface): The configuration dictionary.
    """
    Xfile = config["XMatrix"]
    yfile = config["yvector"]
    nLV = config["latent_vars_model"]
    ext_val_file = config["output_extval"]
    cv_file = config["output_cv"]
    Xtrain_file = config["output_X_train"]
    ytrain_file = config["output_y_train"]
    Xtest_file = config["output_X_test"]
    ytest_file = config["output_y_test"]
    y = pd.read_csv(yfile, header=None).values
    dfX = Utils.load_matrix(Xfile)
    dfX = lj.transform(dfX) if config["lj_transform"] else dfX
    X = dfX.values
    type_ext_val = int(config["extval_type"])
    if type_ext_val == 1:  # manual selection
        test_set = config["test_set"]
        test = [int(i) - 1 for i in test_set.split(',')]
        train = [j for j in range(len(y)) if j not in test]
    elif type_ext_val == 2:  # Kennard-Stone
        size_test_set = int(config["test_set"])
        # parameter is the size of training set
        train, test = kennardstonealgorithm(dfX, len(dfX) - size_test_set)
    else:  # Random selection
        raise NotImplementedError(
            "Random Selection is not yet implemented. Please double check your code and provide either 1 (Manual selection) or 2 (Kennard-stone) for the type of External validation.")
    ext = ExternalValidation(X, y, nLV)
    ext.extVal(train, test, nLV)
    result = ext.validateExtVal(train, test)
    ext.saveExtVal(train, test, ext_val_file)
    cv = CrossValidation(X[train, :], y[train], nLVMax=nLV, scale=True)
    cv.saveParameters(cv_file)
    dfXtrain = dfX.loc[dfX.index[train], dfX.columns]
    dfXtrain.to_csv(Xtrain_file)
    dfytrain = pd.DataFrame(y[train])
    dfytrain.to_csv(ytrain_file,
                    header=False)
    dfXtest = dfX.loc[dfX.index[test], dfX.columns]
    dfXtest.to_csv(Xtest_file)
    dfytest = pd.DataFrame(y[test])
    dfytest.to_csv(ytest_file,
                   header=False)

    return ExtValResult({
        "external_validation": ext,
        "cross_validation": cv,
        "train": train,
        "test": test
    })    
