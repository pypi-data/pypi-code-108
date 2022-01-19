import yaml
import pkg_resources

s122_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/SPEC_0122_mapping.yml')
with open(s122_file, 'rb') as f:
    S122 = yaml.safe_load(f)

constants_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/constants.yml')
with open(constants_file, 'rb') as f:
    CONSTANTS = yaml.safe_load(f)

def load_visp_keywords() -> None:
    """Load the ViSP Instrument keywords from the ViSP Pipeline into the S122 dictionary
    """

    from ViSP_Pipeline.data import S122 as ViSP_S122

    PAC_keys = list(S122.keys())  # I think this is faster than generating it for every visp key?
    for k in ViSP_S122.keys():
        if k not in PAC_keys:
            S122['ViSP_{}'.format(k)] = ViSP_S122[k]

def load_cryo_keywords() -> None:
    """Load the CryoNIRSP Instrument keywords into the S122 dictionary
    """

    from CryoNIRSP_Pipeline.data import S122 as Cryo_S122

    PAC_keys = list(S122.keys())
    for k in Cryo_S122.keys():
        if k not in PAC_keys:
            S122['CRSP_{}'.format(k)] = Cryo_S122[k]

def load_dlnirsp_keywords() -> None:
    """Load the DLNIRSP Instrument keywords into the S122 dictionary
    """

    from DLNIRSP_Pipeline.data import S122 as DL_S122

    PAC_keys = list(S122.keys())
    for k in DL_S122.keys():
        if k not in PAC_keys:
            S122['DLN_{}'.format(k)] = DL_S122[k]
