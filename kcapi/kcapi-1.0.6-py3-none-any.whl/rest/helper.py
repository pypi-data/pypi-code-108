def ValidateParams(param_list, params): 
    for param in param_list: 
        if param not in params:
            raise Exception("Missing parameter: " + param)
    return True    


