from rox.core.entities.default_flag_values import DefaultFlagValues

class NormalizeFlagType:
    @staticmethod
    def normalize_string(string_value):
        return string_value

    @staticmethod
    def normalize_int(string_value):
        try:
            return int(string_value)
        except ValueError:
            return DefaultFlagValues.INT

    @staticmethod
    def normalize_float(string_value):
        try: 
            return float(string_value)
        except ValueError:
            return DefaultFlagValues.FLOAT
