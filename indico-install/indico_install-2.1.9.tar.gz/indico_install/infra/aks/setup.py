from click import prompt
from indico_install.utils import run_cmd
from indico_install.infra.input_utils import postgres_input, auth_with_gsutil


def aks_setup():
    """
    Make sure we have the necessary scripts and auth for installation
    """
    assert run_cmd("which az", silent=True), "Please install the Azure CLI"
    assert run_cmd("which gcloud", silent=True) and run_cmd(
        "which gsutil", silent=True
    ), "Please install the gcloud and gsutil CLI"
    assert "name" in run_cmd(
        "az account show | grep name", silent=True
    ), "Please log in using az login"
    authed = auth_with_gsutil(raise_missing_key=True)
    assert authed, "Unable to auth with gcloud service account"


def ask_for_infra_input(conf):
    cluster = conf.get("cluster", {})
    conf["cluster"] = cluster
    storage_acct_name = prompt(
        "What is the name of the storage account",
        type=str,
        default=cluster.get("storage_acct"),
    )
    storage_acct_key = prompt(
        "What is a storage account key",
        type=str,
        default=cluster.get("storage_acct_key"),
    )
    rwx_fs = prompt(
        "Indico data fileshare name",
        type=str,
        default=conf["clusterVolumes"]["rwx"]["azureFile"]["shareName"],
    )
    rox_fs = prompt(
        "Indico api models fileshare name",
        type=str,
        default=conf["clusterVolumes"]["rox"]["azureFile"]["shareName"],
    )
    conf["cluster"].update(
        {"storage_acct": storage_acct_name, "storage_acct_key": storage_acct_key}
    )
    conf["clusterVolumes"]["rwx"]["azureFile"]["shareName"] = rwx_fs
    conf["clusterVolumes"]["rox"]["azureFile"]["shareName"] = rox_fs
    postgres_input(conf)

    return conf
