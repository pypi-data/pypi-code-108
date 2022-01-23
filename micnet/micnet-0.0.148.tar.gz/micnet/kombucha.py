import pkg_resources
import pandas as pd

def load_kombucha():
    """Return a dataframe with the abundance table of Kombucha

    Contains the following fields:
        ASV          
        Taxa          
        Samples


    """
    stream = pkg_resources.resource_stream(__name__, 'data/kombucha_data.txt')
    return pd.read_csv(stream, sep = '\t',encoding='utf-8')
