import math

from simses.commons.constants import Hydrogen


class AlkalineFluidModel:   # TODO: more detailed approach with losses instead of just Faraday

    def __init__(self):
        self.__koh_weight_concentration = 30

    def __h2_generation_cell(self, current_cell) -> float:
        return current_cell / (2 * Hydrogen.FARADAY_CONST)  # mol/s

    def __o2_generation_cell(self, current_cell) -> float:
        return current_cell / (4 * Hydrogen.FARADAY_CONST)  # mol/s

    def __h2o_use_cell(self, current_cell) -> float:
        return current_cell / (2 * Hydrogen.FARADAY_CONST)  # mol/s

    def __molarity(self, stack_temperature) -> float:
        # Calculate molarity of KOH electrolyte
        # (From "A review of specific conductivities of potassium hydroxide solution for various concentrations and temperatures" by R.J. Gilliam et al)
        molarity = (self.__koh_weight_concentration * (
                183.1221 - 0.56845 * stack_temperature + 984.5679 * math.exp(self.__koh_weight_concentration / 115.96277))) / (
                           100 * 56.105)
        return molarity

    def get_h2_generation_cell(self, current_cell) -> float:
        return self.__h2_generation_cell(current_cell)

    def get_o2_generation_cell(self, current_cell) -> float:
        return self.__o2_generation_cell(current_cell)

    def get_h2o_use_cell(self, current_cell) -> float:
        return self.__h2o_use_cell(current_cell)

    def get_molarity(self, stack_temperature) -> float:
        return self.__molarity(stack_temperature)
