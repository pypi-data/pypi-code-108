import os

def get_diagprefix(name):
    """Determine prefix for path expansion based on static diag list
    The list is copied from gerrit: codac/daq/libddww8/src/islevel0diag.c
    as of 2021-08-20.
    """

    if not isinstance(name, str) or len(name) != 3:
        return None

    # order of dictionary is important due to L0 duplicates !!
    diags = {}

    diags['MH'] = [
        "MHA", "MHB", "MHC", "MHD", "MHE", "MHF", "MHG", "MHH", "MHI"
    ]
    diags['SX'] = [
        "SXA", "SXB", "SXC", "SXD", "SXF", "SXG", "SXH", "SXI", "SXJ", "SXK",
        "SXL", "SXM", "SXN", "SXO", "SXS", "SXT"
    ]
    diags['XX'] = [
        "CGF", "CTA", "CTC", "CXB", "FHA", "FHB", "FHC", "ICA", "ICS", "LIZ",
        "MSX", "NSA", "PCR", "PCS", "PRA", "PRC", "PRF", "PRD", "RFL", "RMA",
        "RMB", "RMC", "TDI", "TSX", "XPR", "XVR", "XVS"
    ]
    diags['YY'] = [
        "CEF", "DTS", "ECQ", "ECE", "ECR", "HEB", "KRF", "LSG", "NPI", "PID",
        "TSC", "UVE", "WPG", "XVT", "XVU"
    ]
    diags['L1'] = [
        "BLB", "BLC", "BPD", "CEC", "CEZ", "COF", "CPZ", "CSX", "DCR", "DCS",
        "DDS", "DTN", "ECK", "ECS", "ECV", "ENR", "EQH", "EQI", "EQR", "FPC",
        "FPG", "FPP", "GIW", "GPI", "GQH", "GQI", "HFC", "ICH", "ICP", "IDA",
        "INJ", "IOB", "JCU", "JFE", "JOU", "JOW", "SPC", "MAE", "MAN", "MAP",
        "MAR", "MBI", "MDO", "MNO", "MOD", "MRI", "MSR", "NEO", "NIS", "NSP",
        "OBS", "RAB", "RAP", "RMD", "RRC", "SCL", "SSX", "TBM", "TFM", "TOT",
        "TTH", "UVS", "VTA", "XRT"
    ]
    diags['L0'] = [
        "ACA", "ACB", "ACQ", "BEP", "BES", "BLK", "BLV", "BOS", "BMT", "BOF",
        "BOL", "BOS", "BRD", "BSK", "CAR", "CCD", "CDH", "CDL", "CER", "CFR",
        "CHR", "CMR", "CMT", "CNR", "COM", "CON", "COO", "COR", "CPR", "CTF",
        "CTI", "CUR", "CXR", "DCD", "DCN", "DEP", "DIN", "DIV", "DSM", "DST",
        "DTM", "DUS", "DVM", "DVS", "ECH", "ECN", "ECU", "END", "EVS", "EVU",
        "EVV", "EZC", "EZD", "FHF", "FVS", "GRA", "GRF", "GRG", "GVS", "HAM",
        "HAR", "HBD", "HDV", "HEL", "HFB", "HST", "HTS", "HVS", "HXR", "IFM",
        "ICF", "ICG", "ICL", "ICR", "ICT", "ION", "JMO", "JOH", "KMT", "KWK",
        "KWN", "KWS", "LBM", "LBO", "LEN", "LIA", "LIB", "LIC", "LIF", "LPS",
        "LSB", "LSF", "LSM", "LSW", "LVS", "MAB", "MAC", "MAD", "MAF", "MAG",
        "MAH", "MAI", "MAK", "MAM", "MAS", "MAU", "MAW", "MAX", "MAY", "MBR",
        "MER", "MGS", "MHA", "MHB", "MHC", "MHD", "MHE", "MHF", "MHG", "MHH",
        "MIC", "MIR", "MPC", "MPG", "MSE", "MSP", "MSS", "MSX", "MUM", "NIB",
        "NIK", "NIR", "NIT", "NPA", "NWB", "NWK", "OSI", "PEL", "PHA", "PHB",
        "PKG", "POT", "PPA", "PPT", "PSL", "RAD", "RAH", "RAV", "REF", "REH",
        "REI", "REV", "RFL", "RMA", "RMB", "ROE", "RSG", "RWB", "SCJ", "SIF",
        "SMF", "SPU", "SST", "TAA", "TAB", "TAC", "TAD", "TAE", "TAF", "TAG",
        "TAH", "TEO", "TER", "TET", "TLS", "UVD", "VEC", "VSS", "VTS", "ZEA",
        "ZEB", "ZEF"
    ]

    for pr in diags.keys():
        if name in diags[pr]:
            return pr

    return 'L1'

def shf(dirlist, i):
    """Check existence of shotfile in the directory given
    """
    for d in dirlist:
        if d.startswith(str(i)):
            return True
    return False

def ddcshotnr(diag, shot=99999, exp='AUGD'):
    """Py-ddcshotnr
    Gets next shotnumber of specified diagnostic from
    specified experiment smaller than the provided shotnumber

    Input:
        diag        str  Diagnostic
        shot(opt)   int  Shot number (default: 99999)
        exp(opt)    str  Exp (default: 'AUGD')
    Error codes:
        -1  :  no suitable shot found under given experiment
        -2  :  wrong input shotnumber (wrong type or out of range)
    """

    # shotnumber needs to be an int and in range, else no result
    if not isinstance(shot, int) or shot > 99999:
        return -3
    # AUGD shotfiles follow a particular path-specification
    if exp == 'AUGD':
        basepath = '/afs/ipp-garching.mpg.de/u/augd/shots/'
        prefix = get_diagprefix(diag)
        fac = 10
    else:
        # private shotfiles use a different path logic
        basepath = '/afs/ipp-garching.mpg.de/u/'+exp.lower()+'/shotfiles/'+diag+'/'
        fac = 1000

    # go backwards starting with directory of given shot
    for sr in range(int(shot/fac), -1, -1):
        fullpath = basepath + '%04d' % sr + '/' + prefix + '/' + diag \
            if exp == 'AUGD' else basepath + str(sr)
        if not os.path.isdir(fullpath):
            continue
        dirlist = os.listdir(fullpath)
        ista = 9 if exp == 'AUGD' else 999
        for i in range(ista, -1, -1):
            # if maxshot happens to be smaller than current check, skip the check
            if shot < sr*fac+i:
                continue
            fshot = '%05d' % int(sr*fac+i) if exp == 'AUGD' else '%03d' % i
            if shf(dirlist, fshot):
                return sr*fac+i

    # no result found anywhere, return -1
    return -1


def previousshot(diag, shot=99999, exp='AUGD'):
    """Alias of ddcshotnr
    """
    return ddcshotnr(diag, shot=shot, exp=exp)


if __name__ == "__main__":
    pass
