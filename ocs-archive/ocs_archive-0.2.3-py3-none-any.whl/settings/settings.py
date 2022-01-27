import os
import ast


def get_tuple_from_environment(variable_name, default):
    return tuple(os.getenv(variable_name, default).strip(',').replace(' ', '').split(','))


# AWS Credentials and defaults
BUCKET = os.getenv('BUCKET', 'testbucket')
S3_SIGNATURE_VERSION = os.getenv('S3_SIGNATURE_VERSION', 's3v4')
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'https://s3.us-west-2.amazonaws.com')
S3_DAYS_TO_IA_STORAGE = int(os.getenv('S3_DAYS_TO_IA_STORAGE', 60))

# Used to specify which type of File Storage to use
FILESTORE_TYPE = os.getenv('FILESTORE_TYPE', 'dummy')

# Used for local File system storage backend as the root storage directory
FILESYSTEM_STORAGE_ROOT_DIR = os.getenv('FILESYSTEM_STORAGE_ROOT_DIR', '')
FILESYSTEM_STORAGE_BASE_URL = os.getenv('FILESYSTEM_STORAGE_BASE_URL', 'http://0.0.0.0/')

# Used to specify the location and authentication details for the Observation Portal
OBSERVATION_PORTAL_BASE_URL = os.getenv('OBSERVATION_PORTAL_BASE_URL')
OBSERVATION_PORTAL_API_TOKEN = os.getenv('OBSERVATION_PORTAL_API_TOKEN')

# Used to specify the proposal tags that denote whether the data from a proposal should be public or private
PRIVATE_PROPOSAL_TAGS = get_tuple_from_environment('PRIVATE_PROPOSAL_TAGS', 'private,internal')
PUBLIC_PROPOSAL_TAGS = get_tuple_from_environment('PUBLIC_PROPOSAL_TAGS', 'public')

# Used to override and update mapping of file extensions to DataFile subclass class dotpath
# The expected format is a string literal representation of a dictionary, mapping extensions
# to Datafile subclass absolute dotpath
FILETYPE_MAPPING_OVERRIDES = ast.literal_eval(os.getenv('FILETYPE_MAPPING_OVERRIDES', "{}"))

# Files we wish to ignore
IGNORED_CHARS = get_tuple_from_environment('IGNORED_CHARS', '-l00,tstnrs')

# Fits headers we don't want to ingest
HEADER_BLACKLIST = get_tuple_from_environment('HEADER_BLACKLIST', 'HISTORY,COMMENT')

# Fits headers that must be present
REQUIRED_HEADERS = get_tuple_from_environment('REQUIRED_HEADERS', 'PROPID,DATE-OBS,INSTRUME,SITEID,TELID,OBSTYPE,BLKUID')

# Possible Null values in headers. These will be normalized to none / empty
NULL_HEADER_VALUES = get_tuple_from_environment('NULL_HEADER_VALUES', 'N/A,UNSPECIFIED,UNKNOWN')

# Calibration observation types (OBSTYPE)
CALIBRATION_TYPES = get_tuple_from_environment('CALIBRATION_TYPES', 'BIAS,DARK,SKYFLAT,EXPERIMENTAL')

# Proposals including these strings will be considered public data
PUBLIC_PROPOSALS = get_tuple_from_environment('PUBLIC_PROPOSALS', 'EPO,calib,standard,pointing')

# Days until a private proposals data becomes public, measured from observation date
DAYS_UNTIL_PUBLIC = int(os.getenv('DAYS_UNTIL_PUBLIC', 365))

# Proposals including these strings will be considered private data (L1PUBDATE far out)
PRIVATE_PROPOSALS = get_tuple_from_environment('PRIVATE_PROPOSALS', 'LCOEngineering')

# File types which are private (L1PUBDATE far out)
PRIVATE_FILE_TYPES = get_tuple_from_environment('PRIVATE_FILE_TYPES', '-t00,-x00')

# Data File related settings (default keys, related frames, etc.)
OBSERVATION_DATE_KEY = os.getenv('OBSERVATION_DATE_KEY', 'DATE-OBS')
OBSERVATION_DAY_KEY = os.getenv('OBSERVATION_DAY_KEY', 'DAY-OBS')
OBSERVATION_END_TIME_KEY = os.getenv('OBSERVATION_END_TIME_KEY', 'UTSTOP')
REDUCTION_LEVEL_KEY = os.getenv('REDUCTION_LEVEL_KEY', 'RLEVEL')
EXPOSURE_TIME_KEY = os.getenv('EXPOSURE_TIME_KEY', 'EXPTIME')
INSTRUMENT_ID_KEY = os.getenv('INSTRUMENT_ID_KEY', 'INSTRUME')
SITE_ID_KEY = os.getenv('SITE_ID_KEY', 'SITEID')
TELESCOPE_ID_KEY = os.getenv('TELESCOPE_ID_KEY', 'TELID')
OBSERVATION_ID_KEY = os.getenv('OBSERVATION_ID_KEY', 'BLKUID')
CONFIGURATION_ID_KEY = os.getenv('CONFIGURATION_ID_KEY', 'MOLUID')
PRIMARY_OPTICAL_ELEMENT_KEY = os.getenv('PRIMARY_OPTICAL_ELEMENT_KEY', 'FILTER')
TARGET_NAME_KEY = os.getenv('TARGET_NAME_KEY', 'OBJECT')
REQUEST_ID_KEY = os.getenv('REQUEST_ID_KEY', 'REQNUM')
REQUESTGROUP_ID_KEY = os.getenv('REQUESTGROUP_ID_KEY', 'TRACKNUM')
CONFIGURATION_TYPE_KEY = os.getenv('CONFIGURATION_TYPE_KEY', 'OBSTYPE')
PROPOSAL_ID_KEY = os.getenv('PROPOSAL_ID_KEY', 'PROPID')
CATALOG_TARGET_FRAME_KEY = os.getenv('CATALOG_TARGET_FRAME_KEY', 'L1IDCAT')
PUBLIC_DATE_KEY = os.getenv('PUBLIC_DATE_KEY', 'L1PUBDAT')
RELATED_FRAME_KEYS = get_tuple_from_environment(
    'RELATED_FRAME_KEYS',
    'L1IDBIAS,L1IDDARK,L1IDFLAT,L1IDSHUT,L1IDMASK,L1IDFRNG,L1IDCAT,L1IDARC,L1ID1D,L1ID2D,L1IDSUM,TARFILE,ORIGNAME,ARCFILE,FLATFILE,GUIDETAR'
)
# Either Radius, Ra, Dec or NAXIS1/2 and CD1/2_1/2 need to be set to support
# automatic extraction of wcs polygon
RADIUS_KEY = os.getenv('RADIUS_KEY', 'RADIUS')
RA_KEY = os.getenv('RA_KEY', 'RA')
DEC_KEY = os.getenv('DEC_KEY', 'DEC')
