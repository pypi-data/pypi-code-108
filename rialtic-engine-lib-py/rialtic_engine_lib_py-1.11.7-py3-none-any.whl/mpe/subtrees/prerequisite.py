from typing import Any, Dict

from schema.insight_engine_response import InsightType

from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.claim_focus import ClaimFocus
from enginelib.decor.result import AbstractResult
from enginelib.decor.tree import Tree

from enginelib.mpe.utils.age_relation import is_patient_age_relation_satisfied
from enginelib.mpe.utils.age_in_uom import get_patient_age_in_days, days_to_uom, yyyymmdd_to_date
from enginelib.rds.multipolicy import rows_for_cpt


class PrerequisiteResult(AbstractResult):
    insight_text = {
        '050N': 'The claim under evaluation is a voided claim. '
                'Voided claims are considered in a different insight engine.',
        '100N': 'There is no coverage policy associated with this procedure code.',
        '150N': 'There is no procedure code with the applicable age requirement '
                'associated with the claim under evaluation.',
        '200N': 'There is no coverage policy associated with this procedure code '
                'after the serviced date.',
        '300N': 'The serviced date of the claim does not fall within a coverage '
                'policy effective date range.',

        # Placeholder
        '300Y': 'PASS',
    }

    insight_type = {
        '050N': InsightType.NotApplicable,
        '100N': InsightType.NotApplicable,
        '150N': InsightType.NotApplicable,
        '200N': InsightType.NotApplicable,
        '300N': InsightType.NotApplicable,

        # Placeholder
        '300Y': InsightType.Error,
    }


tree = Tree(PrerequisiteResult, name='Prerequisite Subtree (library)')


@tree.node(50, 100, '050N')
def related_claim_check(cue: ClaimFocus) -> bool:
    """ Is CLUE <relatedClaim> NOT EQUAL to '8'? """
    return cue.related_claim != '8'


@tree.node(100, 150, '100N')
def filter_procedure_code(clue: ClaimLineFocus, data: Dict[str, Any]) -> bool:
    """ Does the MPE Reference Table have at least one row
    where the CLUE <procedureCode> = {cpt_procedurecode}? """
    data['reference_data_table'] = rows_for_cpt(clue.procedure_code)
    return bool(data['reference_data_table'])


@tree.node(150, 200, '150N')
def filter_age_requirements(clue: ClaimLineFocus, data: Dict[str, Any]) -> bool:
    """ Does the CLUE also conform to at least one of the
    age requirements associated with CLUE <procedureCode>? """
    patient_age_in_days = get_patient_age_in_days(clue)

    table = data['reference_data_table']
    rows = list()
    for row in table:
        indicator = row['age_requirement_indicator'].strip()
        if indicator == '1':
            relation = row['age_requirement_relation'].strip()
            age_min = row['age_requirement_min_value']
            age_max = row['age_requirement_max_value']
            age_uom = row['age_requirement_uom'].lower().strip()
            patient_age_in_uom = days_to_uom(patient_age_in_days, age_uom)
            if not is_patient_age_relation_satisfied(patient_age_in_uom, relation, age_min, age_max):
                continue

        rows.append(row)

    data['reference_data_table'] = rows
    return bool(rows)


@tree.node(200, 300, '200N')
def check_effective_start_date(clue: ClaimLineFocus, data: Dict[str, Any]) -> bool:
    """ Is the CLUE <lineServicedDateFrom> also on or after the {eff_start_date}? """
    table = data['reference_data_table']
    rows = list()
    for row in table:
        if clue.service_period.start >= yyyymmdd_to_date(row['eff_start_date']):
            rows.append(row)

    data['reference_data_table'] = rows
    return bool(rows)


@tree.node(300, '300Y', '300N')
def check_effective_end_date(clue: ClaimLineFocus, data: Dict[str, Any]) -> bool:
    """ Is the CLUE <lineServicedDateFrom> also before {eff_end_date}? """
    table = data['reference_data_table']
    rows = list()
    for row in table:
        if clue.service_period.end < yyyymmdd_to_date(row['eff_end_date']):
            rows.append(row)

    data['reference_data_table'] = rows
    return bool(rows)
