class DatabricksJob:
    def __init__(self, job_dict: dict):
        self.job_dict = job_dict

    @property
    def job_name(self) -> str: return self.job_dict['settings']['name']
