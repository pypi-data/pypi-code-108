# coding: utf-8
###########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################

"""This module is a translation of octave ftseries developped by ESRF ID19 team
It contains the fasttomo global definitions, equivalent to
octave/defineGLOBALS.m
"""

__authors__ = ["C.Nemoz", "H.Payno"]
__license__ = "MIT"
__date__ = "19/03/2019"


import os
import subprocess
import glob
import datetime
from tomwer.core import settings
from tomwer.core import utils
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.process.task import Task
from tomwer.core.signal import Signal
from tomwer.core.utils import ftseriesutils
from tomwer.core.utils import logconfig
import logging
from tomwer.core.scan.scanbase import TomwerScanBase, _TomwerBaseDock
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from silx.test.utils import temp_dir

logger = logging.getLogger(__name__)


class _Ftseries(Task, input_names=("data",), output_names=("data",)):
    """
    Ftseries is the class managing the reconstructions.
    Reconstructions are launched calling the octave fastomo3 scripts.

    Ftseries is able to run one reconstruction at the time only.
    Every requested reconstruction will be stored in a queue (`reconsStack`)
    and be launched one at the time on a dedicated thread.
    """

    # Note : when process is call we don't necessqrly expect to find an
    # 'octave_FT_params.h5' file at the folder level.
    # But updateReconsParam should always have a .h5 file defined

    sigScanReady = Signal(TomwerScanBase)
    """Signal emit when the reconstruction is finished"""

    def __init__(self, recons_stack=None, varinfo=None, inputs=None, name=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=name)
        if "recons_params" in inputs:
            raise KeyError(
                "Do not use recons_params but `pyhst2_recons_params` instead"
            )
        recons_params = inputs.get("pyhst2_params", None)
        if not isinstance(recons_params, ReconsParams):
            raise TypeError(
                "pyhst2_recons_params should be provided as an instance"
                " of tomwer.core.process.reconstruction.ftseries.params.ReconsParams and not {}".format(
                    type(recons_params)
                )
            )
        self._recons_params = recons_params

        """Reconstruction parameters for tomo reconstruction"""
        self.dry_run = inputs.get("dry_run", False)
        """execute the pyhst reconstruction or only create the .par file"""

        self._scan = inputs.get("data", None)
        self._exploreForH5File = inputs.get("explore_for_h5_file", False)
        """If True then look in the scan folder and if contain a .h5 try to
        load to update the reconstruction parameters from it"""
        self._mockMode = inputs.get("mock_mode", False)
        """If we want to skip pyhst reconstruction and create some random
        slice reconstruction"""
        self.reconsStack = recons_stack
        if self.reconsStack is not None:
            self.reconsStack.sigReconsMissParams.connect(self.updateReconsParam)
            self.reconsStack.sigReconsFinished.connect(self._signalReconsReady)

    @property
    def recons_params(self):
        return self._recons_params

    def set_configuration(self, properties):
        if "_rpSetting" in properties:
            self.recons_params.setStructs(properties["_rpSetting"])

    def set_dry_run(self, dry_run):
        self.dry_run = dry_run

    def set_recons_params(self, recons_param):
        assert isinstance(recons_param, ReconsParams)
        self._recons_params = recons_param
        # TODO: this should be update to use am update instead

    def setH5Exploration(self, b):
        self._exploreForH5File = b

    def updatePath(self, path):
        """
        update self._scan and try to load the configuration file for octave

        :param path:the path to the new folder to observe
        """
        if self._exploreForH5File:
            h5file = ftseriesutils.tryToFindH5File(path, "newest")
            "h5 file is the file to load to update the reconstruction parameters"
            if h5file is not None:
                try:
                    self.load_recons_params(h5file)
                except Exception:
                    logger.warning(
                        "Fail to load reconstruction parameters " "from %s" % h5file
                    )
                else:
                    logger.info("Reconstruction parameters loaded from " "%s" % h5file)

        self._scan = ScanFactory.create_scan_object(scan_path=path)

    def pathReceived(self, pathToTheScanCompleted):
        """Callback function when the path of the file to scan is modify
        The default behavior here is to run a first reconstruction without
        waiting any user modifications

        :param pathToTheScanCompleted:the path to the new folder to observe"""
        if pathToTheScanCompleted is None:
            return

        logger.info("%s received" % pathToTheScanCompleted)

        if type(pathToTheScanCompleted) is str:
            _scan = ScanFactory.create_scan_object(scan_path=pathToTheScanCompleted)
        else:
            _scan = pathToTheScanCompleted

        # behavior : when receiving a new scan, reconstruct it right away
        return self.process(scan=_scan)

    def updateCurrentFTSeries(self, scan):
        """Change the Ftseries we want to reconstruct"""
        if scan is not None:
            info = "ask for FTSerie scan %s" % scan.path
            logger.info(
                info,
                extra={
                    logconfig.DOC_TITLE: self._scheme_title,
                    logconfig.SCAN_ID: scan.path,
                },
            )

            self._scan = scan

    def run(self):
        """Call the core function 'run_reconstruction' of the ftseries script
        which will call octave to process reconstruction
        """
        scan = self.inputs.data
        if scan is None:
            return

        if type(scan) is str:
            # if necessary updatePath
            if self._scan is None or scan != self._scan.path:
                self.updatePath(scan)
        elif isinstance(scan, TomwerScanBase):
            self._scan = scan
        elif type(scan) is dict:
            self._scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise TypeError(
                "scan should be a path to a valid scan or an " "instance of TomoScan"
            )

        if (
            self._scan is not None
            and self._scan.path is not None
            and os.path.isdir(self._scan.path)
        ):

            def copy_recons_params():
                """as we have a widget able to define some dark ref parameter
                we have first to copy this parameter value if any"""
                if self._scan.ftseries_recons_params is None:
                    self._scan.ftseries_recons_params = ReconsParams(empty=True)

                self._recons_params.copy(self._scan.ftseries_recons_params.dkrf)

            # first copy some recons params from the input edf tomo scan
            copy_recons_params()

            # then update the scan ftseries_recons_params
            self._scan.ftseries_recons_params.copy(self.recons_params)
            assert (
                self._scan.ftseries_recons_params.axis.do_axis_correction
                == self.recons_params.axis.do_axis_correction
            )

            if self._mockMode:
                # mock are not made within a thread
                logger.info("mocking reconstruction")
                MockEDF.mockReconstruction(self._scan.path)
            elif self.reconsStack is None:
                # run reconstruction without stack
                scan.ftseries_recons_params.copy(self.recons_params)
                inputs = {
                    "pyhst2_params": scan.ftseries_recons_params.to_dict(),
                    "dry_run": self.dry_run,
                }

                run_reconstruction_from_recons_params(scan=self._scan, inputs=inputs)
                self._signalReconsReady(scan=self._scan)
            else:
                # note: _signalReconsReady will be called by the slot associated
                # to the stack signals
                self.reconsStack.add(
                    scan=self._scan,
                    inputs=self.recons_params.to_unique_recons_set(as_to_dict=True),
                    schemeTitle=self._scheme_title,
                    dry_run=self.dry_run,
                )
            self.register_output(key="data", value=self._scan)
            if self._return_dict:
                self.outputs.data = self._scan.to_dict()
            else:
                self.outputs.data = self._scan

    def _infoMissingStrucVar(missingStructures, missingVariables):
        m = "File is missing some structures and/or variables."
        m += "Values of those has been setted to default values."
        m += "Please make sure they are correct."
        m += "\nMissing structures: " + missingStructures
        m += "\nMissing variables: " + missingVariables
        print(m)

    def _signalReconsReady(self, scan):
        assert isinstance(scan, TomwerScanBase)

        info = "scan %s reconstructed" % scan.path
        logger.processEnded(
            info,
            extra={
                logconfig.DOC_TITLE: self._scheme_title,
                logconfig.SCAN_ID: scan.path,
            },
        )

        # if some volraw or volfloat are present at the same level, let
        # synchronize them.
        if settings.isOnLbsram(scan) is True:
            volfloat = os.path.join(os.path.dirname(scan.path), "volraw")
            volraw = os.path.join(os.path.dirname(scan.path), "volfloat")

            for _folder in (volraw, volfloat):

                if os.path.exists(_folder) and os.path.isdir(_folder):
                    target = _folder.replace(
                        settings.get_lbsram_path(), settings.get_dest_path(), 1
                    )
                    logger.info(
                        "start synchronization between %s and %s" % (_folder, target)
                    )
                    if not os.path.exists(target):
                        try:
                            os.makedirs(target)
                        except Exception as e:
                            logger.error(e)
                        else:
                            os.chmod(target, 0o774)
        self.sigScanReady.emit(scan)

    def askUserH5File(self):
        filePath = None
        while filePath is None:
            out = input("please give the path to the h5 file : \n")
            if not os.path.isfile(filePath):
                warning = "given path " + out
                warning += " is not a directory, please give a valid directory"
                logger.warning(warning)
                out = None
        return out

    def askUserAndLoad(self):
        """Process launch by activing the Load button"""
        f = self.askUserH5File()
        if f is not None:
            self.load_recons_params(f)

    def load_recons_params(self, h5file):
        assert os.path.isfile(h5file)
        from .params.fastsetupdefineglobals import FastSetupAll  # avoid cyclic import

        fsdg = FastSetupAll()
        fsdg.readAll(h5file, 3.8)
        self.recons_params.copy(fsdg.structures)

    @staticmethod
    def save_recons_params(recons_params: dict, h5File, displayInfo=True):
        if not isinstance(recons_params, dict):
            raise ValueError("recons_params is expected to be a dict")
        ftseriesutils.saveH5File(
            structs=recons_params, h5File=h5File, displayInfo=displayInfo
        )

    def save(self, h5File, displayInfo=True):
        """Function to overwrite the reconstruction parameters into the h5 file"""
        self.save_recons_params(
            recons_params=self._recons_params.to_dict(),
            h5File=h5File,
            displayInfo=displayInfo,
        )

    def setMockMode(self, b):
        """If the mock mode is activated then during reconstruction won't call
        Octave script for reconstruction but will generate some output files
        according to convention

        :param boolean b: True if we want to active the mock mode
        """
        self._mockMode = b

    def updateReconsParam(self, ftserie):
        if ftserie is None:
            return

        scan = ftserie
        if type(ftserie) is str:
            scan = ScanFactory.create_scan_object(ftserie)
        elif type(ftserie) is dict:
            scan = ScanFactory.create_scan_object_frm_dict(ftserie)
        elif isinstance(scan, _TomwerBaseDock):
            scan = ftserie.instance
        elif isinstance(scan, TomwerScanBase):
            scan = ftserie
        else:
            raise ValueError("Type not managed")
        assert scan is not None
        self.updateCurrentFTSeries(scan)

        # if on lbsram and in low memory then skip it
        if (
            settings.isOnLbsram(scan)
            and utils.isLowOnMemory(settings.get_lbsram_path()) is True
        ):
            # if computer is running into low memory in lbsram skip reconstruction
            mess = "low memory, skip reconstruction for " + scan.path
            logger.processSkipped(mess)
            self._signalReconsReady(self._scan.scanID)
        else:
            return self._askForReconsParamValidation()

    def _askForReconsParamValidation(self):
        logger.warning(
            "Reconstruction parameters validation is only develop "
            "with gui interaction for now. skip it."
        )
        return self.process(self._scan.path)

    def setForceSync(self, b):
        """
        Force synchronisation of the reconstruction

        :param b: True if we want to block ftseries during reconstruction
        """
        if self.reconsStack is not None:
            self.reconsStack.setForceSync(b)


class H5NoFileException(Exception):
    """Exception launch when no .h5 is found by ftseries"""

    pass


def _subprocess_run(*popenargs, _input=None, timeout=None, check=False, **kwargs):
    if _input is not None:
        if "stdin" in kwargs:
            raise ValueError("stdin and input arguments may not both be used.")
        kwargs["stdin"] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    try:
        stdout, stderr = process.communicate(_input)
    except Exception:
        process.kill()
        if timeout is not None:
            process.wait(timeout)
        else:
            process.wait()
        raise
    retcode = process.poll()
    if check and retcode:
        raise subprocess.CalledProcessError(
            retcode, process.args, output=stdout, stderr=stderr
        )
    return retcode, stdout, stderr


def run_reconstruction_from_recons_params(scan: TomwerScanBase, inputs: dict) -> None:
    """

    ..note: in this case the recons_param should be unique (not a set/List
            of ReconsParams)

    :param TomwerScanBase scan:
    :param dict inputs:
    """
    if not isinstance(scan, TomwerScanBase):
        raise TypeError(f"{scan} is expected to be an instance of {TomwerScanBase}")
    if not isinstance(inputs, dict):
        raise TypeError(f"{inputs} is expected to be an instance of {dict}")

    from tomwer.core.process.reconstruction.pyhst.pyhstcaller import PyHSTCaller

    if "data" in inputs:
        logger.warning(
            f"'data key' will be overwrite (replace {inputs['data']} by {scan})"
        )
    inputs["data"] = scan

    pyhstcaller = PyHSTCaller(inputs=inputs)
    pyhstcaller.run()


def run_reconstruction(directory, h5file):
    """Launch a reconstruction

    :param str directory: the acquisition directory
    :param str h5file: the h5 file containing the reconstruction parameters
    """
    with temp_dir() as tmp:
        # initialise global structures with default values
        assert os.path.isdir(directory)

        # manage all sub directories
        dirs = []

        aux = glob.glob(directory)
        laux = len(aux)
        for i in range(laux):
            dirs.append(aux[i])

        # now : new behavior : each directory for which we are running a
        # reconstruction should have an .h5 file

        if h5file is None or not os.path.isfile(h5file):
            raise H5NoFileException("No h5 file found for reconstruction")

        # version march python2/3 avec octave 3.6
        # fail avec octave 3.8

        octavexe = tmp + "/octseries"
        try:
            with open(octavexe, "wb") as file_:
                file_.write(bytes("#!/usr/bin/octave\n", "UTF-8"))
                file_.write(bytes("\n", "UTF-8"))
                file_.write(bytes("load_pars " + h5file + "\n", "UTF-8"))
                file_.write(bytes("global GET_MY_FT\n", "UTF-8"))
                file_.write(bytes("global GENERATOR\n", "UTF-8"))
                file_.write(bytes("GET_MY_FT = 0;\n", "UTF-8"))
                file_.write(bytes("global GENERATOR\n", "UTF-8"))
                file_.write(bytes("GENERATOR = 'tomwer';\n", "UTF-8"))
                file_.write(bytes("cd " + dirs[0] + "\n", "UTF-8"))
                file_.write(bytes("fasttomo3\n", "UTF-8"))
                file_.write(bytes("\n", "UTF-8"))
                file_.close()
            logger.info("creation of %s succeded" % octavexe)
        except Exception:
            logger.error("fail writing of %s" % octavexe)
            raise

        timeout = 15 * 60  # in sec
        try:
            # TODO : set write only to the current user security issue.
            os.chmod(octavexe, 0o775)
            octave_log = directory + "/octave.log"
            with open(octave_log, "ab") as _file:
                mydate = datetime.datetime.now()
                _file.write(
                    bytes(
                        "\n\n\n===== OCTAVE process started on " + str(mydate), "UTF-8"
                    )
                )

            with open(octave_log, "ab") as _file:
                retcode, stdout, stderr = _subprocess_run(
                    octavexe,
                    timeout=timeout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if stdout is not None:
                    print(stdout.decode("utf-8"))
                    _file.write(stdout)
                if retcode > 0 and stderr is not None:
                    _file.write(stderr)
                    logger.error("error append during execution of %s" % octavexe)
                    logger.error(stderr.decode("utf-8"))
                else:
                    logger.info("succeeded execution of %s" % octavexe)
        except subprocess.TimeoutExpired:
            logger.warning(
                "reconstruction for %s take too long (%s)" "" % (octavexe, timeout)
            )
        except Exception:
            logger.error("fail execution of %s" % octavexe)
            raise

        return h5file


def getInfoFile(dir):
    files = glob.glob(dir + "*.info")
    if dir.startswith(settings.get_lbsram_path()):
        seconddir = dir.rstrip(settings.get_lbsram_path())
        if os.path.isdir(seconddir):
            files += glob.glob(seconddir + "*.info")
    return files


# TODO: include this in _Ftseries
class Ftseries(_Ftseries):
    def __init__(self, varinfo=None, inputs=None, name=None):
        recons_params = inputs.get("pyhst2_params", None)
        # lazy loading
        from tomwer.core.process.reconstruction.ftseries.params import ReconsParams

        recons_params = recons_params or ReconsParams()
        inputs["pyhst2_params"] = recons_params
        inputs["force_sync"] = True

        _Ftseries.__init__(
            self, varinfo=varinfo, inputs=inputs, recons_stack=None, name=name
        )
