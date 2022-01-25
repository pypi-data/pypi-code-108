from .base import BaseInfoMapper, register
from .utils import int_or_none

AD = "AD"
RD = "RD"
DP = "DP"


class ADRDDPInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {DP, AD, RD}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(DP)
        ref_depth = call_info.get(RD)

        ao = call_info.get(AD)
        alt_depth = (
            int_or_none(ao[allele_position - 1])
            if isinstance(ao, (tuple, list))
            else int_or_none(ao)
        )

        return total_depth, alt_depth, ref_depth


register(ADRDDPInfoMapper)
