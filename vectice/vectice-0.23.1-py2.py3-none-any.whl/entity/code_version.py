from vectice.entity._user_declared_version import UserDeclaredVersion


class CodeVersion(UserDeclaredVersion):
    @property
    def code_id(self) -> int:
        return int(self["codeId"])

    @property
    def git_version_id(self) -> int:
        return int(self["gitVersionId"])
