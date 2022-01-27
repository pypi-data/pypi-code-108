import json
from enum import Enum
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.modeler.core.Run.ParseRun import Parse_MLClassifier
from Accuinsight.modeler.core.Run.ParseRun import Parse_DLRegression
from Accuinsight.modeler.core.Run.ParseRun import Parse_DLClassification
from Accuinsight.modeler.core.Run.ParseRun import Parse_MLRegression


class ModelType(Enum):
    DL_REGRESSION = 1
    DL_CLASSIFICATION = 2
    ML_REGRESSION = 3
    ML_CLASSIFICATION = 4


def run_parser(parser_type, run_info_json):
    if parser_type is ModelType.DL_REGRESSION:
        return Parse_DLRegression.parse_run_result(run_info_json)

    if parser_type is ModelType.DL_CLASSIFICATION:
        return Parse_DLClassification.parse_run_result(run_info_json)

    if parser_type is ModelType.ML_REGRESSION:
        return Parse_MLRegression.parse_run_result(run_info_json)

    if parser_type is ModelType.ML_CLASSIFICATION:
        return Parse_MLClassifier.parse_run_result(run_info_json)


def get_parser_type(run_info_json):
    parser_type = None
    run_result_path = run_info_json[LcConst.RUN_RESULT_PATH]

    # data_path = run_result_path[LcConst.RUN_MODEL_JSON_PATH]
    visual_json_path = None
    visual_csv_path = None

    if LcConst.RUN_MODEL_VISUAL_JSON_PATH in run_result_path:
        visual_json_path = run_result_path[LcConst.RUN_MODEL_VISUAL_JSON_PATH]

    if LcConst.RUN_MODEL_VISUAL_CSV_PATH in run_result_path:
        visual_csv_path = run_result_path[LcConst.RUN_MODEL_VISUAL_CSV_PATH]

    # determine parser type
    if visual_json_path is None and visual_csv_path is not None:
        parser_type = ModelType.DL_REGRESSION

    if visual_json_path is not None and visual_csv_path is not None:
        parser_type = ModelType.DL_CLASSIFICATION

        visual_json_path = run_result_path[LcConst.RUN_MODEL_VISUAL_JSON_PATH]
        with open(visual_json_path) as json_file:
            visual_json_data = json.load(json_file)

        if LcConst.TRUE_Y in visual_json_data:
            parser_type = ModelType.DL_REGRESSION

    if visual_json_path is None and visual_csv_path is None:
        parser_type = ModelType.ML_REGRESSION

    if visual_json_path is not None and visual_csv_path is None:
        parser_type = ModelType.ML_CLASSIFICATION

    return parser_type


