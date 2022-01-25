from .utils import int_or_none


class BaseInfoMapper(object):
    """
    Map INFO and FORMAT data to 3 key values: total, alt, and ref depth.
    """

    @classmethod
    def keys(cls):
        raise NotImplementedError

    def do_mapping(self, call_info, allele_position, alt_allele):
        raise NotImplementedError

    def calculate_vafs(self, total_depth, alt_depth, ref_depth):
        vaf, vaf_alt, ref_plus_alt = None, None, None

        alt_depth = int_or_none(alt_depth)
        ref_depth = int_or_none(ref_depth)
        total_depth = int_or_none(total_depth)

        if alt_depth is not None and ref_depth is not None:
            ref_plus_alt = alt_depth + ref_depth

        total_depth = total_depth if total_depth is not None else ref_plus_alt

        if total_depth and alt_depth:
            vaf = (float(alt_depth) / total_depth) if alt_depth else None
            vaf_alt = (
                (float(alt_depth) / ref_plus_alt) if ref_plus_alt else vaf
            )

        return vaf, vaf_alt

    def __call__(self, call_info, allele_position, alt_allele):
        total_depth, alt_depth, ref_depth = self.do_mapping(
            call_info, allele_position, alt_allele
        )

        vaf, vaf_alt = self.calculate_vafs(total_depth, alt_depth, ref_depth)

        return dict(
            total_depth=total_depth,
            alt_depth=alt_depth,
            ref_depth=ref_depth,
            vaf=vaf,
            vaf_alt=vaf_alt,
        )


all_mapping = []
lookup = {}


def register(cls, priority=0):
    """ register a given mapper class based it's priority. """
    cls_name = cls.__name__
    lookup[cls_name] = cls
    all_mapping.append((priority, cls_name, cls.keys()))
    all_mapping.sort()


def find(vcf_keys):
    vcf_keys = set(vcf_keys)
    matches = []
    for (priority, cls_name, keys) in all_mapping:
        if keys.issubset(vcf_keys):
            matches.append((priority, len(keys), cls_name))

    if matches:
        cls_name = sorted(matches, reverse=True)[0][-1]
        cls = lookup[cls_name]
        return cls()
