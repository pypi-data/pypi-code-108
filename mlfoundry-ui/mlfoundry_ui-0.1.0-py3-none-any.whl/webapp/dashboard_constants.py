import enum

METRIC_DICT = {
    "cohen_kappa": "Cohen Kappa Score",
    "f1_score": "F1 Score",
    "accuracy": "Accuracy",
    "r2_score": "R2 Score",
    "root_mean_squared_error": "Root Mean Squared Error",
    "mean_squared_error": "Mean Squared Error",
    "mean_absolute_error": "Mean Absolute Error",
    "log_loss": "Log Loss",
    "explained_variance_score": "Variance Score",
}

DATA_SLICES = ["train", "test", "validate", "prediction"]

COLORS = [
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgrey",
    "darkgreen",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
]

BINARY_CLASSIFICATION_MODEL_TYPE = "binary_classification"
MULTICLASS_CLASSIFICATION_MODEL_TYPE = "multiclass_classification"
REGRESSION_MODEL_TYPE = "regression"
TIMESERIES_MODEL_TYPE = "timeseries"

ID_SESSION_STATE_MODEL_VIEW = "id_model"
RUN_NAME_SESSION_STATE_MODEL_VIEW = "run_name_model"
PROJECT_SESSION_STATE_MODEL_VIEW = "project_name_model"
PROJECT_SESSION_STATE_MODEL_COMPARISON = "project_name_comparison"
ACTUAL_PREDICTION_REGRESSION = "actuals_predictions_counts"

MODEL_TYPE_TAG = "modelType"
RUN_NAME_TAG = "run_name"
METRIC_DF_KEY_COL = "key"
METRIC_DF_VALUE_COL = "value"
METRIC_DF_RUNID_COL = "run_id"
METRIC_DF_RUN_NAME_COL = "run_name"

SCHEMA_FILE_NAME = "schema"
SHAP_VALUE_FILE_NAME = "shap"
UNIQUE_COUNTS_FILE_NAME = "unique_count"
STATS_FILE_NAME = "stats"
TIME_SERIES_ACTUAL_PREDS_FILE_NAME = "actuals_prediction"
WHYLOGS_ARTIFACT_DIR = "whylogs"
WHYLOGS_BINEDGES = "bin_edges"
WHYLOGS_COUNTS = "counts"

PRECOMPUTED_METRIC = "pre_computed"
MULTIDIM_METRICS = "multi_dimensional_metrics"
MULTIDIM_METRICS_PRECISION_RECALL = "precision_recall_curve"
MULTIDIM_METRICS_PRECISION = "precision"
MULTIDIM_METRICS_RECALL = "recall"
MULTIDIM_METRICS_ROC = "roc_curve"
MULTIDIM_METRICS_FPR = "fpr"
MULTIDIM_METRICS_TPR = "tpr"
MULTIDIM_METRICS_CONFUSION_MATRIX = "confusion_matrix"


class Pages(enum.Enum):
    SINGLE_RUN_VIEW = "Single Run View"
    RUN_COMPARISON = "Run Comparison"
