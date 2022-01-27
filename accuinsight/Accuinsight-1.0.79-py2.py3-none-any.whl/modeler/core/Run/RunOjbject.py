from Accuinsight.modeler.core.LcConst.LcConst import RUN_OBJ_NAME, RUN_OBJ_JSON_PATH, RUN_OBJ_SHAP_PATH, \
    RUN_OBJ_CSV_PATH, SOURCE_FILE_PATH, SOURCE_FILE_NAME, SOURCE_FILE_DIGEST, SOURCE_FILE_GIT_REPO,\
    SOURCE_FILE_GIT_COMMIT_ID, SOURCE_FILE_IS_DIRTY, PYTHON_DEPENDENCY


class RunObject:
    def __init__(self, run_obj={}):
        self.run_obj = run_obj

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def set_json_path(self, json_path):
        self.run_obj[RUN_OBJ_JSON_PATH] = json_path

    def set_csv_path(self, csv_path):
        self.run_obj[RUN_OBJ_CSV_PATH] = csv_path

    def set_shap_path(self, shap_path):
        self.run_obj[RUN_OBJ_SHAP_PATH] = shap_path

    def set_run_name(self, run_name):
        self.run_obj[RUN_OBJ_NAME] = run_name

    def set_run_file_path(self, run_file_path):
        self.run_obj[SOURCE_FILE_PATH] = run_file_path

    def set_run_file_name(self, run_file_name):
        self.run_obj[SOURCE_FILE_NAME] = run_file_name

    def set_run_file_md5_hash(self, digest):
        self.run_obj[SOURCE_FILE_DIGEST] = digest

    def set_run_file_git_repo(self, git_url):
        self.run_obj[SOURCE_FILE_GIT_REPO] = git_url

    def set_run_file_git_commit_id(self, git_commit_id):
        self.run_obj[SOURCE_FILE_GIT_COMMIT_ID] = git_commit_id

    def set_run_file_git_is_dirty(self, isdirty):
        self.run_obj[SOURCE_FILE_IS_DIRTY] = isdirty

    def set_run_file_python_dependency(self, dependency):
        self.run_obj[PYTHON_DEPENDENCY] = dependency
