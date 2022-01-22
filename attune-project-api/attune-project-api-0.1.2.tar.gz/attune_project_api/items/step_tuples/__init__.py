import re

stepNiceNames = {}
STEP_TYPES = {}


def addStepDeclarative(niceName):
    def f(cls):
        cls.NICE_NAME = niceName
        stepNiceNames[cls.tupleType()] = niceName
        STEP_TYPES[cls.tupleType()] = cls
        return cls

    return f


def extractTextPlaceholders(text):
    # NOTE, Duplicated client side, AttunePlaceholderMod.js,
    # $scope.textPhName = function () { ...
    return re.findall(r"(?<![$]){([A-Za-z0-9_.]+)}", text)


def loadStorageStepTuples():
    from . import step_sql_oracle_tuple
    from . import step_tuple
    from . import step_bootstrap_linux_tuple
    from . import step_push_design_file_compiled_tuple
    from . import step_group_tuple
    from . import step_push_design_file_tuple
    from . import step_ssh_tuple
    from . import step_ssh_prompted_tuple
    from . import step_winrm_tuple
    from . import step_tcp_ping_tuple
    from . import step_project_link_tuple
