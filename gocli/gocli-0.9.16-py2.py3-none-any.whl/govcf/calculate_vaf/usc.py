from .base import BaseInfoMapper, register

AD = "AD"
DP = "DP"


class USCInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {DP, AD}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(DP)
        allele_depths = call_info.get(AD)
        if allele_depths and len(allele_depths) > allele_position:
            ref_depth = allele_depths[0]
            alt_depth = allele_depths[allele_position]
        else:
            alt_depth, ref_depth = None, None  # pragma: no cover

        return total_depth, alt_depth, ref_depth


register(USCInfoMapper)
