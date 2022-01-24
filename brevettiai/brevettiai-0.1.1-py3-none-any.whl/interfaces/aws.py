import os
import re
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

from dataclasses import dataclass, field

from brevettiai.io.credentials import Credentials, LoginError


def parse_sts_assume_role_response(response, platform):
    try:
        content = re.sub(r"\s+", "", response)
        credentials = {k: re.search(f"<{f}>(.+)</{f}>", content).groups()[0] for k, f in
                       dict(secret_key="SecretAccessKey",
                            access_key="AccessKeyId",
                            session_token="SessionToken").items()}

        credentials["region"] = platform.bucket_region
        credentials["endpoint"] = platform.s3_endpoint
        return credentials
    except AttributeError as ex:
        raise AttributeError("Could not parse sts request: " + str(response))


@dataclass
class AWSConfigCredentials(Credentials):
    aws_config_path: str = field(default=os.environ.get("AWS_CREDENTIALS_FILE", os.path.join(str(Path.home()), ".aws")))
    endpoint: str = field(default=None)

    def get_credentials(self, resource_id, resource_type="dataset", mode="r"):
        try:
            return self.get_aws_credentials_from_config_file()
        except Exception as ex:
            raise LoginError(f"Error logging in via AWS Config file '{self.aws_config_path}'") from ex

    def get_aws_credentials_from_config_file(self):
        if self.aws_config_path is not None:
            if os.path.exists(os.path.join(self.aws_config_path, "credentials")):
                if os.path.isfile(os.path.join(self.aws_config_path, "credentials")):
                    profile = os.environ.get("AWS_PROFILE", "default")
                    parser = ConfigParser()
                    parser.read([os.path.join(self.aws_config_path, x) for x in ["config", "credentials"]])

                    expiration = parser.get(profile, 'aws_session_expiration', fallback=None)
                    if expiration is not None:
                        expiration = datetime.strptime(expiration, '%Y-%m-%dT%H:%M:%S%z')
                        assert expiration > datetime.now(expiration.tzinfo), "Amazon login '%s' expired" % profile

                    access_key = parser.get(profile, 'aws_access_key_id')
                    secret_key = parser.get(profile, 'aws_secret_access_key')
                    session_token = parser.get(profile, 'aws_session_token')
                    try:
                        region = parser.get(profile, 'region')
                    except Exception:
                        region = parser.get("profile " + profile, "region")
                    endpoint = self.endpoint or f"s3.{region}.amazonaws.com"
                    return dict(access_key=access_key, secret_key=secret_key,
                                session_token=session_token, region=region, endpoint=endpoint)
