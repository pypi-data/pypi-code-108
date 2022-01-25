from .base import BaseInfoMapper, register
from .utils import int_or_zero


FAO = "FAO"
FDP = "FDP"
FRO = "FRO"


class FaoFdpInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {FAO, FDP}  # FRO is optional

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(FDP)

        alt_depth = call_info.get(FAO)
        alt_depth = (
            int_or_zero(alt_depth[allele_position - 1])
            if isinstance(alt_depth, (tuple, list))
            else int_or_zero(alt_depth)
        )

        ref_depth = call_info.get(FRO)
        if ref_depth is None:
            ref_depth = total_depth - alt_depth

        return total_depth, alt_depth, ref_depth


register(FaoFdpInfoMapper)
