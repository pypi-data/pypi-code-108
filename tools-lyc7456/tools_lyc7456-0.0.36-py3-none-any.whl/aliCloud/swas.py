import json
import sys

from typing import List

from alibabacloud_swas_open20200601.client import Client as SWAS_OPEN20200601Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_swas_open20200601 import models as swas__open20200601_models

# Write by lyc at 2021-11-24

class SWAS:
    def __init__(self, key) -> None:
        self.access_key_id = key['access_key_id']
        self.access_key_secret = key['access_key_secret']
        self.region_id = key['region_id']
        # SWAS
        self.image_id = key['SWAS']['image_id']
        self.plan_id = key['SWAS']['plan_id']
        self.instance_name = key['SWAS']['instance_name']
        self.password = key['SWAS']['password']


    @staticmethod
    def create_client(access_key_id: str, access_key_secret: str,) -> SWAS_OPEN20200601Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(access_key_id=access_key_id, access_key_secret=access_key_secret)
        config.endpoint = 'swas.cn-hongkong.aliyuncs.com'       # 访问的域名
        return SWAS_OPEN20200601Client(config)


    def listImages(self, image_type='system'):
        """[获取镜像列表]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/ListImages

        Args:
            image_type (str, optional): [镜像类型：system：系统镜像；app：应用镜像；custom：自定义镜像]. Defaults to 'system'.

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        list_images_request = swas__open20200601_models.ListImagesRequest(
            region_id=self.region_id,
            image_type=image_type
        )
        return json.dumps(client.list_images(list_images_request).body.to_map())


    def listPlans(self):
        """[获取套餐信息]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/ListPlans

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        list_plans_request = swas__open20200601_models.ListPlansRequest(
            region_id=self.region_id
        )
        return json.dumps(client.list_plans(list_plans_request).body.to_map())


    def createInstances(self, amount=1):
        """[创建实例]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/CreateInstances

        Args:
            amount (int, optional): [创建轻量应用服务器的数量。取值范围：1~20]. Defaults to 1.

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        create_instances_request = swas__open20200601_models.CreateInstancesRequest(
            region_id=self.region_id,
            image_id=self.image_id,
            plan_id=self.plan_id,
            period=1,
            # auto_renew=True,
            # auto_renew_period=1,
            amount=amount
        )
        return json.dumps(client.create_instances(create_instances_request).body.to_map())


    def updateInstanceAttribute(self, instance_id):
        """[修改实例部分信息]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/UpdateInstanceAttribute

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        update_instance_attribute_request = swas__open20200601_models.UpdateInstanceAttributeRequest(
            instance_id=instance_id,
            region_id=self.region_id,
            password=self.password,
            instance_name=self.instance_name
        )
        return json.dumps(client.update_instance_attribute(update_instance_attribute_request).body.to_map())


    def stopInstance(self, instance_id):
        """[停止实例]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/StopInstance

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        stop_instance_request = swas__open20200601_models.StopInstanceRequest(
            instance_id=instance_id,
            region_id=self.region_id
        )
        return json.dumps(client.stop_instance(stop_instance_request).body.to_map())


    def startInstance(self, instance_id):
        """[启动实例]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/StartInstance

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        start_instance_request = swas__open20200601_models.StartInstanceRequest(
            instance_id=instance_id,
            region_id=self.region_id
        )
        return json.dumps(client.start_instance(start_instance_request).body.to_map())


    def rebootInstance(self, instance_id):
        """[重启实例]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/RebootInstance

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        reboot_instance_request = swas__open20200601_models.RebootInstanceRequest(
            instance_id=instance_id,
            region_id=self.region_id
        )
        return json.dumps(client.reboot_instance(reboot_instance_request).body.to_map())


    def listInstances(self, instance_ids='', public_ip_addresses=''):
        """[获取实例列表]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/ListInstances

        Args: 两种查询方式二选一
            instance_ids ([list]): [轻量应用服务器的实例ID。取值可以由多个实例ID组成一个JSON数组]
            public_ip_addresses ([list]): [轻量应用服务器的公网IP。取值可以由多个公网ID组成一个JSON数组]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        if len(instance_ids) > 0:
            list_instances_request = swas__open20200601_models.ListInstancesRequest(
            region_id=self.region_id,
            instance_ids=instance_ids,
            page_size=100
            )
        elif len(public_ip_addresses) > 0:
            list_instances_request = swas__open20200601_models.ListInstancesRequest(
            region_id=self.region_id,
            public_ip_addresses=public_ip_addresses,
            page_size=100
            )
        else:
            list_instances_request = swas__open20200601_models.ListInstancesRequest(
            region_id=self.region_id,
            page_size=100
        )
        return json.dumps(client.list_instances(list_instances_request).body.to_map())


    def listFirewallRules(self, instance_id):
        """[获取实例的防火墙规则]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/ListFirewallRules

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        list_firewall_rules_request = swas__open20200601_models.ListFirewallRulesRequest(
            instance_id=instance_id,
            region_id=self.region_id
        )
        return json.dumps(client.list_firewall_rules(list_firewall_rules_request).body.to_map())


    def deleteFirewallRule(self, instance_id, rule_id):
        """[删除实例防火墙规则]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/DeleteFirewallRule

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]
            rule_id ([str]): [防火墙规则ID]

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        delete_firewall_rule_request = swas__open20200601_models.DeleteFirewallRuleRequest(
            instance_id=instance_id,
            region_id=self.region_id,
            rule_id=rule_id
        )
        return json.dumps(client.delete_firewall_rule(delete_firewall_rule_request).body.to_map())


    def createFirewallRule(self, instance_id, port, rule_protocol='TCP', remark=''):
        """[创建实例的防火墙规则]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/CreateFirewallRule

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]
            port ([str]): [端口或端口范围3306或1/65535]
            rule_protocol ([str]): [传输层协议。取值范围：(TCP|UDP|TcpAndUdp)]. Defaults to 'TCP'.
            remark (str, optional): [防火墙规则的备注]. Defaults to ''.

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        create_firewall_rule_request = swas__open20200601_models.CreateFirewallRuleRequest(
            instance_id=instance_id,
            region_id=self.region_id,
            rule_protocol=rule_protocol,
            port=port,
            remark=remark
        )
        return json.dumps(client.create_firewall_rule(create_firewall_rule_request).body.to_map())


    def renewInstance(self, instance_id, period=1):
        """[续费实例]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/RenewInstance

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]
            period ([int]): [续费时长。单位：月。取值范围：{"1", "3", "6","12", "24", "36"}]. Defaults to '1'.

        Returns:
            [json]: [json response]
        """
        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        renew_instance_request = swas__open20200601_models.RenewInstanceRequest(
            instance_id=instance_id,
            region_id=self.region_id,
            period=period
        )
        return json.dumps(client.renew_instance(renew_instance_request).body.to_map())


    def resetSystem(self, instance_id, image_id=''):
        """[重置系统]https://next.api.aliyun.com/document/SWAS-OPEN/2020-06-01/ResetSystem

        Args:
            instance_id ([str]): [指定的轻量应用服务器的实例ID]
            image_id ([str]): [目标镜像ID。如果不输入目标镜像ID，默认为重置当前镜像。]

        Returns:
            [json]: [json response]
        """

        client = SWAS.create_client(self.access_key_id, self.access_key_secret)
        if len(image_id) > 0:
            reset_system_request = swas__open20200601_models.ResetSystemRequest(
                instance_id=instance_id,
                region_id=self.region_id,
                image_id=image_id
            )
        else:
            reset_system_request = swas__open20200601_models.ResetSystemRequest(
            instance_id=instance_id,
            region_id=self.region_id
        )
        return json.dumps(client.reset_system(reset_system_request).body.to_map())

