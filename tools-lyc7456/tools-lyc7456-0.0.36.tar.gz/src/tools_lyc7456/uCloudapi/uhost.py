import base64
import json
from operator import le
import requests
from tools_lyc7456.uCloudapi.signature import verify_ac

# Write by lyc at 2020-12-4
# Update by lyc at 2021-2-4：增加绑定云主机告警模板id
# Update by lyc at 2021-10-4：优化成包


class UHOST():
    '''优刻得uhost云主机 api封装'''
    def __init__(self, key):
        self.PublicKey = key['PublicKey']           # 公钥
        self.PrivateKey = key['PrivateKey']         # 私钥
        self.api_url = key['api_url']               # api接口url
        self.project_id = key['project_id']         # 项目id
        self.region = key['region']                 # 地域
        self.zone = key['zone']                     # 可用区
        # uhost
        self.name = key['UHOST']['name']                # 云主机名称
        self.image_id = key['UHOST']['image_id']        # 镜像id
        self.password = key['UHOST']['password']        # 密码
        self.cpu = key['UHOST']['cpu']                  # 虚拟CPU核数
        self.memory = key['UHOST']['memory']            # 虚拟内存大小
        self.disk0_size = key['UHOST']['disk0_size']    # 系统盘大小
        self.chargetype = key['UHOST']['chargetype']    # 计费模式
        self.tag = key['UHOST']['tag']                  # 业务组
        self.alarm_template_id = key['UHOST']['alarm_template_id']  # 告警模板id
        # uvpc
        self.bandwidth = key['VPC']['bandwidth']          # 带宽
        self.paymode = key['VPC']['paymode']              # 带宽付费类型
        self.fw_id = key['VPC']['fw_id']                  # 防火墙id



    def describeUHostInstance(self, uhost_id):
        """[获取主机信息 - DescribeUHostInstance]https://docs.ucloud.cn/api/uhost-api/describe_uhost_instance

        Args:
            uhost_id ([string]): [UHost实例ID]

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeUHostInstance',      # 接口名称
                'Region': self.region,
                'Zone': self.zone,
                'UHostIds.0': uhost_id,
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def createUHostInstance(self, disks_0_type='LOCAL_NORMAL', maxcount=1, operatorname='Bgp', features_uni=True):
        """[创建云主机 - CreateUHostInstance]https://docs.ucloud.cn/api/uhost-api/create_uhost_instance

        Args:
            disks_0_type (str, optional): [系统盘类型]. Defaults to 'LOCAL_NORMAL'. 磁盘类型参考：https://docs.ucloud.cn/api/uhost-api/disk_type
            maxcount (int, optional): [本次最大创建主机数量]. Defaults to 1.
            operatorname (str, optional): [弹性IP线路]. "International" 国际线路；"Bgp" 国内IP。默认为 "Bgp".
            features_uni (bool): [弹性IP线路]. 弹性网卡特性。开启了弹性网卡权限位，此特性才生效。默认 True 开启。

        Returns:
            [type]: [description]
        """
        try:
            self.password = (base64.b64encode(self.password.encode("utf-8"))).decode('utf-8')   # 云主机密码使用base64进行编码
            params = {
                'Action': 'CreateUHostInstance',      # 接口名称
                'Region': self.region,
                'Zone': self.zone,
                'ImageId': self.image_id,
                'Password': self.password,
                'Disks.0.Type': disks_0_type,
                'Disks.0.IsBoot': 'True',
                'Disks.0.Size': self.disk0_size,
                'LoginMode': 'Password',
                'Name': self.name,
                'Tag': self.tag,
                'ChargeType': self.chargetype,
                'CPU': self.cpu,
                'Memory': self.memory,
                'SecurityGroupId': self.fw_id,
                'MaxCount': maxcount,
                'NetworkInterface.0.EIP.Bandwidth': self.bandwidth,
                'NetworkInterface.0.EIP.PayMode': self.paymode,
                'NetworkInterface.0.EIP.OperatorName': operatorname,
                'AlarmTemplateId': self.alarm_template_id,
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'Features.UNI':  features_uni,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def stopUHostInstance(self, uhost_id):
        """[关闭主机 - StopUHostInstance]https://docs.ucloud.cn/api/uhost-api/stop_uhost_instance

        Args:
            uhost_id ([string]): [UHost实例ID]

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'StopUHostInstance',      # 接口名称
                'Region': self.region,
                'Zone': self.zone,
                'UHostId': uhost_id,
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def terminateUHostInstance(self, uhost_id):
        """[删除云主机 - TerminateUHostInstance]https://docs.ucloud.cn/api/uhost-api/terminate_uhost_instance

        Args:
            uhost_id ([string]): [UHost实例ID]

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'TerminateUHostInstance',      # 接口名称
                'Region': self.region,
                'UHostId': uhost_id,
                'ReleaseEIP': True,
                'ReleaseUDisk': True,
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err


