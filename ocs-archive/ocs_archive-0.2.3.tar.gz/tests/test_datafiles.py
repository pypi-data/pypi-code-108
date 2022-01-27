import unittest
from unittest.mock import patch
import os
from datetime import timedelta
from dateutil.parser import parse

import responses

from ocs_archive.input.file import File, DataFile, EmptyFile, FileSpecificationException
from ocs_archive.input.fitsfile import FitsFile
from ocs_archive.input.filefactory import FileFactory
from ocs_archive.input.lcofitsfile import LcoFitsFile
from ocs_archive.input.tarwithfitsfile import TarWithFitsFile
from ocs_archive.settings import settings


FITS_PATH = os.path.join(
    os.path.dirname(__file__),
    'test_files/fits/'
)


class TestDataFile(unittest.TestCase):
    def setUp(self):
        self.file = EmptyFile('test.file')

    def test_dayobs_missing(self):
        headers = {'DATE-OBS': '2020-01-31T20:09:56.956'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual('20200131', header_data.get_observation_day())

    @patch('ocs_archive.input.file.settings.PUBLIC_PROPOSALS', ('EPOTHING',))
    def test_public_date_public_file(self):
        headers = {
            'PROPID': 'EPOTHING',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), header_data.get_observation_date())

    @patch('ocs_archive.input.file.settings.DAYS_UNTIL_PUBLIC', 365)
    def test_public_date_normal_file(self):
        headers = {
            'PROPID': 'LCO2015',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        public_date = (parse(header_data.get_observation_date()) + timedelta(days=settings.DAYS_UNTIL_PUBLIC)).isoformat()
        self.assertEqual(header_data.get_public_date(), public_date)

    @patch('ocs_archive.input.file.settings.PRIVATE_FILE_TYPES', ('-t00',))
    def test_public_date_private_t00(self):
        tst_file = EmptyFile('whatever-t00.file')
        headers = {
            'PROPID': 'LCO2015',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        data_file = DataFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), '3014-08-03T00:00:00+00:00')

    @patch('ocs_archive.input.file.settings.PRIVATE_FILE_TYPES', ('-x00',))
    def test_public_date_private_x00(self):
        tst_file = EmptyFile('whatever-x00.file')
        headers = {
            'PROPID': 'LCO2015',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        data_file = DataFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), '3014-08-03T00:00:00+00:00')

    @patch('ocs_archive.input.file.settings.PRIVATE_PROPOSALS', ('LCOEngineering',))
    def test_public_date_private_LCOEngineering(self):
        headers = {
            'PROPID': 'LCOEngineering',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), '3014-08-03T00:00:00+00:00')

    def test_public_date_exists(self):
        headers = {
            'PROPID': 'LCO2015',
            'DATE-OBS': '2099-04-01T00:00:00+00:00',
            'L1PUBDAT': '2099-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), '2099-04-01T00:00:00+00:00')

    @patch('ocs_archive.input.file.settings.PUBLIC_PROPOSALS', ('EPOTHING',))
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_BASE_URL', 'https://obs.portal/')
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_API_TOKEN', 'asdf')
    @patch('ocs_archive.input.file.settings.PRIVATE_PROPOSAL_TAGS', ('private',))
    @responses.activate
    def test_private_in_portal_overrides_public_environment_variable(self):
        headers = {
            'PROPID': 'EPOTHING',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        responses.add(responses.GET, 'https://obs.portal/api/proposals/EPOTHING',
                      json={'tags': ['private']})
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), '3014-08-03T00:00:00+00:00')

    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_BASE_URL', 'https://obs.portal/')
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_API_TOKEN', 'asdf')
    @patch('ocs_archive.input.file.settings.PUBLIC_PROPOSAL_TAGS', ('public',))
    @responses.activate
    def test_public_in_portal(self):
        headers = {
            'PROPID': 'EPOTHING',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        responses.add(responses.GET, 'https://obs.portal/api/proposals/EPOTHING',
                      json={'tags': ['public']})
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), header_data.get_observation_date())

    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_BASE_URL', 'https://obs.portal/')
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_API_TOKEN', 'asdf')
    @patch('ocs_archive.input.file.settings.PRIVATE_PROPOSAL_TAGS', ('private',))
    @responses.activate
    def test_private_in_portal(self):
        headers = {
            'PROPID': 'MyPrivateProposal',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        responses.add(responses.GET, 'https://obs.portal/api/proposals/MyPrivateProposal',
                      json={'tags': ['private']})
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), '3014-08-03T00:00:00+00:00')

    @patch('ocs_archive.input.file.settings.PUBLIC_PROPOSALS', ('EPOTHING',))
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_BASE_URL', 'https://obs.portal/')
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_API_TOKEN', 'asdf')
    @patch('ocs_archive.input.file.settings.PRIVATE_PROPOSAL_TAGS', ('private',))
    @responses.activate
    def test_no_data_privacy_tags_falls_back_to_environment_variables(self):
        headers = {
            'PROPID': 'EPOTHING',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        responses.add(responses.GET, 'https://obs.portal/api/proposals/EPOTHING',
                      json={'tags': ['foo']})
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), header_data.get_observation_date())

    @patch('ocs_archive.input.file.settings.PUBLIC_PROPOSALS', ('MYPUBLICPROP',))
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_BASE_URL', 'https://obs.portal/')
    @patch('ocs_archive.input.file.settings.OBSERVATION_PORTAL_API_TOKEN', 'asdf')
    @patch('ocs_archive.input.file.settings.PRIVATE_PROPOSAL_TAGS', ('private',))
    @responses.activate
    def test_500_error_fallback_to_environment_variable(self):
        headers = {
            'PROPID': 'MYPUBLICPROP',
            'DATE-OBS': '2016-04-01T00:00:00+00:00',
            'OBSTYPE': 'EXPOSE'
        }
        responses.add(responses.GET, 'https://obs.portal/api/proposals/MYPUBLICPROP',
                      status=500)
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_public_date(), header_data.get_observation_date())

    def test_get_wcs_corners_from_dict_for_ccd(self):
        headers = {'CD1_1': 6, 'CD1_2': 2, 'CD2_1': 3, 'CD2_2': 4, 'NAXIS1': 1000, 'NAXIS2': 1100, 'DATE-OBS': '2015-02-19T13:56:05.261'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        result = data_file.get_wcs_corners()
        self.assertIsNotNone(result)
        self.assertIn('type', result)
        self.assertIn('coordinates', result)

    def test_get_wcs_corners_from_dict_for_ccd_with_naxis3(self):
        headers = {'CD1_1': 6, 'CD1_2': 2, 'CD2_1': 3, 'CD2_2': 4, 'NAXIS1': 1000, 'NAXIS2': 1100, 'NAXIS3': 2000, 'DATE-OBS': '2015-02-19T13:56:05.261'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        result = data_file.get_wcs_corners()
        self.assertIsNone(result)

    def test_get_wcs_corners_from_dict_for_ccd_missing_headers(self):
        headers = {'CD1_1': 1, 'CD1_2': 2, 'CD2_1': 3, 'NAXIS1': 1000, 'NAXIS2': 1100, 'DATE-OBS': '2015-02-19T13:56:05.261'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        result = data_file.get_wcs_corners()
        self.assertIsNone(result)

    def test_get_wcs_corners_from_dict_for_nres(self):
        headers = {'RADIUS': 5, 'RA': 110, 'DEC': 30, 'DATE-OBS': '2015-02-19T13:56:05.261'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        result = data_file.get_wcs_corners()
        self.assertIn('type', result)
        self.assertIn('coordinates', result)

    def test_get_wcs_corners_from_dict_for_nres_sexagesimal(self):
        headers = {'RADIUS': 5, 'RA': '11:45:44.212',  'DEC': '-80:01:44.56', 'DATE-OBS': '2015-02-19T13:56:05.261'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        result = data_file.get_wcs_corners()
        self.assertIn('type', result)
        self.assertIn('coordinates', result)

    def test_get_wcs_corners_from_dict_for_nres_missing_headers(self):
        headers = {'RADIUS': 5, 'RA': '', 'DATE-OBS': '2015-02-19T13:56:05.261'}
        data_file = DataFile(self.file, file_metadata=headers, required_headers=[])
        result = data_file.get_wcs_corners()
        self.assertIsNone(result)

    def test_pdf_obstype_basename_to_filestore_path(self):
        headers = {'SITEID': 'cpt', 'INSTRUME': 'nres03',
                     'DATE-OBS': '2015-02-19T13:56:05.261', 'OBSTYPE': 'EXPOSE', 'RLEVEL': 92}
        cpt_file = EmptyFile('cptnrs03-fa13-20150219-0001-e92-summary.pdf')
        data_file = DataFile(cpt_file, file_metadata=headers, required_headers=[])
        self.assertEqual(
            'cpt/nres03/20150219/processed/cptnrs03-fa13-20150219-0001-e92-summary.pdf',
            data_file.get_filestore_path()
        )

    def test_base_extension_to_content_type(self):
        data_file = DataFile(self.file, file_metadata={'DATE-OBS': '2015-02-19T13:56:05.261'}, required_headers=[])
        self.assertEqual('', data_file.get_filestore_content_type())


class TestFits(unittest.TestCase):
    def setUp(self):
        self.fileobj = open(os.path.join(
            FITS_PATH,
            'coj1m011-kb05-20150219-0125-e90.fits.fz'), 'rb'
        )
        self.file = File(self.fileobj, 'coj1m011-kb05-20150219-0125-e90.fits.fz')
        self.required_headers = ('DATE-OBS', 'PROPID')

    def tearDown(self):
        self.fileobj.close()

    def test_null_values(self):
        headers = {
            'OBJECT': 'UNKNOWN',
            'PROPID': 'N/A',
            'BLKUID': 'N/A',
            'INSTRUME': 'fl03',
            'REQNUM': 'UNSPECIFIED'
        }
        data_file = FitsFile(self.file, file_metadata=headers, required_headers=self.required_headers)
        header_data = data_file.get_header_data()
        self.assertEqual('', header_data.get_target_name())
        self.assertEqual('', header_data.get_proposal_id())
        self.assertIsNone(header_data.get_observation_id())
        self.assertEqual('fl03', header_data.get_instrument_id())
        self.assertIsNone(header_data.get_request_id())

    def test_remove_blacklist(self):
        headers = {
            'FOO': 'BAR',
            'BAZ': 'BAM',
        }
        data_file = FitsFile(self.file, file_metadata=headers, blacklist_headers=['FOO'], required_headers=self.required_headers)
        header_data = data_file.get_header_data()
        self.assertNotIn('FOO', header_data.get_headers().keys())
        self.assertIn('BAZ', header_data.get_headers().keys())

    def test_fits_and_fpac_have_same_frame_data_generated(self):
        data_file = FitsFile(self.file, file_metadata={}, required_headers=self.required_headers)
        frame_data_fpac = data_file.get_header_data().get_archive_frame_data()

        with open(os.path.join(FITS_PATH, 'coj1m011-kb05-20150219-0125-e90.fits'), 'rb') as fp:
            open_file = File(fp, 'coj1m011-kb05-20150219-0125-e90.fits')
            data_file = FitsFile(open_file, file_metadata={}, required_headers=self.required_headers)
            frame_data = data_file.get_header_data().get_archive_frame_data()

        self.assertDictEqual(frame_data, frame_data_fpac)

    @patch('ocs_archive.settings.settings.RELATED_FRAME_KEYS', ('L1IDBIAS', 'L1IDFLAT', 'L1IDDARK', 'TARFILE', 'GUIDETAR'))
    def test_normalize_related(self):
        headers = {
            'L1IDBIAS': 'bias_kb78_20151110_bin2x2',
            'L1IDFLAT': 'flat_kb78_20151106_SKYFLAT_bin2x2_V',
            'L1IDDARK': 'dark_kb78_20151110_bin2x2',
            'TARFILE': 'KEY2014A-002_0000476040_ftn_20160108_57396.tar.gz',
            'GUIDETAR': 'somekindoftarball.tar.gz'
        }
        data_file = FitsFile(self.file, file_metadata=headers, blacklist_headers=['FOO'], required_headers=self.required_headers)
        header_data = data_file.get_header_data()
        related_frame_keys = header_data.get_related_frame_keys()
        for key in related_frame_keys:
            self.assertFalse(os.path.splitext(header_data.get_headers()[key])[1])

    def test_basename_to_filestore_path(self):
        headers = {'SITEID': 'coj', 'INSTRUME': 'kb05', 'OBSTYPE': 'EXPOSE', 'RLEVEL': 0}
        data_file = FitsFile(self.file, file_metadata=headers, required_headers=self.required_headers)
        self.assertEqual(
            'coj/kb05/20150219/raw/coj1m011-kb05-20150219-0125-e90.fits.fz',
            data_file.get_filestore_path()
        )

    def test_processed_basename_to_filestore_path(self):
        headers = {'SITEID': 'coj', 'INSTRUME': 'kb05', 'OBSTYPE': 'EXPOSE', 'RLEVEL': 91}
        data_file = FitsFile(self.file, file_metadata=headers, required_headers=self.required_headers)
        self.assertEqual(
            'coj/kb05/20150219/processed/coj1m011-kb05-20150219-0125-e90.fits.fz',
            data_file.get_filestore_path()
        )

    def test_fits_extension_to_content_type(self):
        data_file = FitsFile(self.file, file_metadata={}, required_headers=self.required_headers)
        self.assertEqual('image/fits', data_file.get_filestore_content_type())


class TestLcoFits(unittest.TestCase):
    def setUp(self):
        self.fileobj = open(os.path.join(
            FITS_PATH,
            'coj1m011-kb05-20150219-0125-e90.fits.fz'), 'rb'
        )
        self.file = File(self.fileobj, 'coj1m011-kb05-20150219-0125-e90.fits.fz')
        self.required_headers = ('DATE-OBS', 'PROPID')

    def tearDown(self):
        self.fileobj.close()

    def test_rlevel_present(self):
        headers = {'RLEVEL': 91}
        data_file = LcoFitsFile(self.file, file_metadata=headers, required_headers=self.required_headers)
        header_data = data_file.get_header_data()
        self.assertEqual(91, header_data.get_reduction_level())

    def test_rlevel_missing(self):
        headers = {}
        data_file = LcoFitsFile(self.file, file_metadata=headers, required_headers=self.required_headers)
        header_data = data_file.get_header_data()
        self.assertEqual(90, header_data.get_reduction_level())

    def test_reduction_level(self):
        headers = {}
        data_file = LcoFitsFile(self.file, file_metadata=headers, required_headers=self.required_headers)
        header_data = data_file.get_header_data()
        self.assertEqual(header_data.get_reduction_level(), 90)

        with open(os.path.join(FITS_PATH, 'cpt1m012-fl10-20151216-0073-e00.fits.fz'), 'rb') as fp:
            e00_file = File(fp, 'cpt1m012-fl10-20151216-0073-e00.fits.fz')
            data_file = LcoFitsFile(e00_file, file_metadata=headers, required_headers=self.required_headers)
            header_data = data_file.get_header_data()
            self.assertEqual(header_data.get_reduction_level(), 0)

        with open(os.path.join(FITS_PATH, 'cpt1m010-kb70-20151219-0073-e10.fits.fz'), 'rb') as fp:
            e10_file = File(fp, 'cpt1m010-kb70-20151219-0073-e10.fits.fz')
            data_file = LcoFitsFile(e10_file, file_metadata=headers, required_headers=self.required_headers)
            header_data = data_file.get_header_data()
            self.assertEqual(header_data.get_reduction_level(), 10)

    def test_repair_obstype(self):
        tst_file = EmptyFile('tst1m005-en20-20150511-1234-e00.fits.fz')
        headers = {'OBSTYPE': 'UNKNOWN', 'PROPID': 'Test Proposal', 'DATE-OBS': '2015-05-11T13:56:05.261'}
        data_file = LcoFitsFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual('SPECTRUM', header_data.get_configuration_type())

        tst_file = EmptyFile('tst1m005-en20-20150511-bias-bin1x1.fits.fz')
        headers = {'OBSTYPE': 'UNKNOWN', 'PROPID': 'Test Proposal', 'DATE-OBS': '2015-05-11T13:56:05.261'}
        data_file = LcoFitsFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual('BIAS', header_data.get_configuration_type())

        tst_file = EmptyFile('tstnrs1m005-fa20-20150511-1234-e00.fits.fz')
        headers = {'OBSTYPE': 'UNKNOWN', 'ENCID': 'igla', 'PROPID': 'Test Proposal', 'DATE-OBS': '2015-05-11T13:56:05.261'}
        data_file = LcoFitsFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual('TARGET', header_data.get_configuration_type())

        tst_file = EmptyFile('tst1m005-fa10-20150511-1234-e00.fits.fz')
        headers = {'OBSTYPE': 'UNKNOWN', 'PROPID': 'Test Proposal', 'DATE-OBS': '2015-05-11T13:56:05.261'}
        data_file = LcoFitsFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual('EXPOSE', header_data.get_configuration_type())

    def test_catalog_file(self):
        tst_file = EmptyFile('something-e90_cat.fits.fz')
        headers = {'PROPID': 'Test Proposal', 'DATE-OBS': '2015-05-11T13:56:05.261'}
        data_file = LcoFitsFile(tst_file, file_metadata=headers, required_headers=[])
        header_data = data_file.get_header_data()
        self.assertEqual('something-e90', header_data.get_headers()['L1IDCAT'])

    def test_bpm_obstype_basename_to_filestore_path(self):
        headers = {'SITEID': 'coj', 'INSTRUME': 'kb05', 'DATE-OBS': '2015-02-19T13:56:05.261', 'OBSTYPE': 'BPM', 'PROPID': 'Test Proposal'}
        coj_file = EmptyFile('coj1m011-kb05-20150219-0125-e90.fits.fz')
        data_file = LcoFitsFile(coj_file, file_metadata=headers, required_headers=[])
        self.assertEqual(
            'coj/kb05/bpm/coj1m011-kb05-20150219-0125-e90.fits.fz',
            data_file.get_filestore_path()
        )

    def test_bpm_filename_basename_to_filestore_path(self):
        headers = {'SITEID': 'coj', 'INSTRUME': 'kb05', 'DATE-OBS': '2015-02-19T13:56:05.261', 'OBSTYPE': 'EXPOSE', 'PROPID': 'Test Proposal'}
        coj_file = EmptyFile('coj1m011-kb05-20150219-0125-bpm.fits.fz')
        data_file = LcoFitsFile(coj_file, file_metadata=headers, required_headers=[])
        self.assertEqual(
            'coj/kb05/bpm/coj1m011-kb05-20150219-0125-bpm.fits.fz',
            data_file.get_filestore_path()
        )


class TestTarFits(unittest.TestCase):
    def setUp(self):
        self.fileobj = open(os.path.join(
            FITS_PATH,
            'lscnrs01-fl09-20171109-0049-e91.tar.gz'), 'rb'
        )
        self.file = File(self.fileobj, 'lscnrs01-fl09-20171109-0049-e91.tar.gz')

    def tearDown(self):
        self.fileobj.close()
    
    def test_tar_fits_extension_to_content_type(self):
        headers = {'PROPID': 'TestProposal', 'DATE-OBS': '2017-11-09T13:56:05.261'}
        data_file = TarWithFitsFile(self.file, file_metadata=headers, required_headers=())
        self.assertEqual('application/x-tar', data_file.get_filestore_content_type())

    def test_tar_fits_pulls_out_headers(self):
        data_file = TarWithFitsFile(self.file, file_metadata={}, required_headers=('DATE-OBS', 'PROPID'))
        header_data = data_file.get_header_data()
        self.assertIsNotNone(header_data.get_observation_date())
        self.assertIsNotNone(header_data.get_proposal_id())


class TestFileFactory(unittest.TestCase):
    @patch('ocs_archive.settings.settings.FILETYPE_MAPPING_OVERRIDES', {'.fake.fits': 'ocs_archive.input.fitsfile.FitsFile', '.superpdf': 'ocs_archive.input.file.DataFile'})
    def test_file_factory_uses_settings_to_extend_mapping(self):
        fake_fits_file = EmptyFile('fake_fits_file.fake.fits')
        fake_fits_file_class = FileFactory.get_datafile_class_for_extension(fake_fits_file.extension)
        self.assertIs(fake_fits_file_class, FitsFile)

        fits_file = EmptyFile('fits_file.fits')
        fits_file_class = FileFactory.get_datafile_class_for_extension(fits_file.extension)
        self.assertIs(fits_file_class, FitsFile)

        super_pdf_file = EmptyFile('super_pdf_file.superpdf')
        super_pdf_class = FileFactory.get_datafile_class_for_extension(super_pdf_file.extension)
        self.assertIs(super_pdf_class, DataFile)

    @patch('ocs_archive.settings.settings.FILETYPE_MAPPING_OVERRIDES', {'.fits': 'ocs_archive.input.lcofitsfile.LcoFitsFile'})
    def test_file_factory_uses_settings_to_override_mapping(self):
        fits_file = EmptyFile('fits_file.fits')
        fits_file_class = FileFactory.get_datafile_class_for_extension(fits_file.extension)
        self.assertIs(fits_file_class, LcoFitsFile)

    def test_file_factory_raises_exception_for_nonexistent_extension(self):
        fake_file = EmptyFile('fits_file.fake')
        with self.assertRaises(FileSpecificationException) as fse:
            FileFactory.get_datafile_class_for_extension(fake_file.extension)
        self.assertEqual('file extension .fake is not a currently supported file type', str(fse.exception))

    @patch('ocs_archive.settings.settings.FILETYPE_MAPPING_OVERRIDES', {'.fits': 'this.module.is.fake.fitsfile.FitsFile'})
    def test_file_factory_raises_exception_for_nonexistent_module_override(self):
        fits_file = EmptyFile('fits_file.fits')
        with self.assertRaises(FileSpecificationException) as fse:
            FileFactory.get_datafile_class_for_extension(fits_file.extension)
        self.assertEqual('module this.module.is.fake.fitsfile was not found. Please ensure the class path is correct', str(fse.exception))

    @patch('ocs_archive.settings.settings.FILETYPE_MAPPING_OVERRIDES', {'.fits': 'ocs_archive.input.fitsfile.FakeFitsFile'})
    def test_file_factory_raises_exception_for_nonexistent_class_override(self):
        fits_file = EmptyFile('fits_file.fits')
        with self.assertRaises(FileSpecificationException) as fse:
            FileFactory.get_datafile_class_for_extension(fits_file.extension)
        self.assertEqual('class FakeFitsFile does not exist within module ocs_archive.input.fitsfile. Please ensure the class path is correct', str(fse.exception))

    @patch('ocs_archive.settings.settings.FILETYPE_MAPPING_OVERRIDES', {'.fits': 'ocs_archive.input.file.File'})
    def test_file_factory_raises_exception_for_wrong_subclass_override(self):
        fits_file = EmptyFile('fits_file.fits')
        with self.assertRaises(FileSpecificationException) as fse:
            FileFactory.get_datafile_class_for_extension(fits_file.extension)
        self.assertEqual('class File must be a subclass of the ocs_archive.input.file.DataFile class', str(fse.exception))
