import boto3
import pendulum
import pandas as pd
from logging import getLogger
from botocore.exceptions import ProfileNotFound
from sumatra.config import CONFIG

logger = getLogger("sumatra.admin")

TENANT_PREFIX = "sumatra_"


class AdminClient:
    def __init__(self, aws_profile=None):
        aws_profile = aws_profile or CONFIG.aws_profile
        try:
            boto3.setup_default_session(profile_name=aws_profile)
        except ProfileNotFound:
            raise Exception(
                f"AWS ptofile '{aws_profile}' not found in aws credentials file"
            )
        self._cognito = boto3.client("cognito-idp")
        self._apigateway = boto3.client("apigateway")

    def _tenants_from_groups(self, resp):
        tenants = []
        for group in resp["Groups"]:
            name = group["GroupName"]
            if name.startswith(TENANT_PREFIX) and name != "sumatra_admin":
                tenants.append(name[len(TENANT_PREFIX) :])
        return tenants

    def list_tenants(self):
        resp = self._cognito.list_groups(UserPoolId=CONFIG.user_pool_id)
        return self._tenants_from_groups(resp)

    def list_users(self):
        resp = self._cognito.list_users(UserPoolId=CONFIG.user_pool_id)
        return [list(user.values())[0] for user in resp["Users"]]

    def current_tenant(self, username):
        resp = self._cognito.admin_list_groups_for_user(
            UserPoolId=CONFIG.user_pool_id, Username=username
        )
        tenants = self._tenants_from_groups(resp)
        if len(tenants) > 1:
            logger.warning(f"user '{username}' assigned to multiple tenants: {tenants}")
        if len(tenants) == 0:
            return None
        return tenants[0]

    def _remove_tenant(self, username, tenant=None):
        if tenant is None:
            tenant = self.current_tenant(username)
        self._cognito.admin_remove_user_from_group(
            UserPoolId=CONFIG.user_pool_id,
            GroupName=TENANT_PREFIX + tenant,
            Username=username,
        )

    def _add_tenant(self, username, tenant):
        self._cognito.admin_add_user_to_group(
            UserPoolId=CONFIG.user_pool_id,
            GroupName=TENANT_PREFIX + tenant,
            Username=username,
        )

    def assign_tenant(self, username, tenant):
        current = self.current_tenant(username)
        if current == tenant:
            logger.warning(f"user '{username}' already assigned to tenant '{tenant}'")
            return
        elif current:
            self._remove_tenant(username, current)
        self._add_tenant(username, tenant)

    def _get_keys_with_prefix(self, prefix):
        keys = {}
        resp = self._apigateway.get_api_keys()
        for item in resp.get("items", []):
            name = item["name"]
            if name.startswith(prefix):
                keys[name[len(prefix) :]] = item["id"]
        return keys

    def get_api_keys(self):
        return self._get_keys_with_prefix("api_")

    def get_sdk_keys(self):
        return self._get_keys_with_prefix("sdk_")

    def get_usage_plans(self):
        ids = {}
        resp = self._apigateway.get_usage_plans()
        for item in resp.get("items", []):
            name = item["name"]
            ids[name] = item["id"]
        return ids

    def _get_usage_by_plan(self, days):
        if not days:
            raise Exception("empty date range")
        data_by_plan = {}
        for name, usage_plan_id in self.get_usage_plans().items():
            resp = self._apigateway.get_usage(
                usagePlanId=usage_plan_id, startDate=days[0], endDate=days[-1]
            )
            data = {}
            for key, usage in resp.get("items", {}).items():
                if len(usage) != len(days):
                    raise Exception(
                        f"expected {len(days)} data points, found {len(usage)}"
                    )
                used = [row[0] for row in usage]
                data[key] = used
            data_by_plan[name] = data
        return data_by_plan

    def _usage_for_key(self, data_by_plan, key):
        for _, usage_data in data_by_plan.items():
            for plan_key, usage in usage_data.items():
                if plan_key == key:
                    return usage
        return 0

    def usage_report(self, start_date=None, end_date=None):
        end_date = end_date or pendulum.today()
        start_date = start_date or end_date.subtract(days=6)
        days = [d.to_date_string() for d in end_date - start_date]
        data_by_plan = self._get_usage_by_plan(days)
        api_keys = self.get_api_keys()
        sdk_keys = self.get_sdk_keys()
        df = pd.DataFrame(index=days)
        for tenant in self.list_tenants():
            for key_type, key in [("api", api_keys[tenant]), ("sdk", sdk_keys[tenant])]:
                df[tenant + "_" + key_type] = self._usage_for_key(data_by_plan, key)
        return df.transpose()
