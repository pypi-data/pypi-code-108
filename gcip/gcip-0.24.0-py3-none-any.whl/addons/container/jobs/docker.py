"""This modules provide Jobs executing [Docker CLI](https://docs.docker.com/engine/reference/commandline/cli/) scripts

Those require [Docker to be installed](https://docs.docker.com/engine/install/) on the Gitlab runner.
"""

from typing import Any, Optional
from dataclasses import dataclass

from gcip.core.job import Job, ScriptArgumentNotAllowedError

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


@dataclass
class Build(Job):
    def __init__(
        self,
        *,
        name: str = "docker",
        stage: str = "build",
        repository: str,
        tag: Optional[str] = None,
        context: str = ".",
        **kwargs: Any,
    ) -> None:
        """Runs [```docker build```](https://docs.docker.com/engine/reference/commandline/build/)

        Example:

        ```
        from gcip.addons.container.job.docker import Build
        build_job = Build(repository="myrepo/myimage", tag="v0.1.0")
        ```

        Args:
            repository (str): The Docker repository name ```([<registry>/]<image>)```.
            tag (Optional[str]): A Docker image tag applied to the image. Defaults to `None` which no tag is provided
                to the docker build command. Docker should then apply the default tag ```latest```.
            context (str): The Docker build context (the directory containing the Dockerfile). Defaults to
                the current directory `.`.
            job_name (str): The jobs name used in pipeline. Defaults to `docker`.
            job_stage (str): The jobs stage used in pipeline. Defaults to `build`.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        fq_image_name = repository
        if tag:
            fq_image_name += f"{repository}:{tag}"
        super().__init__(
            script=f"docker build -t {fq_image_name} {context}",
            name=name,
            stage=stage,
        )
        self.add_variables(DOCKER_DRIVER="overlay2", DOCKER_TLS_CERTDIR="")


@dataclass
class Push(Job):
    def __init__(
        self,
        *,
        name: str = "docker",
        stage: str = "deploy",
        registry: Optional[str] = None,
        container_image: str,
        tag: Optional[str] = None,
        user_env_var: Optional[str] = None,
        login_env_var: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Runs [```docker push```](https://docs.docker.com/engine/reference/commandline/push/)
        and optionally [```docker login```](https://docs.docker.com/engine/reference/commandline/login/) before.

        Example:

        ```python
        from gcip.addons.container.docker import Push
        push_job = Push(
                        registry="docker.pkg.github.com/dbsystel/gitlab-ci-python-library",
                        image="gcip",
                        tag="v0.1.0",
                        user_env_var="DOCKER_USER",
                        login_env_var="DOCKER_TOKEN"
                    )
        ```

        The `user_env_var` and `login_env_var` should be created as *protected* and *masked*
        [custom environment variable configured
        in the UI](https://git.tech.rz.db.de/help/ci/variables/README#create-a-custom-variable-in-the-ui).

        Args:
            registry (Optional[str]): The Docker registry the image should be pushed to.
                Defaults to `None` which targets to the official Docker Registry at hub.docker.com.
            image (str): The name of the Docker image to push to the `registry`.
            tag (Optional[str]): The Docker image tag that should be pushed to the `registry`. Defaults to ```latest```.
            user_env_var (Optional[str]): If you have to login to the registry before the push, you have to provide
                the name of the environment variable, which contains the username value, here.
                **DO NOT PROVIDE THE USERNAME VALUE ITSELF!** This would be a security issue!
                Defaults to `None` which skips the docker login attempt.
            login_env_var (Optional[str]): If you have to login to the registry before the push, you have to provide
                the name of the environment variable, which contains the password or token, here.
                **DO NOT PROVIDE THE LOGIN VALUE ITSELF!** This would be a security issue!
                Defaults to `None` which skips the docker login attempt.
            job_name (str): The jobs name used in pipeline. Defaults to `docker`.
            job_stage (str): The jobs stage used in pipeline. Defaults to `deploy`.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        fq_image_name = container_image

        if registry:
            container_image = f"{registry}/{container_image}"

        if tag:
            fq_image_name += f":{tag}"
        super().__init__(
            name=name,
            stage=stage,
            script=f"docker push {fq_image_name}",
            **kwargs,
        )

        if user_env_var and login_env_var:
            self.prepend_scripts(f'docker login -u "${user_env_var}" -p "${login_env_var}"')
