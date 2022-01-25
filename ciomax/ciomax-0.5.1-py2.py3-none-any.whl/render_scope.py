"""
RenderScope

We need to support different submission methods based on the renderer chosen in Render Setup.
* vray - we can submit with vray-standalone on Linux, or with Max on Windows. 
* arnold - we can submit with arnold-for-maya (kick) on Linux, or with Max on Windows.
* all other renderers - we submit with Max on Windows.

A RenderScope encapsulates all the information for one of the above options.
It knows for example the version, the appropriate render commands, the presubmission scripts.
Since the submitter is a modal dialog, we know that the renderer will not change.
"""

from pymxs import runtime as rt
from ciocore import data as coredata

VRAY_STANDALONE_PREFIX = "v-ray-standalone"
ARNOLD_MAYA_PREFIX = "arnold-maya"
MAX_PREFIX = "3dsmax-io"
ARNOLD_MAX_PREFIX = "arnold-3dsmax"
VRAY_MAX_PREFIX = "v-ray-3dsmax"

MAX_TO_MAYA_ARNOLD_MAP = {
  "4.1.2.1": "maya-io 2020.SP4/arnold-maya 4.1.1.1",    # Arnold 6.1.0.1
  "4.2.0.55":"maya-io 2020.SP4/arnold-maya 4.1.1.1",    # Arnold 6.1.0.1
  "4.2.2.20":"maya-io 2020.SP4/arnold-maya 4.1.1.1",    # Arnold 6.1.0.1
  "4.3.0.78":"maya-io 2020.SP4/arnold-maya 4.2.0.0",    # Arnold 6.2.0.0
  "4.3.1.20":"maya-io 2020.SP4/arnold-maya 4.2.1.0",    # Arnold 6.2.0.1 
  "4.3.2.46":"maya-io 2022.SP0/arnold-maya 4.2.3.0",    # Arnold 6.2.1.0
  "4.3.3.21":"maya-io 2022.SP0/arnold-maya 4.2.3.0"     # Arnold 6.2.1.1
  }


VALID_MAYA_ARNOLD_VERSIONS = list(set([MAX_TO_MAYA_ARNOLD_MAP[maxtoa_version] for maxtoa_version in MAX_TO_MAYA_ARNOLD_MAP]))

LAST_MAYA_ARNOLD_VERSION = sorted(VALID_MAYA_ARNOLD_VERSIONS)[-1]

class RenderScope(object):
    """
    RenderScope base class.
    """
 
    __magic_shield = object()

    @classmethod
    def get(cls):
        """Factory which will create render-options based on the chosen render setup."""

        name = str(rt.renderers.current).split(":")[0]

        if name.startswith("V_Ray_GPU"):
            return VrayGPURenderScope(cls.__magic_shield, name)
        elif name.startswith("V_Ray"):
            return VraySWRenderScope(cls.__magic_shield, name)
        elif name == "Arnold":
            return ArnoldRenderScope(cls.__magic_shield, name)
        else:
            return NativeRenderScope(cls.__magic_shield, name)

    def __init__(self, _shield, name):
        assert (
            _shield == RenderScope.__magic_shield
        ), "RenderScope must be created with RenderScope.get()"

        self.package_paths = self.get_render_package_paths()

        self.templates = {
            "max": {
                "command": '3dsmaxcmdio.exe -v 5 -workPath "<project>" -frames <start>-<end> -outputName "<destination>/<scenenamex>..exr"   -preRenderScript "<project>/prerender.py" "<scenedir>/<timestamp>_<scenenamex>.max" ',
                "script": '"<conductor>/ciomax/scripts/save_max_scene.py" "<scenedir>/<timestamp>_<scenenamex>"',
            }
        }

        self._name = name
        self.version = self.get_version()

    def __str__(self):
        return str(self._name)

    @staticmethod
    def get_version():
        raise NotImplementedError

    def closest_version(self, partial_path):
        raise NotImplementedError

    def operating_systems(self, partial_path):
        raise NotImplementedError

    def set_render_packages(self):
        raise NotImplementedError

    def get_script_template(self, path):
        if "(Windows)" in path:
            return self.templates["max"]["script"]
        return self.templates["standalone"]["script"]

    def get_task_template(self, path):
        if "(Windows)" in path:
            return self.templates["max"]["command"]
        return self.templates["standalone"]["command"]

    def all_software_paths(self, path):
        path = path.split("(")[0].strip()
        result = []
        while True:
            result.append(path)
            parts = path.partition("/")
            if not parts[1]:
                return result
            path = parts[0]



class VraySWRenderScope(RenderScope):

    def __init__(self, _shield, name):
        super(VraySWRenderScope, self).__init__(_shield, name)

        self.templates["standalone"] = {
            "command": 'vray -display=0 -verboseLevel=4 -sceneFile="<posix project>/vray/<timestamp>_<scenenamex>.vrscene"  -remapPathFile="<posix project>/vray/<timestamp>_<scenenamex>.xml"   -imgFile="<posix destination>/<scenenamex>.exr" -frames=<start>-<end>',
            "script": '"<conductor>/ciomax/scripts/export_vray.py" "<project>/vray/<timestamp>_<scenenamex>"',
        }


    @staticmethod
    def get_render_package_paths():
        """
        The user can render with Max, or with Vray Standalone
        """
        if not coredata.valid():
            return []
        path_list = coredata.data()["software"].to_path_list()


        max_vray_paths = ["{} (Windows)".format(p) for p in path_list if VRAY_MAX_PREFIX in p ]
        max_vray_paths = sorted(list(set(max_vray_paths)))

        vray_standalone_paths = ["{} (Linux)".format(p) for p in path_list if p.startswith(VRAY_STANDALONE_PREFIX)]
        vray_standalone_paths = sorted(list(set(vray_standalone_paths)))

        return max_vray_paths + vray_standalone_paths

    @staticmethod
    def get_version():
        parts = rt.vrayVersion()[0].split(".")
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return "v-ray-standalone {}".format(version)

    def closest_version(self, partial_path):
        """Try to get an exact match from the list of full versions.

        Otherwise try to determine if it was set to a standalone vray, and if so, see if it matches
        the current version.
        """
        if not self.package_paths:
            return None
        if partial_path and partial_path in self.package_paths:
            return partial_path

        if partial_path.startswith("v-ray"):
            if self.version in self.package_paths:
                return self.version
            return self.package_paths[-1].split("/")[-1]
        elif partial_path in self.package_paths:
            return partial_path
        else:
            result = next(p for p in self.package_paths if p.startswith(MAX_PREFIX) )
            return result

class VrayGPURenderScope(VraySWRenderScope):
    def __init__(self, _shield, name):
        super(VrayGPURenderScope, self).__init__(_shield, name)


class ArnoldRenderScope(RenderScope):
    # OPERATING_SYSTEMS = ["linux", "windows"]
    def __init__(self, _shield, name):
        super(ArnoldRenderScope, self).__init__(_shield, name)

        self.templates["standalone"] = {
            "command": 'kick -nostdin -i "<posix project>/ass/<timestamp>/<scenenamex>.<pad start 4>.ass" -dw -dp -v 5 -of exr -o "<posix destination>/<scenenamex>.<pad start 4>.exr"',
            "script": '"<conductor>/ciomax/scripts/export_ass.py" "<project>/ass/<timestamp>/<scenenamex>."',
        }

    @staticmethod
    def get_render_package_paths():
        """
        The user can render with Max, or with Arnold for Maya
        """
        if not coredata.valid():
            return []
        path_list = coredata.data()["software"].to_path_list()

        max_arnold_paths = ["{} (Windows)".format(p) for p in path_list if ARNOLD_MAX_PREFIX in p ]
        max_arnold_paths = sorted(list(set(max_arnold_paths)))

        arnold_standalone_paths = [
            "{} (Linux)".format(p.split("/")[-1]) for p in path_list if p in VALID_MAYA_ARNOLD_VERSIONS
        ]
        arnold_standalone_paths = sorted(list(set(arnold_standalone_paths)))

        return max_arnold_paths + arnold_standalone_paths

    def all_software_paths(self, path):
        if not path.startswith(ARNOLD_MAYA_PREFIX):
            return super(ArnoldRenderScope, self).all_software_paths(path)
        path = path.split("(")[0].strip()
        # will be array of length 1
        return [p for p in VALID_MAYA_ARNOLD_VERSIONS if p.endswith(path)]



    @staticmethod
    def get_version():
        parts = rt.getFileVersion("maxtoa.dlr").split("\t")[0].split(",")
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return MAX_TO_MAYA_ARNOLD_MAP.get(version, LAST_MAYA_ARNOLD_VERSION)

    def closest_version(self, partial_path):
        """Try to get an exact match from the list of full versions.

        Otherwise try to determine if it was set to a maya, and if so, see if it matches
        the current version.
        """
        if not self.package_paths:
            return None
        found = partial_path and partial_path in (p.split("/")[-1] for p in self.package_paths)
        if found:
            return partial_path

        if partial_path.startswith("arnold"):
            if self.version in self.package_paths:
                result = self.version
            else:
                result = self.package_paths[-1]
            return result.split("/")[-1]
        elif partial_path in self.package_paths:
            return partial_path
        else:
            result = next(p for p in self.package_paths if p.startswith(MAX_PREFIX) )
            return result


class NativeRenderScope(RenderScope):
    # OPERATING_SYSTEMS = ["windows"]
    def __init__(self, _shield, name):
        super(NativeRenderScope, self).__init__(_shield, name)

        msg = "UNABLE TO RENDER {} ON THIS ACCOUNT".format(name)
        self.templates["standalone"] = {
            "command": '{}'.format(msg),
            "script":  '{}'.format(msg),
        }


    @staticmethod
    def get_render_package_paths():
        """
        The user can render with Max
        """
        if not coredata.valid():
            return []

        path_list = coredata.data()["software"].to_path_list()
        max_paths = ["{} (Windows)".format(p) for p in path_list if p.startswith(MAX_PREFIX) and not "/" in p]
        return sorted(list(set(max_paths)))

    @staticmethod
    def get_version():
        return "max 0.0.0.0"

    def closest_version(self, partial_path):
        """Try to get an exact match from the list of full versions."""
        if not self.package_paths:
            return None
        found = partial_path and partial_path in (p.split("/")[-1] for p in self.package_paths)
        if found:
            return partial_path

        # For now, return the first version of Max
        return self.package_paths[0]
