import re
import tarfile

import click
from click import secho

from indico_install.cluster_manager import ClusterManager
from indico_install.config import D_PATH, SERVICES_YAML, ConfigsHolder
from indico_install.infra.input_utils import auth_with_gsutil
from indico_install.utils import options_wrapper, run_cmd, string_to_tag


@click.group("package")
@click.pass_context
def package(ctx):
    """
    Package indico code versions spec'd in a local services.yaml
    """
    ctx.ensure_object(dict)
    ctx.obj["TRACKER"] = ClusterManager()
    pass


@package.group("frontend")
@click.pass_context
def frontend(ctx):
    """
    Handle frontend package operations
    """
    pass


@frontend.command("load")
@click.pass_context
@click.option("--release", required=True, help="Release to download")
def frontend_load(ctx, release=None):
    """
    Download frontend static files TAR and unzip to local directory
    """
    remote_fe_files_path = f"https://storage.googleapis.com/appstack-clients/client-onprem/frontend_package_{release}.tar.gz"

    local_frontend_files_dir = D_PATH / "frontend_package"
    local_frontend_files_dir.mkdir(exist_ok=True)
    run_cmd(f"wget {remote_fe_files_path} -O - | tar -xz -C {local_frontend_files_dir}")

    conf = ctx.obj["TRACKER"].cluster_config
    conf["frontend"]["inCluster"] = True
    ctx.obj["TRACKER"].save()


@frontend.command("save")
@click.option("--tag", required=True, help="Tag to attach to the TAR")
@click.pass_context
def frontend_save(ctx, *, tag):
    """
    Packages together all static frontend files
    from hashes listed in services yaml
    """
    tag = string_to_tag(tag)
    services = ConfigsHolder(SERVICES_YAML)
    frontend_hashes = services["frontend"]["hash"]

    frontend_files_dir = D_PATH / f"frontend_package_{tag}"
    for client, _hash in frontend_hashes.items():
        secho(f"Downloading FE {client} {_hash}...")
        client_dir = frontend_files_dir / client
        client_dir.mkdir(parents=True, exist_ok=True)
        run_cmd(
            f"gsutil -m cp -r gs://appstack-clients/client-onprem/{client}/{_hash} {client_dir}"
        )

    tar_file_path = D_PATH / f"frontend_package_{tag}.tar.gz"
    with tarfile.open(tar_file_path, "w:gz") as tar:
        tar.add(frontend_files_dir, arcname="")

    secho(f"FE files ready in {tar_file_path}", fg="green")
    run_cmd(
        f"gsutil cp {tar_file_path} gs://appstack-clients/client-onprem/{tar_file_path.name}"
    )
    return tar_file_path


@package.group("docker")
@click.pass_context
def docker(ctx):
    """
    Handle docker image package operations
    """
    pass


def create_ecr_repos(repos):
    curr_repositories = run_cmd(
        'aws ecr describe-repositories --no-paginate --output text --query "repositories[].repositoryName"'
    ).split()
    new_repos = set(repos) - set(curr_repositories)
    for repo in new_repos:
        run_cmd(f"aws ecr create-repository --repository-name {repo}")


REPO_CREATION_COMMANDS = {"ecr": create_ecr_repos}


@docker.command("load")
@click.pass_context
@click.option("--release", required=True, help="Release to download")
@click.option(
    "--download/--no-download",
    default=False,
    show_default=True,
    help="Download image TAR and list from remote",
)
@click.option(
    "--remote-repo", help="Push images to this repository URL using docker push"
)
@click.option(
    "--create-repos",
    type=click.Choice(list(REPO_CREATION_COMMANDS.keys())),
    help="Create missing repositories. Only invoked with --remote-repo",
)
@options_wrapper()
def docker_load(
    ctx,
    release=None,
    download=False,
    remote_repo=None,
    create_repos=None,
    yes=False,
):
    """
    Loads docker images from a TAR if specified into your local docker repo

    Will retag and push images listed in IMAGES if a remote-repo is specified
    """
    auth_with_gsutil()
    images_tar = D_PATH / f"indico_images_{release}.tar.gz"
    images_file = D_PATH / f"indico_image_list_{release}.txt"
    if download:
        run_cmd(f"gsutil cp gs://indico-images/{images_tar.name} {D_PATH}")
        run_cmd(f"gsutil cp gs://indico-images/{images_file.name} {D_PATH}")

        assert (
            images_tar.is_file()
        ), f"Could not find TAR file {images_tar}. Is the release correct?"
        secho(f"Going to run command: `docker load < {images_tar}`", fg="yellow")
        if remote_repo or click.prompt(
            "Load docker TAR? This can take many minutes. You may also say No here and run the command in the background"
        ):
            run_cmd(f"docker load < {images_tar}")

    if remote_repo:
        assert images_file.is_file(), f"Could not find image list file {images_file}"

        remote_repo = remote_repo[:-1] if remote_repo.endswith("/") else remote_repo

        conf = ctx.obj["TRACKER"].cluster_config
        conf["dockerRegistry"] = remote_repo
        ctx.obj["TRACKER"].save()

        with open(images_file, "r") as imgf:
            images_list = [l.strip() for l in imgf.readlines()]

        new_tags = []
        for img in images_list:
            raw_img_name = img.split("/")[-1]
            new_tags.append(f"{remote_repo}/{raw_img_name}")

        repos = set([nt.split("/", 1)[1].split(":", 1)[0] for nt in new_tags])

        if create_repos:
            REPO_CREATION_COMMANDS[create_repos](repos)
        else:
            repos = "\n".join(repos)
            secho(
                f"Expecting the following repositories to exist. Use the --create-repos flag to create as necessary:\n{repos}\n"
            )

        for img, new_tag in zip(images_list, new_tags):
            if yes or click.prompt(f"Ready to tag and push {img} as {new_tag}? [yN]"):
                run_cmd(f"docker tag {img} {new_tag}")
                run_cmd(f"docker push {new_tag}")


@docker.command("save")
@click.pass_context
@click.option("--tag", required=True, help="Tag to attach to the TAR")
def docker_save(ctx, *, tag):
    """
    Packages all docker images listed in services yaml
    and any specified in local templates

    Requires authed gsutil for upload
    """
    tag = string_to_tag(tag)
    templates_dir = D_PATH / "templates"
    services = ConfigsHolder(SERVICES_YAML)
    docker_registry = "gcr.io/new-indico"

    images = set(
        [f"{docker_registry}/{image}" for image in services["images"].values()]
    )

    static_images = run_cmd(
        f"grep 'image: ' -r {templates_dir} -h | grep -v '.Values.image' | grep -v 'dockerRegistry }}}}'",
        silent=True,
    ).splitlines()
    static_images = [si.split("image: ", 1)[1] for si in static_images]
    for static_image in static_images:
        if " default " in static_image:
            static_image = re.sub(r'^.*default "(.*)" }}/', r"\g<1>/", static_image)
        images.add(static_image)

    image_list = " ".join(images)
    secho("Pulling:\n" + "\n".join(images))

    docker_tar_path = D_PATH / f"indico_images_{tag}.tar.gz"
    image_file_path = D_PATH / f"indico_image_list_{tag}.txt"
    for img in images:
        run_cmd(f"docker pull {img}")

    run_cmd(f"docker save {image_list} | gzip > {docker_tar_path}")
    with open(image_file_path, "w") as image_file:
        image_file.writelines(f"{img}\n" for img in images)
    secho(
        f"Docker images saved to {docker_tar_path}. Image list is {image_file_path}",
        fg="green",
    )
    run_cmd(f"gsutil cp {docker_tar_path} gs://indico-images/{docker_tar_path.name}")
    run_cmd(f"gsutil cp {image_file_path} gs://indico-images/{image_file_path.name}")
    return (image_file_path, docker_tar_path)
