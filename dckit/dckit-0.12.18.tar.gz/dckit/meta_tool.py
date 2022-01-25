import copy
import functools
import pathlib
import warnings

import dclab
from dclab.rtdc_dataset import config as rt_config
from dclab.rtdc_dataset import fmt_tdms
import h5py
import nptdms


class MetadataEditedWarning(UserWarning):
    pass


def find_data(path):
    """Find tdms and rtdc data files in a directory"""
    path = pathlib.Path(path)

    def sort_path(path):
        """Sorting key for intuitive file sorting

        This sorts a list of RT-DC files according to measurement number,
        e.g. (M2_*.tdms is not sorted after M11_*.tdms):

        /path/to/M1_*.tdms
        /path/to/M2_*.tdms
        /path/to/M10_*.tdms
        /path/to/M11_*.tdms

        Note that the measurement number of .rtdc files is extracted from
        the hdf5 metadata and not from the file name.
        """
        try:
            # try to get measurement number as an integer
            idx = get_run_index(path)
        except BaseException:
            # just use the given path
            name = path.name
        else:
            # assign new "name" for sorting
            name = "{:09d}_{}".format(idx, path.name)
        return path.with_name(name)

    tdmsfiles = fmt_tdms.get_tdms_files(path)
    tdmsfiles = sorted(tdmsfiles, key=sort_path)
    rtdcfiles = [r for r in path.rglob("*.rtdc") if r.is_file()]
    rtdcfiles = sorted(rtdcfiles, key=sort_path)

    files = [pathlib.Path(ff) for ff in rtdcfiles + tdmsfiles]
    return files


def get_chip_region(path):
    fname = pathlib.Path(path).resolve()
    ext = fname.suffix
    if ext == ".rtdc":
        with h5py.File(fname, mode="r") as h5:
            chip_region = h5.attrs["setup:chip region"]
    elif ext == ".tdms":
        name = fname.name
        path = fname.parent
        mx = name.split("_")[0]
        para = path / (mx + "_para.ini")
        if para.exists():
            camcfg = rt_config.load_from_file(para)
            chip_region = camcfg["general"]["region"].lower()
        else:
            config = get_rtdc_config(path)
            chip_region = config["setup"]["chip region"]
    return chip_region


def get_date(path):
    config = get_rtdc_config(path)
    return config["experiment"]["date"]


def get_event_count(path):
    try:
        ec = get_event_count_quick(path)
    except BaseException:
        config = get_rtdc_config(path)
        ec = config["experiment"]["event count"]
    return ec


def get_event_count_quick(fname):
    """Get the number of events in a data set

    Parameters
    ----------
    fname: str
        Path to an experimental data file. The file format is
        determined from the file extension (tdms or rtdc).

    Returns
    -------
    event_count: int
        The number of events in the data set

    Notes
    -----
    For tdms-based data sets, there are multiple ways of determining
    the number of events, which are used in the following order
    (according to which is faster):
    1. The MX_log.ini file "Events" tag
    2. The tdms file (very slow, because it loads the entire tdms file)
       The values obtained with this method are cached on disk to
       speed up future calls with the same argument.
    """
    fname = pathlib.Path(fname).resolve()
    ext = fname.suffix

    if ext == ".rtdc":
        with h5py.File(fname, mode="r") as h5:
            event_count = h5.attrs["experiment:event count"]
    elif ext == ".tdms":
        mdir = fname.parent
        mid = fname.name.split("_")[0]
        # possible data sources
        logf = mdir / (mid + "_log.ini")
        if logf.exists():
            # 1. The MX_log.ini file "Events" tag
            with logf.open(encoding='utf-8') as fd:
                logd = fd.readlines()
            for ll in logd:
                if ll.strip().startswith("Events:"):
                    event_count = int(ll.split(":")[1])
                    break
        else:
            # 2. Open the tdms file
            with nptdms.TdmsFile.open(fname) as tdmsfd:
                event_count = len(tdmsfd["Cell Track"]["time"])
    else:
        raise ValueError("`fname` must be an .rtdc or .tdms file!")

    return event_count


def get_flow_rate(fname):
    """Get the flow rate of a data set

    Parameters
    ----------
    fname: str
        Path to an experimental data file. The file format is
        determined from the file extenssion (tdms or rtdc).

    Returns
    -------
    flow_rate: float
        The flow rate [µL/s] of the data set
    """
    fname = pathlib.Path(fname).resolve()
    ext = fname.suffix

    if ext == ".rtdc":
        with h5py.File(fname, mode="r") as h5:
            flow_rate = h5.attrs["setup:flow rate"]
    elif ext == ".tdms":
        name = fname.name
        path = fname.parent
        mx = name.split("_")[0]
        para = path / (mx + "_para.ini")
        if para.exists():
            camcfg = rt_config.load_from_file(para)
            flow_rate = camcfg["general"]["flow rate [ul/s]"]
        else:
            # analyze the filename
            warnings.warn("{}: trying to manually find flow rate.".
                          format(fname))
            flow_rate = float(fname.split("ul_s")[0].split("_")[-1])
    else:
        raise ValueError("`fname` must be an .rtdc or .tdms file!")

    return flow_rate


def get_rtdc_config(path):
    return get_rtdc_meta(path)[0]


def get_rtdc_logs(path):
    return get_rtdc_meta(path)[1]


@functools.lru_cache(maxsize=1000)
def get_rtdc_meta(path):
    with dclab.new_dataset(path) as ds:
        config = ds.config.copy()
        logs = copy.deepcopy(dict(ds.logs))
        ic = dclab.rtdc_dataset.check.IntegrityChecker(ds)
        if len(ic.check_shapein_issue3_bad_medium()):
            # https://github.com/ZELLMECHANIK-DRESDEN/ShapeIn_Issues/issues/3
            # Try to automatically determine the medium.
            swini = path.with_name(
                path.name.split("_")[0] + "_SoftwareSettings.ini")
            if swini.exists():
                lines = [ll.strip() for ll in swini.read_text().split("\n")]
                if ("Buffer_Medium_ID=0" in lines
                        and "Buffer_Medium=CellCarrierB" in lines):
                    config["setup"]["medium"] = "CellCarrier"
                    warnings.warn("Automatically set medium to 'CellCarrier', "
                                  "because of ID mismatch in '{}' (Shape-In "
                                  "issue #3).".format(swini),
                                  MetadataEditedWarning)
    return config, logs


def get_run_index(fname):
    fname = pathlib.Path(fname).resolve()
    ext = fname.suffix
    if ext == ".rtdc":
        with h5py.File(fname, mode="r") as h5:
            run_index = h5.attrs["experiment:run index"]
    elif ext == ".tdms":
        name = fname.name
        run_index = int(name.split("_")[0].strip("Mm "))
    return run_index


def get_sample_name(fname):
    fname = pathlib.Path(fname).resolve()
    ext = fname.suffix
    if ext == ".rtdc":
        with h5py.File(fname, mode="r") as h5:
            sample = h5.attrs["experiment:sample"]
    elif ext == ".tdms":
        sample = fmt_tdms.get_project_name_from_path(fname)
    if isinstance(sample, bytes):
        sample = sample.decode("utf-8")
    return sample
