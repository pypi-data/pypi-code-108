from typing import Any, Optional

from gcip.core.job import Job, ScriptArgumentNotAllowedError


class TwineUpload(Job):
    def __init__(
        self,
        *,
        name: str = "twine",
        stage: str = "deploy",
        twine_repository_url: Optional[str] = None,
        twine_username_env_var: Optional[str] = "TWINE_USERNAME",
        twine_password_env_var: Optional[str] = "TWINE_PASSWORD",
        **kwargs: Any,
    ) -> None:
        """
        Runs:

        ```
        pip3 install --upgrade twine
        python3 -m twine upload --non-interactive --disable-progress-bar dist/*
        ```

        * Requires artifacts from a build job under `dist/` (e.g. from `bdist_wheel()`)

        Args:
            twine_repository_url (str): The URL to the PyPI repository the python artifacts will be deployed to. Defaults
                to `None`, which means the package is published to `https://pypi.org`.
            twine_username_env_var (Optional[str]): The name of the environment variable, which contains the username value.
                **DO NOT PROVIDE THE USERNAME VALUE ITSELF!** This would be a security issue! Defaults to `TWINE_USERNAME`.
            twine_password_env_var (Optional[str]): The name of the environment variable, which contains the password.
                **DO NOT PROVIDE THE LOGIN VALUE ITSELF!** This would be a security issue! Defaults to `TWINE_PASSWORD`.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script=[
                "pip3 install --upgrade twine",
                "python3 -m twine upload --non-interactive --disable-progress-bar dist/*",
            ],
            **kwargs,
        )
        self.add_variables(
            TWINE_USERNAME=f"${twine_username_env_var}",
            TWINE_PASSWORD=f"${twine_password_env_var}",
        )

        if twine_repository_url:
            self.add_variables(TWINE_REPOSITORY_URL=twine_repository_url)
