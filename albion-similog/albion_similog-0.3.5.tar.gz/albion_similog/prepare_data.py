import pandas as pd

from albion_similog.log import setup_logger


logger = setup_logger(__name__)


def read_and_prepare_data(inputfile, columns=["API", "MD", "_", "ILD"]):
    """Prepare data for running famsa procedure

    Parameters
    ----------
    inputdir : pathlib.Path
        Path of the input data file (the first line is considered as the header, the first column
    as the index)
    columns : list of str
        Expected columns of the dataframe (the first one is skipped as the index). The default
    variable is a typical scheme from which one has the following columns: ID, from, to, value.

    Returns
    -------
    pandas.DataFrame
        Output data, with three columns (API, MD, ILD) that relies respectively to dataseries ID,
    abscissa and ordinates.

    """
    logger.info("Lecture du fichier %s.", inputfile)
    if any([c not in columns for c in ["API", "MD", "ILD"]]):
        raise ValueError(
            "The provided columns (%s) does not contain 'API', 'MD' and/or 'ILD'.",
            columns,
        )
    data = pd.read_csv(
        inputfile,
        index_col=0,
        header=0,
        names=columns,
        dtype={"MD": float, "ILD": float},
    )
    data = data.loc[data["ILD"] > 0, ["API", "MD", "ILD"]]
    data.reset_index(inplace=True, drop=True)
    logger.info("Input data is ready (%s records).", data.shape[0])
    return data
