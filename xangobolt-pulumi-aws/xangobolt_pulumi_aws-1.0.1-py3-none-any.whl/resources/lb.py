from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.alb as lb_classic
import pulumi_aws_native.ec2 as ec2_native



def AppLoadBalancer(stem, props, snet_ids=None, provider=None, parent=None, depends_on=None):
    alb =  lb_classic.LoadBalancer(
        f'alb-{stem}',
        internal=False,
        load_balancer_type="application",
        # security_groups=[aws_security_group["lb_sg"]["id"]],
        subnets=snet_ids,
        enable_deletion_protection=False,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return alb

def TargetGroup(stem, props, vpc_id=None, hcp=None, provider=None, parent=None, depends_on=None):
    tg =  lb_classic.TargetGroup(
        f'tg-{stem}',
       port=80,
       protocol="HTTP",
       health_check=lb_classic.TargetGroupHealthCheckArgs(
           enabled="true",
           path=hcp,
       ),
       vpc_id=vpc_id,
       opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return tg

def TargetGroupAttachment(stem, props, port=None, tg_arn=None,instance_id=None, provider=None, parent=None, depends_on=None):
    tga =  lb_classic.TargetGroupAttachment(
        f'tga-{stem}',
       port=port,
       target_group_arn=tg_arn,
       target_id=instance_id,
       opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return tga


def Listener(stem, props, lb_arn=None, lb_port=None, provider=None, parent=None, depends_on=None):
    listener =  lb_classic.Listener(
        f'fwlsnr-{stem}',
        load_balancer_arn=lb_arn,
        port=lb_port or 80,
        protocol="HTTP",
        default_actions=[lb_classic.ListenerDefaultActionArgs(
            type="redirect",
            redirect=lb_classic.ListenerDefaultActionRedirectArgs(
                port="443",
                protocol="HTTPS",
                status_code="HTTP_301",
            ),
        )],
       opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return listener

def Listener_SSL(stem, props, lb_arn, lb_port=None, tg_arn=None, cert_arn=None, provider=None, parent=None, depends_on=None):
    listener_ssl =  lb_classic.Listener(
        f'rlsnr-{stem}',
        load_balancer_arn=lb_arn,
        port=lb_port or 443,
        protocol="HTTPS",
        ssl_policy="ELBSecurityPolicy-2016-08" ,
        certificate_arn=cert_arn ,
        default_actions=[lb_classic.ListenerDefaultActionArgs(
            type="forward",
            target_group_arn=tg_arn,
            )
        ],
       opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return listener_ssl





    