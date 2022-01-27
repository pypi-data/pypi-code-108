import pandas as pd
import logging
from qsarmodelingpy import Utils
from qsarmodelingpy.ops import OPS
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.filter import filter_matrix
from qsarmodelingpy.validate_yr_lno import validate
from qsarmodelingpy.save_PLS_coefficients import save_coefficients

from qsarmodelingpy.Interfaces import ConfigOPSInterface
# Uncomment the following line to see all console logs (if not yet done in main.py).
# logging.basicConfig(level=logging.DEBUG)


def run(config: ConfigOPSInterface) -> bool:
    """Run Ordered Predictors Selection.

    Args:
        config (qsarmodelingpy.Interfaces.ConfigOPSInterface): The configuration dictionary for OPS

    Returns:
        bool: `True` if the validation has passed, `False` otherwise.
    """

    # Open configuration file in order to look for the matrices and the parameters to run
    # OPS and cross-validation
    xFile = config['XMatrix']
    yFile = config['yvector']
    df = Utils.load_matrix(xFile)
    y = pd.read_csv(yFile, header=None).values
    var_cut = float(config['varcut'])
    corr_cut = float(config['corrcut'])
    autocorr_cut = float(config['autocorrcut'])
    nLVOPS = None if int(config['latent_vars_ops']) == 0 else int(config['latent_vars_ops'])
    nLVModel = None if int(config['latent_vars_model']) == 0 else int(config['latent_vars_model'])
    opsWindow = int(config['ops_window'])
    opsIncrement = int(config['ops_increment'])
    percentage = int(config['vars_percentage'])
    nModels = int(config['models_to_save'])
    yr_crit = float(config['yrand'])
    lno_crit = float(config['lno'])
    out_matrix = config['output_matrix']
    out_cv = config['output_cv']
    out_models = config['output_models']
    autoscale = config['autoscale']

    dfRest = filter_matrix(
        df, y, config['lj_transform'], var_cut, corr_cut, autocorr_cut)

    # Run
    dfRest.to_csv(out_matrix)
    X = dfRest.values
    ops = OPS(X, y, nLVOPS, nLVModel, opsWindow,
              opsIncrement, percentage, nModels, autoscale)
    typeOPS = config['ops_type']
    if typeOPS == 's':
        ops.runOPS()
    elif typeOPS == 'f':
        ops.feedOPS()
    else:
        raise Exception(
            f"Invalid option '{typeOPS}' for OPS type. Use 's' for single run or 'f' for feedOPS.")
    ops.saveModels(out_models)
    var_sel = validate(
        X, y, ops.models["var_sel"], ops.models["Q2"], yr_cut=yr_crit, lno_cut=lno_crit)
    if var_sel:
        dfSel = dfRest.loc[:, dfRest.columns[var_sel]]
        dfSel.to_csv(out_matrix)
        cv = CrossValidation(dfSel.values, y)
        logging.debug("Saving parameters.")
        cv.saveParameters(out_cv)
        logging.debug("Saving coefficients.")
        save_coefficients(dfSel, y, config["output_PLS_model"])
        logging.info("OPS Done")
        return True
    else:
        logging.error("y-randomization or LNO failed!")
        return False
