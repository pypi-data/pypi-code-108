#!/usr/bin/env python
# coding: utf-8


from . import generator as gen

__all__ = [
    "strDiv","strAna",
    # "strDivVar",
]

# String divide
def strDiv(your_string,string_split_size=60):
    output = []
    while True:
        if len(your_string) == 0:
            break
        output.append(your_string[:string_split_size])
        your_string = your_string[string_split_size:]
    return output
    
# String analyze
def strAna(your_string):
    detail = {
        "digit": 0,
        "uppercase": 0,
        "lowercase": 0,
        "other": 0
    }

    for x in your_string:
        if ord(x) in range(48,58): #num
            detail["digit"] += 1
        elif ord(x) in range(65,91): #cap
            detail["uppercase"] += 1
        elif ord(x) in range(97,123): #low
            detail["lowercase"] += 1
        else:
            detail["other"] += 1
    
    return detail
    


def strDivVar(string_or_list,split_size=60,split_var_len=12):
    if type(string_or_list) is str:
        temp = strDiv(string_or_list,split_size)
    elif type(string_or_list) is list:
        temp = string_or_list
    else:
        temp = list(string_or_list)
    output = []
    
    # split variable
    splt_var_len = split_var_len
    splt_len = len(temp)
    splt_name = gen.randStrGen(splt_var_len,splt_len+1)
    for i in range(splt_len):
        output.append(f"{splt_name[i]}='{temp[i]}'")
    
    # joined variable
    temp = []
    for i in range(splt_len):
        if i == 0:
            temp.append(f"{splt_name[-1]}=")
        if (i == splt_len-1):
            temp.append(f"{splt_name[i]}")
        else:
            temp.append(f"{splt_name[i]}+")
    
    output.append("".join(temp))
    output.append(splt_name[-1])
    return output



# Convert string to hex form
def strHex(your_string,output_opt="x"):
    output_option = {
        "normal":0,
        "x":1
    }
    # normal: normal hex string | x: hex string in the form of \x

    outopt = output_option[output_opt]
    
    byte_str = your_string.encode('utf-8')
    hex_str = byte_str.hex()
    
    if outopt == 0:
        return hex_str
    
    elif outopt == 1:
        temp = []
        str_len = len(hex_str)

        for i in range(str_len):
            if i % 2 == 0:
                temp.append(f"\\x")
            temp.append(hex_str[i])
        return ''.join(temp)