# 2021-6-30：Write by lyc at，基础功能封装

# 从Python SDK导入SMS配置管理模块以及安全认证模块
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

# 导入SMS相关模块
import baidubce.services.sms.sms_client as sms
import baidubce.exception as ex


class SMS():
    '''百度云SMS短信服务 Python3 SDK封装'''
    def __init__(self, key):
        self.ak = key['Access_Key']
        self.sk = key['Secret_Access_Key']
        self.endpoint = key['SMS']['Endpoint']
        self.signature_id = key['SMS']['Signature_ID']
        self.template_id = key['SMS']['Template_ID']

        try:
            # 创建BceClientConfiguration
            self.config = BceClientConfiguration(credentials=BceCredentials(
                self.ak, self.sk),
                                                 endpoint=self.endpoint)
            # 新建SmsClient
            self.sms_client = sms.SmsClient(self.config)
        except Exception as err:
            raise Exception(err)  # 连接失败主动抛出异常

    def sendMessage(self, mobile, content):
        '''
        发送短信
        :param mobile: 手机号码
        :param content: dict类型，字典内变量value 类型必须 str，变量名称对应模板变量传入，比如{'code': '1236', 'time': '5'}
        :return: response 响应对象
        '''
        try:
            response = self.sms_client.send_message(self.signature_id,
                                                    self.template_id,
                                                    mobile=mobile,
                                                    content_var_dict=content)
            return response
        except ex.BceHttpClientError as e:
            if isinstance(e.last_error, ex.BceServerError):
                print(
                    'send request failed. Response %s, code: %s, request_id: %s'
                    % (e.last_error.status_code, e.last_error.code,
                       e.last_error.request_id))
            else:
                print('send request failed. Unknown exception: %s' % e)
