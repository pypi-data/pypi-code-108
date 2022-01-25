VALUE = "value"
CONVERTED = "is_converted"


class State:
    def __init__(self):
        self.params = dict()
        self.config = dict()

    def load_params(self, params):
        for key, value in params.items():
            if value is not None:
                self.params[key] = {VALUE: value, CONVERTED: False}


class StatefulParam:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def add_converted_to_state(self, state, value):
        if value is not None:
            state.params[self.name] = {VALUE: value, CONVERTED: True}

    def get_param_value_from_state(self, state, ctx):
        param_state = state.params[self.name]
        if param_state[CONVERTED]:
            return param_state[VALUE]
        else:
            return self.type.convert(param_state[VALUE], self, ctx)

    def get_config_value_from_state(self, state, ctx):
        return self.type.convert(state.config[self.name], self, ctx)
