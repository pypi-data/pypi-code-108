import pytest
import os
import pandas as pd
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from typing import List, Tuple, Optional, Dict, Any
from shutil import copyfile, copy, copy2
from glob import glob

def base_dir() -> str:
    """directory of curren test

    Returns:
        str: directory path of the test
    """
    f_name = os.getenv("PYTEST_CURRENT_TEST").split("::")[0]
    dir_name = os.path.dirname(f_name)
    return dir_name


def path_log(app_name: str = "") -> str:
    """path of the log file

    reads controlDict to get application if app_name not specified

    Args:
        app_name (str, optional): name of the application. Defaults to read controlDict to get application.

    Returns:
        str: path to the log file
    """
    dir_name = base_dir()
    if app_name:
        return os.path.join(dir_name, "log." + app_name)

    controlDict = os.path.join(dir_name, "system/controlDict")
    p = Pyfoam_parser(controlDict)
    app_name = p.value("application")

    return os.path.join(dir_name, "log." + app_name)

def path_logs() -> List[str]:
    """get all log files

    Returns:
        List[str]: pathes to the log files
    """
    dir_name = base_dir()
    logs = []
    for f in os.listdir(dir_name):
        log = os.path.join(dir_name,f)
        if os.path.isfile(log) and "log." in f:
            logs.append(log)
    return logs

def save_logs(request):
    dir_name = base_dir()
    testname = request.node.name
    testname = testname.replace("[","_")
    testname = testname.replace("]","")
    logs = [f for f in os.listdir(dir_name) if "log." in f]
    rootdir = request.config.rootdir
    log_folder = os.path.join(rootdir,"logs",testname)
    print("log_folder",log_folder)
    os.makedirs(log_folder,exist_ok=True)
    for log in logs:
        log_path = os.path.join(dir_name,log)
        copy2(log_path,log_folder)

def current_test():
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]

def copy_log_files():
    dir_name = base_dir()
    dest_dir = os.path.join("logs",current_test())
    os.makedirs(dest_dir,exist_ok=True)
    log_files = glob(r"{}/log.*".format(dir_name))
    for f in log_files:
        copy(f,dest_dir)


def expected_results(index_cols: List[int],index_parameters: Tuple[Any],filename: str="expected_results.csv") -> pd.DataFrame:
    """loads a csv with the expected results and return the row of the selected parameters

    Args:
        index_cols (List[int]): index colums e.g. [0,1] 
        index_parameters (Tuple[Any]): parameter selection ('StdModel',32)
        filename (str, optional): result file. Defaults to "expected_results.csv".

    Returns:
        pd.DataFrame: dataframe sliced with the index parameters
    """    
    dir_name = base_dir()
    expected = pd.read_csv(os.path.join(dir_name, filename),index_col=index_cols)
    return expected.loc[index_parameters]


class Parser:
    """abstract parser class
    """
    def __init__(self, filename: str):
        self.filename = filename

    def value(self, keyword: str):
        pass

    def set(self, keyword: str):
        pass

    def writeFile(self):
        pass


class Pyfoam_parser(Parser):
    """pyfoam based openfoam dict parser that modifes a file

    Args:
        Parser ([type]): abstract class
    """
    def __init__(self, filename: str):
        self.filename = filename
        self._ppp = ParsedParameterFile(self.filename)

    def _nested_get(self, dic: Dict, keyword: str):
        key_list = keyword.split("/")
        key_list[:] = [x for x in key_list if x]
        if len(key_list) == 1:
            return dic[key_list[0]]
        for key in key_list:
            dic = dic[key]
        return dic

    def _nested_set(self, dic: Dict, keyword: str, value: Any):
        key_list = keyword.split("/")
        key_list[:] = [x for x in key_list if x]
        if len(key_list) == 1:
            dic[key_list[-1]] = value
            return
        for key in key_list[:-1]:
            dic = dic.setdefault(key, {})
        dic[key_list[-1]] = value

    def value(self, keyword: str):
        """get value of key word

        Args:
            keyword (str): keyword as string e.g. application

            or in case of a nested dictionary dict1/subDict1/keyword1

        Returns:
            [type]: return value
        """
        return self._nested_get(self._ppp.content, keyword)

    def set(self, keyword: str, value: Any):
        """set value

        Args:
            keyword (str): keyword as string e.g. application

            or in case of a nested dictionary dict1/subDict1/keyword1
            value (Any): new value
        """
        self._nested_set(self._ppp.content, keyword, value)

    def writeFile(self):
        self._ppp.writeFile()

class Case_modifiers:
    """modifes and openfoam case by modifying the case files
    Args:
        case_modifiers (Dict): dict format filename : list of (keyword , value)
        e.g.
        {
            "system/controlDict": [ ("stopAt","writeNow"),
                                    ("endTime",10.1) ],
            "constant/transportProperties": [ ("water/transportModel","Newtonian"),
                                                ("air/transportModel","Newtonian") ]
        }

        subdicts are seperated by /
        dir_name (str): dir of openfoam case
        meta_data (Optional[Dict], optional): stores additional information. Defaults to {}.
    """
    def __init__(
        self, case_modifiers: Dict, dir_name: str, meta_data: Optional[Dict] = {}
    ):
        self.modifiers = case_modifiers
        self.dir_name = dir_name
        self.meta_data = meta_data
        self.success = False
        if "script" not in self.meta_data:
            self.meta_data["script"] = "Allrun -test"

    def __str__(self):
        out = str(self.modifiers)
        if self.meta_data:
            out += str(self.meta_data)
        return out

    def add_mod(self, file_path: str, key:str, val: Any):
        """add new file modification

        Args:
            file_path (str): path to file
            key (str): keyword
            val (Any): value
        """
        if file_path not in self.modifiers:
            self.modifiers[file_path] = []
        self.modifiers[file_path].append((key, val))

    def update_case(self):
        """
        update the based on the specified modifiers
        """
        for key in self.modifiers:
            bkp_file = key + ".orig"

            bkp_path = os.path.join(self.dir_name, bkp_file)
            file_path = os.path.join(self.dir_name, key)
            # backup file
            if not os.path.isfile(bkp_path):
                copyfile(file_path, bkp_path)

            p = Pyfoam_parser(os.path.join(self.dir_name, key))
            for key_val in self.modifiers[key]:
                p.set(key_val[0], key_val[1])
            p.writeFile()

    def revert_change(self):
        """
            revert changes
        """
        for key in self.modifiers:
            bkp_file = key + ".orig"

            bkp_path = os.path.join(self.dir_name, bkp_file)
            file_path = os.path.join(self.dir_name, key)
            if os.path.isfile(bkp_path):
                copyfile(bkp_path, file_path)
            else:
                os.remove(bkp_path)



def check_type(c_mod) -> Case_modifiers:
    if not isinstance(c_mod, Case_modifiers):
        try:
            # can also be a tuple of length of
            if len(c_mod) == 1:  # enables latter extension to multiple parameters
                c_mod = c_mod[0]
            else:
                TypeError("parameter needs to be a Case_modifiers not a tuple")
        except:
            raise TypeError("parameter needs to be a Case_modifiers")
    return c_mod


@pytest.fixture(scope="class")
def run_case(request):
    """fixture that runs case by exectuting a bash script

    The case can be modified by passing the Case_modifiers class

    Default name is script name Allrun can be modified by storing the script name
    in the meta_data of the Case_modifiers:

    c_mod.meta_data["script"] = "SomeScriptName"

    Yields:
        [Case_modifiers]: Case_modifiers information
    """
    mod_case = hasattr(request, "param")
    dir_name = base_dir()
    c_mod = Case_modifiers({}, dir_name)
    if mod_case:
        c_mod = check_type(request.param)

    nsteps = request.config.getoption("--writeNSteps")
    if nsteps:
        c_mod.add_mod("system/controlDict", "startFrom", "latestTime")
        c_mod.add_mod("system/controlDict", "stopAt", "nextWrite")
        c_mod.add_mod("system/controlDict", "writeControl", "timeStep")
        c_mod.add_mod("system/controlDict", "writeInterval", nsteps)

    c_mod.update_case()

    if c_mod.meta_data:
        if "script" not in c_mod.meta_data:
            c_mod.meta_data["script"] = "Allrun -test"
    r_val = os.system(f"{dir_name}/{c_mod.meta_data['script']}")
    c_mod.meta_data['return_value'] = r_val
    c_mod.success = (r_val == 0)
    yield c_mod


@pytest.fixture(scope="class")
def run_reset_case(request):
    """fixture that runs case by exectuting a bash script and reset the case by calling Allclean

    The case can be modified by passing the Case_modifiers class

    Default name is script name Allrun can be modified by storing the script name
    in the meta_data of the Case_modifiers:

    c_mod.meta_data["script"] = "SomeScriptName"

    Yields:
        [Case_modifiers]: Case_modifiers information
    """
    mod_case = hasattr(request, "param")
    dir_name = base_dir()
    c_mod = Case_modifiers({}, dir_name)
    if mod_case:
        c_mod = check_type(request.param)

    nsteps = request.config.getoption("--writeNSteps")
    if nsteps:
        c_mod.add_mod("system/controlDict", "startFrom", "latestTime")
        c_mod.add_mod("system/controlDict", "stopAt", "nextWrite")
        c_mod.add_mod("system/controlDict", "writeControl", "timeStep")
        c_mod.add_mod("system/controlDict", "writeInterval", nsteps)

    c_mod.update_case()

    if c_mod.meta_data:
        if "script" not in c_mod.meta_data:
            c_mod.meta_data["script"] = "Allrun -test"
    r_val = os.system(f"{dir_name}/{c_mod.meta_data['script']}")
    c_mod.meta_data['return_value'] = r_val
    c_mod.success = (r_val == 0)
    yield c_mod

    save_logs(request)

    c_mod.revert_change()
    if request.config.getoption("--no-clean-up"):
        r_val = os.system(f"{dir_name}/Allclean")
        c_mod.meta_data['return_value'] = r_val
        c_mod.success = (r_val == 0)


@pytest.fixture(scope="class")
def modify_case(request):
    """modifies the case without running it

    The case can be modified by passing the Case_modifiers class

    Yields:
        [Case_modifiers]: Case_modifiers information
    """
    mod_case = hasattr(request, "param")
    dir_name = base_dir()
    c_mod = Case_modifiers({}, dir_name)
    if mod_case:
        c_mod = check_type(request.param)

    nsteps = request.config.getoption("--writeNSteps")
    if nsteps:
        c_mod.add_mod("system/controlDict", "startFrom", "latestTime")
        c_mod.add_mod("system/controlDict", "stopAt", "nextWrite")
        c_mod.add_mod("system/controlDict", "writeControl", "timeStep")
        c_mod.add_mod("system/controlDict", "writeInterval", nsteps)

    c_mod.update_case()

    yield c_mod

    c_mod.revert_change()


@pytest.fixture(scope="class")
def clean_case(request):
    """cleans case by running Allcean

    Yields:
        [type]: case modifier
    """
    mod_case = hasattr(request, "param")
    dir_name = base_dir()
    c_mod = Case_modifiers({}, dir_name)
    if mod_case:
        c_mod = check_type(request.param)

    c_mod.revert_change()
    if request.config.getoption("--no-clean-up"):
        r_val = os.system(f"{dir_name}/Allclean")
        c_mod.meta_data['return_value'] = r_val
        c_mod.success = (r_val == 0)

    yield c_mod
