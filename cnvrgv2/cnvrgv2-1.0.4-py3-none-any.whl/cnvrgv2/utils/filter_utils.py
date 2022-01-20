class Operators:
    LIKE = "LIKE"
    GT = ">"
    LT = "<"
    IS = "="


def list_to_multiple_conditions(key, operator, values):
    """
    Will create a list with multiple condition objects
    @param key: The key that will be presented in each condition
    @param operator: The operator to apply in the condition
    @param values: list of values to convert to conditions
    @return: List of conditions
    """
    conditions_list = []
    template_condition = {
            "key": key,
            "operator": operator
        }

    for value in values:
        current_condition = dict(template_condition)
        current_condition["value"] = value
        conditions_list.append(current_condition)

    return conditions_list
