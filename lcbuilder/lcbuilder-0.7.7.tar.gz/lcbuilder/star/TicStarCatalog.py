import numpy as np
from lcbuilder.star.StarCatalog import StarCatalog
from astroquery.mast import Catalogs
import foldedleastsquares as tls


class TicStarCatalog(StarCatalog):
    def __init__(self):
        super().__init__()

    def catalog_info(self, id):
        """Takes TIC_ID, returns stellar information from online catalog using Vizier"""
        if type(id) is not int:
            raise TypeError('TIC_ID ID must be of type "int"')
        result = Catalogs.query_criteria(catalog="Tic", ID=id).as_array()
        Teff = result[0][64]
        lum = result[0]['lum']
        logg = result[0][66]
        radius = result[0][70]
        ra = result[0][13]
        dec = result[0][14]
        radius_max = result[0][71]
        radius_min = result[0][71]
        mass = result[0][72]
        mass_max = result[0][73]
        mass_min = result[0][73]
        if lum is None or np.isnan(lum):
            lum = self.star_luminosity(Teff, radius)
        logg = result[0]["logg"] if "logg" in result[0].dtype.names else None
        logg_err = result[0]["e_logg"] if "e_logg" in result[0].dtype.names else None
        v = result[0]["Vmag"] if "Vmag" in result[0].dtype.names else None
        v_err = result[0]["e_Vmag"] if "e_Vmag" in result[0].dtype.names else None
        j = result[0]["Jmag"] if "Jmag" in result[0].dtype.names else None
        j_err = result[0]["e_Jmag"] if "e_Jmag" in result[0].dtype.names else None
        h = result[0]["Hmag"] if "Hmag" in result[0].dtype.names else None
        h_err = result[0]["e_Hmag"] if "e_Hmag" in result[0].dtype.names else None
        k = result[0]["Kmag"] if "Kmag" in result[0].dtype.names else None
        k_err = result[0]["e_Kmag"] if "e_Kmag" in result[0].dtype.names else None
        ld, mass, mass_min, mass_max, radius, radius_min, radius_max = tls.catalog_info(TIC_ID=id)
        return (ld, Teff, lum, logg, logg_err,
                radius, radius_min, radius_max, mass, mass_min, mass_max, ra, dec, v, v_err, j, j_err,
                h, h_err, k, k_err, None, None, None)
