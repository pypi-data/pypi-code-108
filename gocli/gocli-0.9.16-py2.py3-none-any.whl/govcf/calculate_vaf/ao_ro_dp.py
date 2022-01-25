from .base import BaseInfoMapper, register
from .utils import int_or_none

AO = "AO"
RO = "RO"
DP = "DP"


class AORODPInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {DP, AO, RO}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(DP)

        ref_depth = int_or_none(call_info.get(RO))

        ao = call_info.get(AO)
        alt_depth = (
            int_or_none(ao[allele_position - 1])
            if isinstance(ao, (tuple, list))
            else int_or_none(ao)
        )

        return total_depth, alt_depth, ref_depth


register(AORODPInfoMapper)
