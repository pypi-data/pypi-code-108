def percentage(value, per_value):
    per_result = (value * per_value)/100
    return per_result


def percentage_increase(value, increase_value):
    increase_result = value + (value * increase_value/100)
    return increase_result


def percentage_decrease(value, decrease_value):
    decrease_result = value - (value * decrease_value/100)
    return decrease_result
