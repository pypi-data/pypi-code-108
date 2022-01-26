# Adapted from
#
# 	https://github.com/gravitational/teleport/blob/master/examples/k8s-auth/get-kubeconfig.sh
#
#
# Copyright 2020 Gravitational, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script creates a new k8s Service Account and generates a kubeconfig with
# its credentials. This Service Account has all the necessary permissions to
# manage resources in the specified namespace (default to "coiled"). The kubeconfig
# is saved to the specified output file (defaults to "kubeconfig" in the current
# working directory).
#
# You must configure your local kubectl to point to the right k8s cluster and
# have admin-level access.
#
# Note: all of the k8s resources are created in namespace "coiled". If you
# delete any of these objects, Coiled will stop working.

import base64
import os
import shlex
import shutil
import subprocess
import tempfile

import click

from .utils import CONTEXT_SETTINGS


@click.command(
    context_settings=CONTEXT_SETTINGS,
    help="Create a kubeconfig file for connecting Coiled to a Kubernetes cluster.",
)
@click.option(
    "-n", "--namespace", default="coiled", help="Namespace to grant Coiled access to."
)
@click.option(
    "-o",
    "--output",
    default=os.path.join(os.getcwd(), "kubeconfig"),
    help="Path to output kubeconfig file.",
)
def create_kubeconfig(namespace, output):
    if shutil.which("kubectl") is None:
        raise RuntimeError(
            "Kubectl must be installed in order to use 'coiled create-kubeconfig'. "
            "See https://kubernetes.io/docs/tasks/tools/install-kubectl for installation details."
        )

    coiled_sa = "coiled-sa"

    print("Creating the Kubernetes Service Account with minimal RBAC permissions")
    with tempfile.NamedTemporaryFile(mode="w") as f:
        service_account_content = f"""apiVersion: v1
kind: Namespace
metadata:
  name: {namespace}
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {coiled_sa}
  namespace: {namespace}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: coiled-role
  namespace: {namespace}
rules:
- apiGroups:
  - ""
  resources:
  - "*"
  verbs:
  - "*"
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: coiled-rb
  namespace: {namespace}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: coiled-role
subjects:
- kind: ServiceAccount
  name: {coiled_sa}
  namespace: {namespace}
"""
        f.write(service_account_content)
        f.seek(0)
        subprocess.check_call(["kubectl", "apply", "-f", f.name])

    # Get the service account token and CA cert.
    SA_SECRET_CMD = (
        f"kubectl get -n {namespace} sa/{coiled_sa}"
        + " -o 'jsonpath={.secrets[0]..name}'"
    )
    SA_SECRET_NAME = subprocess.check_output(
        shlex.split(SA_SECRET_CMD),
        encoding="utf8",
    )
    # Note: service account token is stored base64-encoded in the secret but must
    # be plaintext in kubeconfig.
    SA_TOKEN_CMD = (
        f"kubectl get -n {namespace} secrets/{SA_SECRET_NAME}"
        + " -o \"jsonpath={.data['token']}\""
    )
    SA_TOKEN = subprocess.check_output(shlex.split(SA_TOKEN_CMD))
    SA_TOKEN = base64.b64decode(SA_TOKEN).decode("utf8")
    CA_CERT_CMD = (
        f"kubectl get -n {namespace} secrets/{SA_SECRET_NAME}"
        + " -o \"jsonpath={.data['ca\\.crt']}\""  # noqa: W605
    )
    CA_CERT = subprocess.check_output(shlex.split(CA_CERT_CMD), encoding="utf8")

    # Extract cluster IP from the current context
    CURRENT_CONTEXT = subprocess.check_output(
        ["kubectl", "config", "current-context"],
        encoding="utf8",
    ).rstrip()
    CURRENT_CLUSTER_CMD = (
        "kubectl config view -o jsonpath=\"{.contexts[?(@.name == '"
        + f"{CURRENT_CONTEXT}"
        + "'})].context.cluster}\""
    )
    CURRENT_CLUSTER = subprocess.check_output(
        shlex.split(CURRENT_CLUSTER_CMD),
        encoding="utf8",
    )
    CURRENT_CLUSTER_ADDR_CMD = (
        "kubectl config view -o jsonpath=\"{.clusters[?(@.name == '"
        + f"{CURRENT_CLUSTER}"
        + "'})].cluster.server}\""
    )
    CURRENT_CLUSTER_ADDR = subprocess.check_output(
        shlex.split(CURRENT_CLUSTER_ADDR_CMD),
        encoding="utf8",
    )

    # Write kubeconfig file to disk
    print(f"Writing kubeconfig file to {output}")
    with open(output, "w") as f:
        kubeconfig_contents = f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {CA_CERT}
    server: {CURRENT_CLUSTER_ADDR}
  name: {CURRENT_CLUSTER}
contexts:
- context:
    cluster: {CURRENT_CLUSTER}
    user: {coiled_sa}
  name: {CURRENT_CONTEXT}
current-context: {CURRENT_CONTEXT}
kind: Config
preferences: {{}}
users:
- name: {coiled_sa}
  user:
    token: {SA_TOKEN}
"""
        f.write(kubeconfig_contents)
