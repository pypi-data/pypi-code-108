from aws_cdk import core, aws_iam as _iam
from aws_cdk.core import Tags
from aws_cdk_constructs.utils import normalize_environment_parameter, get_version

class ServiceUserForStaticAssets(core.Construct):
    """Construct to create the Service User to deploy the project static files from a CD/CI pipeline

    Args:
        id (str): the logical id of the newly created resource
        
        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices 

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        s3_bucket_name (str): The S3 Bucket in which the application code-base is stored

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
        s3_bucket_name=None,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        environment = normalize_environment_parameter(environment)

        # Apply mandatory tags
        Tags.of(self).add("ApplicationName", app_name.lower().strip())
        Tags.of(self).add("Environment", environment)

        # Apply FAO CDK tags
        Tags.of(self).add("fao-cdk-construct", "service_user_for_static_assets")
        Tags.of(core.Stack.of(self)).add("fao-cdk-version", get_version())
        Tags.of(core.Stack.of(self)).add("fao-cdk", "true")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create conditions

        aws_account = environments_parameters["accounts"][environment.lower()]
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validate input params

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Retrieve info from already existing AWS resources
        # Important: you need an internet connection!

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create AWS resources

        self._service_user = _iam.User(
            self,
            "service_user",
            managed_policies=None,
            user_name="SRVUSR-" + app_name + "_" + environment + "_static_assets",
        )

        self._service_user.add_managed_policy(
            _iam.ManagedPolicy(
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
                    _iam.PolicyStatement(
                        actions=[
                            "kms:GenerateDataKey",
                            "kms:Decrypt",
                        ],
                        resources=["*"],
                        conditions={
                                "ForAnyValue:StringLike": {
                                    "aws:ResourceTag/ApplicationName": app_name
                                }
                            },
                    ),
                ],
            )
        )

        if s3_bucket_name:
            self._service_user.add_managed_policy(
                _iam.ManagedPolicy(
                    self,
                    "service_user_s3_code_bucket_policies",
                    statements=[
                        # S3 Assets bucket permissions
                        _iam.PolicyStatement(
                            actions=["s3:*"],
                            resources=[
                                "arn:aws:s3:::" + s3_bucket_name,
                                "arn:aws:s3:::" + s3_bucket_name + "/*",
                            ],
                        ),
                    ],
                )
            )