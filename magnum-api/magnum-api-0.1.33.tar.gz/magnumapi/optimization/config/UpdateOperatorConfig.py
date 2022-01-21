from dataclasses import dataclass


@dataclass
class OperatorConfig:
    type: str
    params: dict


@dataclass
class UpdateOperatorConfig:
    type: str
    params: dict
    mutation_operator: OperatorConfig
    selection_operator: OperatorConfig
    crossover_operator: OperatorConfig

    def __str__(self) -> str:
        return "type: %s\n" \
               "params: %s\n" \
               "mutation_operator: %s\n" \
               "selection_operator: %s\n" \
               "crossover_operator: %s\n" % (self.type,
                                             self.params,
                                             self.mutation_operator,
                                             self.selection_operator,
                                             self.crossover_operator)

    @staticmethod
    def initialize_config(config_dct: dict) -> "UpdateOperatorConfig":
        return UpdateOperatorConfig(type=config_dct['type'],
                                    params=config_dct['params'],
                                    mutation_operator=OperatorConfig(**config_dct['mutation_operator']),
                                    selection_operator=OperatorConfig(**config_dct['selection_operator']),
                                    crossover_operator=OperatorConfig(**config_dct['crossover_operator']))
