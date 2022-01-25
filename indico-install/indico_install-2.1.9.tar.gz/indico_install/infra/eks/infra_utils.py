from indico_install.infra.eks.config import session
from ipaddress import ip_network
from click import secho, prompt


def find_gw(info, possible_gws):
    # Todo: Use some ip magic
    gws = {g["GatewayName"]: g for g in possible_gws}
    curr_name = info.get("cluster", {}).get("gatewayName", None)
    if curr_name and curr_name in gws:
        return gws[curr_name]

    gw_options = "\n  ".join(list(gws.keys()))
    gw = None
    while not gw:
        gw = prompt(f"Possible gateways:\n  {gw_options}\nWhich gateway?")
        gw = gw if gw in gws else None
    return gws[gw]


@session
def gw_info(info, session=None):
    gws = session.SGWClient.list_gateways()["Gateways"]
    assert len(gws), "No gateways found"
    gw = gws[0] if len(gws) == 1 else find_gw(info, gws)
    gw_arn = gw["GatewayARN"]
    fss = session.SGWClient.list_file_shares(GatewayARN=gw_arn)["FileShareInfoList"]
    shares = session.SGWClient.describe_nfs_file_shares(
        FileShareARNList=[fs["FileShareARN"] for fs in fss]
    )["NFSFileShareInfoList"]
    client_fs = next(
        (
            share
            for share in shares
            if share["Path"] == info["clusterVolumes"]["rwx"]["nfs"]["path"]
        ),
        None,
    )
    indico_fs = next(
        (
            share
            for share in shares
            if share["Path"] == info["clusterVolumes"]["rox"]["nfs"]["path"]
        ),
        None,
    )
    assert client_fs and indico_fs, "Missing a file share in your storage gateway"
    return {"gw_arn": gw_arn, "indico_fs": indico_fs, "client_fs": client_fs}


def is_covered_by(cidr, bigger_cidr):
    covered = False
    # subnet_of is Python 3.7+, compare_networks was deprecated in 3.7
    try:
        covered = cidr.subnet_of(bigger_cidr)
    except AttributeError:
        covered = cidr.compare_networks(bigger_cidr) >= 0
    return covered


@session
def cluster_cidrs(info, session=None):
    cluster = session.EKSClient.describe_cluster(name=info["cluster"]["name"])[
        "cluster"
    ]
    try:
        return [
            ip_network(s["CidrBlock"])
            for s in session.EC2Client.describe_subnets(
                SubnetIds=cluster["resourcesVpcConfig"]["subnetIds"]
            )["Subnets"]
        ]
    except Exception as e:
        secho(f"Error getting CIDR blocks of cluster subnets: {e}", fg="orange")
    return []
