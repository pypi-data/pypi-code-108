import click
from ipaddress import ip_network

from indico_install.infra.eks.config import session
from indico_install.infra.eks.infra_utils import gw_info, cluster_cidrs, is_covered_by


@session
def validate(info, session=None):
    gw_conf = gw_info(info, session=session)
    _val_indicoapifs(gw_conf["indico_fs"], session=session)
    _val_clientdatafs(gw_conf["client_fs"], session=session)
    _val_gateway(gw_conf["gw_arn"], info, session=session)


@session
def _val_clientdatafs(fs, session=None):
    # Make sure the fileshare for the client data is correctly configured
    assert fs["ObjectACL"] == "bucket-owner-full-control"
    assert not fs["ReadOnly"]
    role_arn = fs["Role"]
    try:
        _val_role(role_arn, session=session)
    except Exception as e:
        raise Exception(
            f"Invalid or incorrect IAM role policy found for Client S3 fileshare: {e}"
        )


@session
def _val_indicoapifs(fs, session=None):
    # Make sure the fileshare for the Indico data is correctly configured
    assert fs["ObjectACL"] == "bucket-owner-full-control"
    assert fs["ReadOnly"]

    # Check that there is an attached role to allow the fileshare access to the bucket
    role_arn = fs["Role"]
    try:
        _val_role(role_arn, session=session)
    except Exception as e:
        raise Exception(
            f"Invalid or incorrect IAM role policy found for Indico S3 fileshare {e}"
        )


@session
def _val_gateway(gateway_arn, conf, session=None):
    gw = session.SGWClient.describe_gateway_information(GatewayARN=gateway_arn)
    assert gw["GatewayState"] == "RUNNING"
    assert gw["GatewayType"] == "FILE_S3"
    gw_cache = session.SGWClient.describe_cache(GatewayARN=gateway_arn)
    assert (
        gw_cache["CacheAllocatedInBytes"] >= 100_000_000_000
    ), "Gateway cache must be >= 100GB"
    gw_ip = gw["GatewayNetworkInterfaces"][0]["Ipv4Address"]
    ec2 = session.EC2Client.describe_instances(
        Filters=[
            {
                "Name": "network-interface.addresses.private-ip-address",
                "Values": [gw_ip],
            }
        ]
    )["Reservations"][0]["Instances"][0]
    assert "xlarge" in ec2["InstanceType"]
    ec2_sgs = [sg["GroupId"] for sg in ec2["SecurityGroups"]]
    _val_sgs(ec2_sgs, conf, session=session)
    return gw


@session
def _val_sgs(sg_ids, conf, session=None):
    """
    Make sure the Gateway is exposed correctly to our cluster
    """
    sgs = session.EC2Client.describe_security_groups(GroupIds=sg_ids)["SecurityGroups"]
    all_ingress_rules = [
        {
            "from": perm.get("FromPort", 0),
            "to": perm.get("ToPort", 65535),
            "ips": [ip_network(ipr["CidrIp"]) for ipr in perm["IpRanges"]],
        }
        for sg in sgs
        for perm in sg["IpPermissions"]
    ]

    if not any(
        [
            r["from"] <= 2049 <= r["to"]
            and all(
                [
                    any([is_covered_by(s, ip) for ip in r["ips"]])
                    for s in cluster_cidrs(conf, session=session)
                ]
            )
            for r in all_ingress_rules
        ]
    ):
        click.secho(
            "Gateway security rules may not expose NFS port 2049 to all cluster subnets. Please review (may be a false positive)",
            fg="yellow",
        )


@session
def _val_role(role_arn, session=None):
    role_name = role_arn.split(":")[-1].split("/")[-1]
    role_policy = session.IAMClient.get_role(RoleName=role_name)["Role"]
    assert any(
        [
            s["Action"] == "sts:AssumeRole"
            and s["Principal"]["Service"] == "storagegateway.amazonaws.com"
            for s in role_policy["AssumeRolePolicyDocument"]["Statement"]
        ]
    ), f"Fileshare role {role_name} must allow AssumeRole to access S3"
