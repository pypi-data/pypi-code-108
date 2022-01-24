from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.query import get_query_by_slug


@rule("nusl", "marcxml", "/999C1", phase="pre")
def call_funding_reference(el, **kwargs):
    return funding_reference(el, **kwargs) # pragma: no cover


def funding_reference(el, **kwargs):
    res = []
    if isinstance(el, (tuple, list)):
        for _ in el:
            res.append(get_funder(_))
    if isinstance(el, dict):
        res.append(get_funder(el))
    return {
        "fundingReference": res
    }


def get_funder(el):
    res = {}
    project_id = el.get("a")
    if project_id:
        res["projectID"] = project_id
        funder = get_funder_from_id(project_id)
        if funder:
            res["funder"] = funder
    return res


def get_funder_from_id(funder_id: str):
    dict_ = {
        '1A': 'MZ0', '1B': 'MZE', '1C': 'MZP', '1D': 'MZP', '1E': 'AV0', '1F': 'MD0', '1G': 'MZE',
        '1H': 'MPO', '1I': 'MZP', '1J': 'MPS', '1K': 'MSM', '1L': 'MSM', '1M': 'MSM', '1N': 'MSM',
        '1P': 'MSM', '1Q': 'AV0', '1R': 'MZE', '2A': 'MPO', '2B': 'MSM', '2C': 'MSM', '2D': 'MSM',
        '2E': 'MSM', '2F': 'MSM', '2G': 'MSM', '7A': 'MSM', '7B': 'MSM', '7C': 'MSM', '7D': 'MSM',
        '7E': 'MSM', '7F': 'MSM', '7G': 'MSM', '7H': 'MSM', '8A': 'MSM', '8B': 'MSM', '8C': 'MSM',
        '8D': 'MSM', '8E': 'MSM', '8F': 'MSM', '8G': 'MSM', '8H': 'MSM', '8J': 'MSM', '8X': 'MSM',
        'AA': 'CBU', 'AB': 'CBU', 'BI': 'BIS', 'CA': 'MD0', 'CB': 'MD0', 'CC': 'MD0', 'CD': 'MI0',
        'CE': 'MD0', 'CF': 'MI0', 'CG': 'MD0', 'CI': 'MD0', 'DA': 'MK0', 'DB': 'MK0', 'DC': 'MK0',
        'DD': 'MK0', 'DE': 'MK0', 'DF': 'MK0', 'DG': 'MK0', 'DM': 'MK0', 'EA': 'MPO', 'EB': 'MPO',
        'EC': 'MPO', 'ED': 'MSM', 'EE': 'MSM', 'EF': 'MSM', 'EG': 'MPO', 'EP': 'MZE', 'FA': 'MPO',
        'FB': 'MPO', 'FC': 'MPO', 'FD': 'MPO', 'FE': 'MPO', 'FF': 'MPO', 'FI': 'MPO', 'FR': 'MPO',
        'FT': 'MPO', 'FV': 'MPO', 'GA': 'GA0', 'GB': 'GA0', 'GC': 'GA0', 'GD': 'GA0', 'GE': 'GA0',
        'GF': 'GA0', 'GH': 'GA0', 'GJ': 'GA0', 'GK': 'MK0', 'GP': 'GA0', 'GS': 'GA0', 'GV': 'GA0',
        'GX': 'GA0', 'HA': 'MPS', 'HB': 'MPS', 'HC': 'MPS', 'HR': 'MPS', 'HS': 'MPS', 'IA': 'AV0',
        'IB': 'AV0', 'IC': 'AV0', 'ID': 'MSM', 'IE': 'MZE', 'IN': 'MSM', 'IP': 'AV0', 'IS': 'MSM',
        'JA': 'SUJ', 'JB': 'SUJ', 'JC': 'SUJ', 'KA': 'AV0', 'KJ': 'AV0', 'KK': 'MK0', 'KS': 'AV0',
        'KZ': 'MK0', 'LA': 'MSM', 'LB': 'MSM', 'LC': 'MSM', 'LD': 'MSM', 'LE': 'MSM', 'LF': 'MSM',
        'LG': 'MSM', 'LH': 'MSM', 'LI': 'MSM', 'LJ': 'MSM', 'LK': 'MSM', 'LL': 'MSM', 'LM': 'MSM',
        'LN': 'MSM', 'LO': 'MSM', 'LP': 'MSM', 'LQ': 'MSM', 'LR': 'MSM', 'LS': 'MSM', 'LT': 'MSM',
        'LZ': 'MSM', 'ME': 'MSM', 'MI': 'URV', 'MP': 'MPO', 'NA': 'MZ0', 'NB': 'MZ0', 'NC': 'MZ0',
        'ND': 'MZ0', 'NE': 'MZ0', 'NF': 'MZ0', 'NG': 'MZ0', 'NH': 'MZ0', 'NI': 'MZ0', 'NJ': 'MZ0',
        'NK': 'MZ0', 'NL': 'MZ0', 'NM': 'MZ0', 'NN': 'MZ0', 'NO': 'MZ0', 'NR': 'MZ0', 'NS': 'MZ0',
        'NT': 'MZ0', 'NV': 'MZ0', 'OB': 'MO0', 'OC': 'MSM', 'OD': 'MO0', 'OE': 'MSM', 'OF': 'MO0',
        'OK': 'MSM', 'ON': 'MO0', 'OP': 'MO0', 'OR': 'MO0', 'OS': 'MO0', 'OT': 'MO0', 'OV': 'MO0',
        'OW': 'MO0', 'PD': 'MD0', 'PG': 'MSM', 'PK': 'MK0', 'PL': 'MZ0', 'PR': 'MPO', 'QA': 'MZE',
        'QB': 'MZE', 'QC': 'MZE', 'QD': 'MZE', 'QE': 'MZE', 'QF': 'MZE', 'QG': 'MZE', 'QH': 'MZE',
        'QI': 'MZE', 'QJ': 'MZE', 'QK': 'MZE', 'RC': 'MS0', 'RD': 'MS0', 'RE': 'MZE', 'RK': 'MK0',
        'RM': 'MZV', 'RP': 'MPO', 'RZ': 'MZ0', 'SA': 'MZP', 'SC': 'MZP', 'SD': 'MZP', 'SE': 'MZP',
        'SG': 'MZP', 'SH': 'MZP', 'SI': 'MZP', 'SJ': 'MZP', 'SK': 'MZP', 'SL': 'MZP', 'SM': 'MZP',
        'SN': 'MZP', 'SP': 'MZP', 'ST': 'NBU', 'SU': 'NBU', 'SZ': 'MZP', 'TA': 'TA0', 'TB': 'TA0',
        'TD': 'TA0', 'TE': 'TA0', 'TF': 'TA0', 'TG': 'TA0', 'TH': 'TA0', 'TI': 'TA0', 'TJ': 'TA0',
        'TK': 'TA0', 'TL': 'TA0', 'TM': 'TA0', 'TN': 'TA0', 'TO': 'TA0', 'TR': 'MPO', 'UB': 'KHK',
        'UC': 'KHK', 'UD': 'KLI', 'UE': 'KKV', 'UF': 'KHP', 'UH': 'KHP', 'US': 'MV0', 'VA': 'MV0',
        'VD': 'MV0', 'VE': 'MV0', 'VF': 'MV0', 'VG': 'MV0', 'VH': 'MV0', 'VI': 'MV0', 'VS': 'MSM',
        'VV': 'MSM', 'VZ': 'MSM', 'WA': 'MMR', 'WB': 'MMR', 'WD': 'MMR', 'WE': 'MMR', 'YA': 'MI0',
        'ZO': 'MZP', 'ZZ': 'MZP', 'RV': 'MPS', 'PV': 'MSM', 'PT': 'MH0', 'RS': 'MSM', 'PZ': 'MH0',
        'RB': 'MZV', 'PE': 'MH0', 'RN': 'MV0', 'PI': 'MH0', 'RH': 'MH0', 'PO': 'MH0', 'IZ': 'MZ0',
        'ZK': 'CUZ', 'RO': 'MO0', 'RR': 'MZP', 'TC': 'MPO', 'MO': 'MO0', 'MH': 'MH0', 'MJ': 'URV',
        'MR': 'MZP', 'SB': 'MZP', 'OU': 'MSM', 'UA': 'KUL', 'SF': 'MZP', '8I': 'MSM', 'CK': 'TA0',
        'FW': 'TA0', 'FX': 'MPO', 'GM': 'GA0', 'NU': 'MZ0', 'OY': 'MO0', 'SS': 'TA0', 'TP': 'TA0',
        'VJ': 'MV0'
    }
    id_prefix = funder_id[:2]
    slug = dict_.get(id_prefix)
    if not slug:
        return
    query = get_query_by_slug(taxonomy_code="funders", slug=slug)
    term = query.one_or_none()
    if not term: # pragma: no cover
        return
    return get_taxonomy_json(code="funders", slug=term.slug).paginated_data
