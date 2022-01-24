#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#
"""cobs.py: COBS encoding and decoding for message packets."""

class COBSParser:
    def __init__(self) -> None:
        ...

    @staticmethod
    def encode(data: bytes) -> bytearray:
        encoded = [0x00]
        code_p = 0  # Location of code to write.
        code = 1  # Code to write.
        for byte in data:
            if byte:
                encoded.append(byte)
                code += 1
            if not byte:
                encoded[code_p] = code
                code = 1  # Reset the code.
                code_p = len(encoded)  # Set location for next code.
                encoded.append(0x00)
        encoded[code_p] = code  # Final code.
        return bytearray(encoded)

    @staticmethod
    def decode(data: bytes) -> bytearray:
        decoded = []
        code_p =  0
        code = 0xff
        for byte in data:
            if code_p:  # Decode block byte
                decoded.append(byte)
            else:
                if code != 0xff:  # Encoded zero, write it.
                    decoded.append(0x00)
                code_p = code = byte  # Next block position.
                if not code:  # delimeter
                    break
            code_p -= 1
        return bytearray(decoded)  # Excluding delim

                    
