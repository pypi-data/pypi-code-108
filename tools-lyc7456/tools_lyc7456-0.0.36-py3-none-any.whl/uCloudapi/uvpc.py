import json, requests
from tools_lyc7456.uCloudapi.signature import verify_ac

# Write by lyc at 2020-12-4
# Update by lyc at 2021-10-4：优化成包
# Update by lyc at 2021-11-9：增加方法 createBandwidthPackage()

class UVPC():
    '''优刻得UVPC封装'''
    def __init__(self, key):
        self.PublicKey = key['PublicKey']           # 公钥
        self.PrivateKey = key['PrivateKey']         # 私钥
        self.api_url = key['api_url']               # api接口url
        self.project_id = key['project_id']         # 项目id
        self.region = key['region']                 # 地域
        # uvpc
        self.vpc_id = key['VPC']['vpc_id']          # VPC id
        self.subnet_id = key['VPC']['subnet_id']    # 子网 id
        self.bandwidth = key['VPC']['bandwidth']    # EIP带宽值
        self.paymode = key['VPC']['paymode']        # EIP计费模式
        self.chargetype = key['VPC']['chargetype']  # EIP付费模式
        self.fw_id = key['VPC']['fw_id']            # 防火墙 id


    def allocateEip(self, operatorname='Bgp'):
        """[申请弹性IP - AllocateEIP]https://docs.ucloud.cn/api/unet-api/allocate_eip

        Args:
            operatorname (bool, optional): [弹性IP线路]. "International" 国际线路；"Bgp" 国内IP。默认为 "Bgp".

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'AllocateEIP',            # 接口名称
                'Region': self.region,              # 地区
                'OperatorName': operatorname,
                'Bandwidth': self.bandwidth,
                'PayMode': self.paymode,
                'ChargeType': self.chargetype,
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


    def releaseEip(self, eip_id):
        """[释放弹性IP - ReleaseEIP]https://docs.ucloud.cn/api/unet-api/release_eip

        Args:
            eip_id (string): [弹性ip资源id].

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'ReleaseEIP',         # 接口名称
                'Region': self.region,
                'EIPId': eip_id,
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


    def bindEip(self, eip_id, resource_id, resource_type='uhost'):
        """[绑定弹性IP - BindEIP]https://docs.ucloud.cn/api/unet-api/bind_eip

        Args:
            eip_id ([string]): [弹性ip资源id]
            resource_id ([string]): [弹性IP请求绑定的资源id]
            resource_type (str, optional): [弹性IP请求绑定的资源类型]. 枚举值为: uhost: 云主机; ulb, 负载均衡器; uni：虚拟网卡; 默认值 'uhost'.

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'BindEIP',                # 接口名称
                'Region': self.region,
                'EIPId': eip_id,
                'ResourceType': resource_type,
                'ResourceId': resource_id,
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



    def unbindEip(self, eip_id, resource_id, resource_type='uhost'):
        """[解绑弹性IP - UnBindEIP]https://docs.ucloud.cn/api/unet-api/un_bind_eip

        Args:
            eip_id ([string]): [弹性ip资源id]
            resource_id ([string]): [弹性IP请求绑定的资源id]
            resource_type (str, optional): [弹性IP请求绑定的资源类型]. 枚举值为: uhost: 云主机; ulb, 负载均衡器; uni：虚拟网卡; 默认值 'uhost'.

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'UnBindEIP',      # 接口名称
                'Region': self.region,
                'EIPId': eip_id,
                'ResourceId': resource_id,
                'ResourceType': resource_type,
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



    def describeEIP(self, eip_id='', eip_ip=''):
        """[获取弹性IP信息 - DescribeEIP]https://docs.ucloud.cn/api/unet-api/describe_eip
        
        以下参数有且只能二选一：
        Args:
            eip_id ([string]): [弹性ip资源id]
            eip_ip ([string]): [弹性ip公网IP地址]

        Returns:
            [str]: [response]
        """
        try:
            if len(eip_id) > 0:
                params = {
                    'Action': 'DescribeEIP',      # 接口名称
                    'Region': self.region,
                    'EIPIds.0': eip_id,
                    'ProjectId': self.project_id,
                    'PublicKey': self.PublicKey,
                }
            elif len(eip_ip) > 0:
                params = {
                    'Action': 'DescribeEIP',      # 接口名称
                    'Region': self.region,
                    'IPs.0': eip_ip,
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



    def createNetworkInterface(self):
        """[创建虚拟网卡]

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'CreateNetworkInterface',  # 接口名称
                'Region': self.region,
                'VPCId': self.vpc_id,
                'SubnetId': self.subnet_id,
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



    def deleteNetworkInterface(self, uni_id):
        """[删除虚拟网卡]

        Args:
            uni_id ([string]): [虚拟网卡id]

        Returns:
            [dict]: [response]
        """
        try:
            params = {
                'Action': 'DeleteNetworkInterface',  # 接口名称
                'Region': self.region,
                'InterfaceId': uni_id,
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


    def grantFirewall(self, uni_id, resource_type='uhost'):
        """[应用防火墙 - GrantFirewall]https://docs.ucloud.cn/api/unet-api/grant_firewall

        Args:
            uni_id ([string]): [虚拟网卡资源ID]
            resource_type (str, optional): [弹性IP请求绑定的资源类型]. 枚举值为: uhost: 云主机; ulb, 负载均衡器; uni：虚拟网卡; 默认值 'uhost'.

        Returns:
            [dict]: [response]
        """
        try:
            params = {
                'Action': 'GrantFirewall',  # 接口名称
                'Region': self.region,
                'FWId': self.fw_id,
                'ResourceType': resource_type,
                'ResourceId': uni_id,
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



    def attachNetworkInterface(self, uni_id, uhost_id):
        """[虚拟网卡绑定云主机]

        Args:
            uni_id ([string]): [虚拟网卡id]
            uhost_id ([string]): [云主机资源id]

        Returns:
            [dict]: [response]
        """
        try:
            params = {
                'Action': 'AttachNetworkInterface',  # 接口名称
                'Region': self.region,
                'InterfaceId': uni_id,
                'InstanceId': uhost_id,
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



    def describeNetworkInterface(self, uhost_id):
        '''获取网卡绑定信息'''
        try:
            params = {
                'Action': 'DescribeNetworkInterface',  # 接口名称
                'Region': self.region,
                'Limit': 1000,  # 1000个网卡内可以获取到，1000个以上需要重写递归循环
                'Offset': 0,
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



    def detachNetworkInterface(self, uni_id, uhost_id):
        """[虚拟网卡解绑云主机]

        Args:
            uni_id ([string]): [虚拟网卡id]
            uhost_id ([string]): [云主机资源id]

        Returns:
            [dict]: [response]
        """
        try:
            params = {
                'Action': 'DetachNetworkInterface',  # 接口名称
                'Region': self.region,
                'InterfaceId': uni_id,
                'InstanceId': uhost_id,
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



    def createBandwidthPackage(self, eip_id, bandwidth_package_value, bandwidth_package_timerange):
        """[创建带宽包 - CreateBandwidthPackage]https://docs.ucloud.cn/api/unet-api/describe_eip
        
        Args:
            eip_id ([string]): [所绑定弹性IP的资源ID]
            bandwidth_package_value ([int]): [带宽包大小(单位Mbps), 取值范围[2,800] (最大值受地域限制)]
            bandwidth_package_timerange([int]): 带宽包有效时长, 取值范围为大于0的整数, 即该带宽包在EnableTime到 EnableTime+TimeRange时间段内生效

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'CreateBandwidthPackage',
                'Region': self.region,
                'Bandwidth': bandwidth_package_value,
                'EIPId': eip_id,
                'TimeRange': bandwidth_package_timerange,
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



    def modifyUPathBandwidth(self, upath_id, upath_bandwidth):
        """[修改加速线路带宽 - ModifyUPathBandwidth]https://docs.ucloud.cn/api/pathx-api/modify_u_path_bandwidth
        
        以下参数有且只能二选一：
        Args:
            upath_id ([string]): [UPath 加速线路实例Id]
            upath_bandwidth([int]): 带宽,单位Mbps 区间[1,800]。

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'ModifyUPathBandwidth',
                'UPathId': upath_id,
                'Bandwidth': upath_bandwidth,
                'PublicKey': self.PublicKey,
                'ProjectId': self.project_id,
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



