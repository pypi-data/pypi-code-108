#!/usr/bin/env python
# coding: utf-8


import base64
import codecs
import zlib
from . import generator as gen
from . import string as ss

__all__ = [
    "toSingleLine",
]


# convert multiple lines of code into single line
def toSingleLine(yourcode):
    newcode = yourcode.encode('utf-8').hex()
    #newcode = ss.strHex(yourcode,"normal")
    output = f"exec(bytes.fromhex('{newcode}').decode('utf-8'))"
    return output

# in dev
def obfuscate_base(
    your_code,
    encode_option="full",
    encode_codec="rot_13",):

    encode_opt = {
        "b64":0,
        "full":1
    }
    # b64: encode in base64 form only
    # full: base64, compress, rot13
    encode_codec_opt = ["rot_13"]
  
    if encode_option not in encode_opt:
        return -1 # break if invalid option
    else:
        ec_opt = encode_opt[encode_option]
    
    if encode_codec not in encode_codec_opt:
        return -1
    

    if ec_opt == 0:
        txte = base64.b64encode(str.encode(your_code)).decode()
    
    # convert code to base64 -> compress -> convert to base64 -> rot13
    elif ec_opt == 1:
        b64text = base64.b64encode(your_code.encode())
        txtcomp = zlib.compress(b64text)
        b64t2 = base64.b64encode(txtcomp)
        txte = codecs.encode(b64t2.decode(), encode_codec)
    
    return txte

# in dev
def obfuscate_out(
    your_code,
    encode_option="full",
    encode_codec="rot_13",
    str_splt=60,
    *arg, **kwarg):

    input_str = obfuscate_base(your_code,
                               encode_option,
                               encode_codec)
    
    output = []

    # variable length parameter - can change
    out_dct = {
        "lib_func_var_len": 11,
        "split_var_len": 12,
        "decode_var_len": 15
    }

    # import library
    lib_lst = ["base64","codecs","zlib"]
    lib_func_len = out_dct["lib_func_var_len"]
    lib_func = gen.randStrGen(lib_func_len,len(lib_lst))
    lib_dct = dict(zip(lib_lst,lib_func))

    demo = """
        eval(compile(base64.b64decode(zlib.decompress(base64.b64decode(codecs.encode(txte,"rot_13").encode()))),<string>,exec))
    """
    pass