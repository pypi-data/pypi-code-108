from ipaddress import ip_network

from click import secho
from indico_install.infra.eks.config import session
from indico_install.infra.eks.infra_utils import gw_info, is_covered_by


@session
def validate(info, session=None):
    """
    Validates the following:
    - defined EKS cluster lies within this VPC
    - defined RDS allows connections within this VPC
    - subnets have necessary cluster tags for K8S
    """
    cluster = session.EKSClient.describe_cluster(name=info["cluster"]["name"])[
        "cluster"
    ]
    vpc = _val_vpc(cluster, session=session)
    subnet_ids = _val_subnets(cluster, vpc, session=session)
    _val_postgres(info["postgres"]["app"]["host"], vpc, subnet_ids, session=session)
    _val_fileshares(info, vpc, subnet_ids, session=session)


@session
def _val_postgres(db_endpoint, vpc, subnet_ids, session=None):
    # Make sure RDS instance is in VPC as well
    # and accessible within certain subnets
    db_name = db_endpoint.split(".")[0]
    postgres = session.RDSClient.describe_db_instances(
        Filters=[
            {
                "Name": "db-cluster-id"
                if "cluster" in db_endpoint
                else "db-instance-id",
                "Values": [db_name],
            }
        ]
    )["DBInstances"]
    assert postgres, f"Unable to find db with name {db_name}"
    postgres = postgres[0]

    assert postgres["DBSubnetGroup"]["VpcId"] == vpc.vpc_id, "DB not in expected VPC"

    # Make sure db is accessible from all cluster subnets
    uncovered_subnet_cidrs = {
        s.subnet_id: ip_network(s.cidr_block)
        for s in vpc.subnets.filter(SubnetIds=subnet_ids)
    }
    db_sgs = ",".join(
        [f'`{sg["DBSecurityGroupName"]}`' for sg in postgres["DBSecurityGroups"]]
    )
    db_vpc_sgs = [sg["VpcSecurityGroupId"] for sg in postgres["VpcSecurityGroups"]]

    if db_sgs:
        _val_postgres_db_sgs(vpc, uncovered_subnet_cidrs, db_sgs, session)

    if db_vpc_sgs:
        _val_postgres_db_vpc_sgs(vpc, uncovered_subnet_cidrs, db_vpc_sgs, session)

    if uncovered_subnet_cidrs:
        secho(
            f"subnets {list(uncovered_subnet_cidrs.keys())} may not covered in the "
            "DB security group rules for your database. Please review (may be a false positive)",
            fg="yellow",
        )


def _val_postgres_db_vpc_sgs(vpc, subnet_cidrs, db_vpc_sgs, session):
    sgs = session.EC2Client.describe_security_groups(GroupIds=db_vpc_sgs)[
        "SecurityGroups"
    ]
    for sub, cidr in dict(subnet_cidrs).items():
        for sg in sgs:
            if sg["VpcId"] == vpc.vpc_id and any(
                [
                    is_covered_by(cidr, ip_network(ipr["CidrIp"]))
                    for ipperm in sg["IpPermissions"]
                    for ipr in ipperm["IpRanges"]
                ]
            ):
                subnet_cidrs.pop(sub)
                break


def _val_postgres_db_sgs(vpc, subnet_cidrs, db_sgs, session):
    all_db_sgs = list(
        session.RDSClient.get_paginator("describe_db_security_groups")
        .paginate(PaginationConfig={"PageSize": 100})
        .search(f"DBSecurityGroups[?contains([{db_sgs}], DBSecurityGroupName)]")
    )
    for sub, cidr in dict(subnet_cidrs).items():
        for sg in all_db_sgs:
            if sg["VpcId"] == vpc.vpc_id and any(
                [
                    is_covered_by(cidr, ip_network(sg_cidr["CIDRIP"]))
                    for ipr in sg["IPRanges"]
                    for sg_cidr in ipr
                ]
            ):
                subnet_cidrs.pop(sub)
                break


@session
def _val_fileshares(info, vpc, subnet_ids, session=None):
    subnet_cidrs = [
        ip_network(s.cidr_block) for s in vpc.subnets.filter(SubnetIds=subnet_ids)
    ]
    gw_data = gw_info(info, session=session)
    shares = [gw_data["indico_fs"], gw_data["client_fs"]]

    for fs in shares:
        clients = [ip_network(client_cidr) for client_cidr in fs["ClientList"]]
        # Make sure all the subnets are covered in the client list of the fileshare
        for cidr in subnet_cidrs:
            if not any([is_covered_by(cidr, client) for client in clients]):
                secho(
                    f"{fs['FileShareId']} may not allow access to subnet CIDR {cidr}",
                    fg="yellow",
                )


@session
def _val_subnets(cluster, vpc, session):
    # Check that subnets are tagged correctly
    subnet_ids = cluster["resourcesVpcConfig"]["subnetIds"]
    private_sub_tag = {"Key": "kubernetes.io/role/internal-elb", "Value": "1"}
    public_sub_tag = {"Key": "kubernetes.io/role/elb", "Value": "1"}
    cluster_tag = {"Key": f"kubernetes.io/cluster/{cluster['name']}", "Value": "shared"}
    cluster_owned_tag = {
        "Key": f"kubernetes.io/cluster/{cluster['name']}",
        "Value": "owned",
    }

    total_ips = 0
    for subnet in vpc.subnets.filter(SubnetIds=subnet_ids):
        total_ips += subnet.available_ip_address_count
        assert (
            subnet.state == "available"
        ), f"Subnet {subnet.subnet_id} is not available"
        assert (
            private_sub_tag in subnet.tags or public_sub_tag in subnet.tags
        ), f"No elb tag on {subnet.subnet_id}"
        assert (
            cluster_tag in subnet.tags or cluster_owned_tag in subnet.tags
        ), f"Missing {cluster_tag} on {subnet.subnet_id}"
    assert total_ips >= 250, "A minimum of 250 IP addresses must be available in total"
    return subnet_ids


@session
def _val_vpc(cluster, session=None):
    # Check that VPC supports DNS and is available
    vpc_id = cluster["resourcesVpcConfig"]["vpcId"]
    assert vpc_id, "Missing VPC id!"
    my_vpc = session.EC2Resource.Vpc(vpc_id)
    assert my_vpc.state == "available"

    errors = 0
    try:
        assert my_vpc.describe_attribute(Attribute="enableDnsSupport")[
            "EnableDnsSupport"
        ]["Value"]
    except Exception:
        secho("Unable to validate that vpc has dns support enabled")
        errors += 1
    try:
        assert my_vpc.describe_attribute(Attribute="enableDnsHostnames")[
            "EnableDnsHostnames"
        ]["Value"]
    except Exception:
        secho("Unable to validate that vpc has dns hostname support enabled")
        errors += 1
    if errors:
        raise Exception("Errors in validating vpc")
    return my_vpc
