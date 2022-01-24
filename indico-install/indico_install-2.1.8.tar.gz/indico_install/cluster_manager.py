import json
import time
from collections import OrderedDict
from datetime import datetime

from click import prompt, secho

from indico_install.config import REMOTE_TEMPLATES_PATH, merge_dicts, yaml
from indico_install.utils import (
    current_user,
    diff_dicts,
    get_deployed_frontend,
    get_deployed_images,
    load_from_configmap,
    run_cmd,
    string_to_tag,
)

TRACKER_CONFIGMAP = "cluster-manager"
TRACKER_CONFIGMAP_BACKUP = "cluster-manager-backup-"
LOCK_TIMEOUT = 60  # seconds to wait for configmap lock
UPDRAFT_BUCKET = "gs://indico-templates"
TRACKER_BACKUP_LIMIT = 30


"""
Updraft Library
"""


def get_services_yaml_from_tag(updraft_tag, apps_only=True):
    remote_services_yaml = REMOTE_TEMPLATES_PATH + updraft_tag + "/services.yaml"
    out = run_cmd(f"wget -qO- {remote_services_yaml} 2>&1", silent=True)
    try:
        services = yaml.safe_load(out)
    except Exception:
        secho(f"Updraft version {updraft_tag} does not exist", fg="red")
        return None
    if apps_only:
        services["services"] = {
            s: v
            for s, v in services["services"].items()
            if v.get("group", None) not in ("static", "configs") and "nginx" not in s
        }
    return services


def get_services_from_tag(updraft_tag):
    services = get_services_yaml_from_tag(updraft_tag, apps_only=True)
    results = {}
    for app in sorted(services["services"]):
        app_img = services["images"].get(app.replace("-", "")) or next(
            (
                services["images"][i]
                for i in services["images"].keys()
                if app.split("-")[0] in i
            ),
            None,
        )
        if app_img:
            results[app] = app_img
    results["stratosphere"] = services["frontend"]["hash"]
    return results


def _list_versions():
    version = "IPA-[0-9]?[0-9]?[0-9]"
    out = run_cmd(f"gsutil ls -d {UPDRAFT_BUCKET}/{version}", silent=True).splitlines()
    return [
        i[len(UPDRAFT_BUCKET) :].replace("/", "") for i in sorted(out, reverse=True)
    ]


def list_backups():
    out = run_cmd(
        "kubectl get cm --no-headers -o custom-columns=Name:.metadata.name 2>&1 "
        "| grep {TRACKER_CONFIGMAP_BACKUP}",
        silent=True,
    )
    return [] if not out else sorted(out.splitlines(), reverse=True)

def list_namespaces():
    namespaces = run_cmd(
        "kubectl get namespaces --no-headers=true | awk '{print $1}'",
        silent=True,
    )
    namespaces_list = namespaces.split("\n")
    return namespaces_list

def get_default_namespace(cluster_config, namespace):
    default_namespace = cluster_config.get(namespace, "default")
    return default_namespace


class ClusterManager(object):
    """
    TODO: make this hold state of the actual input file
    so we have documentation on what this looks like
    Probably with versions!
    """

    information_keys = ("indico_version", "cluster_config")

    def __init__(self, reconcile=False, input_yaml=None):
        """
        Initializes a version cluster_manager for the current cluster
        and preloads with existing data
        """
        self.indico_version = None
        self._lock = None
        self.cm_exists = False
        self.cluster_config = OrderedDict({})

        self.load_from_cluster()
        if not self.cm_exists:
            if not input_yaml:
                secho(
                    "Input yaml not provided to initialize Cluster Manager",
                    fg="yellow",
                )
                return
            with open(input_yaml, "r") as f:
                self.cluster_config = yaml.safe_load(f)
                self.indico_version = string_to_tag(prompt("Last known release tag"))
        elif input_yaml:
            secho("Ignoring input yaml. Manager exists", fg="yellow")

        # Inject our cluster version into the cluster manager for use
        self._inject_version()
        if reconcile:
            self.reconcile()

    @property
    def current_state(self):
        state = {"stratosphere": self.cluster_config["frontend"].get("hash")}
        for svc, val in self.cluster_config["services"].items():
            img = val.get("values", {}).get("image")
            if not img or "nginx" in svc or "nginx" in img:
                continue
            state[svc] = img
        return state

    @property
    def registry(self):
        return self.cluster_config.get("dockerRegistry", "gcr.io/new-indico") + "/"

    @classmethod
    def diff(cls, version_1, version_2):
        old_service_hashes = get_services_from_tag(version_1)
        new_service_hashes = get_services_from_tag(version_2)
        return diff_dicts(old_service_hashes, new_service_hashes)

    def clean_services(self):
        updates = {}
        if "services" in self.cluster_config:
            services = {}
            unneeded = []
            for svc, val in self.cluster_config["services"].items():
                if "values" not in val:
                    continue
                keys_to_migrate = [
                    k
                    for k in ("image", "updated_by", "updated_at")
                    if k in val["values"]
                ]
                if keys_to_migrate:
                    services[svc] = {
                        "values": {k: val["values"].pop(k) for k in keys_to_migrate}
                    }

                # we don't want empty values floating around either
                if not val["values"]:
                    del val["values"]
                if not val:
                    unneeded.append(svc)
            [self.cluster_config["services"].pop(svc) for svc in unneeded]
            updates["services"] = services
        fe_config = self.cluster_config.get("frontend", {})
        updates["frontend"] = {
            k: self.cluster_config["frontend"].pop(k)
            for k in ("hash", "updated_by", "updated_at")
            if k in fe_config
        }
        return updates

    def update_default_namespace(self):
        namespaces = list_namespaces()
        if self.default_namespace_exists():
            default_namespace = self.cluster_config["defaultNamespace"]
            for namespace in namespaces:
                if namespace == default_namespace:
                    return None
            run_cmd(f"kubectl create namespace {default_namespace}")
        return True

    def set_default_namespace(self):
        if self.default_namespace_exists():
            default_namespace = self.cluster_config["defaultNamespace"]
            run_cmd(f"kubectl config set-context --current --namespace={default_namespace}")
        else:
            run_cmd("kubectl config set-context --current --namespace=default")

    def default_namespace_exists(self):
        if "defaultNamespace" in self.cluster_config:
            return True
        else:
            return False





    @classmethod
    def get_updraft_versions(cls, number):
        res_list = _list_versions()
        return res_list[:number] if number else res_list

    def load_from_cluster(self, backup_conf: str = None):
        """
        Use the version configmap on the cluster to populate this Tracker instance
        """
        conf = backup_conf if backup_conf else TRACKER_CONFIGMAP
        known_info = load_from_configmap(conf, data_parser=json.loads)
        if known_info:
            known_info = known_info["data"]
            self.cm_exists = True
            self.indico_version = known_info.get("indico_version")
            self.cluster_config = OrderedDict(
                known_info.get("cluster_config", self.cluster_config)
            )
            self._inject_version()
        return known_info is not None

    def edit_cluster_config(self, changes=None, version=None, replace=False):
        """
        Take a patch for cluster config and apply
        """
        if changes:
            self.cluster_config = (
                changes if replace else merge_dicts(self.cluster_config, changes)
            )
        if version:
            self.indico_version = version
            self._inject_version()

    def _already_locked(self):
        """
        Determine if configmap is locked by someone other than us
        Return:
            - None if no lock
            - 0 if the lock is owned by us
            - True if a lock exists, is not owned by us, and is still valid
        """
        out = run_cmd(
            f"kubectl get cm {TRACKER_CONFIGMAP} --show-labels --no-headers 2>&1"
            "| awk '{print $4}'",
            silent=True,
        )
        if "NotFound" in out:
            return None
        lock_label = next((i for i in out.split(",") if i.startswith("lock")), None)
        if not lock_label:
            return

        lock = float(lock_label.split("=", 1)[1])
        if lock == self._lock:
            return 0
        return time.time() - lock < LOCK_TIMEOUT

    def lock(self, retries=15):
        """
        Locks configmap for LOCK_TIMEOUT seconds
        Raises TimeoutError if existing lock is not released during retries
        No op if manager does not exist
        """
        if not self.cm_exists:
            return
        curr_lock = self._already_locked()
        if curr_lock == 0:
            return self._lock

        needed_to_wait = curr_lock
        while curr_lock and retries:
            retries -= 1
            secho("Waiting for lock...", fg="yellow")
            time.sleep(2)
            curr_lock = self._already_locked()

        if curr_lock:
            raise TimeoutError("Lock was not acquired. Please try again later")

        self._lock = time.time()
        run_cmd(
            f"kubectl label cm {TRACKER_CONFIGMAP} lock={self._lock} --overwrite",
            silent=True,
        )
        if needed_to_wait:
            self.load_from_cluster()
        return self._lock

    def unlock(self, force=False):
        """
        Unlocks config manager only if the lock is owned by us
        """
        if not self.cm_exists:
            return
        curr_lock = self._already_locked()
        if not (curr_lock == 0 and force):  # owned by someone else
            return
        run_cmd(f"kubectl label cm {TRACKER_CONFIGMAP} lock-", silent=True)

    def reconcile(self):
        """
        If there is a difference between what's on the cluster
        and the ClusterManager, update self
        """
        info = get_deployed_images()
        fe = get_deployed_frontend(config=False)
        if not info and not fe:
            secho("Cluster must be new - no existing deployments found!", fg="yellow")
            return

        self.edit_cluster_config(
            changes={
                "frontend": {"hash": fe} if fe else {},
                "services": {
                    k: {"values": {"image": v.replace(self.registry, "")}}
                    for k, v in info.items()
                },
            }
        )

    def _inject_version(self):
        self.cluster_config["IPA_VERSION"] = self.indico_version

    def update_from_current(self, services):
        """
        Similar to update, but we pull the images of the services
        directly from the cluster. Unlike reconciling, we associate
        the changes with the current user and time
        """
        info = {k: v for k, v in get_deployed_images().items() if k in services}
        updated_fe = (
            get_deployed_frontend()
            if next((s for s in services if "app-edge-nginx" in s), None)
            else None
        )
        self.update(state=info, frontend=updated_fe)

    def update(self, state: dict = None, frontend: str = None, save=True):
        """
        Version is some release tag
        state is a dictionary of {svc: image}
        """
        if not state and not frontend:
            return
        changes = {}
        curr_user = current_user()
        curr_time = str(datetime.now())
        if state:
            changes["services"] = OrderedDict(
                {
                    k: {
                        "values": {
                            "image": v.replace(self.registry, ""),
                            "updated_by": curr_user,
                            "updated_at": curr_time,
                        }
                    }
                    for k, v in sorted(state.items())
                }
            )
        if frontend:
            changes["frontend"] = {
                "hash": frontend,
                "updated_by": curr_user,
                "updated_at": curr_time,
            }

        self.lock()
        try:
            self.edit_cluster_config(changes)

            if save:
                self.save()
        finally:
            self.unlock()

    def to_dict(self):
        return OrderedDict({k: getattr(self, k) for k in self.information_keys})

    def to_configmap(self, backup=False):
        default_namespace = get_default_namespace(self.cluster_config, "defaultNamespace")
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "namespace": default_namespace,
                "name": TRACKER_CONFIGMAP_BACKUP
                + datetime.today().strftime("%Y%m%d-%H%M")
                if backup
                else TRACKER_CONFIGMAP
            },
            "data": OrderedDict({k: json.dumps(v) for k, v in self.to_dict().items()}),
        }

    def to_str(self):
        return yaml.dump(self.to_dict(), default_flow_style=False)

    def save(self, backup=False):
        """
        Update configmap on cluster with self
        We use json instead of YAML to avoid issues with boolean encoding
        """
        self.update_default_namespace()
        run_cmd(
            f"echo '{json.dumps(self.to_configmap(backup=backup))}' | kubectl apply -f -",
            silent=True,
        )
        if backup:
            for bk_cm in list_backups()[TRACKER_BACKUP_LIMIT:]:
                run_cmd(f"kubectl delete cm {bk_cm} 2>&1", silent=True)

    def diff_version(self, tag=None):
        self.reconcile()
        tag = tag or self.indico_version
        if not tag or tag.startswith("GIT: "):
            return
        old_service_hashes = get_services_from_tag(tag)
        return diff_dicts(old_service_hashes, self.current_state)
