from tktl.core import ExtendedEnum


class TemplateT(str, ExtendedEnum):
    REPAYMENT = "repayment"
    BARE = "bare"
    PRECOMPUTED = "precomputed"


class UserRepoConfigFileNameT(str, ExtendedEnum):
    YAML = "tktl.yaml"
    YML = "tktl.yml"


class UserProjectFileT(str, ExtendedEnum):
    FILE = "file"
    DIRECTORY = "dir"


class RequiredUserProjectPathsT(str, ExtendedEnum):
    SRC = "src"
    ASSETS = "assets"
    TESTS = "tests"
    TKTL_YML = "tktl.yml"
    TKTL_YAML = "tktl.yaml"
    DOCKERFILE = ".buildfile"
    REQS = "requirements.txt"

    @classmethod
    def strictly_required_files(cls):
        return {cls.DOCKERFILE.value, cls.REQS.value}

    @classmethod
    def strictly_required_dirs(cls):
        return {cls.SRC.value, cls.ASSETS.value}


class DeploymentStateFailed(str, ExtendedEnum):
    BUILDING_FAILED = "building_failed"
    DEPLOYING_FAILED = "deploying_failed"
    ROUTING_FAILED = "routing_failed"
    PROFILING_FAILED = "profiling_failed"
    ERRORED = "errored"


class DeploymentStateSucceed(str, ExtendedEnum):
    RUNNING = "running"


class DeploymentStatePending(str, ExtendedEnum):
    BUILDING = "building"
    DEPLOYING = "deploying"
    ROUTING = "routing"
    PROFILING = "profiling"


class DeploymentStatesT(str, ExtendedEnum):

    BUILDING = "building"
    DEPLOYING = "deploying"
    ROUTING = "routing"
    PROFILING = "profiling"
    RUNNING = "running"
    DELETED = "deleted"

    BUILDING_FAILED = "building_failed"
    DEPLOYING_FAILED = "deploying_failed"

    ROUTING_FAILED = "routing_failed"
    PROFILING_FAILED = "profiling_failed"

    # Error after entering the running state
    ERRORED = "errored"


class ProjectAssetT(str, ExtendedEnum):
    DATA = "data"
    MODEL = "model"


class ProjectAssetSourceT(str, ExtendedEnum):
    S3 = "s3"
    LOCAL = "local"
    LFS = "lfs"


class EndpointKinds(str, ExtendedEnum):
    CUSTOM = "custom"
    TABULAR = "tabular"
    BINARY = "binary"
    REGRESSION = "regression"
    MULTICLASS = "multiclass"


class RestSchemaTypes(ExtendedEnum):
    DICT = "Dict"
    SEQUENCE = "Sequence"
    ARRAY = "Array"
    FLAT_ARRAY = "FlatArray"
    SERIES = "Series"
    DATAFRAME = "DataFrame"
    SINGLE_VALUE = "SingleValue"
    CUSTOM_MODEL = "CustomModel"
    ANY = "Any"


class AccessKind(str, ExtendedEnum):
    # see also corresponding AccessKind on t-api
    OWNER = "owner"
    VIEWER = "viewer"


class LazifyType(str, ExtendedEnum):
    """Type of lazification to be performed"""

    SHAP = "Shap"
    FIRST_VALID = "FirstValid"
