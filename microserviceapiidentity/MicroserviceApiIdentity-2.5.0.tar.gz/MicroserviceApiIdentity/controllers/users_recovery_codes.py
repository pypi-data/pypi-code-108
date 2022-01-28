import string
import random
from MicroserviceApiIdentity.models import RecoveryCodesModel


class UsersRecoveryCodesController:
    @staticmethod
    def delete(user_id) -> bool:
        """Удаление всех созданных кодов для указанного оользователя

        >>> UsersRecoveryCodesController.delete("")
        True

        :param user_id:
        :return: Bool
        """
        RecoveryCodesModel.delete_all_by_user(user_id)
        return True

    @staticmethod
    def check(user_id, code):
        return RecoveryCodesModel.check(user_id, code)

    @staticmethod
    def code_generate(size: int = 6, chars: str = string.ascii_uppercase + string.digits) -> str:
        """Генерирует рандомную строку

        >>> UsersRecoveryCodesController.code_generate()
        qwe123

        See also: https://pythonsnippets.bloghoster.org/10003/
        """
        return ''.join(random.choice(chars) for _ in range(size))
