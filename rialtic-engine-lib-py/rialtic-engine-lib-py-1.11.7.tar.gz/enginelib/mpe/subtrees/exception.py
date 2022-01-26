"""
Usage: in order to use the library version of the Exception Subtree, you need to set the
following parameters in the registry. (The right hand sides are only examples.)

    registry['check_specific_condition'] = 'non-coverage'  # i.e. noun
    registry['check_specific_reason'] = 'is not covered'   # i.e. sentence without subject

Also, since we are dealing with a policy-row from the master table, we expect to get the
exact row in data['reference_data_row'], which needs to be a dictionary: for each column
in the master table there needs to be a key in data['reference_data_row']. The required
keys for this tree are:

    age_exception_indicator
    age_exception_min_value
    age_exception_relation
    age_exception_max_value
    age_exception_uom
    icd_exception_indicator
    icd_exception_list
    policy_attribution

Please, see /specification/mpe_exception_subtree.pdf for the specification of this tree.
"""

from typing import Dict, Any

from schema.insight_engine_response import InsightType

from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.decor.registry import Registry
from enginelib.decor.result import AbstractResult
from enginelib.decor.tree import Tree

from enginelib.mpe.utils.age_relation import is_patient_age_relation_satisfied, get_age_rationale
from enginelib.rds.icd10 import ICD10Collection
from enginelib.mpe.utils.age_in_uom import get_patient_age_in_days, days_to_uom


class ExceptionResult(AbstractResult):
    insight_type = {
        '10100Y': InsightType.ManualReview,
        '10200N': InsightType.ClaimLineNotPayable,
        '10300N': InsightType.ClaimLineNotPayable,
        '10400Y': InsightType.ManualReview,
        '10400N': InsightType.ClaimLineNotPayable,
        '10500Y': InsightType.ManualReview,
        '10500N': InsightType.ClaimLineNotPayable
    }

    insight_text = {
        '10100Y': 'Patient age {patient_age} is {age_exception_rationale}, therefore '
                  '{clue_procedure_code} may be covered if medical necessity is established, '
                  'despite {check_specific_condition} per {policy_attribution}.',
        '10200N': 'Procedure code {clue_procedure_code} {check_specific_reason}, '
                  'no applicable exceptions, according to {policy_attribution}.',
        '10300N': 'Procedure code {clue_procedure_code} {check_specific_reason}, and patient '
                  'age exception ({age_exception_rationale} where patient age is {patient_age}) '
                  'criteria were not fulfilled, according to {policy_attribution}.',
        '10400Y': 'The indication exception requirement was met ({diagnosis_exception}), therefore '
                  '{clue_procedure_code} may be covered if medical necessity is established, '
                  'despite {check_specific_condition}, per {policy_attribution}.',
        '10400N': 'Procedure code {clue_procedure_code} {check_specific_reason}, '
                  'and diagnosis code {clue_diagnosis} does not fulfill condition '
                  'exception criteria, according to {policy_attribution}.',
        '10500Y': 'While the patient age exception criteria was not met, the indication '
                  'exception requirement was met ({diagnosis_exception}), therefore '
                  '{clue_procedure_code} may be covered if medical necessity is established, '
                  'despite {check_specific_condition} per {policy_attribution}.',
        '10500N': 'Procedure code {clue_procedure_code} {check_specific_reason}, and '
                  'neither age nor condition exception criteria were fulfilled, according '
                  'to {policy_attribution}. Age exception criteria: {age_exception_rationale} '
                  'where patient age is {patient_age}. Diagnosis code {clue_diagnosis} does '
                  'not fulfill condition exception criteria.',
    }


tree = Tree(ExceptionResult, name='Exception Subtree (library)')


@tree.node(10000, 10100, 10200)
def is_there_applicable_age_exception(data: Dict[str, Any], registry: Registry) -> bool:
    """ Is there an applicable patient age exception? """
    row = data['reference_data_row']

    # Set parameters policy_attribution and clue_procedure_code:
    registry['policy_attribution'] = row['policy_attribution']
    registry['clue_procedure_code'] = registry.clue.procedure_code

    if row['age_exception_indicator'].strip() != '1':
        return False

    # Set parameters age_exception_rationale and patient_age:
    row = data['reference_data_row']
    age_uom = row['age_exception_uom'].lower().strip()
    registry['age_exception_rationale'] = get_age_exception_rationale(data)
    patient_age_in_days = get_patient_age_in_days(registry.clue)
    patient_age_in_uom = days_to_uom(patient_age_in_days, age_uom)
    registry['patient_age'] = f'{patient_age_in_uom} {age_uom}(s)'
    return True


@tree.node(10100, '10100Y', 10300)
def does_patient_meet_age_exception_criteria(clue: ClaimLineFocus, data: Dict[str, Any]) -> bool:
    """ Does the |patient age| meet the patient age exception criteria? """
    row = data['reference_data_row']
    relation = row['age_exception_relation'].strip()
    age_max = row['age_exception_max_value']
    age_min = row['age_exception_min_value']
    age_uom = row['age_exception_uom'].lower().strip()

    patient_age_in_days = get_patient_age_in_days(clue)
    patient_age_in_uom = days_to_uom(patient_age_in_days, age_uom)
    return is_patient_age_relation_satisfied(
        patient_age_in_uom,
        relation,
        age_min,
        age_max
    )


@tree.node(10200, 10400, '10200N')
@tree.node(10300, 10500, '10300N')
def is_icd_exception_indicator_on(data: Dict[str, Any]) -> bool:
    """ Does {icd_exception_indicator} = '1'? """
    row = data['reference_data_row']
    return row['icd_exception_indicator'].strip() == '1'


@tree.node(10400, '10400Y', '10400N')
@tree.node(10500, '10500Y', '10500N')
def does_patient_meet_icd_exception_criteria(
        clue: ClaimLineFocus,
        data: Dict[str, Any],
        registry: Registry) -> bool:
    """ Do any of the CUE diagnosis codes meet the Condition Exception criteria? """

    row = data['reference_data_row']
    icd10_collection = ICD10Collection.construct(row['icd_exception_list'], clue.service_period.start)

    diagnosis = registry.clue.diagnosis_codes
    for diag_code in diagnosis:
        if diag_code in icd10_collection:
            registry['diagnosis_exception'] = diag_code
            return True

    registry['clue_diagnosis'] = f'{diagnosis}'
    return False


def get_age_exception_rationale(data: Dict[str, Any]) -> str:
    row = data['reference_data_row']
    relation = row['age_exception_relation'].strip()
    age_max = row['age_exception_max_value']
    age_min = row['age_exception_min_value']
    age_uom = row['age_exception_uom'].lower().strip()

    return get_age_rationale(relation, age_min, age_max, age_uom)
