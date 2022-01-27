from function_tools.validators import (
    BaseValidator,
)
from m3_edm.functions.change_electronic_document_status.errors import (
    ChangeElectronicDocumentStatusError,
)
from m3_edm.functions.change_electronic_document_status.strings import (
    WRONG_DOCUMENT_TRANSITION_STATUSES_ERROR,
)


class ChangeElectronicDocumentStatusRunnerValidator(BaseValidator):
    """
    Валидатор пускателя функции "ЭДО - Смена статуса электронного документа"
    """

    def validate(self, runnable):
        pass


class ChangeElectronicDocumentStatusFunctionValidator(BaseValidator):
    """
    Валидатор функции "ЭДО - Смена статуса электронного документа"
    """

    def validate(self, runnable):
        self._check_statuses(runnable)

    def _check_statuses(self, runnable):
        """
        Проверка статусов документа и перехода на соответствие
        """
        if runnable.helper.cache.document.status_id != runnable.helper.cache.transition.from_status_id:
            error = ChangeElectronicDocumentStatusError(message=WRONG_DOCUMENT_TRANSITION_STATUSES_ERROR)

            runnable.result.append_entity(error)
