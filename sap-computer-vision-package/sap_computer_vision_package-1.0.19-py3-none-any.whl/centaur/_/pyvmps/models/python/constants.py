class ExporterVar:
    """ExporterVar."""

    config_file_name = "config.json"
    interface_file_name = "interface.py"
    source_dir = "source/"
    assets_dir = "assets/"
    vendor_dir = "vendor/"
    pip_dependencies_file_name = "pip_dependencies.txt"

    initialize_func_name = "initialize"
    predict_func_name = "predict"
    classify_func_name = "classify"
    explain_func_name = "explain"
    regress_func_name = "regress"
    supported_verbs = ("predict", "classify", "explain", "regress")


class PickledModel:
    """PickledModel."""

    config_file_name = "config.json"
    pickled_file_name = "func.pkl"
    initialize_func_name = "initialize"
    predict_func_name = "predict"
    modules_dir = "source/"
    pip_dependencies_file_name = "pip_dependencies.txt"
