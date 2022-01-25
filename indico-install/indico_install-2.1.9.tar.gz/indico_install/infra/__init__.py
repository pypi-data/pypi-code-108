import click
import json
from OpenSSL import crypto
from click import prompt, secho

from indico_install.utils import run_cmd
from indico_install.infra.input_utils import download_indicoapi_data, auth_with_gsutil
from indico_install.kube.svc.restart import restart
from indico_install.infra.single_node import single_node
from indico_install.infra.gke import gke
from indico_install.infra.aks import aks
from indico_install.cluster_manager import ClusterManager, get_default_namespace


# Here we try and include the EKS function
# It depends on boto3 which may not be installed
# in which case we include a stub instead
try:
    from indico_install.infra.eks import eks
except Exception:

    @click.command("eks")
    def eks():
        """Not available"""
        pass

default_namespace = get_default_namespace(ClusterManager().cluster_config, "defaultNamespace")

@click.group("infra")
@click.pass_context
def infra(ctx):
    """
    Indico infrastructure setup and validation. Supports EKS, GKE, and single node installations.

    EKS Note! must install package with "eks" extras for EKS
    """
    pass


def update_secret(secret_name, namespace=default_namespace):
    """
    Update an existing secret
    """
    if run_cmd(f"kubectl get secrets -n {namespace} | grep {secret_name}", silent=True):
        del_secret = prompt(
            f"Generate secret: '{secret_name}'? If 'yes' existing secret will be deleted",
            type=bool,
            default=False,
        )
        if del_secret:
            run_cmd(f"kubectl delete secret -n {namespace} {secret_name}")
            return True
        else:
            return False
    else:
        return True

def generate_cert(
    country="US",
    state="MA",
    locality="Boston",
    org="Indico Data Solutions, Inc",
    org_unit="Engineering",
    common_name="indico.io",
    expiration_days=3652,
):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)
    cert = crypto.X509()
    cert.get_subject().C = country
    cert.get_subject().ST = state
    cert.get_subject().L = locality
    cert.get_subject().O = org
    cert.get_subject().OU = org_unit
    cert.get_subject().CN = common_name

    cert.set_issuer(cert.get_subject())
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(int(expiration_days) * 24 * 60 * 60)

    cert.set_pubkey(key)
    cert.sign(key, "sha512")

    return {
        "crt": crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode(),
        "key": crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode(),
    }


@infra.command("generate-saml-cert")
@click.pass_context
@click.argument("host", required=True, type=str)
def generate_saml_cert(ctx, host=None):
    """
    Generate key/certificate for SSO
    """
    if not update_secret("indico-sso-cert"):
        return
    crypto_output = generate_cert(common_name=host)
    secho("Generating key/certificate", fg="green")
    run_cmd(
        f"""kubectl create secret generic indico-sso-cert --from-literal=sp.key="{crypto_output.get('key')}" --from-literal=sp.crt="{crypto_output.get('crt')}" """,
        silent=True,
    )
    ctx.invoke(restart, services=["noct"], contains=False, wait="2m")

try:
    from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
except ModuleNotFoundError:
    @infra.command("generate-saml-settings")
    def generate_saml_cert():
        """Not available"""
        secho("The generate-saml-settings command is not available. Please install required packages (i.e., 'sudo apt-get install libxml2-dev libxmlsec1-dev')  and then 'pip3 install indico-install[saml]'", fg="red")
else:
    @infra.command("generate-saml-settings")
    @click.pass_context
    @click.argument("host", required=True, type=str)
    @click.argument("metadata_url", required=False, type=str)
    @click.option(
        "-f",
        "--custom-saml",
        help="Optional path to a saml settings.json file; if specified, will upload the given file as a noct secret",
    )
    @click.option(
        "-a",
        "--advanced-settings",
        help="Optional path to a saml advanced_settings.json file; if specified, will upload the given file as a noct secret",
    )
    def generate_saml(
        ctx, host=None, metadata_url=None, custom_saml=None, advanced_settings=None
    ):
        """
        Generate and inject SAML settings from Azure AD Saml2
        Before running, complete the following steps:
        1. Register the indico platform as an app registration in Azure AD
        2. Add https://<indico IPA hostname>/auth/users/saml/acs" to the web redirection url whitelist

        HOST is the URL of the indico platform
        METADATA_URL is the federation metadata URL

        Example usage:
        indico infra generate-saml app.indico.io https://login.microsoftonline.com/12346-78910-11121314/federationmetadata/2007-06/federationmetadata.xml

        Alternatively, inject a custom settings.json file:
        indico infra generate-saml -f custom-settings.json

        An 'advanced_settings.json' file can be added with:
        indico infra generate-saml -f custom-settings.json -a advanced_settings.json

        See here for more details: https://github.com/onelogin/python3-saml

        """
        settings_secret_name = "indico-sso-settings"
        if run_cmd(f"kubectl get secrets | grep {settings_secret_name}", silent=True):
            del_secret = prompt(
                f"Secret named '{settings_secret_name}' already exists; remove and create a new secret?",
                type=bool,
                default=False,
            )
            if del_secret:
                run_cmd(f"kubectl delete secret {settings_secret_name}")
            else:
                return
        # load advanced_settings json if it exists
        adv_settings_content = ""
        if advanced_settings:
            with open(advanced_settings) as settings_file:
                adv_settings = json.load(settings_file)
            adv_settings_content = json.dumps(adv_settings, indent=4)
        advanced_secret = (
            f"--from-literal=advanced_settings.json='{adv_settings_content}'"
            if adv_settings_content
            else ""
        )
        if custom_saml:
            with open(custom_saml) as settings_file:
                settings = json.load(settings_file)
            settings_content = json.dumps(settings, indent=4)
            run_cmd(
                f"""kubectl create secret generic {settings_secret_name} --from-literal=settings.json='{settings_content}' """
                + f"{advanced_secret}",
                silent=True,
            )
            ctx.invoke(restart, services=["noct"], contains=False, wait="2m")
            return

        # not using custom settings
        if not (host and metadata_url):
            click.secho(
                "Please provide a host and metadata url if not using a custom settings.json file",
                fg="red",
            )
            return
        idp_info = OneLogin_Saml2_IdPMetadataParser.parse_remote(metadata_url)
        jacs = {
            "url": "https://" + host + "/auth/users/saml/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        }
        jsls = {
            "url": "https://" + host + "/auth/users/saml/sls",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        }
        jsp = {
            "entityId": "https://" + host + "/auth/users/saml/metadata",
            "assertionConsumerService": jacs,
            "singleLogoutService": jsls,
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        }
        stg = {"strict": "true", "debug": "true", "sp": jsp, "idp": idp_info["idp"]}
        settings_content = json.dumps(stg, indent=4)
        run_cmd(
            f"""kubectl create secret generic {settings_secret_name} --from-literal=settings.json='{settings_content}' """
            + f"{advanced_secret}",
            silent=True,
        )
        ctx.invoke(restart, services=["noct"], contains=False, wait="2m")


@infra.command("download-apidata")
@click.pass_context
@click.argument("version", required=True, type=str)
@click.option(
    "--extract/--no-extract",
    default=True,
    show_default=True,
    help="Automatically extract the downloaded TAR",
)
def download_api_data(ctx, version, *, extract):
    """
    Download VERSION of API data TAR from google cloud to local --deployment-root.
    Un-tar the file into a directory of the same name, also in the deployment-root
    VERSION is something like "v7".

    Requires Authentication with GSutil to download the TAR, but will attempt to auth with an existing key if it exists.

    Will not download TAR if it already exists.
    Will not extract the TAR if the data directory already exists in --deployment-root
    """
    auth_with_gsutil()
    download_indicoapi_data(version=version, extract=extract)


for command_group in [single_node, gke, eks, aks]:
    infra.add_command(command_group)


@infra.command("generate-metrics-cert")
@click.pass_context
def generate_metrics_cert(ctx):
    """
    Generate key/certificate for external metrics usage
    """
    crypto_output = generate_cert()
    run_cmd("kubectl create ns custom-metrics > /dev/null 2>&1", silent=True)
    if not update_secret("cm-adapter-serving-certs", namespace="custom-metrics"):
        return
    secho("Generating key/certificate", fg="green")
    run_cmd(
        f"""kubectl create secret generic cm-adapter-serving-certs -n custom-metrics --from-literal=serving.key="{crypto_output.get('key')}" --from-literal=serving.crt="{crypto_output.get('crt')}" """,
        silent=True,
    )
