import os
import typing as t

from click import ClickException
from docker.errors import APIError  # type: ignore
from pydantic import ValidationError

from tktl.core.exceptions import (
    MissingDocker,
    NoContentsFoundException,
    UserRepoValidationException,
)
from tktl.core.loggers import LOG
from tktl.core.managers.docker import DockerManager
from tktl.core.managers.project import ProjectManager
from tktl.core.schemas.project import ProjectValidationOutput
from tktl.core.validation.outputs import (
    ConfigFileValidationFailure,
    ProjectValidationFailure,
)


def get_docker_manager(path: str) -> DockerManager:
    try:
        return DockerManager(path)
    except MissingDocker:
        raise ClickException(
            "Couldn't locate docker. Please make sure it is installed, "
            "or use the DOCKER_HOST environment variable."
        )


def validate_project_config(path: str):
    try:
        LOG.log("=== VALIDATE PROJECT CONFIG STEP ===")
        ProjectManager.validate_project_config(path)
    except ValidationError as e:
        validation_output = ProjectValidationOutput(
            title=ConfigFileValidationFailure.title,
            summary=ConfigFileValidationFailure.summary,
            text=ConfigFileValidationFailure.format_step_results(validation_errors=e),
        )
        _log_failure(validation_output)
        return
    except (NoContentsFoundException, UserRepoValidationException) as e:
        validation_output = ProjectValidationOutput(
            title=ProjectValidationFailure.title,
            summary=ProjectValidationFailure.summary,
            text=ProjectValidationFailure.format_step_results(validation_errors=e),
        )
        _log_failure(validation_output)
        return
    LOG.log("Project scaffolding is valid!", color="green")


def _log_failure(validation_output: ProjectValidationOutput):
    LOG.log(f"Project scaffolding is invalid: {validation_output.title}", color="red")
    LOG.log(validation_output.summary, color="red", err=True)
    LOG.log(validation_output.text, color="red", err=True)


def build_image(
    dm: DockerManager,
    path: str,
    cache: bool,
    prune: bool,
    secrets: t.Dict[str, str] = None,
) -> str:
    LOG.log("=== BUILD STEP ===")
    abs_path = os.path.abspath(os.path.join(path, ".buildfile"))

    buildargs = {
        "tktl_local": "true",
        **(secrets if secrets else {}),
    }

    image = dm.build_image(
        dockerfile=abs_path, cache=cache, prune=prune, buildargs=buildargs
    )

    return image


def status_output(status, allowed_status_codes: t.List[int] = [0]):
    if status["StatusCode"] in allowed_status_codes:
        LOG.log("Success", color="green")
    else:
        LOG.log("Error", color="red")
        exit(1)


def validate_import(
    dm: DockerManager, image: str,
):
    LOG.log("=== VALIDATE IMPORT STEP ===")
    status, _ = dm.test_import(image)
    status_output(status)


def validate_endpoint_sample(
    dm: DockerManager, image: str,
):
    LOG.log("=== VALIDATE ENDPOINT SAMPLE DATA STEP ===")
    status, _ = dm.test_endpoint_sample(image)
    status_output(status)


def validate_unittest(dm: DockerManager, image: str):
    LOG.log("=== VALIDATE UNITTEST STEP ===")
    status, _ = dm.test_unittest(image)
    status_output(status, [0, 5])


def validate_integration(
    dm: DockerManager, image: str, timeout: int, retries: int,
):
    LOG.log("=== VALIDATE INTEGRATION STEP ===")
    LOG.log("Waiting for service to start...")
    (rest_response, grpc_response, _, _,) = dm.run_and_check_health(
        image,
        kill_on_success=True,
        auth_enabled=False,
        timeout=timeout,
        retries=retries,
    )
    if _validate_container_response(
        rest_response=rest_response, grpc_response=grpc_response
    ):
        LOG.log("Success", color="green")
    else:
        LOG.log("Unable to run container. See stack trace for more info", color="red")
        exit(1)


def validate_profiling(
    dm: DockerManager, image: str, timeout: int, retries: int, prune: bool
):
    LOG.log("=== VALIDATE PROFILING STEP ===")
    LOG.log("Initiating service...")
    (
        rest_response,
        grpc_response,
        arrow_container,
        rest_container,
    ) = dm.run_and_check_health(
        image,
        kill_on_success=False,
        auth_enabled=False,
        timeout=timeout,
        retries=retries,
    )
    success = _validate_container_response(
        rest_response=rest_response, grpc_response=grpc_response
    )
    if not success:
        raise ClickException(
            "Failed to run service container. "
            "Ensure service can run with `tktl validate integration`"
        )
    try:
        LOG.log("Initiating remote profiling...")
        status, container = dm.run_profiling_container()
        status_output(status)
        if prune:
            dm.remove_image(image=container.image.id)
    finally:
        try:
            arrow_container.kill()
            rest_container.kill()
            if prune:
                dm.remove_image(image=rest_container.image.id)
                dm.remove_image(image=arrow_container.image.id)
        except APIError:
            pass


def _validate_rest_response(rest_response):
    if rest_response is None:
        LOG.log("Could not access REST endpoint", color="red")
    elif rest_response.status_code != 204:
        LOG.log(f"Response status code {rest_response.status_code}", color="red")
    else:
        return True
    return False


def _validate_grpc_response(grpc_response):
    if grpc_response is None:
        LOG.log("Could not access gRPC endpoint", color="red")
    else:
        return True
    return False


def _validate_container_response(rest_response, grpc_response):
    return _validate_rest_response(
        rest_response=rest_response
    ) and _validate_grpc_response(grpc_response=grpc_response)
