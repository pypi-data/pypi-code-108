from astroquery.vizier import Vizier
from lcbuilder.star.StarCatalog import StarCatalog
import foldedleastsquares as tls


class EpicStarCatalog(StarCatalog):
    def __init__(self):
        super().__init__()

    def catalog_info(self, id):
        """Takes EPIC_ID, returns stellar information from online catalog using Vizier"""
        if type(id) is not int:
            raise TypeError('EPIC_ID ID must be of type "int"')
        if (id < 201000001) or (id > 251813738):
            raise TypeError("EPIC_ID ID must be in range 201000001 to 251813738")
        columns = ["Teff", "logg", "Rad", "E_Rad", "e_Rad", "Mass", "E_Mass", "e_Mass", "RAJ2000", "DEJ2000",
                   "Vmag", "e_Vmag", "Jmag", "e_Jmag", "Hmag", "e_Hmag", "Ksmag", "e_Ksmag", "Kpmag", "[Fe/H]",
                   "E_[Fe/H]", "e_[Fe/H]", "E_logg", "e_logg"]
        catalog = "IV/34/epic"
        result = (
            Vizier(columns=columns)
                .query_constraints(ID=id, catalog=catalog)[0]
                .as_array()
        )
        Teff = result[0]["Teff"]
        logg = result[0]["logg"]
        radius = result[0]["Rad"]
        radius_max = result[0]["E_Rad"]
        radius_min = result[0]["e_Rad"]
        mass = result[0]["Mass"]
        mass_max = result[0]["E_Mass"]
        mass_min = result[0]["e_Mass"]
        ra = result[0]["RAJ2000"]
        dec = result[0]["DEJ2000"]
        v = result[0]["Vmag"] if "Vmag" in result[0].dtype.names else None
        v_err = result[0]["e_Vmag"] if "e_Vmag" in result[0].dtype.names else None
        j = result[0]["Jmag"] if "Jmag" in result[0].dtype.names else None
        j_err = result[0]["e_Jmag"] if "e_Jmag" in result[0].dtype.names else None
        h = result[0]["Hmag"] if "Hmag" in result[0].dtype.names else None
        h_err = result[0]["e_Hmag"] if "e_Hmag" in result[0].dtype.names else None
        k = result[0]["Ksmag"] if "Ksmag" in result[0].dtype.names else None
        k_err = result[0]["e_Ksmag"] if "e_Ksmag" in result[0].dtype.names else None
        kp = result[0]["Kpmag"] if "Kpmag" in result[0].dtype.names else None
        feh = result[0]["__Fe_H_"] if "__Fe_H_" in result[0].dtype.names else None
        feh_up_err = result[0]["E_[Fe/H]"] if "E_[Fe/H]" in result[0].dtype.names else None
        feh_lo_err = result[0]["e_[Fe/H]"] if "e_[Fe/H]" in result[0].dtype.names else None
        logg_up_err = result[0]["E_logg"] if "E_logg" in result[0].dtype.names else None
        logg_lo_err = result[0]["e_logg"] if "e_logg" in result[0].dtype.names else None
        logg_err = None
        if logg_up_err is not None and logg_lo_err is not None:
            logg_err = logg_up_err if logg_up_err > logg_lo_err else logg_lo_err
        elif logg_up_err is not None:
            logg_err = logg_up_err
        elif logg_lo_err is not None:
            logg_err = logg_lo_err
        feh_err = None
        if feh_up_err is not None and feh_lo_err is not None:
            feh_err = feh_up_err if feh_up_err > feh_lo_err else feh_lo_err
        elif feh_up_err is not None:
            feh_err = feh_up_err
        elif feh_lo_err is not None:
            feh_err = feh_lo_err
        lum = self.star_luminosity(Teff, radius)
        ld, mass, mass_min, mass_max, radius, radius_min, radius_max = tls.catalog_info(EPIC_ID=id)
        return (ld, Teff, lum, logg, logg_err, radius, radius_min, radius_max, mass, mass_min, mass_max, ra, dec, v,
                v_err, j, j_err, h, h_err, k, k_err, kp, feh, feh)
