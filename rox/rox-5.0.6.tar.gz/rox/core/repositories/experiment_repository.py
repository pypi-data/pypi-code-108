class ExperimentRepository:
    def __init__(self):
        self.experiments = []

    def set_experiments(self, experiments):
        self.experiments = experiments

    def get_experiment_by_flag(self, flag_name):
        return next((e for e in self.experiments if flag_name in e.flags), None)

    def get_all_experiments(self):
        return self.experiments
