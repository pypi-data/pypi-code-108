from canvas_workflow_kit.value_set.value_set import ValueSet


class StructuredAssessmentQuestionnaireMoodDisorder(ValueSet):

    VALUE_SET_NAME = 'SCAN Mood Disorder Structured Assessment Questionnaire'

    INTERNAL = {'COGN_SCAN_MOOD_DISORDER'}


class QuestionnairePVQ(ValueSet):

    VALUE_SET_NAME = 'SCAN Pre-visit Questionnaire'

    SNOMEDCT = {'456201000124103'}


class StructuredAssessmentQuestionnaireUrinarySymptoms(ValueSet):

    VALUE_SET_NAME = 'SCAN Urinary Symptoms Structured Assessment Questionnaire'

    INTERNAL = {'MEDI_SCAN_URINARY_SYMPTOMS_ASSESSMENT'}

class StructuredAssessmentQuestionnaireCognitiveDisorders(ValueSet):

    VALUE_SET_NAME = 'SCAN Cognitive Disorders Structured Assessment Questionnaire'

    INTERNAL = {'COGN_SCAN_COGNITIVE_DISORDERS_ASSESSMENT'}


class QuestionnaireHealthCHECReferrals(ValueSet):

    VALUE_SET_NAME = 'SCAN HealthCHEC Referrals Questionnaire'

    INTERNAL = {'COOR_183522000'}


class QuestionnaireComprehensiveGeriatricAssessment(ValueSet):

    VALUE_SET_NAME = 'SCAN Comprehensive Geriatric Assessment Questionnaire'

    SNOMEDCT = {'CGA_711013002'}
