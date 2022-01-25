from .variant_files import iterate_vcf_files, iterate_vcf_calls
from .bed_filter import BEDFilter


__all__ = ("iterate_vcf_files", "iterate_vcf_calls", "BEDFilter")

__author__ = """Ian Maurer"""
__email__ = "ian@genomoncology.com"
__version__ = "0.8.0"

__uri__ = "http://pypi.org/project/govcf"
__copyright__ = "Copyright (c) 2018 genomoncology.com"
__description__ = "govcf: GenomOncology VCF Call Generator"
__doc__ = __description__ + " <" + __uri__ + ">"
__title__ = "govcf"
