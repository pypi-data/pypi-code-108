from django.contrib import admin

from .models import (
    DoneEvaluation,
    EvaluationGroup,
    EvaluationItem,
    EvaluationKeyPair,
    EvaluationPart,
    EvaluationPhase,
    EvaluationRegistration,
    EvaluationResult,
)

admin.site.register(EvaluationRegistration)
admin.site.register(EvaluationGroup)
admin.site.register(EvaluationResult)
admin.site.register(EvaluationItem)
admin.site.register(EvaluationPart)
admin.site.register(EvaluationPhase)
admin.site.register(DoneEvaluation)
admin.site.register(EvaluationKeyPair)
