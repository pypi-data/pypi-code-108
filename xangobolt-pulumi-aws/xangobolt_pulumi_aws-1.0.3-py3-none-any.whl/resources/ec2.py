from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.ec2 as ec2_classic
import pulumi_aws_native.ec2 as ec2_native

def vpc_classic(stem, props, provider=None, parent=None, depends_on=None):
    vpc_net = ec2_classic.Vpc(
        f'vpc-{stem}',
        cidr_block=props.base_cidr,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return vpc_net

def vpc_native(stem, props, provider=None, parent=None, depends_on=None):
    vpc_net = ec2_classic.Vpc(
        f'vpc-{stem}',
        cidr_block=props.base_cidr,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return vpc_net


def internet_gateway(stem, vpc_Id, props, provider=None, parent=None, depends_on=None):
    igw = ec2_classic.InternetGateway(
        f'igw-{stem}',
        vpc_id=vpc_Id,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return igw

def subnet(stem, props, vpc_Id, cidr_block, az, public, provider=None, parent=None, depends_on=None):
    snet =  ec2_classic.Subnet(
        f'subnet-{stem}',
        vpc_id=vpc_Id,
        cidr_block=cidr_block,
        availability_zone=az,
        map_public_ip_on_launch=public,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return snet


def DefaultRouteTable(stem, props, default_route_table_id, provider=None, parent=None, depends_on=None):
    default_route_table =  ec2_classic.DefaultRouteTable(
        f'route_table-{stem}',
        default_route_table_id=default_route_table_id,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return default_route_table

def RouteTable(stem, props, vpc_id, provider=None, parent=None, depends_on=None):
    route_table =  ec2_classic.RouteTable(
        f'route_table-{stem}',
        vpc_id=vpc_id,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return route_table


def Route(stem, props, route_table_id, gateway_id, destination_cidr, provider=None, parent=None, depends_on=None):
    route =  ec2_classic.Route(
        f'route-{stem}',
        route_table_id=route_table_id,
        gateway_id=gateway_id,
        destination_cidr_block=destination_cidr,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return route

def RouteTableAssociation(stem, props, subnet_id, route_table_id, provider=None, parent=None, depends_on=None):
    route =  ec2_classic.RouteTableAssociation(
        f'rta-{stem}',
        subnet_id=subnet_id,
        route_table_id=route_table_id,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return route

def SecurityGroup(stem, props, vpc_id=None, provider=None, parent=None, depends_on=None):
    sg =  ec2_classic.SecurityGroup(
        f'secgrp-{stem}',
        name=f'secgrp-{stem}',
        vpc_id=vpc_id,
        egress=[ec2_classic.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="all",
            cidr_blocks=["0.0.0.0/0"],
        )],
        ingress=[ec2_classic.SecurityGroupIngressArgs(
            description="SSH management",
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        ec2_classic.SecurityGroupIngressArgs(
            description="All",
            from_port=0,
            to_port=65535,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"]
        )],
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sg

def SecurityGroupRule(stem, props, sg_id=None, provider=None, parent=None, depends_on=None):
    sgr =  ec2_classic.SecurityGroupRule(
        f'secgrprule-{stem}',
        type="egress",
        from_port=0,
        to_port=65535,
        protocol="all",
        cidr_blocks=["0.0.0.0/0"],
        security_group_id=sg_id,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sgr


def LaunchTemplates(stem, props, sg_ids=None, vpc_id=None, snet_ids=None, iam_ip_arn=None, image_id=None, instance_type=None, key_name=None, user_data=None, provider=None, parent=None, depends_on=None):
    lt =  ec2_classic.LaunchTemplate(
        f'lt-{stem}',
        image_id=image_id,
        instance_type=instance_type,
        key_name=key_name,
        iam_instance_profile=ec2_classic.LaunchTemplateIamInstanceProfileArgs(
            arn=iam_ip_arn
        ),
        # vpc_security_group_ids=sg_ids,
        # or [SecurityGroup(stem, props, vpc_id=vpc_id, provider=provider, parent=parent, depends_on=depends_on)],
        block_device_mappings=[ec2_classic.LaunchTemplateBlockDeviceMappingArgs(
            device_name="/dev/xvda",
            ebs=ec2_classic.LaunchTemplateBlockDeviceMappingEbsArgs(
                volume_size=100,
            ),
        )],
        capacity_reservation_specification=ec2_classic.LaunchTemplateCapacityReservationSpecificationArgs(
            capacity_reservation_preference="open",
        ),
        # cpu_options=ec2_classic.LaunchTemplateCpuOptionsArgs(
        #     core_count=4,
        #     threads_per_core=2,
        # ),
        credit_specification=ec2_classic.LaunchTemplateCreditSpecificationArgs(
            cpu_credits="standard",
        ),
        network_interfaces=[ec2_classic.LaunchTemplateNetworkInterfaceArgs(
            associate_public_ip_address="true",
            security_groups=sg_ids,
            subnet_id=snet_ids[0],
            delete_on_termination='true',
        )],
        placement=ec2_classic.LaunchTemplatePlacementArgs(
            availability_zone="ca-central-1a",
        ),
        user_data=user_data,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return lt


def Instance(stem, props, ami=None, lt_id=None, sg_id=None, provider=None, parent=None, depends_on=None):
    ec2 =  ec2_classic.Instance(
        f'ec2-{stem}',
        launch_template=ec2_classic.InstanceLaunchTemplateArgs(
            id=lt_id,
            version="$Latest",
        ),
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return ec2