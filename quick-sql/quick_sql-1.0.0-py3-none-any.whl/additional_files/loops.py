from errors import *
from table import *

def columns_loop(list_of_col):
    length=len(list_of_col)
    return_output = ""
    count = 0
    if type(list_of_col) != list:
        raise ValueError("Only list are allowed")

    else:
        for i in list_of_col:
            count += 1
            if count != length:
                return_output += str(i) + ","

            else:
                return_output += str(i)

    return return_output

def data_loop(list_of_data):
    length = len(list_of_data)
    return_output = ""
    count = 0 

    if type(list_of_data) != list:
        raise ListError("Only list are allowed")

    else:
        for i in list_of_data:
            count += 1
            if type(i) == str:
                if count != length:
                    return_output += "\'" + i + "\'" + ","

                else:
                    return_output += "\'" + i + "\'"
                
            else:
                if count != length:
                    return_output += str(i) + ","

                else:
                    return_output += str(i)

    return return_output

def update_loop(list_of_colData):
    length = len(list_of_colData)
    return_output = ""
    count = 0

    if type(list_of_colData) != list:
        raise ListError("Only list are allowed")

    else:
        if length == 2:
            for i in list_of_colData:
                count += 1
                if i == list_of_colData[0]:
                    return_output += str(i) + "="
                
                elif i == list_of_colData[1] and type(i) == int:
                    return_output += str(i)

                else:
                    return_output += "\'"+ str(i) + "\'"

        else:
            raise ListLengthError("Length of list must be equal to 2")

    return return_output


def update_loop_str(param):
    if type(param) == int:
        return str(param)
    else:
        return "\'" + param +"\'"


