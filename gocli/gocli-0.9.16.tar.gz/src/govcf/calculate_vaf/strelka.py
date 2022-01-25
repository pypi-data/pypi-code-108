from .base import BaseInfoMapper, register

TIR = "TIR"
DP = "DP"


class StrelkaInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {TIR, DP, "AU", "CU", "GU", "TU"}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(DP)

        if TIR in call_info:
            alt_depth = call_info.get(TIR, [None])[0]
        else:
            alt_depth = call_info.get("%sU" % alt_allele, [None])[0]

        ref_depth = (
            (total_depth - alt_depth)
            if None not in (total_depth, alt_depth)
            else None
        )

        return total_depth, alt_depth, ref_depth


register(StrelkaInfoMapper)
