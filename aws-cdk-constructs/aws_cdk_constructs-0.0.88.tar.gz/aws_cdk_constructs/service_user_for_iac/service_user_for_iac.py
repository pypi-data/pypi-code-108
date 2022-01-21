from aws_cdk import core, aws_iam as _iam
from aws_cdk.core import Tags
from aws_cdk_constructs.utils import normalize_environment_parameter, get_version

class ServiceUserForIAC(core.Construct):
    """Construct to create the Service User to deploy a stack from a CD/CI pipeline

    Args:
        id (str): the logical id of the newly created resource
        
        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices 

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        s3_assets_bucket_name (str): The S3 Bucket in which the application assets are stored

        s3_code_bucket_name (str): The S3 Bucket in which the application code-base is stored

    """
    @property
    def service_user(self):
        """Returns the Service User object

        Returns:
            aws_cdk.aws_iam.User: The Service User object
        """
        return self._service_user

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        app_name,
        environment,
        environments_parameters,
        s3_code_bucket_name=None,
        s3_assets_bucket_name=None,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        environment = normalize_environment_parameter(environment)

        # Apply mandatory tags
        Tags.of(self).add("ApplicationName", app_name.lower().strip())
        Tags.of(self).add("Environment", environment)
        
        # Apply FAO CDK tags
        Tags.of(self).add("fao-cdk-construct", "service_user_for_iac")
        Tags.of(core.Stack.of(self)).add("fao-cdk-version", get_version())
        Tags.of(core.Stack.of(self)).add("fao-cdk", "true")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create conditions

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validate input params

        aws_account = environments_parameters["accounts"][environment.lower()]

        account_id = aws_account["id"]

        kms_ssm_key = aws_account["kms_ssm_key"]
        kms_rds_key = aws_account["kms_rds_key"]
        kms_ebs_key = aws_account["kms_ebs_key"]

        # S3 buckets 
        s3_buckets = [
            "arn:aws:s3:::" + app_name + "*", 
            "arn:aws:s3:::" + app_name.replace("-", "") + "*", 
            "arn:aws:s3:::" + app_name.replace("-", ".") + "*", 
            "arn:aws:s3:::awsserverlessrepo-changesets-*",
            "arn:aws:s3:::cdktoolkit*",
            "arn:aws:s3:::cdk-*",

            ]

        if s3_code_bucket_name is not None:
            s3_buckets.append("arn:aws:s3:::" + s3_code_bucket_name + "*")
            
        if s3_assets_bucket_name is not None:
            s3_buckets.append("arn:aws:s3:::" + s3_assets_bucket_name + "*")
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Retrieve info from already existing AWS resources
        # Important: you need an internet connection!

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create AWS resources

        # Manage policy for IAC deployment
        managed_policy_for_iac = _iam.ManagedPolicy(
            self,
            "managed_policy",
            description=app_name + " managed policy for IAC",
            statements=[
                # Resource ALL
                _iam.PolicyStatement(
                    actions=[
                        "cloudformation:Describe*",
                        "cloudformation:ValidateTemplate",
                        "cloudformation:CreateChangeSet",
                        "cloudformation:ExecuteChangeSe",
                        "ec2:CreateSecurityGroup",
                        "ec2:*SecurityGroup*",
                        "ec2:Describe*",
                        "ec2:*Tag*",
                        "serverlessrepo:SearchApplications",
                        "serverlessrepo:GetApplication",
                        "serverlessrepo:*CloudFormationTemplate",
                        "serverlessrepo:*CloudFormationChangeSet",
                        "serverlessrepo:List*",
                        "serverlessrepo:Get*",
                        "secretsmanager:GetRandomPassword",
                        "elasticloadbalancingv2:Describe*",
                        "elasticloadbalancing:Describe*",
                        "elasticloadbalancing:Delete*",
                        "elasticloadbalancingv2:*",
                        "elasticloadbalancing:*",
                        "elasticloadbalancing:ModifyLoadBalancerAttributes*",
                        "autoscaling:Describe*",
                        "iam:PutRolePolicy",
                        "iam:getRolePolicy",
                        "iam:GetUser",
                        "iam:DeleteRolePolicy",
                        "iam:DetachUserPolicy",
                        "iam:ListAccessKeys",
                        "iam:DeleteUser",
                        "iam:AttachUserPolicy",
                        "iam:PassRole",
                        "iam:DeleteAccessKey",
                        "rds:DescribeEngineDefaultParameters",
                        "rds:DescribeEvents",
                        "elasticfilesystem:*MountTarget*",
                        "elasticfilesystem:DescribeMountTargets",
                        "elasticfilesystem:DescribeFileSystems",
                        "ec2:*Volume*",
                        "elasticfilesystem:ListTagsForResource",
                        "elasticfilesystem:DescribeFileSystemPolicy",
                        "elasticfilesystem:TagResource",
                        "elasticfilesystem:UntagResource",
                        "autoscaling:DeletePolicy",
                        "cognito-idp:*UserPoolClient",
                        "cloudfront:TagResource"
                    ],
                    resources=["*"],
                ),
                # Filter by ARN pattern
                _iam.PolicyStatement(
                    actions=[
                        "cloudformation:*",
                    ],
                    resources=[
                        "arn:aws:cloudformation:*:*:stack/" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "s3:*",
                    ],
                    resources=s3_buckets,
                ),
                _iam.PolicyStatement(
                    actions=[
                        "ec2:*",
                    ],
                    resources=["arn:aws:ec2:eu-west-1:*:*/" + app_name + "*"],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "ec2:*",
                    ],
                    resources=["*"],
                    conditions={
                        "ForAnyValue:StringEquals": {
                            "ec2:ResourceTag/ApplicationName": app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        "elasticloadbalancingv2:*",
                        "elasticloadbalancing:*",
                    ],
                    resources=[
                        "arn:aws:elasticloadbalancing:eu-west-1:*:*/" + app_name + "*"
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "rds:*",
                    ],
                    resources=[
                        "arn:aws:rds:eu-west-1:*:*:" + app_name + "*",
                        "arn:aws:rds:eu-west-1:*:*:*default*",
                        ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "secretsmanager:*",
                    ],
                    resources=[
                        "arn:aws:secretsmanager:eu-west-1:*:*:" + app_name + "*"
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "lambda:*",
                    ],
                    resources=["arn:aws:lambda:*:*:*:" + app_name + "*"],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "autoscaling:*",
                    ],
                    resources=[
                        "arn:aws:autoscaling:eu-west-1:*:*:*:*" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "elasticfilesystem:*",
                    ],
                    resources=[
                        "arn:aws:elasticfilesystem:eu-west-1:*:*:*:*" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "iam:*",
                    ],
                    resources=[
                        "arn:aws:iam::*:user/" + app_name + "*",
                        # "arn:aws:iam::*:federated-user/" + app_name + "*",
                        "arn:aws:iam::*:role/" + app_name + "*",
                        "arn:aws:iam::*:group/" + app_name + "*",
                        "arn:aws:iam::*:instance-profile/" + app_name + "*",
                        # "arn:aws:iam::*:mfa/" + app_name + "*",
                        # "arn:aws:iam::*:server-certificate/" + app_name + "*",
                        "arn:aws:iam::*:policy/" + app_name + "*",
                        # "arn:aws:iam::*:sms-mfa/" + app_name + "*",
                        # "arn:aws:iam::*:saml-provider/" + app_name + "*",
                        # "arn:aws:iam::*:oidc-provider/" + app_name + "*",
                        # "arn:aws:iam::*:report/" + app_name + "*",
                        # "arn:aws:iam::*:access-report/" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "cloudfront:*",
                    ],
                    resources=[
                        "arn:aws:cloudfront:eu-west-1:*:*:*:*" + app_name + "*",
                        "arn:aws:cloudfront::*:distribution/*"
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "kendra:*",
                    ],
                    resources=[
                        "arn:aws:kendra:eu-west-1:*:*" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "cloudwatch:*",
                    ],
                    resources=[
                        "arn:aws:cloudwatch:*:*:dashboard/" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "cloudwatch:*",
                    ],
                    resources=[
                        "arn:aws:cloudwatch:*:alarm:" + app_name + "*",
                    ],
                ),
                # Filter by TAG
                _iam.PolicyStatement(
                    actions=[
                        "cloudformation:*",
                        "s3:*",
                        "ec2:*",
                        "elasticloadbalancingv2:*",
                        "elasticloadbalancing:*",
                        "rds:*",
                        "secretsmanager:*",
                        "autoscaling:*",
                        "lambda:*",
                        "logs:*",
                        "iam:*",
                        "elasticfilesystem:*",
                        "cloudfront:*",
                        "kendra:*",
                    ],
                    resources=["*"],
                    conditions={
                        "ForAnyValue:StringLike": {
                            "aws:RequestTag/ApplicationName": app_name,
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        "cloudformation:*",
                        "s3:*",
                        "ec2:*",
                        "elasticloadbalancingv2:*",
                        "elasticloadbalancing:*",
                        "rds:*",
                        "secretsmanager:*",
                        "autoscaling:*",
                        "lambda:*",
                        "logs:*",
                        "iam:*",
                        "elasticfilesystem:*",
                        "cloudfront:*",
                        "kendra:*",
                    ],
                    resources=["*"],
                    conditions={
                        "ForAnyValue:StringLike": {
                            "ec2:ResourceTag/ApplicationName": app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        "cloudwatch:*",
                    ],
                    resources=["*"],
                    conditions={
                            "ForAnyValue:StringLike": {
                                "ec2:ResourceTag/ApplicationName": app_name
                            }
                        },
                ),
                _iam.PolicyStatement(
                    actions=[
                        "kms:*",
                    ],
                    resources=["*"],
                    conditions={
                            "ForAnyValue:StringLike": {
                                "aws:ResourceTag/ApplicationName": app_name
                            }
                        },
                ),
                # Filter by SPECIFIC RESOURCE
                _iam.PolicyStatement(
                    actions=[
                        "kms:Decrypt",
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:Describe*",
                        "kms:CreateGrant",
                        "kms:DescribeKey",
                    ],
                    resources=[
                        "arn:aws:kms:eu-west-1:" + account_id + ":key/" + kms_ebs_key,
                        "arn:aws:kms:eu-west-1:" + account_id + ":key/" + kms_rds_key,
                        "arn:aws:kms:eu-west-1:" + account_id + ":key/" + kms_ssm_key,
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        "ssm:Describe*",
                        "ssm:Get*",
                        "ssm:List*",
                        "ssm:Put*",
                        "ssm:AddTags*",
                    ],
                    resources=[
                        "arn:aws:ssm:*:"
                        + "*"
                        + ":parameter/*"
                        + app_name
                        + "*",
                        "arn:aws:ssm:*:"
                        + account_id
                        + ":parameter/"
                        + "common/"
                        + "*"
                    ],
                ),
            ],
        )

        # Managed policy for Configuration deployement
        managed_policy_for_static_assets =  _iam.ManagedPolicy(
                self,
                "service_user_policies",
                statements=[
                    # S3 Configuration bucket permissions
                    _iam.PolicyStatement(
                        actions=["s3:*"],
                        resources=[
                            "arn:aws:s3:::"
                            + aws_account["s3_config_bucket"]
                            + "/"
                            + app_name
                            + "/"
                            + environment
                            + "/",
                            "arn:aws:s3:::"
                            + aws_account["s3_config_bucket"]
                            + "/"
                            + app_name
                            + "/"
                            + environment
                            + "/*",
                        ],
                    ),
                    _iam.PolicyStatement(
                        actions=["s3:ListBucket*"],
                        resources=["arn:aws:s3:::" + aws_account["s3_config_bucket"]],
                    ),
                ],
            )
    
        # Service user
        self._service_user = _iam.User(
            self,
            "service_user",
            managed_policies=[
                managed_policy_for_iac,
                managed_policy_for_static_assets,
                ],
            user_name="SRVUSR-" + app_name + "_" + environment + "_iac",
        )

        # S3 Code bucket permissions
        if s3_code_bucket_name:
            self._service_user.add_managed_policy(
                _iam.ManagedPolicy(
                    self,
                    "service_user_s3_code_bucket_policies",
                    statements=[
                        # S3 Assets bucket permissions
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

            # S3 Assets bucket permissions
        # S3 Assets bucket permissions
        if s3_assets_bucket_name:
            self._service_user.add_managed_policy(
                _iam.ManagedPolicy(
                    self,
                    "service_user_s3_assets_bucket_policies",
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

