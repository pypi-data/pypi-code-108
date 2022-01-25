class DatabricksJobInstance:
    def __init__(self,
                 job_name: str,
                 job_id: str = None,
                 jar_params: str = None,
                 notebook_params: str = None,
                 python_params: str = None,
                 spark_submit_params: str = None):
        self.job_name = job_name
        self.job_id = job_id
        self.jar_params = jar_params
        self.notebook_params = notebook_params
        self.python_params = python_params
        self.spark_submit_params = spark_submit_params
