import os
from pathlib import Path
import yaml
from typing import Optional


class Config:
    """Config for client.

    Reads configuration from `~/.continual/continual.yaml` or `CONTINUAL_CONFIG` if
    not set during initialization.  Priority of config variables is `__init__`,
    environmental variables, and then the configuration file.

    Environmental variables are:

    * `CONTINUAL_CONFIG` - Configuration file.
    * `CONTINUAL_API_KEY` - API Key.
    * `CONTINUAL_PROJECT` - Default project.
    * `CONTINUAL_ENVIRONMENT` - Default environment.
    * `CONTINUAL_ENDPOINT` - Cluster endpoint.
    * `CONTINUAL_STYLE` - Continual style
    """

    email: str = ""
    """Email."""

    api_key: str = ""
    """API key."""

    project: str = ""
    """Default project."""

    environment: str = ""
    """Default environment."""

    endpoint: str = "https://api.continual.ai"
    """Cluster endpoint."""

    _configfile: str

    style: str = ""
    """Default template style"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        project: Optional[str] = None,
        environment: Optional[str] = None,
        endpoint: Optional[str] = None,
        style: Optional[str] = None,
    ) -> None:
        """Initialize config.

        Args:
            api_key: API key.
            email: Email address.
            project: Default project.
            endpoint: Cluster endpoint.
            style: Continual style.
        """
        self._configfile = os.path.join(os.getcwd(), ".continual.yaml")
        if not os.path.exists(self._configfile):
            self._configfile = os.environ.get(
                "CONTINUAL_CONFIG",
                os.path.join(Path.home(), ".continual", "continual.yaml"),
            )
        config = dict()
        if os.path.exists(self._configfile):
            with open(self._configfile, "r") as stream:
                config = yaml.safe_load(stream) or dict()
        self.api_key = (
            api_key or os.environ.get("CONTINUAL_API_KEY") or config.get("api_key")
        )
        self.project = (
            project or os.environ.get("CONTINUAL_PROJECT") or config.get("project")
        )
        if self.project is not None and self.project != "" and "/" not in self.project:
            self.project = "projects/" + self.project
        env_from_proj = None
        if self.project is not None and "@" in self.project:
            # don't overwrite environment if it was explicity set in its own field.
            # Ideally this shouldn't ever really happen
            env_from_proj = self.project.split("@")[1]
            self.project = self.project.split("@")[0]
        self.environment = (
            environment
            or env_from_proj
            or os.environ.get("CONTINUAL_ENVIRONMENT")
            or config.get("environment")
        )

        self.endpoint = (
            endpoint
            or os.environ.get("CONTINUAL_ENDPOINT")
            or config.get("endpoint", "https://api.continual.ai")
        )
        self.email = email or config.get("email")

        self.style = style or config.get("style") or os.environ.get("CONTINUAL_STYLE")
        if self.style is None:
            self.style = "GREEN"

    def set_project(self, project: str, save=True) -> str:
        if project and "/" not in project:
            project = "projects/" + project

        if "@" in project:
            self.environment = project.split("@")[1]
            self.project = project.split("@")[0]
        else:
            self.project = project

        if save:
            self.save()

        return self.project

    def set_environment(self, environment: str, save=True) -> str:
        if environment and "@" in environment:
            environment = environment.split("@")[-1]

        self.environment = environment
        if save:
            self.save()

        return self.environment

    def show(self):
        """Print config information."""
        print(f"Config File:", self._configfile)
        print(f"Email: {self.email or ''}")
        print(f"Endpoint: {self.endpoint or ''}")
        print(f"Project: {self.project or ''}")
        print(f"Environment: {self.environment or ''}")
        print(f"Style: {self.style or ''}")
        if self.api_key is None or self.api_key == "":
            print("API Key:")
        else:
            print("API Key: ****************")

    def save(self):
        """Save config to config file."""
        Path(os.path.dirname(self._configfile)).mkdir(parents=True, exist_ok=True)
        with open(self._configfile, "w") as outfile:
            config = dict(
                email=self.email,
                api_key=self.api_key,
                project=self.project,
                environment=self.environment,
                endpoint=self.endpoint,
                style=self.style,
            )
            yaml.dump(config, outfile)
