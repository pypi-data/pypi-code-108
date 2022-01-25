import json
import re
from collections import OrderedDict

from indico_install.utils.base import run_cmd

APP_MAP = {
    "review": "moonbow",
    "teach": "crowdlabel",
    "auth": "noct",
    "datasets": "sharknado",
    "discover": "elmosfire",
    "default": "default",
    "kit": "indiKit",
}

STRATOSEARCH = re.compile(r"set \$clientversion ([^;]*);")


def get_nginx_conf():
    """ Get nginx conf from app-edge """
    return run_cmd(
        """kubectl get configmap app-edge-nginx-conf -o json | jq '.data["nginx.conf"]'""",
        silent=True,
    )


def get_app_hashes():
    output = run_cmd(
        r"""echo -e $(kubectl get configmap app-edge-nginx-conf -o json | jq '.data["nginx.conf"]') | grep -A 10 'map \$appname \$clientloc'""",
        silent=True,
    )
    output = output[output.find("{") + 1 : output.find("}")].strip()
    output = output.split()

    app_hashes = {}
    for idx in range(0, len(output), 2):
        app_hash = output[idx + 1]
        app_hashes[APP_MAP[output[idx]]] = app_hash[app_hash.rfind("/") + 1 : -1]
    return app_hashes


def get_non_matching_images(configs, only_first=False):
    output = run_cmd(
        "kubectl get deploy -o wide -A | grep indico | awk '{print $2\"=\"$8s}'",
        silent=True,
    )
    images = {
        x[0]: ("deployment", x[1].split(",")[0])
        for x in [y.split("=") for y in output.split("\n") if y.strip()]
    }

    output = run_cmd(
        "kubectl get statefulset -o wide  | grep indico | awk '{print $1\"=\"$5}'",
        silent=True,
    )

    images.update(
        {
            x[0]: ("statefulset", x[1])
            for x in [y.split("=") for y in output.split("\n") if y.strip()]
        }
    )
    for (deployment, (resource, image)) in images.items():
        if image.startswith("gcr.io/new-indico"):
            image = image[len("gcr.io/new-indico") + 1 :]
        elif image.startswith("indicoio"):
            image = image[len("indicoio") + 1 :]

        images[deployment] = (resource, image)

    for app, saved_image in configs["images"].items():
        for (deployment, (resource, cluster_image)) in images.items():
            formatted_deployment = deployment.replace("-", "").replace("_", "").lower()

            if app.lower() == formatted_deployment or app.lower() in cluster_image.replace(
                ".", ""
            ).replace(
                "-", ""
            ).replace(
                "_", ""
            ):
                if saved_image != cluster_image:
                    yield (app, resource, deployment, saved_image, cluster_image)
                if only_first:
                    break


def get_deployed_images(filter_nginx=True):
    out = run_cmd(
        "kubectl get deployments -l 'inditype in (service, celerytask)' "
        "-o custom-columns=NAME:.metadata.name,IMAGE:{.spec.template.spec.containers[0].image} --no-headers",
        silent=True,
    ).splitlines()
    out.extend(
        run_cmd(
            "kubectl get statefulsets -l 'inditype in (service, celerytask)' "
            "-o custom-columns=NAME:.metadata.name,IMAGE:{.spec.template.spec.containers[0].image} --no-headers",
            silent=True,
        ).splitlines()
    )
    return OrderedDict(
        {
            tuple(line.strip().split(None, 1))
            for line in sorted(out)
            if not (filter_nginx and "nginx" in line)
        }
    )


def get_pod_name(search):
    """
    Get full pod name by a search term
    Returns list of matching pod names
    """
    out = run_cmd(
        f"kubectl get -l app={search} pods --no-headers -o custom-columns=NAME:.metadata.name",
        silent=True,
    )
    return out.splitlines()


def get_frontend_config_hash():
    conf = run_cmd("kubectl get configmap app-edge-nginx-conf -o json", silent=True)
    try:
        return STRATOSEARCH.search(conf).group(1)
    except AttributeError:
        return None


def get_deployed_frontend(config=True):
    if config:
        return get_frontend_config_hash()
    try:
        pod_name = get_pod_name("app-edge")[0]
        out = run_cmd(
            f"kubectl exec -it {pod_name} -- grep '\$clientversion' /etc/nginx/nginx.conf",
            silent=True,
        )
        fe_hash = out.split(" ")[-1]
        return fe_hash.replace(";", "")
    except (AttributeError, IndexError):
        return None


def load_from_configmap(configmap_name, data_parser=None):
    out = run_cmd(f"kubectl get configmap {configmap_name} -o json 2>&1", silent=True)
    if "Error from server" in out:
        return
    try:
        res = json.loads(out)
        if data_parser:
            res["data"] = {k: data_parser(v) for k, v in res["data"].items()}
        return res
    except Exception:
        pass
    return


def get_cluster_nodes():
    return run_cmd(
        "kubectl get nodes --no-headers "
        "-o custom-columns=NAME:.metadata.name 2>/dev/null",
        silent=True,
    ).splitlines()


def find_names(svc_type, service, contains=True):
    if not contains:
        if svc_type in ("pdb", "poddisruptionbudget") and not service.endswith("-pdb"):
            service += "-pdb"
        service = f"^{service}$"
    return run_cmd(
        'kubectl get %s --no-headers -o custom-columns=NAME:.metadata.name | grep "%s"'
        % (svc_type, service),
        silent=True,
    ).splitlines()


def get_resources(svc_type, service):
    out = run_cmd(
        "kubectl get %s %s -o=jsonpath='{.spec.template.spec.containers[*].resources}"
        % (svc_type, service)
    )
    return json.loads(out)


def patch_resources(svc_type, service, resources):
    patch_command = json.dumps(
        [
            {
                "op": "replace",
                "path": "/spec/template/spec/containers/0/resources",
                "value": resources,
            }
        ]
    )
    patch_command = f"k patch {svc_type} {service} --type='json' -p='{patch_command}'"
