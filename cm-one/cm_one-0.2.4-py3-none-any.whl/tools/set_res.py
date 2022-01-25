# Based on
# https://github.com/ravenscroftj/SPE/blob/master/sm/__init__.py

# Execute from any test script as an external process:
# https://kb.froglogic.com/display/KB/Article+-+Executing+external+applications

# Execute on a remote system through "squish_dir/bin/squishserver":
# https://doc.froglogic.com/squish/latest/rgs-squish.html#rgs-remotesystem


import ctypes
import struct
import sys


def set_res(width, height, bpp=32):
    DM_BITSPERPEL = 0x00040000
    DM_PELSWIDTH = 0x00080000
    DM_PELSHEIGHT = 0x00100000
    CDS_UPDATEREGISTRY = 0x00000001
    SIZEOF_DEVMODE = 148

    user32 = ctypes.WinDLL('user32.dll')
    DevModeData = (struct.calcsize("32BHH") * '\x00').encode("utf-8")
    DevModeData += struct.pack("H", SIZEOF_DEVMODE)
    DevModeData += (struct.calcsize("H") * '\x00').encode("utf-8")
    dwFields = (width and DM_PELSWIDTH or 0) | (height and DM_PELSHEIGHT or 0) | (bpp and DM_BITSPERPEL or 0)
    DevModeData += struct.pack("L", dwFields)
    DevModeData += (struct.calcsize("l9h32BHL") * '\x00').encode("utf-8")
    DevModeData += struct.pack("LLL", bpp or 0, width or 0, height or 0)
    DevModeData += (struct.calcsize("8L") * '\x00').encode("utf-8")
    result = user32.ChangeDisplaySettingsA(DevModeData, CDS_UPDATEREGISTRY)
    return result == 0 # success if zero, some failure otherwise


#if __name__ == "__main__":
#    result = set_res(int('1920'), int('1080'))
#    print(sys.argv[1], type(sys.argv[1]))
#    sys.exit(result)
