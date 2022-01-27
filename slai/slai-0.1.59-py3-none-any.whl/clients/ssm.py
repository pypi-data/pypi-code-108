import boto3

from slai.exceptions import InvalidAWSProfile, InvalidServicePrefix
from botocore.exceptions import ProfileNotFound


class SSMClient:
    def __init__(self, *, aws_profile, aws_region):
        try:
            self.session = boto3.Session(
                profile_name=aws_profile, region_name=aws_region
            )
        except ProfileNotFound:
            raise InvalidAWSProfile("profile_not_found")

        self.sts_client = self.session.client("sts")
        self.ssm_client = self.session.client("ssm")

    def get_account_id(self):
        return self.sts_client.get_caller_identity()["Account"]

    def put_parameter(self, *, key, value):
        # TODO: add error handling
        response = self.ssm_client.put_parameter(
            Name=key,
            Value=value,
            Type="String",
            Overwrite=True,
        )
        return response

    def get_parameter(self, *, key):
        response = self.ssm_client.get_parameter(Name=key)
        value = response["Parameter"]["Value"]
        return value

    def list_parameters(self, *, prefix):
        parameters = []

        response = self.ssm_client.describe_parameters(MaxResults=10)
        next_token = response["NextToken"]

        while next_token:
            next_token = response.get("NextToken")
            if not next_token:
                break

            parameters.extend(response["Parameters"])
            response = self.ssm_client.describe_parameters(
                MaxResults=20, NextToken=next_token
            )

        parameter_names = []

        if prefix is None:
            raise InvalidServicePrefix("invalid_service_name")

        for param in parameters:
            if prefix in param["Name"]:
                parameter_names.append(param["Name"])

        return parameter_names
