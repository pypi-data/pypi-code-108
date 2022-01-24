import os
import numpy as np
from tomoscan.io import HDF5File
from silx.third_party.EdfFile import EdfFile
from ..io.utils import get_first_hdf5_entry
from .utils import parse_params_values
from .cli_configs import GenerateInfoConfig


edf_header_hdf5_path = {
    # EDF Header
    "count_time": "/technique/scan/exposure_time", # ms in HDF5
    "date": "/start_time",
    "energy": "/technique/scan/energy",
    "flip": "/technique/detector/flipping", # [x, y] in HDF5
    "motors": "/instrument/positioners",
    "optic_used": "/technique/optic/magnification",
}

info_hdf5_path = {
    "Energy": "/technique/scan/energy",
    "Distance": "/technique/scan/sample_detector_distance", # mm in HDF5 and EDF
    # ~ "Prefix": TODO
    "Directory": "/technique/saving/path",
    "ScanRange": "/technique/scan/scan_range",
    "TOMO_N": "/technique/scan/tomo_n",
    "REF_ON": "/technique/scan/ref_on",
    "REF_N": "/technique/reference/ref_n",
    "DARK_N": "/technique/dark/dark_n",
    "Dim_1": "/technique/detector/size", # array
    "Dim_2": "/technique/detector/size", # array
    "Count_time": "/technique/scan/exposure_time", # ms in HDF5, s in EDF ?
    "Shutter_time": "/technique/scan/shutter_time", # ms in HDF5, s in EDF ?
    "Optic_used": "/technique/optic/magnification",
    "PixelSize": "/technique/detector/pixel_size", # array (microns)
    "Date": "/start_time",
    "Scan_Type": "/technique/scan/scan_type",
    "SrCurrent": "/instrument/machine/current",
    "Comment": "/technique/scan/comment", # empty ?
}


def decode_bytes(content):
    if isinstance(content, bytes):
        return content.decode()
    else:
        return content


def simulate_edf_header(fname, entry, return_dict=False):
    edf_header = {
        "ByteOrder": "LowByteFirst",
    }
    with HDF5File(fname, "r") as fid:
        for edf_name, h5_path in edf_header_hdf5_path.items():
            if edf_name == "motors": continue
            h5_path = entry + h5_path
            edf_header[edf_name] = decode_bytes(fid[h5_path][()])
        h5_motors = decode_bytes(fid[entry + edf_header_hdf5_path["motors"]])
        edf_header["motor_mne"] = list(h5_motors.keys())
        edf_header["motor_pos"] = [v[()] for v in h5_motors.values()]

    # remove "scan_numbers" from motors
    try:
        idx = edf_header["motor_mne"].index("scan_numbers")
        edf_header["motor_mne"].pop(idx)
        edf_header["motor_pos"].pop(idx)
    except ValueError:
        pass

    # remove invalid values from motor_pos
    invalid_values = ["*DIS*"]
    try:
        for invalid_val in invalid_values:
            idx = edf_header["motor_pos"].index(invalid_val)
            edf_header["motor_mne"].pop(idx)
            edf_header["motor_pos"].pop(idx)
    except ValueError:
        pass

    # Format
    edf_header["flip"] = "<flip x : %s,flip y : %s>" % (edf_header["flip"][0], edf_header["flip"][1])
    edf_header["motor_mne"] = " ".join(edf_header["motor_mne"])
    edf_header["motor_pos"] = " ".join(list(map(str, edf_header["motor_pos"])))
    edf_header["count_time"] = edf_header["count_time"] * 1e-3 # HDF5: ms -> EDF: s

    if return_dict:
        return edf_header
    res = ""
    for k, v in edf_header.items():
        res = res + "%s = %s ;\n" % (k, v)
    return res


def simulate_info_file(fname, entry, return_dict=False):
    info_file_content = {}
    with HDF5File(fname, "r") as fid:
        for info_name, h5_path in info_hdf5_path.items():
            h5_path = entry + h5_path
            info_file_content[info_name] = decode_bytes(fid[h5_path][()])

    info_file_content["Dim_1"] = info_file_content["Dim_1"][0]
    info_file_content["Dim_2"] = info_file_content["Dim_2"][1]
    info_file_content["PixelSize"] = info_file_content["PixelSize"][0]
    info_file_content["Prefix"] = os.path.basename(fname)
    info_file_content["Col_end"] = info_file_content["Dim_1"] - 1
    info_file_content["Col_beg"] = 0
    info_file_content["Row_end"] = info_file_content["Dim_2"] - 1
    info_file_content["Row_beg"] = 0
    for what in ["Count_time", "Shutter_time"]:
        info_file_content[what] = info_file_content[what] * 1e-3

    if return_dict:
        return info_file_content
    # Format
    res = ""
    for k, v in info_file_content.items():
        k_s = str("%s=" % k)
        sep = " " * (24 - len(k_s))
        res = res + k_s + sep + str("%s\n" % v)
    return res



def get_hst_saturations(hist, bins, numels):
    aMin = bins[0]
    aMax = bins[-1]
    hist_sum = numels * 1.

    hist_cum = np.cumsum(hist)
    hist_cum_rev = np.cumsum(hist[::-1])

    i_s1 = np.where(hist_cum > 0.00001*hist_sum)[0][0]
    sat1 = aMin+i_s1*(aMax-aMin)/(hist.size - 1)

    i_S1 = np.where(hist_cum > 0.002*hist_sum)[0][0]
    Sat1 = aMin+i_S1*(aMax-aMin)/(hist.size-1)

    i_s2 = np.argwhere(hist_cum_rev > 0.00001*hist_sum)[0][0]
    sat2 = aMin+(hist.size - 1 - i_s2)*(aMax-aMin)/(hist.size - 1)

    i_S2 = np.argwhere(hist_cum_rev > 0.002*hist_sum)[0][0]
    Sat2 = aMin+(hist.size - 1 - i_S2)*(aMax-aMin)/(hist.size-1)

    return sat1, sat2, Sat1, Sat2


def simulate_hst_vol_header(fname, entry=None, return_dict=False):
    with HDF5File(fname, "r") as fid:
        try:
            histogram_path = entry + "/histogram/results/data"
            histogram_config_path = entry + "/histogram/configuration"
            Nz, Ny, Nx = fid[histogram_config_path]["volume_shape"][()]
            vol_header_content = {
                "NUM_X": Nx,
                "NUM_Y": Ny,
                "NUM_Z": Nz,
                "BYTEORDER": "LOWBYTEFIRST",
            }
            hist = fid[histogram_path][()]
        except KeyError as err:
            print("Could not load histogram from %s: %s" % (fname, err))
            return {} if return_dict else ""
    bins = hist[1]
    hist = hist[0]
    vmin = bins[0]
    vmax = bins[-1] + (bins[-1] - bins[-2])
    s1, s2, S1, S2 = get_hst_saturations(hist, bins, Nx*Ny*Nz)
    vmin = bins[0]
    vmax = bins[-1] + (bins[-1] - bins[-2])
    vol_header_content.update({
        "ValMin": vmin,
        "ValMax": vmax,
        "s1": s1,
        "s2": s2,
        "S1": S1,
        "S2": S2,
    })
    if return_dict:
        return vol_header_content
    res = ""
    for k, v in vol_header_content.items():
        res = res + "%s =  %s\n" % (k, v)
    return res


def format_as_info(d):
    res = ""
    for k, v in d.items():
        k_s = str("%s=" % k)
        sep = " " * (24 - len(k_s))
        res = res + k_s + sep + str("%s\n" % v)
    return res


def generate_merged_info_file_content(
    hist_fname=None, hist_entry=None,
    bliss_fname=None, bliss_entry=None,
    first_edf_proj=None, info_file=None
):
    # EDF Header
    if first_edf_proj is None:
        edf_header = simulate_edf_header(
            bliss_fname, bliss_entry, return_dict=True
        )
    else:
        edf_header = EdfFile(first_edf_proj).GetHeader(0)
    # .info File
    if info_file is None:
        info_file_content = simulate_info_file(
            bliss_fname, bliss_entry, return_dict=True
        )
        info_file_content = format_as_info(info_file_content)
    else:
        with open(info_file, "r") as f:
            info_file_content = f.read()
    # .vol File
    vol_file_content = simulate_hst_vol_header(
        hist_fname, entry=hist_entry, return_dict=True
    )
    #
    res = format_as_info(edf_header)
    res += info_file_content
    res += format_as_info(vol_file_content)
    return res



def str_or_none(s):
    if len(s.strip()) == 0:
        return None
    return s



def generate_merged_info_file():
    args = parse_params_values(
        GenerateInfoConfig,
        parser_description="Generate a .info file"
    )

    hist_fname = str_or_none(args["hist_file"])
    hist_entry = str_or_none(args["hist_entry"])
    bliss_fname = str_or_none(args["bliss_file"])
    bliss_entry = str_or_none(args["bliss_entry"])
    first_edf_proj = str_or_none(args["edf_proj"])
    info_file = str_or_none(args["info_file"])
    if hist_fname is not None and hist_entry is None:
        hist_entry = get_first_hdf5_entry(hist_fname)
    if bliss_fname is not None and bliss_entry is None:
        bliss_entry = get_first_hdf5_entry(bliss_fname)


    if not((bliss_fname is None) ^ (info_file is None)):
        print("Error: please provide either --bliss_file or --info_file")
        exit(1)

    if info_file is not None and first_edf_proj is None:
        print("Error: please provide also --edf_proj when using the EDF format")
        exit(1)

    content = generate_merged_info_file_content(
        hist_fname=hist_fname,
        hist_entry=hist_entry,
        bliss_fname=bliss_fname,
        bliss_entry=bliss_entry,
        first_edf_proj=first_edf_proj,
        info_file=info_file
    )
    with open(args["output"], "w") as f:
        f.write(content)


