import tarfile

from click import confirm, prompt, secho

from indico_install.config import D_PATH
from indico_install.utils import convertb64, find_gcs_key, run_cmd


def auth_with_gsutil(raise_missing_key=False):
    gcs_key = find_gcs_key(quiet=not raise_missing_key)
    if not gcs_key:
        if raise_missing_key:
            raise AssertionError("Unable to find a key for Google auth")
        else:
            return

    authed = run_cmd(
        f"gcloud auth activate-service-account --key-file={D_PATH / gcs_key} 2>&1", silent=True
    )
    return gcs_key if "Activated service account" in authed else None


def postgres_input(conf):
    db_details = conf["postgres"]["app"]
    host = prompt("What is your DB endpoint?", type=str, default=db_details.get("host"))
    user = prompt("What is your DB user?", type=str, default=db_details.get("user"))
    password = prompt(
        "What is your DB password? Type 'USE OLD' to use existing pw.",
        hide_input=True,
        confirmation_prompt=True,
        default="USE OLD" if db_details.get("password") else None,
    )
    password = (
        db_details.get("password") if password == "USE OLD" else convertb64(password)
    )
    conf["postgres"]["app"].update({"host": host, "password": password, "user": user})


def download_indicoapi_data(version=None, extract=True):
    indicoapi_version = version or prompt(
        "Version of api model data to download", default="v10"
    )
    indicoapi_tar = f"indicoapi_data_{indicoapi_version}.tar.gz"

    tar_path = D_PATH / indicoapi_tar
    data_path = D_PATH / f"indicoapi_data_{indicoapi_version}"
    if not data_path.exists() or confirm(
        f"Overwrite existing directory {data_path}", default=True
    ):
        if tar_path.exists():
            secho(f"Skipping download - using {tar_path}", fg="yellow")
        else:
            run_cmd(
                f"mkdir -p {data_path} && "
                f"gsutil cp -r gs://indicoapi-data/{indicoapi_tar} {D_PATH}"
            )
            assert tar_path.exists(), "Unable to download indicoapi_data successfully"
        if extract:
            secho(f"Extracting TAR to {data_path}. This may take a while!", fg="yellow")
            tar = tarfile.open(tar_path, "r:gz")
            tar.extractall(path=data_path)
            tar.close()
            secho(f"Unzipped data to {data_path}", fg="green")
        else:
            secho("Please extract and upload TAR {tar_path} when ready")
            return

    return data_path
