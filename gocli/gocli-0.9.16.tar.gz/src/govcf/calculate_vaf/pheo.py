from .base import BaseInfoMapper, register
from .utils import int_or_zero

DP = "DP"
DP4 = "DP4"


class PheoInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {DP, DP4}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(DP)

        dp4 = call_info.get(DP4, None)
        alt_depth, ref_depth = None, None
        if dp4 and (len(dp4) == 4):
            ref_depth = int_or_zero(dp4[0]) + int_or_zero(dp4[1])
            alt_depth = int_or_zero(dp4[2]) + int_or_zero(dp4[3])

        return total_depth, alt_depth, ref_depth


register(PheoInfoMapper, -1)
