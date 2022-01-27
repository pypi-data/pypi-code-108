import pandas as pd
import logging
from qsarmodelingpy import Utils
from qsarmodelingpy.Interfaces import ConfigGAInterface
from qsarmodelingpy.ga import Ga
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.filter import filter_matrix
import qsarmodelingpy.lj_cut as lj
from qsarmodelingpy.validate_yr_lno import validate
from qsarmodelingpy.save_PLS_coefficients import save_coefficients


def run(config: ConfigGAInterface) -> bool:
    """Run Generic Algorithm.

    Args:
        config (qsarmodelingpy.Interfaces.ConfigGAInterface): The configuration dictionary for GA

    Returns:
        bool: `True` if the validation has passed, `False` otherwise.
    """
    xFile = config['XMatrix']
    yFile = config['yvector']
    df = Utils.load_matrix(xFile)
    y = pd.read_csv(yFile, header=None).values
    var_cut = float(config['varcut'])
    corr_cut = float(config['corrcut'])
    autocorr_cut = float(config['autocorrcut'])
    nLVModel = None if int(config['max_latent_model']) == 0 else int(
        config['max_latent_model'])
    min_size = int(config['min_vars_model'])
    max_size = int(config['max_vars_model'])
    size_population = int(config['population_size'])
    mig_rate = float(config['migration_rate'])
    cxpb = float(config['crossover_rate'])
    mutpb = float(config['mutation_rate'])
    ngen = int(config['generations'])
    yr_crit = float(config['yrand'])
    lno_crit = float(config['lno'])
    out_matrix = config['output_matrix']
    out_cv = config['output_cv']
    Q2_file = config['output_q2']
    var_sel_file = config['output_selected']
    autoscale = config['autoscale']

    dfRest = filter_matrix(
        df, y, config['lj_transform'], var_cut, corr_cut, autocorr_cut)

    # Run
    X = dfRest.values
    if nLVModel is None:
        nLVModel = int(dfRest.shape[0]/5)
    ga = Ga(X, y, nLVModel, autoscale, min_size, max_size,
            size_population, mig_rate, cxpb, mutpb, ngen)
    ga.run()
    ga.saveQ2(Q2_file)
    ga.savePop(var_sel_file)
    Q2 = ga.Q2
    Q2 = [Q2[i][0] for i, _ in enumerate(Q2)]
    logging.debug(f"Starting the validation")
    var_sel = validate(X, y, ga.pop_selected, Q2,
                       yr_cut=yr_crit, lno_cut=lno_crit)
    logging.debug(f"Validation finished.")
    if var_sel:
        dfSel = dfRest.loc[:, dfRest.columns[var_sel]]
        dfSel.to_csv(out_matrix)
        cv = CrossValidation(dfSel.values, y)
        cv.saveParameters(out_cv)
        save_coefficients(dfSel, y, config["output_PLS_model"])
        logging.info("Genetic Algorithm Done")
        return True
    else:
        logging.error("y-randomization or Leave-N-Out failed!")
        return False
