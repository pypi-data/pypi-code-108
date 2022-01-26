from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.autoscaling as as_classic
import pulumi_aws_native.ec2 as ec2_native
from resources import ec2

def AutoScaleingGroup(stem, props, sg_ids=None, vpc_id=None, snet_ids=None, lt_id=None, iam_ip_arn=None, provider=None, parent=None, depends_on=None):
    # launch_template = ec2.LaunchTemplates(stem, props, provider, parent=parent)
    asg =  as_classic.Group(
        f'asg-{stem}',
        # availability_zones=props.availability_zone_names,
        max_size=2,
        min_size=1,
        # vpc_zone_identifiers=snet_ids,
        launch_template=as_classic.GroupLaunchTemplateArgs(
            id=lt_id or ec2.LaunchTemplates(stem, props, sg_ids=sg_ids, vpc_id=vpc_id, snet_ids=snet_ids, iam_ip_arn=iam_ip_arn, provider=provider, parent=parent, depends_on=depends_on),
            version="$Latest",
        ),
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return asg


def AutoScaleingGroupAttachment(stem, props, tg_arn=None, asg_name=None, provider=None, parent=None, depends_on=None):
    # launch_template = ec2.LaunchTemplates(stem, props, provider, parent=parent)
    asga =  as_classic.Attachment(
        f'asga-{stem}',
        alb_target_group_arn=tg_arn,
        autoscaling_group_name=asg_name,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return asga

    