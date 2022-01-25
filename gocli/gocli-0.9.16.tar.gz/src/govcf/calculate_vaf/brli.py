from .base import BaseInfoMapper, register
from .utils import int_or_none

FAD = "FAD"
FRD = "FRD"
FDP = "FDP"


class BRLIInfoMapper(BaseInfoMapper):
    @classmethod
    def keys(cls):
        return {FAD, FRD, FDP}

    def do_mapping(self, call_info, allele_position, alt_allele):
        total_depth = call_info.get(FDP)

        ref_depth = int_or_none(call_info.get(FRD))

        fad = call_info.get(FAD)
        alt_depth = (
            int_or_none(fad[allele_position - 1])
            if isinstance(fad, (tuple, list))
            else int_or_none(fad)
        )

        return total_depth, alt_depth, ref_depth


register(BRLIInfoMapper)
