import os
from typing import List, Optional, Tuple, Union

from pydantic import ValidationError
from taktile_types.schemas.repository.config_yaml import TaktileYAMLConfig
from yaml import safe_load

from tktl.core.exceptions import NoContentsFoundException, UserRepoValidationException
from tktl.core.schemas.project import (
    ProjectContentMultiItemT,
    ProjectContentT,
    ProjectDirectory,
    ProjectFile,
    ProjectFileWithContent,
)
from tktl.core.t import (
    RequiredUserProjectPathsT,
    UserProjectFileT,
    UserRepoConfigFileNameT,
)


def get_user_repo_contents(path: str) -> Optional[ProjectContentT]:
    contents: List[Union[ProjectFile, ProjectDirectory]] = []
    files = [os.path.join(path, f) for f in os.listdir(path)]
    for item in files:
        if os.path.isfile(item):
            contents.append(ProjectFile(name=os.path.basename(item), path=item))
        elif os.path.isdir(item):
            contents.append(ProjectDirectory(name=os.path.basename(item), path=item))
    return contents


def validate_project_contents(
    path: str,
) -> Tuple[TaktileYAMLConfig, ProjectContentMultiItemT]:
    contents = get_user_repo_contents(path=path)
    config_found = False
    config_file = None
    required_files = RequiredUserProjectPathsT.strictly_required_files()
    required_dirs = RequiredUserProjectPathsT.strictly_required_dirs()

    if not contents:
        raise NoContentsFoundException(
            missing_config=True,
            missing_directories=list(required_dirs),
            missing_files=list(required_files),
        )

    for file in contents:
        if file.type == UserProjectFileT.FILE.value:  # type: ignore
            if file.name in UserRepoConfigFileNameT.set():  # type: ignore
                config_found = True
                config_file = file
            elif file.name in required_files:  # type: ignore
                required_files.remove(file.name)  # type: ignore
        elif file.type == UserProjectFileT.DIRECTORY.value:  # type: ignore
            if file.name in required_dirs:  # type: ignore # type: ignore
                required_dirs.remove(file.name)  # type: ignore

    if not config_found or required_dirs or required_files:
        raise UserRepoValidationException(
            missing_files=list(required_files),
            missing_directories=list(required_dirs),
            missing_config=not config_found,
        )
    config_file_with_content = decode_file_content(config_file)  # type: ignore
    return config_file_with_content, contents  # type: ignore


def decode_file_content(
    file_with_content: ProjectFileWithContent,
) -> Union[TaktileYAMLConfig, ValidationError]:
    with open(file_with_content.path, "r") as yml:
        as_dict = safe_load(yml)
    return TaktileYAMLConfig(**as_dict)
