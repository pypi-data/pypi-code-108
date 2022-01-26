def get_tiny_dag():

    stages = []
    return stages

def get_flat_dag():

    stages = []
    return stages


def get_multi_output_flat_dag(n_jobs=-1):

    stages = []
    return stages


def get_multi_output_tiny_dag(n_jobs=-1):

    stages = []
    return stages


def get_regression_chain_flat_dag():

    stages = []
    return stages

def get_regression_chain_tiny_dag():
    
    stages = []
    return stages


def get_MIMO_flat_dag():

    stages = []
    return stages

def get_MIMO_complete_flat_dag():

    stages = []
    return stages

def get_xgboost_multi_dag(n_jobs=-1):

    stages = []
    return stages

def get_lgbm_multi_dag(n_jobs=-1):

    stages = []
    return stages

def get_xgb_dag():

    stages = []
    return stages

def get_lgbm_dag():

    stages = []
    return stages



tiny_reg_dag = get_tiny_dag()
flat_reg_dag = get_flat_dag()
multi_output_flat_dag = get_multi_output_flat_dag()
multi_output_tiny_dag = get_multi_output_tiny_dag()
regression_chain_flat_dag = get_regression_chain_flat_dag()
regression_chain_tiny_dag = get_regression_chain_tiny_dag()
mimo_flat_dag = get_MIMO_flat_dag()
complete_mino_flat_dag = get_MIMO_complete_flat_dag()
xgb_dag = get_xgb_dag()
xgboost_multi_dag = get_xgboost_multi_dag()
try:
    lgbm_multi_dag = get_lgbm_multi_dag()
except:
    lgbm_multi_dag = None
try:
    lgbm_dag = get_lgbm_dag()
except:
    lgbm_dag = None