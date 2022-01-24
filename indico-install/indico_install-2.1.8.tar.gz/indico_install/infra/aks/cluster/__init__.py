from indico_install.utils import run_cmd


def check(conf):
    assert (
        int(run_cmd("kubectl get nodes | wc -l")) >= 2
    ), "At least 2 nodes are required in the cluster"


def create(conf):
    run_cmd(
        "kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/1.0.0-beta/nvidia-device-plugin.yml"
    )
