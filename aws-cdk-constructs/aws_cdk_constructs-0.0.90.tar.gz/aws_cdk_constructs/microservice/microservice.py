from aws_cdk import (
    core,
    aws_elasticloadbalancingv2 as _alb,
    aws_ec2 as _ec2,
    aws_s3 as _s3,
    aws_certificatemanager as _certificate,
    aws_autoscaling as _asg,
    aws_autoscaling_hooktargets as _asg_hooktargets,
    aws_sns as _sns,
    aws_iam as _iam,
    aws_efs as _efs,
    aws_kms as _kms,
    aws_ssm as _ssm,
    aws_lambda as _lambda,
    aws_sns_subscriptions as _sns_subscriptions
)
from aws_cdk.core import Tags
import json
import os
import re
from aws_cdk_constructs.utils import normalize_environment_parameter, get_version

alphanumericPattern = pattern = re.compile("\W")

class Microservice(core.Construct):
    """A CDK construct to create a "computational tier" for your system.
    The construct will make easy to develop a fully compliant macro infrastructure component that includes EC2 instances, served by an Application Load Balancer.

    Internally the construct includes:

    - Application Load Balancer, configurable to be 'internal' or 'interet-facing' or to integrate with Cognito

    - Load Balancer listeners, configurable to be HTTPS or HTTP
    
    - Auto Scaling 

    - Target group

    - Launch configuration


    Args:
        id (str): the logical id of the newly created resource
        
        access_log_bucket_name (str): Default: "fao-elb-logs". To enable Load Balancer acces logs to be stored in the specified S3 bucket
        
        additional_variables (dict): You can specify additional parameters that will be available as environment variables for the EC2 user-data script
        
        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        authorization_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        client_id (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        client_secret (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        downstream_port: Used with 'downstream_port', 'downstream_security_group'. In case the EC2 server should integrate with another AWS resource, specify the integration port. This is generally used to specify a database port, whenever an EC2 fetches data from a database.
        In case the EC2 should send traffic to other AWS resources (a.k.a. downstream), specify the port to which send traffic to (e.g. if the EC2 uses a MySQL database, specify the MySQL database port 3306)

        downstream_security_group (str): Used with 'downstream_port', 'downstream_security_group'. In case the EC2 server should integrate with a target AWS resource, specify the target resource security group. This is generally used to specify a database security group, whenever an EC2 fetches data from a database. In case the EC2 should send traffic to other AWS resources (a.k.a. downstream), specify the security group Id of those resources (e.g. if the EC2 uses a database, specify the database cluster security group)

        ebs_snapshot_id (str): In case you want to create a secondary EBS volume from an EBS snapshot for your EC2 instance, this parameter is used to specify the snaphost id. Only use this parameter when your system cannot horizontally scale!

        ebs_volume_size (str): In case you want to create a secondary EBS volume for your EC2 instance, this parameter is used to specify the volume size. The parameter specify the desired GB. Only use this parameter when your system cannot horizontally scale!

        ec2_ami_id (str): Specify the EC2 AMI id to use to create the EC2 instance. Use "LATEST" the use laster Linux Hardened AMI.

        ec2_health_check_path (str):  Specify the Target Group health check path to use to monitor the state of the EC2 instances. EC2 instances will be constantly monitored, performing requests to this path. The request must receive a successful response code to consider the EC2 healthy. Otherwise the EC2 will be terminated and regenerated. It must start with a slash "/"

        ec2_instance_type (str): Specify the instance type of your EC2 instance. EC2 instance types https://aws.amazon.com/ec2/instance-types

        ec2_traffic_port (str): Specify the port the EC2 instance will listen to. This is used also as the Target Group Health check configuration port. For example (str)if you EC2 is equipped with an Apache Tomcat, listening on port 8080, use this parameter to specify 8080. It's important to note that this is not port the final user will use to connect to the system, as the Load Balancer will be in-front of the EC2.This is the port that the load balancer will use to forward traffic to the EC2 (e.g. Tomacat uses port 8080, Node.js uses port 3000).

        ec2_traffic_protocol (str): Specify the protcol the EC2 instance will listen to. This is used also as the Target Group Health check configuration protocol

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices 

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        issuer (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        main_component_name (str): This is just a metadata. Textually specify the component the EC2 instance will host (e.g. tomcat, drupal, ...)

        autoscaling_group_min_size (str): Optional - Auto Scaling group minimum size. Automatically set 2 is stack is Higly Available, 1 otherwise

        autoscaling_group_max_size (str): Optional - Auto Scaling group maximym size. Automatically set 4 is stack is Higly Available, 1 otherwise

        s3_assets_bucket_name (str): S3 bucket name used to store the assets of the application

        s3_code_bucket_name (str): S3 bucket name used to store the code of the application

        ssl_certificate_arn (str): In case you want to enable HTTPS for your stack, specify the SSL certificate ARN to use. This configuration will force the creation of 2 load balancer Listeners (str)one on port 443 that proxies to the Target Group, a second one on port 80 to redirect the traffic to port 443 and enforce HTTPS. In case the application implements HTTPS, specify the ARN of the SSL Certificate to use. You can find it in AWS Certificate Manager

        token_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        traffic_port (str): Specify the port the Application Load Balancer will listen to. This is the port the final users will contact to browse the system. If HTTPS is enabled, this parameter will be forced to be 443. This is the port that the application will use to accpet traffic (e.g. if the application uses HTTPS, specify 443; if the application uses HTTP, specify 80; etc.).

        upstream_security_group (str): In case the application is published as part of a parent app, please specify the security group of the resource will sent traffic to the app (e.g. if the app is part of fao.org website, given that the app will be receive traffic from the fao.org reverse proxies, specify the fao.org reverse proxy security group ID)

        user_data_s3_key (str): Installation of tools, libs and any other requirements will be performed programmatically via user-data script. Please specify the S3 key of the user-data script to use. This file must be stored within the S3 configuration bucket of the specific environment, following the pattern ${ConfBucket}/${ApplicationName}/${Environment}/${UserDataS3Key} (e.g. dev-fao-aws-configuration-files/myApp1/Development/user-data.sh, prod-fao-aws-configuration-files/myApp2/Production/user-data.sh,)

        user_info_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        will_be_ha (str): Only applicatble if the EC2 is stateless! True/False depending to the fact your system can be configure to be highly available.

        will_be_public (str): Whether of not the application should be publicly accessible

        will_send_email (str): Whether of not the application should send email. Real email messages will be sent only from the Production environment. For the other evinronment the system will be configured to use the CSI dev SMTP server

        will_use_efs (str): Wether or not should create a EFS

        will_use_cdn (str): Wether or not the Application Load Balancer should receive traffic only from Cloudflare CDN
        
        will_use_ldap (str): Wether or not the EC2 instance should be able to integrate with LDAP. This configuration set-up the LDAP client security group to the EC2

        existing_efs_security_group (str): In case you want to enble access to an existing EFS, provide its security group resource. If provided, `existing_efs_security_group_id` will be ignored
        
        existing_efs_security_group_id (str): In case you want to enble access to an existing EFS, provide its already-existing security group ID. If `existing_efs_security_group`, this will be ignored. Important: `existing_efs_security_group_id` works only if the Security Group is already existing and deployed on AWS. Not compabible with security groups created during the first deployment.

        tag_scheduler_uptime (str): specifies the time range in which the AWS resource should be kept up and running - format `HH:mm-HH:mm` (i.e. 'start'-'end'), where the 'start' time must be before 'end'
        
        tag_scheduler_uptime_days (str): weekdays in which the `SchedulerUptime` tag should be enforced. If not specified, `SchedulerUptime` will be enforced during each day of the week - format integer from 1 to 7, where 1 is Monday
        
        tag_scheduler_uptime_skip (str): to skip optimization check - format Boolean (`true`, `false`),

        network_load_balancer_ip_1 (Optional | str): nlb ip 1
        
        network_load_balancer_ip_2 (Optional | str): nlb ip 2
        
        network_load_balancer_subnet_1 (Optional | str): private subnet 1

        network_load_balancer_subnet_2 (Optional | str): private subnet 2

        network_load_balancer_source_autoscaling_group (Optional | aws_autoscaling.AutoScalingGroup): the asg that can communicate with the nlb machines

        stickiness_cookie_duration_in_hours: (Optinal | str) if provided sticky sessions will be configured for the Application Load Balancer.

        load_balancer_idle_timeout_in_seconds: (Optional | str) if provided idle timeout will be  configured for the Application Load Balancer.

        rubrik_backup (str): to enable/disable Rubrik backup using tag `RubrikBackup` - format Boolean (`true`, `false`). Default: true

    """

    @property
    def ec2_role(self):
        return self._ec2_role

    @property
    def vpc(self):
        """[summary]
        Returns the VPC in which the stack is deployed on

        Returns:
            aws_ec2.Vpc: the VPC in which the stack is deployed on
        """
        return self._vpc

    @property
    def alb_logs_bucket(self):
        """Returns S3 bucket that the Application Load Balancer is using for storing the logs

        Returns:
            str: the S3 bucket that the Application Load Balancer is using for storing the logs
        """
        return self._alb_logs_bucket

    @property
    def tcp_connection_ec2_traffic_port(self):
        """Returns the EC2 traffic port as TCP connection

        Returns:
            aws_ec2.Port.tcp: the EC2 traffic port
        """
        return self._tcp_connection_ec2_traffic_port

    @property
    def tcp_connection_traffic_port(self):
        """Returns the Load Balancer port as TCP connection

        Returns:
            aws_ec2.Port.tcp: the Load Balancer port
        """
        return self._tcp_connection_traffic_port

    @property
    def target_group(self):
        """Returns the security group in use by the EC2

        Returns:
            aws_alb.ApplicationTargetGroup: the Application Target gruop
        """
        return self._tg

    @property
    def auto_scaling_group(self):
        """Returns the Auto Scaling Group object

        Returns:
            aws_ec2.AutoScalingGroup: the Auto Scaling Group
        """
        return self._asg

    @property
    def network_load_balancer(self):
        """Returns the Network Load Balancer object

        Returns:
            aws_alb.NetworkLoadBalancer: the Load Balancer
        """
        return self.nlb
    
    @property
    def load_balancer(self):
        """Returns the Application Load Balancer object

        Returns:
            aws_alb.ApplicationLoadBalancer: the Load Balancer
        """
        return self.alb

    @property
    def load_balancer_security_group(self):
        """Returns the security group in use by the application load balancer

        Returns:
            aws_ec2.SecurityGroup: the security group in use by the application load balancer
        """
        return self.alb_security_group

    @property
    def ec2_instance_security_group(self):
        """Return the security group in use by the EC2 instance

        Returns:
            aws_ec2.SecurityGroup: the security group in use by the EC2 instance
        """
        return self.ec2_security_group

    @property
    def user_data(self):
        """Return the user-data used by the EC2 instance on boot

        Returns:
            aws_ec2.UserData: the user-data used by the EC2 instance on boot
        """
        return self.base_user_data
    
    @property
    def efs(self):
        """Return the EFS resource, in case it was created

        Returns:
            aws_efs.FileSystem: he EFS resource
        """
        return self._efs
    
    @property
    def efs_security_group(self):
        """Return the EFS's security group, in case it was created

        Returns:
            aws_ec2.SecurityGroup: the security group in use by the EFS FileSystem
        """
        return self._efs_security_group

    def enable_fao_private_access(self, security_group):
        """Apply the correct ingress rules to the provided security group to enable access from the FAO internal networks
        
        Args:
            security_group (aws_ec2.SecurityGroup): The security group to configure to enable access from FAO network
    
        Returns:
            aws_ec2.SecurityGroup: the provided security group
        """ 
        security_group.add_ingress_rule(
            peer=self.pulse_cidr_as_peer(self._environments_parameters),
            connection=self.tcp_connection_traffic_port,
            description="Pulse Secure",
        )

        security_group.add_ingress_rule(
            peer=self.fao_hq_clients_as_peer(self._environments_parameters),
            connection=self.tcp_connection_traffic_port,
            description="FAO HQ Clients",
        )
        security_group.add_ingress_rule(
            peer=self.azure_dev_avd_as_peer(self._environments_parameters),
            connection=self.tcp_connection_traffic_port,
            description="Azure Development Virtual Desktop",
        )

        security_group.add_ingress_rule(
            peer=self.azure_dev_cpc_as_peer(self._environments_parameters),
            connection=self.tcp_connection_traffic_port,
            description="Azure Development Cloud PC",
        )

        return security_group

    def create_network_target_group(
        self,
        id,
        app_name,
        ec2_traffic_port,
    ):
        """Create a Network Target Group
        
        Args:
            id (str): the logical id of the newly created resource

            app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

            ec2_traffic_port (str): Specify the port the EC2 instance will listen to. This is used also as the Target Group Health check configuration port. For example (str)if you EC2 is equipped with an Apache Tomcat, listening on port 8080, use this parameter to specify 8080. It's important to note that this is not port the final user will use to connect to the system, as the Load Balancer will be in-front of the EC2.This is the port that the load balancer will use to forward traffic to the EC2 (e.g. Tomacat uses port 8080, Node.js uses port 3000).

        """

        nlb_tg_hc=_alb.HealthCheck(
            healthy_threshold_count=2,
            interval=core.Duration.seconds(30),
            port=ec2_traffic_port,
            protocol=_alb.Protocol.TCP,
            unhealthy_threshold_count=2
        )

        nlb_target_group = _alb.NetworkTargetGroup(
            self,
            id + "_nlb_tg",
            port=int(ec2_traffic_port),
            protocol=_alb.Protocol.TCP,
            health_check=nlb_tg_hc,
            target_type=_alb.TargetType.INSTANCE,
            vpc=self.vpc
        )
        
        return nlb_target_group

    def create_target_group(
        self,
        id,
        app_name,
        environment,
        ec2_traffic_port,
        ec2_health_check_path,
        protocol=_alb.ApplicationProtocol.HTTP,
        stickiness_cookie_duration_in_hours=None,
    ):
        """Create a Target Group object
        
        Args:
            id (str): the logical id of the newly created resource

            app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

            ec2_traffic_port (str): Specify the port the EC2 instance will listen to. This is used also as the Target Group Health check configuration port. For example (str)if you EC2 is equipped with an Apache Tomcat, listening on port 8080, use this parameter to specify 8080. It's important to note that this is not port the final user will use to connect to the system, as the Load Balancer will be in-front of the EC2.This is the port that the load balancer will use to forward traffic to the EC2 (e.g. Tomacat uses port 8080, Node.js uses port 3000).

            ec2_health_check_path (str):  Specify the Target Group health check path to use to monitor the state of the EC2 instances. EC2 instances will be constantly monitored, performing requests to this path. The request must receive a successful response code to consider the EC2 healthy. Otherwise the EC2 will be terminated and regenerated. It must start with a slash "/"
            
            protocol (aws_alb.ApplicationProtocol): Default=_alb.ApplicationProtocol.HTTP. The protocol the target group uses to receive traffic
        
            stickiness_cookie_duration_in_hours: (Optinal | str) if provided sticky sessions will be configured for the Application Load Balancer.
            
        Returns:
            aws_ec2.SecurityGroup: the provided security group
        """ 

        environment = normalize_environment_parameter(environment)

        tg = _alb.ApplicationTargetGroup(
            self,
            id,
            port=int(ec2_traffic_port),  # Must be a int
            protocol=protocol,
            vpc=self._vpc,
            target_type=_alb.TargetType.INSTANCE,
            target_group_name=(app_name + id + ec2_traffic_port).replace("_", "-"),
            stickiness_cookie_duration=core.Duration.hours(int(stickiness_cookie_duration_in_hours)) if stickiness_cookie_duration_in_hours else None,
        )
        tg.configure_health_check(
            enabled=True,
            healthy_http_codes="200-399",
            healthy_threshold_count=2,
            interval=core.Duration.seconds(6),
            path=ec2_health_check_path,
            port=ec2_traffic_port,
            protocol=protocol,
            timeout=core.Duration.seconds(5),
            unhealthy_threshold_count=2,
        )

        # Apply mandatory tags
        Tags.of(tg).add("ApplicationName", app_name.lower().strip())
        Tags.of(tg).add("Environment", environment)

        return tg

    def create_network_load_balancer(self, scope, id, environment, network_load_balancer_ip_1, network_load_balancer_ip_2, network_load_balancer_subnet_1, network_load_balancer_subnet_2):
        """Create a network load balancer

        Args:
            id (str): the logical id of the newly created resource
        """
        environment = normalize_environment_parameter(environment)
        is_production = environment == "Production"
        
        nlb = _alb.NetworkLoadBalancer(self, id + '_nlb',
            cross_zone_enabled=True,
            vpc=self.vpc,
            deletion_protection=is_production,
            internet_facing=False
        )

        cfnNlb = nlb.node.default_child
        cfnNlb.add_deletion_override("Properties.Subnets")
        cfnNlb.add_property_override(
            property_path="SubnetMappings",
            value=[
                {"SubnetId": network_load_balancer_subnet_1, "PrivateIPv4Address": network_load_balancer_ip_1},
                {"SubnetId": network_load_balancer_subnet_2, "PrivateIPv4Address": network_load_balancer_ip_2}
            ]
        )

        return nlb

    def create_load_balancer(self, scope, id, app_name, environment, environments_parameters, security_group=None, internet_facing=False, load_balancer_name=None, use_cdn=False, main_component_name=None, load_balancer_idle_timeout_in_seconds=None):
        """Create a Load Balancer resource
        
        Args:
            id (str): the logical id of the newly created resource

            security_group (Optional | [aws_ec2.SecurityGroup]): The security group to configure to enable access from FAO network

            internet_facing (str): if the load balancer should be internet-facing or not

            load_balancer_name (str): the load balancer name

            use_cdn (bool): if the Application Load Balancer should accept traffic only from CDN. If this is set to True, the `
            _group` parameter will be ignored

            main_component_name (Optional | str): This is just a metadata. Textually specify the component the EC2 instance will host (e.g. tomcat, drupal, ...)

            load_balancer_idle_timeout_in_seconds: (Optional | str) if provided idle timeout will be  configured for the Application Load Balancer. (Default is 50s)
    
        Returns:
            aws_alb.ApplicationLoadBalancer: the newly created Load Balancer
        """ 
        environment = normalize_environment_parameter(environment)
        is_production = environment == "Production"
        
        if load_balancer_name is None:
            load_balancer_name = id
        
        if load_balancer_idle_timeout_in_seconds is None:
            load_balancer_idle_timeout_in_seconds = '50'

        # In case CDN is in use, create a new Security Group with access
        # Only from Cloudflare and replace the provided Security Group with the newly 
        # created one 
        if use_cdn:
            cdn_security_group = self.create_security_group(
                self, 
                "alb_secg_cdn", 
                app_name, 
                environment, 
                app_name + '_' + main_component_name + "_alb_secg_cdn",
                )

            # Cloudflare doc https://support.cloudflare.com/hc/en-us/articles/360037983412-Configuring-an-Amazon-Web-Services-static-site-to-use-Cloudflare
            cloudflare_ips_v4 = [
                "103.21.244.0/22",
                "103.22.200.0/22",
                "103.31.4.0/22",
                "104.16.0.0/13", 
                "104.24.0.0/14",
                "108.162.192.0/18",
                "131.0.72.0/22",
                "141.101.64.0/18",
                "162.158.0.0/15",
                "172.64.0.0/13",
                "173.245.48.0/20",
                "188.114.96.0/20",
                "190.93.240.0/20",
                "197.234.240.0/22",
                "198.41.128.0/17",
            ]
            for ip in cloudflare_ips_v4:
                cdn_security_group.add_ingress_rule(                
                    peer=_ec2.Peer.ipv4(ip),
                    connection=self._tcp_connection_traffic_port,
                    description="Cloudflare ipv4",
                    )     

            # Cloudflare doc https://support.cloudflare.com/hc/en-us/articles/360037983412-Configuring-an-Amazon-Web-Services-static-site-to-use-Cloudflare
            cloudflare_ips_v6 = [
                "2400:cb00::/32",
                "2405:8100::/32",
                "2405:b500::/32",
                "2606:4700::/32",
                "2803:f800::/32",
                "2c0f:f248::/32",
                "2a06:98c0::/29",
            ]
            for ip in cloudflare_ips_v6:
                cdn_security_group.add_ingress_rule(                
                    peer=_ec2.Peer.ipv6(ip),
                    connection=self._tcp_connection_traffic_port,
                    description="Cloudflare ipv6",
                    )     
                    
            security_group = cdn_security_group

        alb = _alb.ApplicationLoadBalancer(
            scope,
            id,
            load_balancer_name=load_balancer_name,
            vpc=self.vpc,
            internet_facing=internet_facing,
            idle_timeout=core.Duration.seconds(int(load_balancer_idle_timeout_in_seconds)),
            security_group=security_group,
            deletion_protection=is_production
        )

        # Enable access from App Proxy if the Load Balancer is private
        if internet_facing is False:
            aws_account = environments_parameters["accounts"][environment.lower()]
            app_proxy_security_group = _ec2.SecurityGroup.from_security_group_id(
                self, "upstream_security_group_app_proxy_"+main_component_name, aws_account["app_proxy_security_group"], mutable=False
            )
            alb.add_security_group(app_proxy_security_group)
        
        # Enable logging
        alb.log_access_logs(self._alb_logs_bucket, prefix=self._app_name)

        # Apply mandatory tags
        Tags.of(alb).add("ApplicationName", app_name.lower().strip())
        Tags.of(alb).add("Environment", environment)

        return alb

    def create_security_group(
        self, scope, id, app_name, environment, security_group_name, allow_all_outbound=True
    ):
        """Create a Security Group resource
        
        Args:
            id (str): the logical id of the newly created resource
            
            security_group_name (str): The security group name

            allow_all_outbound (str): if the security group should enable outgoing traffic. Default=True
    
        Returns:
            aws_ec2.SecurityGroup: the newly created security group
        """ 
        environment = normalize_environment_parameter(environment)
        sg = _ec2.SecurityGroup(
            scope,
            id,
            vpc=self._vpc,
            security_group_name=security_group_name,
            allow_all_outbound=allow_all_outbound,
        )

        # Apply mandatory tags
        Tags.of(sg).add("ApplicationName", app_name.lower().strip())
        Tags.of(sg).add("Environment", environment)

        return sg

    # to update the userData definition after the first initialization
    def set_user_data_additional_variables(self, variables: dict):
        """Add the provided variables as environment variables for the user-data script
        
        Args:
            variables (dict): the dict containing the variables to add to the user data as environment variables
    
        Returns:
            aws_ec2.UserData: the updated user data
        """ 
        ADDITIONAL_VARIABLES_PLACEHOLDER = "#ADDITIONAL_VARIABLES_HERE"
        for vkey in variables:
            new_variable_string = (
                'echo "export _KEY_=_VALUE_" >> $MY_VARS_FILE\n'
                + ADDITIONAL_VARIABLES_PLACEHOLDER
            )
            new_variable_string = new_variable_string.replace("_KEY_", vkey)
            new_variable_string = new_variable_string.replace(
                "_VALUE_", variables[vkey]
            )
            self.base_user_data = self.base_user_data.replace(
                ADDITIONAL_VARIABLES_PLACEHOLDER, new_variable_string
            )

        return self.base_user_data

    # to update the userData definition after the first initialization
    def update_user_data(self, base_user_data: str, asg_name=None):
        """Replace the auto generated user-data with the provided one

        Args:
            user_data (aws_ec2.UserData): The User Data to use in the EC2 instance
            asg_name (Optional | str): The asg name
        
        Returns:
            aws_ec2.UserData: the provided user data
        """ 
        self.auto_scaling_group.node.find_child('LaunchConfig').add_property_override(property_path="UserData", value=core.Fn.base64(base_user_data))
        self.auto_scaling_group.add_user_data(base_user_data)

    @staticmethod
    def pulse_cidr_as_peer(environments_parameters):
        """Returns the Pulse secure network as Peer

        Args:
            environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.
 
        Returns:
            aws_ec2.Peer: The Pulse secure network as Peer resource 
        """ 
        fao_networks = environments_parameters["networking"]
        return _ec2.Peer.ipv4(fao_networks["pulse"])

    @staticmethod
    def fao_hq_clients_as_peer(environments_parameters):
        """Returns the HQ client subnet as Peer

        Args:
            environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.
 
        Returns:
            aws_ec2.Peer: the HQ client subnet as Peer resource 
        """ 
        fao_networks = environments_parameters["networking"]
        return _ec2.Peer.ipv4(fao_networks["fao_hq_clients"])

    @staticmethod
    def azure_dev_avd_as_peer(environments_parameters):
        """Returns the Azure Development Virtual Desktop network as Peer

        Args:
            environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        Returns:
            aws_ec2.Peer: The Azure Development Virtual Desktop network as Peer resource
        """
        fao_networks = environments_parameters["networking"]
        return _ec2.Peer.ipv4(fao_networks["azure_dev_avd"])

    @staticmethod
    def azure_dev_cpc_as_peer(environments_parameters):
        """Returns the The Azure Development Cloud PC network as Peer

        Args:
            environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        Returns:
            aws_ec2.Peer: The Azure Development Cloud PC network as Peer resource
        """
        fao_networks = environments_parameters["networking"]
        return _ec2.Peer.ipv4(fao_networks["azure_dev_cpc"])


    def asg_name(self):
        """Return the Auto Scaling Group name

        Returns:
            str: the Auto Scaling Group name
       
        """
        return "asg"

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        app_name,
        environment,
        environments_parameters,
        main_component_name,
        will_be_public=False,
        will_send_email=False,
        ec2_ami_id=None,
        ec2_instance_type=None,
        autoscaling_group_max_size=None,
        autoscaling_group_min_size=None,
        s3_code_bucket_name=None,
        s3_assets_bucket_name=None,
        traffic_port=None,
        ec2_traffic_port=None,
        ec2_traffic_protocol=_alb.ApplicationProtocol.HTTP,
        upstream_security_group=None,
        ec2_health_check_path=None,
        user_data_s3_key="user-data.sh",
        downstream_security_group=None,
        downstream_port=None,
        ssl_certificate_arn=None,
        will_be_ha=True,
        ebs_volume_size=None,
        ebs_snapshot_id=None,
        will_use_efs=False,
        will_use_cdn=False,
        access_log_bucket_name="fao-elb-logs",
        authorization_endpoint=None,
        token_endpoint=None,
        issuer=None,
        client_id=None,
        client_secret=None,
        user_info_endpoint=None,
        will_use_ldap=None,
        additional_variables: dict = None,
        existing_efs_security_group = None,
        existing_efs_security_group_id = None,
        tag_scheduler_uptime="",
        tag_scheduler_uptime_days="",
        tag_scheduler_uptime_skip="",
        network_load_balancer_ip_1=None,
        network_load_balancer_ip_2=None,
        network_load_balancer_subnet_1=None,
        network_load_balancer_subnet_2=None,
        network_load_balancer_source_autoscaling_group=None,
        stickiness_cookie_duration_in_hours=None,
        load_balancer_idle_timeout_in_seconds=None,
        rubrik_backup="True",
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)
    
        environment = normalize_environment_parameter(environment)
        
        # Apply mandatory tags
        Tags.of(self).add("ApplicationName", app_name, apply_to_launched_instances=True,)
        Tags.of(self).add("Environment", environment, apply_to_launched_instances=True,)

        # Apply FAO CDK tags
        Tags.of(self).add("fao-cdk-construct", "microservice")
        Tags.of(core.Stack.of(self)).add("fao-cdk-version", get_version())
        Tags.of(core.Stack.of(self)).add("fao-cdk", "true")

        self.id = id

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create conditions
        is_https = not not ssl_certificate_arn
        is_not_https = not is_https

        sends_emails = (
            will_send_email
            and isinstance(will_send_email, str)
            and will_send_email.lower() == "true"
        )

        is_public = (
            will_be_public
            and isinstance(will_be_public, str)
            and will_be_public.lower() == "true"
        )
        is_private = not is_public

        is_production = environment == "Production"
        is_not_production = not is_production

        has_upstream = not not upstream_security_group
        has_not_upstream = not has_upstream
        use_cdn = (
            will_use_cdn and isinstance(will_use_cdn, str) and will_use_cdn.lower() == "true"
        )
        not_use_cdn = not use_cdn
        
        is_public_and_no_upstream = is_public and has_not_upstream
        is_public_and_has_upstream = is_public and has_upstream
        is_public_and_no_upstream_and_no_cdn = is_public and has_not_upstream and not_use_cdn
        is_private_and_is_https = is_private and is_https
        is_private_and_has_upstream = is_private and has_upstream
        is_public_has_no_upstream_and_is_https = (
            has_not_upstream and is_public and is_https
        )
        is_public_has_upstream_and_is_https = has_upstream and is_public and is_https
        is_public_has_no_upstream_and_is_https_and_no_cdn = is_public_has_no_upstream_and_is_https and not_use_cdn

        has_downstream = not not downstream_security_group
        has_not_downstream = not has_downstream

        is_ha = (
            will_be_ha and isinstance(will_be_ha, str) and will_be_ha.lower() == "true"
        )
        is_not_ha = not is_ha

        is_network_load_balancer = (network_load_balancer_ip_1 and 
                                    network_load_balancer_ip_2 and
                                    network_load_balancer_subnet_1 and
                                    network_load_balancer_subnet_2 and
                                    network_load_balancer_source_autoscaling_group)

        is_network_load_balancer_partially_configured = (network_load_balancer_ip_1 or 
                                    network_load_balancer_ip_2 or
                                    network_load_balancer_subnet_1 or
                                    network_load_balancer_subnet_2 or
                                    network_load_balancer_source_autoscaling_group)
        
        if is_network_load_balancer_partially_configured and not is_network_load_balancer:
            raise Exception(
                "Network load balancer needs the following parameters: network_load_balancer_ip_1, network_load_balancer_ip_2, network_load_balancer_subnet_1, network_load_balancer_subnet_2, network_load_balancer_source_autoscaling_group"
            )
        
        is_application_load_balancer = not is_network_load_balancer
        

        use_ebs = not not ebs_volume_size
        create_ebs = use_ebs and is_not_ha

        create_efs = (
            will_use_efs
            and isinstance(will_use_efs, str)
            and will_use_efs.lower() == "true"
        )


        self._environments_parameters = environments_parameters
        aws_account = self._environments_parameters["accounts"][environment.lower()]

        az_in_use = aws_account["az"]

        account_id = aws_account["id"]

        self._app_name = app_name

        has_oidc = (
            authorization_endpoint
            and token_endpoint
            and issuer
            and client_id
            and client_secret
            and user_info_endpoint
        )
        has_not_oidc = not has_oidc

        has_at_least_one_oidc = (
            authorization_endpoint
            or token_endpoint
            or issuer
            or client_id
            or client_secret
            or user_info_endpoint
        )

        has_additional_variables = additional_variables

        ROOT_VOLUME_SIZE = 50
        AUTOSCALING_GROUP_LOGICAL_ID = re.sub(
            alphanumericPattern, "", "".join([main_component_name, "AutoScalingGroup"])
        )

        use_ldap = (
            will_use_ldap and isinstance(will_use_ldap, str) and will_use_ldap.lower() == "true"
        )

        to_be_backed_up = (
            rubrik_backup
            and isinstance(rubrik_backup, str)
            and rubrik_backup.lower() == "true"
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validate input params

        if has_additional_variables and type(additional_variables) is not dict:
            raise Exception(
                "additional_variables should be passed as a python dictionary"
            )

        if has_at_least_one_oidc and not has_oidc:
            raise Exception(
                "OIDC configuration is not valid! If you aimed to configure OIDC listener please provide each of the parmas: authorization_endpoint, token_endpoint, issuer, client_id, client_secret, user_info_endpoint"
            )

        # MUST EXIST environments_parameters, enviroment
        # How to raise an exception in python
        #  raise Exception(
        #     "Impossible to find the mandatory env variable APPLICATION_NAME"
        # )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Retrieve info from already existing AWS resources
        # Important: you need an internet connection!

        # VPC
        self._vpc = _ec2.Vpc.from_vpc_attributes (self, 
            "VPC", 
            vpc_id=aws_account["vpc"], 
            public_subnet_ids=aws_account["public_subnet_ids"], 
            private_subnet_ids=aws_account["private_subnet_ids"], 
            availability_zones=aws_account["availability_zones"], 
        )

        # ALB logs bucket
        self._alb_logs_bucket = _s3.Bucket.from_bucket_name(
            self, "alb_logs_bucket", access_log_bucket_name
        )

        # SNS ASG notifications topic
        asg_notifications_topic = _sns.Topic.from_topic_arn(
            self, "asg_notifications_topic", aws_account["asg_sns_topic"]
        )

        # Shared CIDRs and peers for security groups
        self._tcp_connection_traffic_port = _ec2.Port.tcp(int(traffic_port)) if is_application_load_balancer else None
        self._tcp_connection_ec2_traffic_port = _ec2.Port.tcp(int(ec2_traffic_port))
        self._pulse_cidr_as_peer = self.pulse_cidr_as_peer(self._environments_parameters)
        self._fao_hq_clients_as_peer = self.fao_hq_clients_as_peer(
            self._environments_parameters
        )
        self._azure_dev_avd_as_peer = self.azure_dev_avd_as_peer(
            self._environments_parameters
        )
        self._azure_dev_cpc_as_peer = self.azure_dev_cpc_as_peer(
            self._environments_parameters
        )
        if has_upstream:
            upstream_security_group_as_peer = _ec2.SecurityGroup.from_security_group_id(
                self, "upstream_security_group_"+main_component_name, upstream_security_group, mutable=True
            )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create AWS resources

        # ~~~~~~~~~~~~~~~~
        # EBS
        # ~~~~~~~~~~~~~~~~
        if create_ebs:
            ebs = _ec2.CfnVolume(
                self,
                "ebs",
                availability_zone=az_in_use,
                encrypted=True,
                kms_key_id=aws_account["kms_ebs_key"],
                size=int(ebs_volume_size),
                snapshot_id=ebs_snapshot_id,
            )

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Rubrik backup tag

            if to_be_backed_up:
                Tags.of(ebs).add("RubrikBackup", "true")
            else:
                Tags.of(ebs).add("RubrikBackup", "false")

            # if is_production:
            #     ebs.add_override("DeletionPolicy", core.RemovalPolicy.SNAPSHOT)

        # ~~~~~~~~~~~~~~~~
        # Target group
        # ~~~~~~~~~~~~~~~~
        if(is_network_load_balancer):
            self._tg = self.create_network_target_group(
                main_component_name, app_name, ec2_traffic_port
            )
        else:
            self._tg = self.create_target_group(
                main_component_name, app_name, environment, ec2_traffic_port, ec2_health_check_path, protocol=ec2_traffic_protocol, stickiness_cookie_duration_in_hours=stickiness_cookie_duration_in_hours
            )

        if(is_application_load_balancer):
            # ~~~~~~~~~~~~~~~~
            # Elastic Load Balancer Security Group
            # ~~~~~~~~~~~~~~~~
            self.alb_security_group = self.create_security_group(
                self, 
                "alb_secg", 
                app_name, 
                environment, 
                app_name + '_' + main_component_name + "_alb_secg"
            )

            if is_private:
                self.enable_fao_private_access(self.alb_security_group)

            if is_public_and_no_upstream_and_no_cdn:
                self.alb_security_group.add_ingress_rule(
                    peer=_ec2.Peer.any_ipv4(),
                    connection=self._tcp_connection_traffic_port,
                    description="Everyone",
                )

            if is_public_and_has_upstream:
                self.alb_security_group.add_ingress_rule(
                    peer=upstream_security_group_as_peer,
                    connection=self._tcp_connection_traffic_port,
                    description="From upstream",
                )

            # Used when HTTPS is forced. These rules enable the redirect from HTTP -> HTTPS
            if is_private_and_is_https:
                self.alb_security_group.add_ingress_rule(
                    peer=self._pulse_cidr_as_peer,
                    connection=_ec2.Port.tcp(80),
                    description="Pulse Secure",
                )
                self.alb_security_group.add_ingress_rule(
                    peer=self._fao_hq_clients_as_peer,
                    connection=_ec2.Port.tcp(80),
                    description="FAO HQ Clients",
                )
                self.alb_security_group.add_ingress_rule(
                    peer=self._azure_dev_avd_as_peer,
                    connection=_ec2.Port.tcp(80),
                    description="Azure Development Virtual Desktop network",
                )
                self.alb_security_group.add_ingress_rule(
                    peer=self._azure_dev_cpc_as_peer,
                    connection=_ec2.Port.tcp(80),
                    description="Azure Development Cloud PC Network",
                )
            # Used when HTTPS is forced. These rules enable the redirect from HTTP -> HTTPS
            if is_public_has_no_upstream_and_is_https_and_no_cdn:
                self.alb_security_group.add_ingress_rule(
                    peer=_ec2.Peer.any_ipv4(),
                    connection=_ec2.Port.tcp(80),
                    description="Everyone to HTTPS",
                )
            # Used when HTTPS is forced. These rules enable the redirect from HTTP -> HTTPS
            if is_public_has_upstream_and_is_https:
                self.alb_security_group.add_ingress_rule(
                    peer=upstream_security_group_as_peer,
                    connection=_ec2.Port.tcp(80),
                    description="Upstream to HTTPS",
                )

            if is_private_and_has_upstream:
                self.alb_security_group.add_ingress_rule(
                    peer=upstream_security_group_as_peer,
                    connection=self._tcp_connection_traffic_port,
                    description="From upstream",
                )

            if is_not_production:
                self.alb_security_group.add_ingress_rule(
                    peer=_ec2.Peer.ipv4("168.202.4.57/32"),
                    connection=self._tcp_connection_traffic_port,
                    description="From Security Scan tool",
                )

        # ~~~~~~~~~~~~~~~~
        # Elastic Load Balancer v2
        # ~~~~~~~~~~~~~~~~
        if(is_network_load_balancer):
            self.nlb = self.create_network_load_balancer(
                self,
                "nlb",
                environment,
                network_load_balancer_ip_1,
                network_load_balancer_ip_2,
                network_load_balancer_subnet_1,
                network_load_balancer_subnet_2
            )
            self.nlb.add_listener(
                'instance_nlb_listener',
                port=int(ec2_traffic_port),
                protocol=_alb.Protocol.TCP,
                default_target_groups=[self._tg]
            )
        else:
            self.alb = self.create_load_balancer(
                self, 
                "alb", 
                app_name, 
                environment, 
                environments_parameters, 
                self.alb_security_group, 
                internet_facing=is_public, 
                load_balancer_name='-'.join([app_name, main_component_name, 'alb']), 
                use_cdn=use_cdn,
                main_component_name=main_component_name,
                load_balancer_idle_timeout_in_seconds=load_balancer_idle_timeout_in_seconds
            )
        
        if(is_application_load_balancer):
            # Listeners
            if is_not_https:
                self.alb.add_listener(
                    "is_not_https",
                    port=int(traffic_port),
                    open=False, 
                    protocol=_alb.ApplicationProtocol.HTTP,
                    default_target_groups=[self._tg],
                )

            if is_https:
                # HTTP listener forces HTTPS
                self.alb.add_listener(
                    "redirect_to_https",
                    port=80,
                    open=False, 
                    protocol=_alb.ApplicationProtocol.HTTP,
                    default_action=_alb.ListenerAction.redirect(
                        host="#{host}",
                        path="/#{path}",
                        port="443",
                        protocol="HTTPS",
                        query="#{query}",
                        permanent=True,
                    ),
                )

                # HTTPS certificate
                certificate = _certificate.Certificate.from_certificate_arn(
                    self, "https_certificate", certificate_arn=ssl_certificate_arn
                )

                if has_not_oidc:
                    self.alb.add_listener(
                        "is_https",
                        port=int(traffic_port),
                        protocol=_alb.ApplicationProtocol.HTTPS,
                        certificates=[certificate],
                        default_target_groups=[self._tg],
                        open=False, 
                        ssl_policy=_alb.SslPolicy.FORWARD_SECRECY_TLS12_RES
                    )

                if has_oidc:
                    # Default action: forward to TG
                    listener_default_action = _alb.ListenerAction.forward(
                        target_groups=[self._tg]
                    )

                    # OIDC action: authenticate with Cognito and concatenate the forward
                    oidc_listener_action = _alb.ListenerAction.authenticate_oidc(
                        authorization_endpoint=authorization_endpoint,
                        token_endpoint=token_endpoint,
                        issuer=issuer,
                        client_id=client_id,
                        client_secret=core.SecretValue(value=client_secret),
                        user_info_endpoint=user_info_endpoint,
                        next=listener_default_action,
                    )

                    # Create listener
                    self.alb.add_listener(
                        "is_https",
                        port=int(traffic_port),
                        open=False, 
                        protocol=_alb.ApplicationProtocol.HTTPS,
                        certificates=[certificate],
                        default_action=oidc_listener_action,
                        ssl_policy=_alb.SslPolicy.FORWARD_SECRECY_TLS12_RES
                    )

        # ~~~~~~~~~~~~~~~~
        # Instance profile
        # ~~~~~~~~~~~~~~~~

        self._ec2_role = _iam.Role(
            self,
            "asg_role",
            description=app_name + "_" + main_component_name + "_ec2_role",
            assumed_by=_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                # AWS managed policy to allow sending logs and custom metrics to CloudWatch
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchAgentServerPolicy"
                ),
                # AWS managed policy to allow Session Manager console connections to the EC2 instance
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
            ],
            role_name=app_name + "_" + main_component_name + "_ec2_role",
        )

        # Inline policies
        self._ec2_role.attach_inline_policy(
            _iam.Policy(
                self,
                "ec2_policies",
                statements=[
                    # Policy for EBS
                    _iam.PolicyStatement(
                        actions=["ec2:AttachVolume", "ec2:DescribeVolumeStatus"],
                        resources=["*"],
                    ),
                    # S3 access to get from the config bucket configuration files, code packages and libraries
                    _iam.PolicyStatement(
                        actions=["s3:List*"],
                        resources=[
                            "arn:aws:s3:::" + aws_account["s3_config_bucket"],
                            "arn:aws:s3:::"
                            + aws_account["s3_config_bucket"]
                            + "/"
                            + self._app_name
                            + "/*",
                        ],
                    ),
                    _iam.PolicyStatement(
                        actions=["s3:*"],
                        resources=[
                            "arn:aws:s3:::"
                            + aws_account["s3_config_bucket"]
                            + "/"
                            + self._app_name
                            + "/"
                            + environment,
                            "arn:aws:s3:::"
                            + aws_account["s3_config_bucket"]
                            + "/"
                            + self._app_name
                            + "/"
                            + environment
                            + "/*",
                        ],
                    ),
                    # S3 access to get SentinelOne
                    _iam.PolicyStatement(
                        actions=["s3:List*", "s3:Get*"],
                        resources=[
                            "arn:aws:s3:::"
                            + aws_account["s3_config_bucket"]
                            + "/sentinelone/linux/*",
                        ],
                    ),
                    # KMS LimitedAccess just to use the keys
                    _iam.PolicyStatement(
                        actions=[
                            "kms:Decrypt",
                            "kms:Encrypt",
                            "kms:ReEncrypt*",
                            "kms:GenerateDataKey*",
                            "kms:Describe*",
                        ],
                        resources=[
                            "arn:aws:kms:eu-west-1:"
                            + core.Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ":key/"
                            + aws_account["kms_ssm_key"],
                            "arn:aws:kms:eu-west-1:"
                            + core.Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ":key/"
                            + aws_account["kms_ebs_key"],
                        ],
                    ),
                    _iam.PolicyStatement(
                        actions=[
                            "kms:CreateGrant",
                            "kms:ListGrants",
                            "kms:RevokeGrant",
                        ],
                        resources=[
                            "arn:aws:kms:eu-west-1:"
                            + core.Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ":key/"
                            + aws_account["kms_ebs_key"],
                        ],
                    ),
                    # SSM Parameter store access
                    _iam.PolicyStatement(
                        actions=[
                            "ssm:Describe*",
                            "ssm:Get*",
                            "ssm:List*",
                        ],
                        resources=[
                            "arn:aws:kms:eu-west-1:"
                            + core.Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ":parameter/"
                            + self._app_name
                            + "/*"
                        ],
                    ),
                ],
            )
        )

        # Assets bucket policies
        if s3_assets_bucket_name:
            self._ec2_role.attach_inline_policy(
                _iam.Policy(
                    self,
                    "ec2_s3_assets_bucket_policies",
                    statements=[
                        _iam.PolicyStatement(
                            actions=["s3:*"],
                            resources=[
                                "arn:aws:s3:::" + s3_assets_bucket_name,
                                "arn:aws:s3:::" + s3_assets_bucket_name + "/*",
                            ],
                        ),
                    ],
                )
            )
        # Code bucket policies
        if s3_code_bucket_name:
            self._ec2_role.attach_inline_policy(
                _iam.Policy(
                    self,
                    "service_user_policies",
                    statements=[
                        _iam.PolicyStatement(
                            actions=["s3:*"],
                            resources=[
                                "arn:aws:s3:::" + s3_code_bucket_name,
                                "arn:aws:s3:::" + s3_code_bucket_name + "/*",
                            ],
                        ),
                    ],
                )
            )

        # ~~~~~~~~~~~~~~~~
        # EFS
        # ~~~~~~~~~~~~~~~~
        self._efs = None
        self._efs_security_group = None

        if create_efs:
            efs_removal_policy = core.RemovalPolicy.DESTROY
            if is_production:
                efs_removal_policy = core.RemovalPolicy.RETAIN
            # efs_key = _kms.Key.from_key_arn(self, "efs_key", aws_account["kms_ebs_key"])
            self._efs = _efs.FileSystem(self, main_component_name+"efs", vpc=self._vpc, encrypted=False, removal_policy=efs_removal_policy)
            # you will find an additional EFS instruction after ASG

            self._efs_security_group = self.efs.node.find_child("EfsSecurityGroup")

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Rubrik backup tag

            if to_be_backed_up:
                Tags.of(self._efs).add("RubrikBackup", "true")
            else:
                Tags.of(self._efs).add("RubrikBackup", "false")
        # ~~~~~~~~~~~~~~~~
        # User data
        # ~~~~~~~~~~~~~~~~

        # Look to the path of your current working directory
        dirname = os.path.dirname(__file__)
        file_path = os.path.join(dirname, "base_user_data.sh")

        # Read the base user data from file
        with open(file_path) as self.base_user_data_content:
            self.base_user_data = self.base_user_data_content.read()
        self.base_user_data_content.close()

        # Inject parameter within the user data script template.
        # To add an environemnt variable to the user data:
        # 1. Add a line to the self.base_user_data.sh
        # 2. Replace the placeholder with a proper value as done below
        self.base_user_data = self.base_user_data.replace(
            "_S3Bucket_", aws_account["s3_config_bucket"]
        )
        self.base_user_data = self.base_user_data.replace(
            "_DataVolumeId_", ebs.ref if create_ebs else ""
        )
        self.base_user_data = self.base_user_data.replace(
            "_SMTPServer_", aws_account["smtp_server_endpoint"]
        )
        self.base_user_data = self.base_user_data.replace(
            "_SMTPPort_", aws_account["smtp_server_port"]
        )
        self.base_user_data = self.base_user_data.replace(
            "_ApplicationName_", self._app_name
        )
        self.base_user_data = self.base_user_data.replace("_Environment_", environment)
        if s3_code_bucket_name:
            self.base_user_data = self.base_user_data.replace(
                "_S3CodeBucket_", s3_code_bucket_name
            )
        if s3_assets_bucket_name: 
            self.base_user_data = self.base_user_data.replace(
                "_S3AssetsBucket_", s3_assets_bucket_name
            )
        self.base_user_data = self.base_user_data.replace(
            "_IsAppPublic_", str(is_public)
        )
        self.base_user_data = self.base_user_data.replace("_AzInUse_", az_in_use)
        self.base_user_data = self.base_user_data.replace(
            "_UserDataS3Key_", user_data_s3_key
        )
        # This is a Cloud Formation parameter. Change this value to automatically trigger a rolling update
        toggle_to_trigger_rolling_update = core.CfnParameter(
            self, 
            "toggle_to_trigger_rolling_update_cfn_param", 
            type="String",
            description="Just alter with whatever value you want this parameter to trigger a rolling update",
            default="__default__")
        toggle_to_trigger_rolling_update.override_logical_id("ToggleToTriggerRollingUpdate"+main_component_name.capitalize())
        self.base_user_data = self.base_user_data.replace(
            "_ToggleToTriggerRollingUpdate_", toggle_to_trigger_rolling_update.value_as_string
        )
        self.base_user_data = self.base_user_data.replace(
            "_EC2_TRAFFIC_PORT_", ec2_traffic_port
        )
        if create_efs:
            self.base_user_data = self.base_user_data.replace(
                "_EFS_", self.efs.file_system_id
            )

        if has_additional_variables:
            self.set_user_data_additional_variables(additional_variables)

        user_data = _ec2.UserData.custom(self.base_user_data)

        az_in_use = aws_account["az"]
        # ~~~~~~~~~~~~~~~~
        # Auto Scaling Group
        # ~~~~~~~~~~~~~~~~
        if ec2_ami_id == "LATEST":
            ec2_ami_id = _ssm.StringParameter.value_for_string_parameter(
            self, "/common/linuxHardenedAmi/latest")

        instance_type = _ec2.InstanceType(ec2_instance_type)
        machine_image = _ec2.GenericLinuxImage({"eu-west-1": ec2_ami_id})
        vpc_subnets = _ec2.SubnetSelection(availability_zones=[az_in_use])

        # ~~~~~~~~~~~~~~~~
        # Block device mapping
        # ~~~~~~~~~~~~~~~~
        volume = _asg.BlockDeviceVolume()
        volume.ebs(
            ROOT_VOLUME_SIZE,
        )
        block_devices = _asg.BlockDevice(device_name="/dev/xvda", volume=volume)
        
        rolling_update_configuration = _asg.RollingUpdateConfiguration(
                max_batch_size=1,
                min_instances_in_service=2 if is_ha else 0,
                min_successful_instances_percent=100,
                pause_time=core.Duration.minutes(30),
                # ASG best practice https://aws.amazon.com/premiumsupport/knowledge-center/auto-scaling-group-rolling-updates/
                suspend_processes=[
                    _asg.ScalingProcess.HEALTH_CHECK,
                    _asg.ScalingProcess.REPLACE_UNHEALTHY,
                    _asg.ScalingProcess.AZ_REBALANCE,
                    _asg.ScalingProcess.ALARM_NOTIFICATION,
                    _asg.ScalingProcess.SCHEDULED_ACTIONS,
                ],
                wait_on_resource_signals=is_ha,
            )

        min_capacity = int(autoscaling_group_min_size) if autoscaling_group_min_size else 2 if is_ha else 1
        max_capacity = int(autoscaling_group_max_size) if autoscaling_group_max_size else 4 if is_ha else 1
        
        asg = _asg.AutoScalingGroup(
            self,
            self.asg_name(),
            instance_type=instance_type,
            machine_image=machine_image,
            vpc=self._vpc,
            vpc_subnets=vpc_subnets if create_ebs else None,
            cooldown=core.Duration.seconds(120),
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            allow_all_outbound=True,
            health_check=_asg.HealthCheck.elb(grace=core.Duration.minutes(10)),
            ignore_unmodified_size_properties=True,
            notifications_topic=asg_notifications_topic,
            user_data=user_data,
            instance_monitoring=_asg.Monitoring.DETAILED,
            role=self._ec2_role,
            resource_signal_timeout=core.Duration.minutes(30),
            # block_devices=[block_devices],
            update_type=_asg.UpdateType.ROLLING_UPDATE,
            rolling_update_configuration=rolling_update_configuration,
        )
        
        ags_config = asg.node.find_child("LaunchConfig")
        ags_config.add_property_override(
            property_path="BlockDeviceMappings",
            value=[
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {"VolumeSize": ROOT_VOLUME_SIZE, "Encrypted": True},
                }
            ],
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Rubrik backup tag

        ASG = asg.node.find_child("ASG")
        if to_be_backed_up:
            Tags.of(ASG).add("RubrikBackup", "true", apply_to_launched_instances=True)
        else:
            Tags.of(ASG).add("RubrikBackup", "false", apply_to_launched_instances=True)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Scheduler tags
        if is_not_production:
            ASG = asg.node.find_child("ASG")
            if tag_scheduler_uptime_skip:
                Tags.of(ASG).add("SchedulerSkip", tag_scheduler_uptime_skip, apply_to_launched_instances=True,)

            if tag_scheduler_uptime:
                Tags.of(ASG).add("SchedulerUptime", tag_scheduler_uptime, apply_to_launched_instances=True,)

            if tag_scheduler_uptime_days:
                Tags.of(ASG).add("SchedulerUptimeDays", tag_scheduler_uptime_days, apply_to_launched_instances=True,)   

        # Configure the CFT signal to user data. To overcome the issue that the
        # ASG Logical Id cannot is hard to retrieve, let override it (easier withe the current CDK version)
        # and pass the fixed ASG logical Id as param of the CFN signal
        asg.node.default_child.override_logical_id(AUTOSCALING_GROUP_LOGICAL_ID)
        asg.add_user_data(
            "/opt/aws/bin/cfn-signal -e $? --stack {} --resource {} --region eu-west-1".format(
                core.Stack.of(self).stack_name, AUTOSCALING_GROUP_LOGICAL_ID
            )
        )

        # Attach Target group
        if(is_network_load_balancer):
            asg.attach_to_network_target_group(self._tg)
        else:
            asg.attach_to_application_target_group(self._tg)

        # ~~~~~~~~~~~~~~~~
        # EFS: enble access from ASG
        # ~~~~~~~~~~~~~~~~
        if create_efs:
            # EFS is created above
            self._efs.connections.allow_default_port_from(asg)

        # Add EC2 security group
        self.ec2_security_group = _ec2.SecurityGroup(
            self,
            main_component_name + "_ec2_secg",
            vpc=self._vpc,
            security_group_name=app_name + "_" + main_component_name + "_ec2_secg",
            allow_all_outbound=True,
        )
        
        if(is_application_load_balancer):
            self.ec2_security_group.add_ingress_rule(
                peer=self.alb_security_group,
                connection=self.tcp_connection_ec2_traffic_port,
                description="From Load Balancer",
            )

        asg.add_security_group(self.ec2_security_group)

        # Enable access to already existing EFS
        if existing_efs_security_group or existing_efs_security_group_id:

            # In case `self.existing_efs_security_group` is provided use it, otherwise retrive the security group from AWS.
            # Important: `self.existing_efs_security_group_id` works only if the Security Group is already deployed. Not compabible with security groups created during the 
            # first deployment            
            existing_efs_security_group_resource = existing_efs_security_group if existing_efs_security_group else _ec2.SecurityGroup.from_security_group_id(
                self,
                "self.existing_efs_security_group",
                existing_efs_security_group,
                mutable=False,
            )

            existing_efs_security_group_resource.add_ingress_rule(
                peer=self.ec2_security_group,
                connection=_ec2.Port.tcp(2049),
                description="EFS access from EC2 " + app_name,
            )

            if to_be_backed_up:
                rubrik_cloud_cluster_secg_id = "sg-0f80734443f5059b2"
                production_aws_account_id = self._environments_parameters["accounts"]["production"]["id"]
                _ec2.CfnSecurityGroupIngress(
                    self,
                    "self.efs_access_from_rubrik_cloud_cluster",
                    ip_protocol = "tcp",
                    description="EFS access from Rubrik CDM Cloud Cluster",
                    group_id = existing_efs_security_group_resource.security_group_id,
                    source_security_group_id = rubrik_cloud_cluster_secg_id,
                    source_security_group_owner_id = production_aws_account_id,
                    from_port = 2049,
                    to_port = 2049
                )

        # Add mandatory FAO security groups
        # Bastion host access
        bastion_host_security_group = _ec2.SecurityGroup.from_security_group_id(
            self,
            main_component_name + "_bastion_host_security_group",
            aws_account["bastion_host_security_group"],
            mutable=False,
        )
        asg.add_security_group(bastion_host_security_group)

        # Scan engin access
        scan_target_security_group = _ec2.SecurityGroup.from_security_group_id(
            self,
            main_component_name + "_scan_target_security_group",
            aws_account["scan_target_security_group"],
            mutable=False,
        )
        asg.add_security_group(scan_target_security_group)

        # Security group to send email
        if sends_emails:
            smtp_access_security_group = _ec2.SecurityGroup.from_security_group_id(
                self,
                main_component_name + "_smtp_relay_security_group",
                aws_account["smtp_relay_security_group"],
                mutable=False,
            )
            asg.add_security_group(smtp_access_security_group)

        if use_ldap:
            ldap_access_security_group = _ec2.SecurityGroup.from_security_group_id(
                self,
                main_component_name + "_ldap_access_security_group",
                aws_account["ldap_access_security_group"],
                mutable=False,
            )
            asg.add_security_group(ldap_access_security_group)      

        # Scaling policies
        asg.scale_on_cpu_utilization(
            "asg_cpu_scaling",
            target_utilization_percent=80,
            cooldown=core.Duration.minutes(10),
        )

        # Lifecycle hooks
        asg_notifications_lifecycle_hook_role = _iam.Role.from_role_arn(
            self,
            "asg_notifications_lifecycle_hook_role",
            role_arn=aws_account["asg_cw_alerts_lc_hooks_role"],
            mutable=False,
        )
        notification_metadata = json.dumps(
            {"label": self._app_name + "-" + main_component_name}
        )

        asg_notifications_lifecycle_hook_launch_topic = _sns.Topic.from_topic_arn(
            self,
            "asg_notifications_lifecycle_hook_launch_topic",
            aws_account["asg_cw_alerts_lc_hooks_launch_sns"],
        )
        launch_notification_target = _asg_hooktargets.TopicHook(
            asg_notifications_lifecycle_hook_launch_topic
        )
        asg.add_lifecycle_hook(
            "asg_lifecycle_hooks_launch",
            lifecycle_transition=_asg.LifecycleTransition.INSTANCE_LAUNCHING,
            notification_target=launch_notification_target,
            default_result=_asg.DefaultResult.CONTINUE,
            heartbeat_timeout=core.Duration.seconds(60),
            notification_metadata=notification_metadata,
            role=asg_notifications_lifecycle_hook_role,
        )

        asg_notifications_lifecycle_hook_terminate_topic = _sns.Topic.from_topic_arn(
            self,
            "asg_notifications_lifecycle_hook_terminate_topic",
            aws_account["asg_cw_alerts_lc_hooks_terminate_sns"],
        )
        terminate_notification_target = _asg_hooktargets.TopicHook(
            asg_notifications_lifecycle_hook_terminate_topic
        )
        asg.add_lifecycle_hook(
            "asg_lifecycle_hooks_terminate",
            lifecycle_transition=_asg.LifecycleTransition.INSTANCE_TERMINATING,
            notification_target=terminate_notification_target,
            default_result=_asg.DefaultResult.CONTINUE,
            heartbeat_timeout=core.Duration.seconds(60),
            notification_metadata=notification_metadata,
            role=asg_notifications_lifecycle_hook_role,
        )

        # Downsteam
        if has_downstream:
            downstream_security_group = _ec2.SecurityGroup.from_security_group_id(
                self,
                "downstream_security_group",
                downstream_security_group,
                mutable=True,
            )
            tcp_connection_downstream_port = _ec2.Port.tcp(int(downstream_port))
            downstream_security_group.add_ingress_rule(
                peer=self.ec2_security_group,
                connection=tcp_connection_downstream_port,
                description="EC2 to downstream",
            )

        self._asg = asg

        self.base_user_data = self.auto_scaling_group.user_data.render()
        
        if(is_network_load_balancer):
            self.ec2_security_group.add_ingress_rule(
                peer=_ec2.Peer.ipv4(network_load_balancer_ip_1+"/32"),
                connection=_ec2.Port.tcp(int(ec2_traffic_port)),
                description="zone A NLB IP to R",
            )

            self.ec2_security_group.add_ingress_rule(
                peer=_ec2.Peer.ipv4(network_load_balancer_ip_2+"/32"),
                connection=_ec2.Port.tcp(int(ec2_traffic_port)),
                description="zone B NLB IP to B",
            )

            if(network_load_balancer_source_autoscaling_group is not None):
                role = _iam.Role(
                    self,
                    app_name + "_" + main_component_name + "_manage_connection_to_nlb_instance_role",
                    description=app_name + "_" + main_component_name + "_manage_connection_to_nlb_instance_role",
                    assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                    managed_policies=[
                        # AWS managed policy to allow sending logs and custom metrics to CloudWatch
                        _iam.ManagedPolicy.from_aws_managed_policy_name(
                            "service-role/AWSLambdaBasicExecutionRole"
                        )
                    ],
                    role_name=app_name + "_" + main_component_name + "_manage_connection_to_nlb_instance_role",
                )

                role.attach_inline_policy(
                    _iam.Policy(
                        self,
                        app_name + "_" + main_component_name + "_manage_nlb_instance_security_group_policy",
                        statements=[
                            # Policy for EBS
                            _iam.PolicyStatement(
                                actions=[
                                    "ec2:DescribeSecurityGroups",
                                    "ec2:DescribeInstances", 
                                    "ec2:AuthorizeSecurityGroupIngress",
                                    "ec2:RevokeSecurityGroupIngress"
                                ],
                                resources=["*"],
                                conditions={
                                    "ForAllValues:StringLike": {
                                        "aws:RequestTag/aws:cloudformation:ApplicationName": app_name
                                    }
                                }
                            )
                        ]
                    )
                )

                configuration_bucket = _s3.Bucket.from_bucket_name(
                    self, "configuration_bucket", aws_account["s3_config_bucket"]
                )

                lambda_function = _lambda.Function(self, app_name + "_" + main_component_name + "_manage_connection_to_nlb_instance_security_group_ingress",
                    runtime=_lambda.Runtime.NODEJS_12_X,
                    code=_lambda.Code.from_asset(
                        path=os.path.join(dirname, './manage_connection_to_nlb_instance_security_group_ingress')
                    ),
                    handler="lambda_function.handler",
                    memory_size=128,
                    timeout=core.Duration.seconds(120),
                    role=role,
                    environment= dict(
                        PORT= ec2_traffic_port,
                        SECURITY_GROUP= self.ec2_security_group.security_group_id
                    )
                )

                topic = _sns.Topic(self, 'autoscaling_notification')
                topic.add_subscription(_sns_subscriptions.LambdaSubscription(lambda_function))

                network_load_balancer_source_autoscaling_group.add_lifecycle_hook(
                    main_component_name + '_nlb-lifecycle-hook-launch',
                    lifecycle_transition = _asg.LifecycleTransition.INSTANCE_LAUNCHING,
                    notification_target = _asg_hooktargets.TopicHook(topic),
                    default_result=_asg.DefaultResult.CONTINUE,
                    heartbeat_timeout=core.Duration.seconds(60),
                    notification_metadata=json.dumps({"label": self._app_name + "-" + main_component_name}),
                )

                network_load_balancer_source_autoscaling_group.add_lifecycle_hook(
                    main_component_name + '_nlb-lifecycle-hook-terminate',
                    lifecycle_transition = _asg.LifecycleTransition.INSTANCE_TERMINATING,
                    notification_target = _asg_hooktargets.TopicHook(topic),
                    default_result=_asg.DefaultResult.CONTINUE,
                    heartbeat_timeout=core.Duration.seconds(60),
                    notification_metadata=json.dumps({"label": self._app_name + "-" + main_component_name}),
                )