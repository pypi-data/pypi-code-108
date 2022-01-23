"""
Preprocessor used as additive scrambler in kaitai struct
"""


def pop_count(inp):
    """
    Function to determine the population count in the bit-stream
    "borrowed" in gnuradio
    """
    pop_cnt = inp - ((inp >> 1) & 0o33333333333) - ((inp >> 2) & 0o11111111111)
    return ((pop_cnt + (pop_cnt >> 3)) & 0o30707070707) % 63


def additive_scramble(in_bytes, poly, seed, length):
    """
    Function for implementing an additive scrambler (aka synchronous or
    linear-feedback shift register scrambler) and descrambler.
    """
    in_bits = byte2bit(in_bytes)
    bit_len = len(in_bits)
    out_bits = [0] * bit_len
    lfsr = LFSR(poly, seed, length)
    reg_bit = 0
    for j in range(bit_len):
        reg_bit = lfsr.next_bit()
        out_bits[j] = in_bits[j] ^ reg_bit
    return bit2byte(out_bits)


def byte2bit(in_bytes):
    """
    Function for converting a byte stream into the corresponding bit stream.
    Original Author: Filippo Valmori
    """
    in_len = len(in_bytes)
    out_len = (in_len << 3)
    out_bits = [0] * out_len
    for j in range(out_len):
        byte_idx = (j >> 3)
        bit_idx = 7 - (j % 8)
        if (in_bytes[byte_idx] >> bit_idx) % 2:
            out_bits[j] = 1
    return out_bits


def bit2byte(in_bits):
    """
    Function for converting a bit stream into the corresponding byte stream.
    Original Author: Filippo Valmori
    """
    in_len = len(in_bits)
    out_len = (in_len >> 3)
    out_bytes = [0] * out_len
    for j in range(in_len):
        if in_bits[j]:
            byte_idx = (j >> 3)
            bit_idx = 7 - (j % 8)
            out_bytes[byte_idx] += (1 << bit_idx)
    return out_bytes


class LFSR:
    """
    Linear feedback shift register
    """
    def __init__(self, mask, seed, length):
        """
        Initialisation of the LFSR
        Obvious, isn't it!? ;-)

        :param mask: the polynomial mask
        :param seed: the initial state
        :param lenght: the legth of the register (length = 7 == 8 bits!)
        """
        self.mask = mask
        self.reg = seed
        self.length = length

    def next_bit(self):
        """
        Returns the next bit of the LFSR shift
        """
        output = self.reg & 1
        newbit = pop_count(self.reg & self.mask) % 2
        self.reg = ((self.reg >> 1) | (newbit << self.length))
        return output

    def next_byte(self):
        """
        Returns the next whole byte
        """
        output = self.reg & 0xFF
        for _ in range(8):
            self.next_bit()
        return output


class Scrambler(object):  # pylint: disable=too-few-public-methods
    """
    Scrambler preprocessor class
    """
    def __init__(self, poly, seed, length):
        """
        Inititalize the scrambler

        :param poly: the polynom
        :param seed: the initial state of the LFSR
        """

        self.poly = poly
        self.seed = seed
        self.length = length

    def decode(self, inp):  # pylint: disable=no-self-use
        """
        Scrambler method

        :param inp: the data to be processed

        :returns: the scrambled/descrambled data
        """

        out = bytearray(
            additive_scramble(bytearray(inp), self.poly, self.seed,
                              self.length))
        return out
