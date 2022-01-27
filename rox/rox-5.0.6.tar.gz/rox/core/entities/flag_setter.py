class FlagSetter:
    def __init__(self, flag_repository, parser, experiment_repository, impression_invoker):
        self.flag_repository = flag_repository
        self.parser = parser
        self.experiment_repository = experiment_repository
        self.impression_invoker = impression_invoker

        self.flag_repository.register_flag_added_handler(self.flag_repository_flag_added)

    def flag_repository_flag_added(self, variant):
        exp = self.experiment_repository.get_experiment_by_flag(variant.name)
        self.set_flag_data(variant, exp)

    def set_experiments(self):
        flags_with_condition = []

        for exp in self.experiment_repository.get_all_experiments():
            for flag_name in exp.flags:
                flag = self.flag_repository.get_flag(flag_name)
                if flag is not None:
                    self.set_flag_data(flag, exp)
                    flags_with_condition.append(flag_name)

        for flag in self.flag_repository.get_all_flags().values():
            if flag.name not in flags_with_condition:
                self.set_flag_data(flag)

    def set_flag_data(self, variant, experiment=None):
        variant.set_for_evaluation(self.parser, self.impression_invoker, experiment)
