from indico_install.infra.eks.config import session
import json
from indico_install.utils import run_cmd


@session
def validate(config, session=None):
    """
    Validates the following:
    Cluster is in healthy status
    Nodes are up and connected
    """

    # Check the cluster via kubectl
    nodes = [n.split() for n in run_cmd("kubectl get nodes --no-headers").splitlines()]
    assert len(nodes) >= 2, "Minimum 2 nodes required"
    assert all([n[1] == "Ready" for n in nodes]), "Not all nodes are ready"
    [_validate_node(n[0]) for n in nodes]

    # Now we check to make sure GPU is enabled within the cluster
    nvidia_pods = run_cmd(
        "kubectl get pods --all-namespaces | grep 'nvidia' | grep 'Running'",
        silent=True,
    ).strip()
    assert nvidia_pods != "", "The cluster does not have NVIDIA GPU pods running."


def _validate_node(node_name):
    node_attrs = json.loads(
        run_cmd(f"kubectl get node {node_name} -o json", silent=True)
    )

    # Test memory
    mem = node_attrs["status"]["capacity"]["memory"]
    mem_units = mem[-2:]
    mem = int(mem[:-2])
    if mem_units.startswith("K"):
        mem = mem / 6
    elif mem_units == "B":
        mem = mem / 9
    assert mem >= 100.0, "Not enough memory on pods"

    # Check gpu availability on the nodes
    mem = node_attrs["status"]["capacity"].get("nvidia.com/gpu")
    assert mem and int(mem) >= 1, f"GPUs not available on node {node_name}"
