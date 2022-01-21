class CanvasCodeSet:
    CODES = {
        'CANVAS0001': {
            'code': 'CANVAS0001',
            'description': 'Questionnaire used to determine if the patient has sufficient risk for COVID-19 to require a follow-up.',
            'short_description': 'COVID-19 Follow-up qualification questionnaire',
        },
        'CANVAS0002': {
            'code': 'CANVAS0002',
            'description': 'Question used to determine if the patient has exhibited symptoms commonly associated with COVID-19.',
            'short_description': 'COVID-19 Symptoms Question',
        },
        'CANVAS0003': {
            'code': 'CANVAS0003',
            'description': 'Question used to determine if the patient has traveled within the past 14 days.',
            'short_description': 'COVID-19 Recent Travel Question',
        },
        'CANVAS0004': {
            'code': 'CANVAS0004',
            'description': 'Question used to determine if the patient has been exposed to someone with a confirmed case of COVID-19.',
            'short_description': 'COVID-19 Exposure Question',
        },
        'CANVAS0005': {
            'code': 'CANVAS0005',
            'description': 'Question used to override COVID-19 risk scoring and force a follow-up.',
            'short_description': 'COVID-19 Forced Follow-up Question',
        },
        'CANVAS0006': {
            'code': 'CANVAS0006',
            'description': 'Questionnaire used to check in on patients with higher risk for COVID-19',
            'short_description': 'COVID-19 High Risk Check-in Questionnaire',
        },
        'CANVAS0007': {
            'code': 'CANVAS0007',
            'description': "Question used to gauge patient's knowledge of the Coronavirus situation.",
            'short_description': 'COVID-19 Knowledge Check Question',
        },
        'CANVAS0008': {
            'code': 'CANVAS0008',
            'description': 'Question used to check which COVID-19 prevention steps the patient has started using.',
            'short_description': 'COVID-19 Preventive Steps Employed Question',
        },
        'CANVAS0009': {
            'code': 'CANVAS0009',
            'description': 'Question used to ask if the patient has any questions about COVID-19 prevention.',
            'short_description': 'Question About COVID-19 Prevention Questions',
        },
        'CANVAS0010': {
            'code': 'CANVAS0010',
            'description': 'Question used to determine patient worry about COVID-19 impacts.',
            'short_description': 'COVID-19 Impact Worry Question',
        },
        'CANVAS0011': {
            'code': 'CANVAS0011',
            'description': 'Question used to identify patient social isolation mitigation strategy.',
            'short_description': 'COVID-19 Social Isolation Mitigation Strategy Question',
        },
        'CANVAS0012': {
            'code': 'CANVAS0012',
            'description': 'Question asking what help the patient would like from the clinic.',
            'short_description': 'Question asking what help the patient would like from the clinic.',
        },
        'CANVAS0013': {
            'code': 'CANVAS0013',
            'description': 'Question used to note the internal assessment of the COVID-19 outreach call.',
            'short_description': 'COVID-19 Outreach Call Internal Assessment',
        },
    }

    @staticmethod
    def code(key: str) -> str:
        return CanvasCodeSet.CODES.get(key, {'code': ''})['code']
