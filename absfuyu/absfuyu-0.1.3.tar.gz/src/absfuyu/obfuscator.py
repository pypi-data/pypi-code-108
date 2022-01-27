#!/usr/bin/env python
# coding: utf-8
"""
Obfuscator Module
-----------------
"""



# Module level
##############################################################
__all__ = [
    "toSingleLine", "obfuscate", "toTxt",
]



# Library
##############################################################
import base64
import codecs
from typing import List, Union
import zlib

from absfuyu import generator as gen
from absfuyu import strings as ss



# Function
##############################################################


def toSingleLine(your_code: str = "") -> str:
    """
    Summary
    -------
    Convert multiple lines of code into single line

    Parameters
    ----------
    your_code : str
        Multiple line of code

    Returns
    -------
    str
        Execution hex string
    """

    newcode = your_code.encode('utf-8').hex()
    #newcode = ss.strHex(yourcode,"normal")
    output = f"exec(bytes.fromhex('{newcode}').decode('utf-8'))"
    return output

# in dev
def _obfuscate_base(
        your_code: str,
        encode_option: str = "full",
        encode_codec: str = "rot_13",
    ) -> Union[str, None]:
    """
    Summary
    -------
    Convert multiple lines of code through multiple transformation
    (base64 -> compress -> base64 -> caesar (13))

    Parameters
    ----------
    your_code : str
        Multiple line of code
    
    encode_option : str
        "full": base64, compress, rot13 (default)
        "b64": encode in base64 form only
    
    encode_codec : str
        "rot_13": the only option (for now)

    Returns
    -------
    str
        Obfuscated string
    """

    encode_opt = {
        "b64":0,
        "full":1
    }
    # b64: encode in base64 form only
    # full: base64, compress, rot13
    
    # Currently, there is only one encode codec
    encode_codec_opt = ["rot_13"]
  
    if encode_option not in encode_opt:
        return None # break if invalid option
    else:
        ec_opt = encode_opt[encode_option]
    
    if encode_codec not in encode_codec_opt:
        return None
    

    if ec_opt == 0: #b64
        txte = base64.b64encode(str.encode(your_code)).decode()
    
    # convert code to base64 -> compress -> convert to base64 -> rot13
    elif ec_opt == 1: #full
        b64text = base64.b64encode(your_code.encode())
        txtcomp = zlib.compress(b64text)
        b64t2 = base64.b64encode(txtcomp)
        txte = codecs.encode(b64t2.decode(), encode_codec)
    
    return txte


def _obfuscate_out(
        your_code: str,
        encode_option: str = "full",
        encode_codec: str = "rot_13",
        str_splt: int = 60,
        var_len: int = 12,
        fake_data: bool = False,
        *arg, **kwarg
    ) -> Union[List[str], None]:
    """
    Summary
    -------
    Convert multiple lines of code through multiple transformation
    (base64 -> compress -> base64 -> caesar (13))
    
    Then return a list (obfuscated code) that can
    be print or export into .txt file

    Parameters
    ----------
    your_code : str
        Multiple line of code
    
    encode_option : str
        "full": base64, compress, rot13 (default)
        "b64": encode in base64 form only
    
    encode_codec : str
        "rot_13": the only option (for now)
    
    str_splt : int
        split the long line of code every x character
        (default: x = 60)
    
    var_len : int
        Length of variable name
        (default: 12)
    
    fake_data : bool
        generate additional meaningless data
        (dafault: False)

    Returns
    -------
    list
        Obfuscated list that ready to print
    """
    
    encode_opt = {
        "b64":0,
        "full":1
    }
    # b64: encode in base64 form only
    # full: base64, compress, rot13
    
    # Currently, there is only one encode codec
    encode_codec_opt = ["rot_13"]
  
    if encode_option not in encode_opt:
        return None # break if invalid option
    else:
        ec_opt = encode_opt[encode_option]
    
    if encode_codec not in encode_codec_opt:
        return None

    
    # Obfuscate code
    input_str = _obfuscate_base(
        your_code,
        encode_option,
        encode_codec
    )

    if input_str is None:
        return None
    
    # ==================================
    # Generate output
    output = []

    # Output option:
    # variable length parameter - can change
    out_dct = {
        "lib_func_var_len": var_len-1,
        "split_var_len": var_len,
        "decode_var_len": var_len+3
    }

    # import library
    lib_lst = ["base64","codecs","zlib"]
    lib_func_len = out_dct["lib_func_var_len"]
    lib_func = gen.randStrGen(
                    lib_func_len,
                    len(lib_lst),
                    char="alphabet")
    lib_dct = dict(zip(lib_lst,lib_func))

    if ec_opt == 0: #b64
        lib_hex = "import " + lib_lst[0]
        lib_hex_f = ss.strHex(lib_hex)
        output.append(f"exec('{lib_hex_f}')")
    
    elif ec_opt == 1: #full
        temp = []
        for i, v in enumerate(lib_lst):
            temp.append(f"import {v}")
        lib_hex = "\n".join(temp)
        lib_hex_f = ss.strHex(lib_hex) # convert to hex
        output.append(f"exec('{lib_hex_f}')")

    # append divided long text list
    splt_var_len = out_dct["split_var_len"]
    input_lst = ss.strDivVar(input_str,str_splt,splt_var_len)
    encoded_str = input_lst[-1] # Main var name that will later be used
    for i in range(len(input_lst)):
        if i != len(input_lst)-1:
            output.append(input_lst[i])
    
    # decode: encoded_str
    dc_var_len = out_dct["decode_var_len"]
    dc_name_lst = gen.randStrGen(dc_var_len,3,char="alphabet")
    if ec_opt == 1: #full
        b64c = base64.b64encode(encode_codec.encode()).decode()
        b64dc = f"base64.b64decode('{b64c}'.encode())"
        hex_0 = ss.strHex(b64dc)
        output.append(f"{dc_name_lst[0]}=eval('{hex_0}').decode()")
    hex_1 = ss.strHex("<string>")
    output.append(f"{dc_name_lst[1]}='{hex_1}'")
    hex_2 = ss.strHex("exec")
    output.append(f"{dc_name_lst[2]}='{hex_2}'")

    if ec_opt == 0: #b64
        #eval(compile(base64.b64decode(txtdcomp),'<string>','exec'))
        temp = []
        temp.append(f"eval(compile(base64.")
        temp.append(f"b64decode({encoded_str}),{dc_name_lst[1]},")
        temp.append(f"{dc_name_lst[2]}))")
        preHex = "".join(temp)
        t_hex = ss.strHex(preHex)
        output.append(f"exec('{t_hex}')")
    
    elif ec_opt == 1: #full
        temp = []
        temp.append(f"eval(compile(base64.")
        temp.append(f"b64decode(zlib.decompress(base64.")
        temp.append(f"b64decode(codecs.")
        temp.append(f"encode({encoded_str},{dc_name_lst[0]}).")
        temp.append(f"encode()))),{dc_name_lst[1]},{dc_name_lst[2]}))")
        preHex = "".join(temp)
        t_hex = ss.strHex(preHex)
        output.append(f"exec('{t_hex}')")
    
    if fake_data:
        f1 = gen.randStrGen(len(input_str))
        f2 = ss.strDivVar(f1,str_splt,out_dct["split_var_len"])
        for i, v in enumerate(f2):
            if i != len(f2)-1:
                output.append(v)
        bait_lst = gen.randStrGen(out_dct["split_var_len"],25,char="alphabet")
        for x in bait_lst:
            output.append(f"{x}='{gen.randStrGen(str_splt,1,string_type_if_1=True)}'")

    return output



def obfuscate(
        your_code: str,
        oneLine: bool = False,
        str_splt: List[int] = [10,80],
        var_len: int = 12,
    ) -> Union[str, None]:
    """
    Summary
    -------
    Fully obsfucate code in 2 phase

    Parameters
    ----------
    your_code : str
        Multiple line of code
    
    oneLine : bool
        return 1 line of code when True
        
    str_splt : list[int] with 2 items
        split the long line of code every
        x[0] character in phase 1;    
        split the long line of code every
        x[1] character in phase 1
        (default: x = [10,80])
    
    var_len : int
        Length of variable name
        (default: 12)

    Returns
    -------
    str
        An obfuscated string
    """

    obfus1 = _obfuscate_out(
                your_code,
                "full",
                str_splt=str_splt[0],
                var_len=var_len,
                fake_data=True)
    obfus1c = ""
    for x in obfus1:
        obfus1c += x+"\n"
    
    obfus2 =  _obfuscate_out(
                obfus1c,
                "b64",
                str_splt=str_splt[1],
                var_len=var_len)
    obfus2c = ""
    for x in obfus2:
        obfus2c += x+"\n"
    
    if not oneLine:
        return obfus2c
    else:
        return toSingleLine(obfus2c)



def toTxt(
        text_list: Union[list,str],
        txt_name: str = "code",
        txt_path: str = "",
        txt_format: str = "txt",
        additional_text: str = "",
    ) -> None:
    """
    Summary
    -------
    Write items from a list to text file

    Parameters
    ----------
    text_list : list or str
        text list need to write
    
    txt_name : str
        name for the output file
        (default: "code")
    
    txt_path : str
        location to export
    
    txt_format : str
        text extension (like .txt or .py)
    
    additional_text : str
        add additional text at the end of file

    Returns
    -------
    a file on the computer
        Exported text file
    """

    # format_option = ["txt","py"]
    
    txtfile = open(f"{txt_path}\{txt_name}.{txt_format}","w")
    txtfile = open(f"{txt_path}\{txt_name}.{txt_format}","a")

    if isinstance(text_list, str):
        for i in range(len(text_list)):
            txtfile.writelines(str(text_list[i]))
    else:
        for i in range(len(text_list)):
            txtfile.writelines(str(text_list[i])+"\n")
    
    txtfile.writelines(str(additional_text))

    return None


if __name__ == "__main__":
    pass