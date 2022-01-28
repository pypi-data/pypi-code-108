import logging
import numpy as np

from lcbuilder.LcBuild import LcBuild
from lcbuilder.constants import CUTOUT_SIZE, LIGHTKURVE_CACHE_DIR
from lcbuilder.objectinfo.MissionObjectInfo import MissionObjectInfo
from lcbuilder.photometry.aperture_extractor import ApertureExtractor
from lcbuilder.star import starinfo
from lcbuilder.objectinfo.ObjectProcessingError import ObjectProcessingError
from lcbuilder.objectinfo.preparer.LightcurveBuilder import LightcurveBuilder
import lightkurve as lk
import matplotlib.pyplot as plt
import os


class MissionLightcurveBuilder(LightcurveBuilder):
    def __init__(self):
        super().__init__()

    def build(self, object_info: MissionObjectInfo, sherlock_dir, caches_root_dir):
        mission_id = object_info.mission_id()
        sherlock_id = object_info.sherlock_id()
        logging.info("Retrieving star catalog info...")
        mission, mission_prefix, id = super().parse_object_id(mission_id)
        if mission_prefix not in self.star_catalogs:
            raise ValueError("Wrong object id " + mission_id)
        cadence = object_info.cadence if object_info.cadence is not None else "short"
        author = object_info.author if object_info.author is not None else self.authors[mission]
        star_info = starinfo.StarInfo(sherlock_id, *self.star_catalogs[mission_prefix].catalog_info(id))
        logging.info("Downloading lightcurve files...")
        sectors = None if object_info.sectors == 'all' or mission != "TESS" else object_info.sectors
        campaigns = None if object_info.sectors == 'all' or mission != "K2" else object_info.sectors
        quarters = None if object_info.sectors == 'all' or mission != "Kepler" else object_info.sectors
        tokens = sectors if sectors is not None else campaigns if campaigns is not None else quarters
        tokens = tokens if tokens is not None else "all"
        apertures = {}
        tpf_search_results = lk.search_targetpixelfile(str(mission_id))
        for tpf_search_result in tpf_search_results:
            logging.info("There is data for Mission: %s, Year %.0f, Author: %s, ExpTime: %.0f",
                         tpf_search_result.mission[0], tpf_search_result.year[0], tpf_search_result.author[0],
                         tpf_search_result.exptime[0].value)
        if object_info.apertures is None:
            lcf_search_results = lk.search_lightcurve(str(mission_id), mission=mission, cadence=cadence,
                                           sector=sectors, quarter=quarters,
                                           campaign=campaigns, author=author)
            lcf = lcf_search_results.download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR)
            tpfs = lk.search_targetpixelfile(str(mission_id), mission=mission, cadence=cadence,
                                           sector=sectors, quarter=quarters,
                                           campaign=campaigns, author=author)\
                .download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                              cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
            if lcf is None:
                raise ObjectProcessingError("The target " + str(mission_id) + " is not available for the author " + author +
                                 ", cadence " + str(cadence) + "s and sectors " + str(tokens))
            lc_data = self.extract_lc_data(lcf)
            lc = None
            matching_objects = []
            for tpf in tpfs:
                if mission_prefix == self.MISSION_ID_KEPLER:
                    sector = tpf.quarter
                elif mission_prefix == self.MISSION_ID_TESS:
                    sector = tpf.sector
                if mission_prefix == self.MISSION_ID_KEPLER_2:
                    sector = tpf.campaign
                apertures[sector] = ApertureExtractor.from_boolean_mask(tpf.pipeline_mask, tpf.column, tpf.row)
            for i in range(0, len(lcf.data)):
                if lcf.data[i].label == mission_id:
                    if lc is None:
                        lc = lcf.data[i].normalize()
                    else:
                        lc = lc.append(lcf.data[i].normalize())
                else:
                    matching_objects.append(lcf.data[i].label)
            matching_objects = set(matching_objects)
            if len(matching_objects) > 0:
                logging.warning("================================================")
                logging.warning("TICS IN THE SAME PIXEL: " + str(matching_objects))
                logging.warning("================================================")
            if lc is None:
                tokens = sectors if sectors is not None else campaigns if campaigns is not None else quarters
                tokens = tokens if tokens is not None else "all"
                raise ObjectProcessingError("The target " + str(mission_id) + " is not available for the author " + author +
                                 ", cadence " + str(cadence) + "s and sectors " + str(tokens))
            lc = lc.remove_nans()
            transits_min_count = self.__calculate_transits_min_count(len(lcf))
            if mission_prefix == self.MISSION_ID_KEPLER:
                sectors = [lcfile.quarter for lcfile in lcf]
            elif mission_prefix == self.MISSION_ID_TESS:
                sectors = [file.sector for file in lcf]
            elif mission_prefix == self.MISSION_ID_KEPLER_2:
                logging.info("Correcting K2 motion in light curve...")
                sectors = [lcfile.campaign for lcfile in lcf]
                lc = lc.to_corrector("sff").correct(windows=20)
            source = "tpf"
        else:
            logging.info("Using user apertures!")
            tpf_search_results = lk.search_targetpixelfile(str(mission_id), mission=mission, cadence=cadence,
                                             sector=sectors, quarter=quarters, campaign=campaigns,
                                             author=author)
            tpfs = tpf_search_results.download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                                                   cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
            source = "tpf"
            apertures = object_info.apertures
            lc = None
            for tpf in tpfs:
                if mission_prefix == self.MISSION_ID_KEPLER:
                    sector = tpf.quarter
                elif mission_prefix == self.MISSION_ID_TESS:
                    sector = tpf.sector
                elif mission_prefix == self.MISSION_ID_KEPLER_2:
                    sector = tpf.campaign
                boolean_aperture = ApertureExtractor.from_pixels_to_boolean_mask(apertures[sector], tpf.column, tpf.row,
                                                                         CUTOUT_SIZE, CUTOUT_SIZE)
                tpf.plot(aperture_mask=boolean_aperture, mask_color='red')
                plt.savefig(sherlock_dir + "/fov/Aperture_[" + str(sector) + "].png")
                plt.close()
                if mission_prefix == self.MISSION_ID_KEPLER:
                    corrector = lk.KeplerCBVCorrector(tpf)
                    corrector.plot_cbvs([1, 2, 3, 4, 5, 6, 7])
                    raw_lc = tpf.to_lightcurve(aperture_mask=boolean_aperture).remove_nans()
                    plt.savefig(sherlock_dir + "/Corrector_components[" + str(sector) + "].png")
                    plt.close()
                    it_lc = corrector.correct([1, 2, 3, 4, 5])
                    ax = raw_lc.plot(color='C3', label='SAP Flux', linestyle='-')
                    it_lc.plot(ax=ax, color='C2', label='CBV Corrected SAP Flux', linestyle='-')
                    plt.savefig(sherlock_dir + "/Raw_vs_CBVcorrected_lc[" + str(sector) + "].png")
                    plt.close()
                elif mission_prefix == self.MISSION_ID_KEPLER_2:
                    raw_lc = tpf.to_lightcurve(aperture_mask=boolean_aperture).remove_nans()
                    it_lc = raw_lc.to_corrector("sff").correct(windows=20)
                    ax = raw_lc.plot(color='C3', label='SAP Flux', linestyle='-')
                    it_lc.plot(ax=ax, color='C2', label='CBV Corrected SAP Flux', linestyle='-')
                    plt.savefig(sherlock_dir + "/Raw_vs_SFFcorrected_lc[" + str(sector) + "].png")
                    plt.close()
                elif mission_prefix == self.MISSION_ID_TESS:
                    temp_lc = tpf.to_lightcurve(aperture_mask=boolean_aperture)
                    where_are_NaNs = np.isnan(temp_lc.flux)
                    temp_lc = temp_lc[np.where(~where_are_NaNs)]
                    regressors = tpf.flux[np.argwhere(~where_are_NaNs), ~boolean_aperture]
                    temp_token_lc = [temp_lc[i: i + 2000] for i in range(0, len(temp_lc), 2000)]
                    regressors_token = [regressors[i: i + 2000] for i in range(0, len(regressors), 2000)]
                    it_lc = None
                    raw_it_lc = None
                    item_index = 0
                    for temp_token_lc_item in temp_token_lc:
                        regressors_token_item = regressors_token[item_index]
                        design_matrix = lk.DesignMatrix(regressors_token_item, name='regressors').pca(5).append_constant()
                        corr_lc = lk.RegressionCorrector(temp_token_lc_item).correct(design_matrix)
                        if it_lc is None:
                            it_lc = corr_lc
                            raw_it_lc = temp_token_lc_item
                        else:
                            it_lc = it_lc.append(corr_lc)
                            raw_it_lc = raw_it_lc.append(temp_token_lc_item)
                        item_index = item_index + 1
                    ax = raw_it_lc.plot(label='Raw light curve')
                    it_lc.plot(ax=ax, label='Corrected light curve')
                    plt.savefig(sherlock_dir + "/Raw_vs_DMcorrected_lc[" + str(sector) + "].png")
                    plt.close()
                if lc is None:
                    lc = it_lc.normalize()
                else:
                    lc = lc.append(it_lc.normalize())
            lc = lc.remove_nans()
            lc.plot(label="Normalized light curve")
            plt.savefig(sherlock_dir + "/Normalized_lc[" + str(sector) + "].png")
            plt.close()
            transits_min_count = self.__calculate_transits_min_count(len(tpfs))
            if mission_prefix == self.MISSION_ID_KEPLER or mission_id == self.MISSION_ID_KEPLER_2:
                sectors = [lcfile.quarter for lcfile in tpfs]
            elif mission_prefix == self.MISSION_ID_TESS:
                sectors = [file.sector for file in tpfs]
            if mission_prefix == self.MISSION_ID_KEPLER_2:
                logging.info("Correcting K2 motion in light curve...")
                sectors = [lcfile.campaign for lcfile in tpfs]
            sectors = None if sectors is None else np.unique(sectors)
            lc_data = None
        return LcBuild(lc, lc_data, star_info, transits_min_count, cadence, None, sectors, source, apertures)

    def __calculate_transits_min_count(self, len_data):
        return 1 if len_data == 1 else 2

