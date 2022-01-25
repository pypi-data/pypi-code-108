from .base import BaseInfoMapper, register
from .utils import int_or_none

CLCAD2 = "CLCAD2"
DP = "DP"


class CLCBioInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {DP, CLCAD2}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(DP)

        clcad2 = call_info.get(CLCAD2, [None] * 4)
        ref_depth = int_or_none(clcad2[0])
        alt_depth = int_or_none(clcad2[allele_position])

        return total_depth, alt_depth, ref_depth


register(CLCBioInfoMapper)
