import glob
import logging
import os
import platform
import shutil
import subprocess
import tempfile
from typing import List

import pydelica.exception as pde
from pydelica.options import LibrarySetup


class Compiler:
    """Performs compilation of Modelica using the OMC compiler"""

    def __init__(self, open_modelica_library_path: str = None) -> None:
        """Initialise a compiler object

        Parameters
        ----------
        open_modelica_library_path : str, optional
            location of the OM libraries, else use defaults for system

        Raises
        ------
        pde.BinaryNotFoundError
            if an OMC compiler binary could not be found
        """
        self._logger = logging.getLogger("PyDelica.Compiler")
        self._environment = os.environ.copy()
        self._library = LibrarySetup()
        if "OPENMODELICAHOME" in os.environ:
            _omc_cmd = "omc.exe" if platform.system() == "Windows" else "omc"
            self._omc_binary = os.path.join(
                os.environ["OPENMODELICAHOME"], "bin", _omc_cmd
            )
        elif shutil.which("omc"):
            self._omc_binary = shutil.which("omc")
        else:
            raise pde.BinaryNotFoundError("Failed to find OMC binary")

        if platform.system() == "Windows":
            _mod_tool_bin = os.path.join(
                os.environ["OPENMODELICAHOME"],
                "tools",
                "msys",
                "mingw64",
                "bin",
            )
            self._environment["PATH"] = (
                f"{_mod_tool_bin}" + os.pathsep + self._environment["PATH"]
            )
            self._environment["PATH"] = (
                f"{os.path.dirname(self._omc_binary)}"
                + os.pathsep
                + self._environment["PATH"]
            )
        self._logger.debug(f"Using Compiler: {self._omc_binary}")

    def compile(
        self,
        modelica_source_file: str,
        model_addr: str = None,
        c_source_dir: str = None,
        extra_models: List[str] = None,
    ) -> str:
        """Compile Modelica source file

        Parameters
        ----------
        modelica_source_file : str
            Modelica source file to compile
        model_addr : str, optional
            Model within source file to compile, default is first found
        c_source_dir : str, optional
            directory containing any additional required C sources
        extra_models: List[str], optional
            Additional other model dependencies

        Returns
        -------
        str
            location of output binary
        """
        _temp_source_dir = tempfile.mkdtemp()
        _temp_build_dir = tempfile.mkdtemp()

        # Check if there is a 'Resources/Include' directory in the same
        # location as the Modelica script

        _candidate_c_inc = os.path.join(
            os.path.dirname(modelica_source_file), "Resources", "Include"
        )

        if os.path.exists(_candidate_c_inc) and not c_source_dir:
            c_source_dir = _candidate_c_inc

        if c_source_dir:
            self._prepare_c_incls(c_source_dir, _temp_source_dir)
        modelica_source_file = os.path.abspath(modelica_source_file)

        # Copy sources to a temporary source location
        self._logger.debug(
            "Copying sources to temporary directory '%s'", _temp_source_dir
        )
        _temp_model_source = os.path.join(
            _temp_source_dir, os.path.basename(modelica_source_file)
        )
        shutil.copy(modelica_source_file, _temp_model_source)

        if not os.path.exists(modelica_source_file):
            raise FileNotFoundError(
                f"Could not compile Modelica file '{modelica_source_file}',"
                " file does not exist"
            )

        _args = [self._omc_binary, "-s", _temp_model_source]

        if extra_models:
            for model in extra_models:
                _orig_model = os.path.join(os.path.dirname(modelica_source_file), model)
                if not os.path.exists(_orig_model):
                    raise FileNotFoundError(
                        f"Could not compile supplementary Modelica file '{model}',"
                        " file does not exist"
                    )
                _temp_model_source = os.path.join(
                    _temp_source_dir, os.path.basename(model)
                )
                shutil.copy(_orig_model, _temp_model_source)
                _args.append(_temp_model_source)

        _args.append("Modelica")

        if self._logger.getEffectiveLevel() == logging.DEBUG:
            _args.append("-d")

        if model_addr:
            _args.append(f"+i={model_addr}")

        _cmd_str = " ".join(_args)

        self._logger.debug(f"Executing Command: {_cmd_str}")

        _gen = None

        # Disable environment setting on Windows as it does not work at present
        if platform.system() == "Windows":
            _environ = None
        else:
            _environ = os.environ.copy()
            _environ["OPENMODELICALIBRARY"] = self._library.get_library()

        try:
            _gen = subprocess.run(
                _args,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                env=_environ,
                cwd=_temp_build_dir,
            )

            pde.parse_error_string_compiler(_gen.stdout, _gen.stderr)
        except FileNotFoundError as e:
            self._logger.error("Failed to run command '%s'", _cmd_str)
            self._logger.debug("PATH: %s", self._environment["PATH"])
            if _gen:
                self._logger.error("Traceback: %s", _gen.stdout)
            raise e
        except pde.OMExecutionError as e:
            self._logger.error("Failed to run command '%s'", _cmd_str)
            if _gen:
                self._logger.error("Traceback: %s", _gen.stdout)
            raise e
        except pde.OMBuildError as e:
            if "lexer failed" in e.args[0]:
                self._logger.warning(e.args[0])
            else:
                if _gen:
                    self._logger.error("Traceback: %s", _gen.stdout)
                raise e

        self._logger.debug(_gen.stdout)

        if _gen and _gen.stderr:
            self._logger.error(_gen.stderr)

        _make_file = glob.glob(os.path.join(_temp_build_dir, "*.makefile"))

        if not _make_file:
            self._logger.error(
                "Output directory contents [%s]: %s",
                _temp_build_dir,
                os.listdir(_temp_build_dir),
            )
            raise pde.ModelicaFileGenerationError(
                f"Failed to find a Makefile in the directory: {_temp_build_dir}, "
                "Modelica failed to generated required files."
            )

        _make_file = _make_file[0]

        if platform.system() == "Windows":
            _make_cmd = os.path.join(
                os.environ["OPENMODELICAHOME"],
                "share",
                "omc",
                "scripts",
                "Compile.bat",
            )
            _make_file = os.path.basename(_make_file)
            _build_cmd = [
                _make_cmd,
                os.path.splitext(_make_file)[0],
                "gcc",
                "mingw64",
                "parallel",
                "4",
                "0",
            ]

        elif not shutil.which("make"):
            raise pde.BinaryNotFoundError("Could not find GNU-Make on this system")
        else:
            _make_cmd = shutil.which("make")
            _build_cmd = [_make_cmd, "-f", _make_file]

        self._logger.debug(f"Build Command: {' '.join(_build_cmd)}")

        _build = subprocess.run(
            _build_cmd,
            shell=False,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env=self._environment,
            cwd=_temp_build_dir,
        )

        try:
            pde.parse_error_string_compiler(_build.stdout, _build.stderr)
        except pde.OMBuildError as e:
            self._logger.error(_build.stderr)
            raise e

        if _build.stdout:
            self._logger.debug(_build.stdout)

        if _gen.stderr:
            self._logger.error(_build.stderr)

        return _temp_build_dir

    def _prepare_c_incls(self, c_source_dir: str, _temp_dir: str):
        self._logger.debug("Checking for C sources in '%s'", c_source_dir)
        _c_sources = glob.glob(os.path.join(c_source_dir, "*.c"))
        _c_sources += glob.glob(os.path.join(c_source_dir, "*.C"))
        _include = os.path.join(_temp_dir, "Resources", "Include")
        os.makedirs(_include)
        for source in _c_sources:
            _file_name = os.path.basename(source)
            self._logger.debug("Found '%s'", _file_name)
            shutil.copy(source, os.path.join(_include, _file_name))
