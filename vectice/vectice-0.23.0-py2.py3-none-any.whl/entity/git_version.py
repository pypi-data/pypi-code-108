from vectice.entity._versioned_entity import VersionedEntity


class GitVersion(VersionedEntity):
    @property
    def repository_name(self) -> str:
        return str(self["repositoryName"])

    @property
    def branch_name(self) -> str:
        return str(self["branchName"])

    @property
    def commit_hash(self) -> str:
        return str(self["commitHash"])

    @property
    def commit_comment(self) -> str:
        return str(self["commitComment"])

    @property
    def commit_author_name(self) -> str:
        return str(self["commitAuthorName"])

    @property
    def commit_author_email(self) -> str:
        return str(self["commitAuthorEmail"])

    @property
    def is_dirty(self) -> bool:
        return bool(self["isDirty"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def workspace_id(self) -> int:
        return int(self["workspaceId"])
