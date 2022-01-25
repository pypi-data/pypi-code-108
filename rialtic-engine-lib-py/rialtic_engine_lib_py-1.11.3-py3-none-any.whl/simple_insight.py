import uuid

from schema.insight_engine_request import InsightEngineRequest
from schema.insight_engine_response import InsightType, TranslatedMessage, Insight, Defense, MessageBundle

from enginelib.utils import unique_identifier


class SimpleInsight():
    """A class that represents a simple insight
    that originates from the policy.
    """

    insight_type: InsightType = InsightType.Error
    text: str = ""

    def __init__(self, insight_type: InsightType, text: str, **kwargs):
        self.insight_type = insight_type
        self.text = text
        self.defense = kwargs.get('defense', None)
        self.defense_uuid = kwargs.get('defenseuuid', None)

    def __eq__(self, other):
        return self.insight_type == other.insight_type and self.text == other.text

    def __hash__(self):
        return hash((self.insight_type, self.text))

    def __repr__(self):
        return str(self.insight_type) + ", " + self.text

    def create_insight(self, request: InsightEngineRequest) -> Insight:
        tmessage = TranslatedMessage()
        tmessage.lang = "en"
        tmessage.message = self.defense
        tmessage.id = self.defense_uuid

        script = MessageBundle()
        script.uuid = str(uuid.uuid4())
        script.messages = [tmessage]

        defense = Defense()
        defense.script = script

        insight = Insight()
        insight.id = unique_identifier(request.claim.id)
        insight.description = self.text
        insight.type = self.insight_type
        insight.defense = defense

        return insight
