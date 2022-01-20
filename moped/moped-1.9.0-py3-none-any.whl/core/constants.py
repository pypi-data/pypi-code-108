"""File containts constants for modelling purposes.

This might be reworked in future versions, as it feels
rather archaic. But so far it does its job.
"""

from __future__ import annotations

__all__ = ["BIOMASS_TEMPLATES"]

BIOMASS_TEMPLATES = {
    "ecoli": {
        "TRP_c": -0.055234,
        "GLT_c": -0.255712,
        "MALONYL-COA_c": -3.1e-05,
        "GTP_c": -0.209121,
        "NADP_c": -0.000112,
        "WATER_c": -48.752916,
        "LEU_c": -0.437778,
        "ASN_c": -0.234232,
        "L-ASPARTATE_c": -0.234232,
        "L-ALPHA-ALANINE_c": -0.499149,
        "ARG_c": -0.28742,
        "TYR_c": -0.133993,
        "THR_c": -0.246506,
        "CTP_c": -0.129799,
        "SER_c": -0.209684,
        "ATP_c": -54.119975,
        "GLN_c": -0.255712,
        "MET_c": -0.149336,
        "LYS_c": -0.333448,
        "ACETYL-COA_c": -0.000279,
        "CYS_c": -0.088988,
        "HIS_c": -0.092056,
        "VAL_c": -0.411184,
        "UTP_c": -0.140101,
        "ILE_c": -0.282306,
        "NADPH_c": -0.000335,
        "NAD_c": -0.001787,
        "PRO_c": -0.214798,
        "PHE_c": -0.180021,
        "GLY_c": -0.595297,
        "Pi_c": 53.945874,
        "PROTON_c": 51.472,
        "ADP_c": 53.95,
    }
}
