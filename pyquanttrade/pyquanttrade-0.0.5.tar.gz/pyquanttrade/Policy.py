class Policy:
    """
    Represents the mathematical rationale of a quantitative investing strategy

    Attributes
    ----------
    long_stop_loss : float
        Stop loss when the position is long
    short_stop_loss : float
        Stop loss when the position is short
    long_stop_loss_trailling : float
        Trailling stop loss when the position is long
    short_stop_loss_trailling : float
        Trailling stop loss when the position is short

    Methods
    -------
    execute(cls, day, data, trades)
        Returns the investing actions to take
    sell_short_when()
        Returns the function to analyse of a short position should be opened
    buy_long_when()
        Returns the function to analyse if a long position should be opened
    close_short_when()
        Returns the functions to analyse if a short position should be closed
    close_long_when()
        Returns the functions to analyse if a long position should be closed
    """

    plot_functions = []

    long_stop_loss = 1
    short_stop_loss = 1
    long_stop_loss_trailling = False
    short_stop_loss_trailling = False

    ticker = "Hello"  # This remains so that the system does not break

    @staticmethod
    def sell_short_when():
        return lambda day, ticker, trades, data: False

    @staticmethod
    def buy_long_when():
        return lambda day, ticker, trades, data: False

    @staticmethod
    def close_short_when():
        return lambda day, ticker, trades, data: False

    @staticmethod
    def close_long_when():
        return lambda day, ticker, trades, data: False

    @classmethod
    def execute(cls, day, data, trades):
        actions = []

        f = cls.close_long_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Close_long"]

        f = cls.close_short_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Close_short"]

        f = cls.sell_short_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Sell_short"]

        f = cls.buy_long_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Buy_long"]

        return actions


def build_policy(policy_dict):
    created_policy = type(policy_dict["name"], (Policy,), {})
    for attribute in policy_dict["policy"]["parameters"]:
        setattr(
            created_policy, attribute, policy_dict["policy"]["parameters"][attribute]
        )
    for function in policy_dict["policy"]["functions"]:
        function_definition = policy_dict["policy"]["functions"][function]
        setattr(
            created_policy, function, lambda: set_head_function(function_definition)
        )
    return created_policy


def set_head_function(function_definition):
    module_name = next(iter(function_definition))
    function_name = function_definition[module_name]
    params_definition = function_definition["params"]
    params = []
    head_function = getattr(globals()[module_name], function_name)
    for param in params_definition:
        if next(iter(param)) in ["functions", "indicators"]:
            params.append(set_head_function(param))
        else:
            params.append(next(iter(param.values())))
    return head_function(*params)
