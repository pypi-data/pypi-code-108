import uuid
from typing import Dict
from jinja2 import Template


def apply_template(template, parameters):
    j2_template = Template(template)
    return j2_template.render(parameters)


OVERLAP_QUERY_TEMPLATE = """
INSERT INTO {{ results_table }}
(CLEAN_ROOM_ID, QUESTION_ID, QUESTION_RUN_ID, ATTRIBUTE, ATTRIBUTE_VALUE, SEGMENT_CATEGORY, SEGMENT_NAME, OVERLAP)
(SELECT T1.CLEAN_ROOM_ID AS CLEAN_ROOM_ID, '{{ question_id }}' AS QUESTION_ID, '{{ question_run_id}}' AS QUESTION_RUN_ID,
'{{ attribute }}' AS ATTRIBUTE, T1.{{ attribute }} AS ATTRIBUTE_VALUE,
T2.{{ segment_category_column }} AS SEGMENT_CATEGORY, T2.{{ segment_name_column }} AS SEGMENT_NAME,
COUNT(DISTINCT T2.{{ user_identity_column }}) AS OVERLAP
FROM {{ crm_data_source }} T1, {{ audience_segment_map_data_source }} T2
WHERE T1.{{ user_identity_column }} = T2.{{ user_identity_column}}
GROUP BY 1, 2, 3, 4, 5, 6, 7)
"""


def get_crm_segment_map_overlap_query(
        clean_room_id: str, question_id: str, question_run_id: str,
        query_metadata: Dict[str, str], run_parameters: Dict[str, str]
) -> str:
    crm_data_source = query_metadata.get('crm_data_source', None)
    if crm_data_source is None:
        raise ValueError("'crm_data_source' query metadata is missing")

    audience_segment_map_data_source = query_metadata.get('audience_segment_map_data_source', None)
    if audience_segment_map_data_source is None:
        raise ValueError("'audience_segment_map_data_source' query metadata is missing")

    user_identity_column = query_metadata.get('clean_room_identity_column', None)
    if user_identity_column is None:
        raise ValueError("'clean_room_identity_column' query metadata is missing")

    attribute = run_parameters.get('attribute', None)
    if attribute is None:
        raise ValueError("'attribute' run parameter is missing")

    segment_category_column = run_parameters.get('segment_category_column', None)
    if segment_category_column is None:
        segment_category_column = 'All'

    segment_name_column = run_parameters.get('segment_name_column', None)
    if segment_name_column is None:
        raise ValueError("'segment_name_column' run parameter is missing")

    sf_clean_room_id = clean_room_id.replace('-', '').upper()
    sf_question_id = question_id.replace('-', '').upper()

    full_crm_data_source = 'HABU_CR_%s.CLEAN_ROOM.%s' % (sf_clean_room_id, crm_data_source)
    full_audience_segment_map_data_source = 'HABU_CR_%s_PARTNER_SHARE_DB.CLEAN_ROOM.%s' % (sf_clean_room_id, audience_segment_map_data_source)

    results_table = 'HABU_CLEAN_ROOM_%s.CLEAN_ROOM_RUN_RESULTS.HABU_CRQ_%s' % (sf_clean_room_id, sf_question_id)
    params = {
        'results_table': results_table,
        'question_id': question_id,
        'question_run_id': question_run_id,
        'attribute': attribute,
        'segment_category_column': segment_category_column,
        'segment_name_column': segment_name_column,
        'crm_data_source': full_crm_data_source,
        'audience_segment_map_data_source': full_audience_segment_map_data_source,
        'user_identity_column': user_identity_column
    }
    return apply_template(OVERLAP_QUERY_TEMPLATE, params)


if __name__ == "__main__":
    """
    Generate the overlap query for the Disney + Batliboi (FIVE_FIFTEEN) use-case
    UserSegmentMap => AUDIENCE_ANALYSIS (S_HOUSEHOLD_ID, SEGMENT_CATEGORY, SEGMENT_NAME)
    CRM => USER_CRM_DATA_ADID  (ID, GENDER, AGE_RANGE, HOUSEHOLD_INCOME, PROFESSION, CUSTOMER_STATUS) 
    
    Clean Room uses custom ID Graph with the "Parent ID Column" set to S_HOUSEHOLD_ID
    
    For more details, see https://docs.google.com/document/d/1fUOYPWyc3M30znO-NdNINgoGKsMVDFho6zjief4i5lY/edit
    """
    query = get_crm_segment_map_overlap_query(
        clean_room_id='a2841fda-ace2-48ee-b8f1-9973972e85b6',
        question_id='204c88c1-1cc0-474e-a4a1-e7e9d0096f58',
        question_run_id=str(uuid.uuid4()),
        query_metadata={
            'crm_data_source': 'V_USER_CRM_DATA_ADID',
            'audience_segment_map_data_source': 'V_AUDIENCE_ANALYSIS',
            'clean_room_identity_column': 'S_HOUSEHOLD_ID'
        },
        run_parameters={
            'attribute': 'GENDER',
            'segment_category_column': 'SEGMENT_CATEGORY',
            'segment_name_column': 'SEGMENT_NAME'
        }
    )
    print("*** DISNEY (AUDIENCE_ANALYSIS) + BATLIBOI (USER_CRM_DATA_ADID) CRM <-> UserSegment Map Overlap Query ***")
    print(query)
    print()

    """
    Generate the overlap query for the NinthWonder + Batliboi (FIVE_FIFTEEN) use-case
    UserSegment => USER_SEGMENT_MAP (MAID, AUDIENCE_SEGMENT_ID, AUDIENCE_SEGMENT_NAME)
    CRM => USER_CRM_DATA_ADID  (ID, GENDER, AGE_RANGE, HOUSEHOLD_INCOME, PROFESSION, CUSTOMER_STATUS) 
    
    Clean Room uses Habu ID Graph with the "Parent ID Column" set to HABU_USER_ID
    
    For more details, see https://docs.google.com/document/d/1zwkMu389L2NxvxsTSfJDhGefWlHtmGHwIpgfjSy69po/edit?pli=1
    """
    query = get_crm_segment_map_overlap_query(
        clean_room_id='a9a2abd4-c411-48ec-8e59-f7794fd518e9',
        question_id='25fedb31-c8c6-4328-b6d4-fad3a8b270b3',
        question_run_id=str(uuid.uuid4()),
        query_metadata={
            'crm_data_source': 'V_USER_CRM_DATA',
            'audience_segment_map_data_source': 'V_USER_SEGMENT_MAP',
            'clean_room_identity_column': 'HABU_USER_ID'
        },
        run_parameters={
            'attribute': 'GENDER',
            'segment_name_column': 'AUDIENCE_SEGMENT'
        }
    )
    print("*** NINTHWONDER (USER_SEGMENT_MAP) + BATLIBOI (USER_CRM_DATA) CRM <-> UserSegment Map Overlap Query ***")
    print(query)
    print()
