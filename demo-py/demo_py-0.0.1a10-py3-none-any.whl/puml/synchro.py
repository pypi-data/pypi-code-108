# Python implementation of: 
#   https://plantuml.com/synchro2.min.js
# See also ... 
#   * encoded-entry.html
#   * pako.js

# https://careerkarma.com/blog/python-indexerror-list-assignment-index-out-of-range/
# https://stackoverflow.com/questions/5653533/why-does-this-iterative-list-growing-code-give-indexerror-list-assignment-index


import zlib


def generate6BitEncodingMap():
    r = {}
    for i in range(0, 64):
        if (i < 10):
            # digits
            r[i] = chr(0x30 + i); 
        elif (i < 36):
            # uppercase letters
            r[i] = chr(0x41 + (i - 10))
        elif (i < 62):
            # lowercase letters
            r[i] = chr(0x61 + (i - 36))
        elif (i == 62):
            r[i] = '-'
        else: 
            r[i] = '_'
    return r


def generate6BitDecodingMap(encodingMap):
    return {
        e: i
        for i, e in encodingMap.items()
    }


SIXBIT_ENCODING_MAP = generate6BitEncodingMap()
SIXBIT_DECODING_MAP = generate6BitDecodingMap(SIXBIT_ENCODING_MAP)


def append3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    r = ""
    r += SIXBIT_ENCODING_MAP[c1 & 0x3F]
    r += SIXBIT_ENCODING_MAP[c2 & 0x3F]
    r += SIXBIT_ENCODING_MAP[c3 & 0x3F]
    r += SIXBIT_ENCODING_MAP[c4 & 0x3F]
    return r


def decode3bytes(r, cc1, cc2, cc3, cc4):
    c1 = SIXBIT_DECODING_MAP[cc1]
    c2 = SIXBIT_DECODING_MAP[cc2]
    c3 = SIXBIT_DECODING_MAP[cc3]
    c4 = SIXBIT_DECODING_MAP[cc4]
    yield ((c1 << 2) | (c2 >> 4))
    yield (((c2 & 0x0F) << 4) | (c3 >> 2))
    yield (((c3 & 0x3) << 6) | c4)


def encode(data):
    # print(type(data), data, data[2])
    r = ""
    for i in range(0, len(data), 3):
        if (i + 2 == len(data)):
            r += append3bytes(data[i], data[i + 1], 0)
        elif (i + 1 == len(data)):
            r += append3bytes(data[i], 0, 0)
        else:
            r += append3bytes(data[i], data[i + 1], data[i + 2])
    return r


def decode(s):
    if not ( (len(s) % 4) == 0 ):
        raise Exception("Failed decoding: [" + s + "]")
    r = []
    for i in range(0, len(s), 4):
        for b in decode3bytes(
            r,
            s[i],
            s[i + 1],
            s[i + 2],
            s[i + 3]
        ):
            r.append(b)
    # print(r)
    # return "".join([str(x) for x in r])
    return bytearray(r)


def compress(raw_str):
    # print("input::raw_str", raw_str)
    compressed_bytesarry = zlib.compress(raw_str.encode('utf-8'), 9)
    # print("\tcompressed_bytesarry", compressed_bytesarry)
    encoded_bytearray = encode(compressed_bytesarry)
    # print("output::encoded_bytearray", encoded_bytearray)
    return encoded_bytearray


def decompress(encoded_bytearray):
    # print("input::encoded_bytearray", encoded_bytearray)
    decoded_bytesarray = decode(encoded_bytearray)
    # print("\tdecoded_bytesarray", decoded_bytesarray)
    decompressed_string = zlib.decompress(decoded_bytesarray).decode('utf-8')
    # print("output::decompressed_string", decompressed_string)
    return decompressed_string


# print(SIXBIT_ENCODING_MAP)
# print(SIXBIT_DECODING_MAP)
# print("compressed: ", c)
# print("decompressed: ", decompress(c))