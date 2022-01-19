from typing import Tuple


def _init_age_bounds(relation: str, age_min_str: str, age_max_str: str) -> Tuple[int, int]:
    age_min = age_max = 0
    if relation[-1] in ['O', 'X'] or relation[0] == relation[-1] == '—':
        age_max = int(age_max_str)
    if relation[0] in ['O', 'X'] or relation[0] == relation[-1] == '—':
        age_min = int(age_min_str)

    return age_min, age_max


def get_age_rationale(relation: str, age_min_str: str, age_max_str: str, age_uom: str):
    age_min, age_max = _init_age_bounds(relation, age_min_str, age_max_str)

    relation_rationale = {
        '—O': f'less than {age_max} {age_uom}(s)',
        '—X': f'less than or equal to {age_max} {age_uom}(s)',
        'X—': f'greater than or equal to {age_min} {age_uom}(s)',
        'O—': f'greater than {age_min} {age_uom}(s)',
        'X—O': f'greater than or equal to {age_min} AND less than {age_max} {age_uom}(s)',
        'X—X': f'greater than or equal to {age_min} and less than or equal to {age_max} {age_uom}(s)',
        'O—X': f'greater than {age_min} and Less than or equal to {age_max} {age_uom}(s)',
        'O—O': f'greater than {age_min} and less than {age_max} {age_uom}(s)',
        '—OO—': f'less than {age_min} or greater than {age_max} {age_uom}(s)',
        '—XX—': f'less than or equal to {age_min} or greater than or equal to {age_max} {age_uom}(s)',
        '—OX—': f'less than {age_min} or greater than or equal to {age_max} {age_uom}(s)',
        '—XO—': f'less than or equal to {age_min} or greater than {age_max} {age_uom}(s)'
    }

    return relation_rationale.get(relation, relation)


def is_patient_age_relation_satisfied(
        patient_age_in_uom: int,
        relation: str,
        age_min_str: str,
        age_max_str: str) -> bool:

    age_min, age_max = _init_age_bounds(relation, age_min_str, age_max_str)

    relation_condition = {
        '—O': patient_age_in_uom < age_max,
        # less than or equal to {age_exception_max_value} {age_exception_uom}(s)
        '—X': patient_age_in_uom <= age_max,
        # greater than or equal to {age_exception_min_value} {age_exception_uom}(s)
        'X—': age_min <= patient_age_in_uom,
        # greater than {age_exception_min_value} {age_exception_uom}(s)
        'O—': age_min < patient_age_in_uom,
        # greater than or equal to {age_exception_min_value} AND less than
        #     {age_exception_max_value} {age_exception_uom}(s)
        'X—O': age_min <= patient_age_in_uom < age_max,
        # greater than or equal to {age_exception_min_value} AND less than or
        #     equal to {age_exception_max_value} {age_exception_uom}(s)
        'X—X': age_min <= patient_age_in_uom <= age_max,
        # greater than {age_exception_min_value} AND less than or equal to
        #     {age_exception_max_value} {age_exception_uom}(s)
        'O—X': age_min < patient_age_in_uom <= age_max,
        # greater than {age_exception_min_value} AND less than
        #     {age_exception_max_value} {age_exception_uom}(s)
        'O—O': age_min < patient_age_in_uom < age_max,
        # less than {age_exception_min_value} or greater than
        #     {age_exception_max_value} {age_exception_uom}(s)
        '—OO—': patient_age_in_uom < age_min or age_max < patient_age_in_uom,
        # less than or equal to {age_exception_min_value} or greater than
        #     or equal to {age_exception_max_value} {age_exception_uom}(s)
        '—XX—': patient_age_in_uom <= age_min or age_max <= patient_age_in_uom,
        # less than {age_exception_min_value} or greater than or equal to
        #     {age_exception_max_value} {age_exception_uom}(s)
        '—OX—': patient_age_in_uom < age_min or age_max <= patient_age_in_uom,
        # less than or equal to {age_exception_min_value} or greater than
        #     {age_exception_max_value} {age_exception_uom}(s)
        '—XO—': patient_age_in_uom <= age_min or age_max < patient_age_in_uom
    }

    return relation_condition[relation]
