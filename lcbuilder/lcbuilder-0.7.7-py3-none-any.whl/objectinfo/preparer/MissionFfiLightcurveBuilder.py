import logging
import os
import sys
import lcbuilder.eleanor
from lcbuilder import constants
from lcbuilder.LcBuild import LcBuild
from lcbuilder.constants import CUTOUT_SIZE, LIGHTKURVE_CACHE_DIR, ELEANOR_CACHE_DIR
from lcbuilder.photometry.aperture_extractor import ApertureExtractor

sys.modules['eleanor'] = sys.modules['lcbuilder.eleanor']
import eleanor
from lcbuilder.eleanor.targetdata import TargetData
import re
import numpy as np
import pandas
import astropy.io.fits as astropy_fits
from astropy.coordinates import SkyCoord
from lcbuilder.star import starinfo
from lcbuilder.objectinfo.MissionFfiCoordsObjectInfo import MissionFfiCoordsObjectInfo
from lcbuilder.objectinfo.preparer.LightcurveBuilder import LightcurveBuilder
from lcbuilder.star.TicStarCatalog import TicStarCatalog
from astropy import units as u
import lightkurve as lk
from lightkurve.correctors import SFFCorrector
import matplotlib.pyplot as plt

class MissionFfiLightcurveBuilder(LightcurveBuilder):
    def __init__(self):
        super().__init__()
        self.star_catalog = TicStarCatalog()

    def build(self, object_info, sherlock_dir, caches_root_dir):
        mission_id = object_info.mission_id()
        sherlock_id = object_info.sherlock_id()
        logging.info("Retrieving star catalog info...")
        mission, mission_prefix, id = super().parse_object_id(mission_id)
        cadence = object_info.cadence if object_info.cadence is not None else "long"
        author = object_info.author if object_info.author is not None else self.authors[mission]
        transits_min_count = 1
        star_info = None
        if mission_prefix not in self.star_catalogs:
            raise ValueError("Wrong object id " + mission_id)
        sectors = None if object_info.sectors == 'all' or mission != "TESS" else object_info.sectors
        campaigns = None if object_info.sectors == 'all' or mission != "K2" else object_info.sectors
        quarters = None if object_info.sectors == 'all' or mission != "Kepler" else object_info.sectors
        apertures = {}
        tpf_search_results = lk.search_targetpixelfile(str(mission_id))
        for tpf_search_result in tpf_search_results:
            logging.info("There is data for Mission: %s, Year %.0f, Author: %s, ExpTime: %.0f",
                         tpf_search_result.mission[0], tpf_search_result.year[0], tpf_search_result.author[0],
                         tpf_search_result.exptime[0].value)
        if mission_prefix == self.MISSION_ID_KEPLER or mission_prefix == self.MISSION_ID_KEPLER_2:
            source = "tpf"
            lcf_search_results = lk.search_lightcurvefile(str(mission_id), mission=mission, cadence=cadence,
                                           author=author, sector=sectors, quarter=quarters,
                                           campaign=campaigns)
            lcf = lcf_search_results.download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR)
            tpfs = lk.search_targetpixelfile(str(mission_id), mission=mission, cadence=cadence,
                                           sector=sectors, quarter=quarters,
                                           campaign=campaigns, author=author)\
                .download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                              cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
            lc_data = self.extract_lc_data(lcf)
            lc = lcf.PDCSAP_FLUX.stitch().remove_nans()
            transits_min_count = 1 if len(lcf) == 0 else 2
            if mission_prefix == self.MISSION_ID_KEPLER:
                sectors = [lcfile.quarter for lcfile in lcf]
            elif mission_prefix == self.MISSION_ID_KEPLER_2:
                logging.info("Correcting K2 motion in light curve...")
                sectors = [lcfile.campaign for lcfile in lcf]
                lc = SFFCorrector(lc).correct(windows=20)
            for tpf in tpfs:
                if mission_prefix == self.MISSION_ID_KEPLER:
                    sector = tpf.quarter
                elif mission_prefix == self.MISSION_ID_KEPLER_2:
                    sector = tpf.campaign
                apertures[sector] = ApertureExtractor.from_boolean_mask(tpf.pipeline_mask, tpf.column, tpf.row)
            star_info = starinfo.StarInfo(sherlock_id, *self.star_catalogs[mission_prefix].catalog_info(id))
        else:
            source = "eleanor"
            if isinstance(object_info, MissionFfiCoordsObjectInfo):
                coords = SkyCoord(ra=object_info.ra, dec=object_info.dec, unit=(u.deg, u.deg))
                star = eleanor.source.multi_sectors(coords=coords, sectors=object_info.sectors,
                                                    post_dir=caches_root_dir + ELEANOR_CACHE_DIR,
                                                    metadata_path=caches_root_dir + ELEANOR_CACHE_DIR)
            else:
                object_id_parsed = re.search(super().NUMBERS_REGEX, object_info.id)
                object_id_parsed = object_info.id[object_id_parsed.regs[0][0]:object_id_parsed.regs[0][1]]
                star = eleanor.multi_sectors(tic=object_id_parsed, sectors=object_info.sectors,
                                             post_dir=caches_root_dir + ELEANOR_CACHE_DIR,
                                             metadata_path=caches_root_dir + ELEANOR_CACHE_DIR)
            if star is None:
                raise ValueError("No data for this object")
            if star[0].tic:
                # TODO FIX star info objectid
                logging.info("Assotiated TIC is " + str(star[0].tic))
                tpfs = lk.search_targetpixelfile("TIC " + str(star[0].tic), mission="TESS", cadence=cadence,
                                                 sector=sectors, quarter=quarters,
                                                 campaign=campaigns, author="TESS-SPOC") \
                    .download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                                  cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
                star_info = starinfo.StarInfo(object_info.sherlock_id(), *self.star_catalog.catalog_info(int(star[0].tic)))
            data = []
            for s in star:
                datum = TargetData(s, height=CUTOUT_SIZE, width=CUTOUT_SIZE, do_pca=True)
                data.append(datum)
                for tpf in tpfs:
                    if tpf.sector == s.sector:
                        apertures[s.sector] = ApertureExtractor.from_boolean_mask(datum.aperture.astype(bool),
                                                                                  tpf.column, tpf.row)
            quality_bitmask = np.bitwise_and(data[0].quality.astype(int), 175)
            lc_data = self.extract_eleanor_lc_data(data)
            lc = data[0].to_lightkurve(data[0].__dict__[object_info.eleanor_corr_flux],
                                       quality_mask=quality_bitmask).remove_nans().flatten()
            sectors = [datum.source_info.sector for datum in data]
            if len(data) > 1:
                for datum in data[1:]:
                    quality_bitmask = np.bitwise_and(datum.quality, 175)
                    lc = lc.append(datum.to_lightkurve(datum.pca_flux, quality_mask=quality_bitmask).remove_nans()
                                   .flatten())
                transits_min_count = 2
        return LcBuild(lc, lc_data, star_info, transits_min_count, cadence, None, sectors, source, apertures)

    def extract_eleanor_lc_data(selfself, eleanor_data):
        time = []
        flux = []
        flux_err = []
        background_flux = []
        quality = []
        centroids_x = []
        centroids_y = []
        motion_x = []
        motion_y = []
        [time.append(data.time) for data in eleanor_data]
        [flux.append(data.pca_flux) for data in eleanor_data]
        [flux_err.append(data.flux_err) for data in eleanor_data]
        [background_flux.append(data.flux_bkg) for data in eleanor_data]
        try:
            [quality.append(data.quality) for data in eleanor_data]
        except KeyError:
            logging.info("QUALITY info is not available.")
            [quality.append(np.full(len(data.time), np.nan)) for data in eleanor_data]
        [centroids_x.append(data.centroid_xs - data.cen_x) for data in eleanor_data]
        [centroids_y.append(data.centroid_ys - data.cen_y) for data in eleanor_data]
        [motion_x.append(data.x_com) for data in eleanor_data]
        [motion_y.append(data.y_com) for data in eleanor_data]
        time = np.concatenate(time)
        flux = np.concatenate(flux)
        flux_err = np.concatenate(flux_err)
        background_flux = np.concatenate(background_flux)
        quality = np.concatenate(quality)
        centroids_x = np.concatenate(centroids_x)
        centroids_y = np.concatenate(centroids_y)
        motion_x = np.concatenate(motion_x)
        motion_y = np.concatenate(motion_y)
        lc_data = pandas.DataFrame(columns=['time', 'flux', 'flux_err', 'background_flux', 'quality', 'centroids_x',
                                            'centroids_y', 'motion_x', 'motion_y'])
        lc_data['time'] = time
        lc_data['flux'] = flux
        lc_data['flux_err'] = flux_err
        lc_data['background_flux'] = background_flux
        lc_data['quality'] = quality
        lc_data['centroids_x'] = centroids_x
        lc_data['centroids_y'] = centroids_y
        lc_data['motion_x'] = motion_x
        lc_data['motion_y'] = motion_y
        return lc_data

    def __plot_tpf(self, tpf, sector, aperture, dir):
        dir = dir + "/fov/"
        if not os.path.exists(dir):
            os.mkdir(dir)
        tpf.plot_pixels(aperture_mask=aperture)
        plt.savefig(dir + "/Flux_pixels[" + str(sector) + "].png")
        plt.close()