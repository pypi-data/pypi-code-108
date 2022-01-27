# @Time    : 2022/1/27 8:59
# @Author  : kang.yang@qizhidao.com
# @File    : test_demo.py
import qrunner


class TestDemo(qrunner.TestCase):
    """
    测试demo类
    """
    def start(self):
        self.phone = '13652435335'
        self.password = 'wz123456'
        self.index_url = 'https://www.qizhidao.com'

    def test_case_01(self):
        """
        账号密码登录
        @return:
        """
        self.set_title('账号密码登录')
        self.open(self.index_url)
        self.el(xpath="//span[contains(text(), '登录/注册')]")\
            .click()
        self.el(xpath="//span[contains(text(), '帐号密码登录')]") \
            .click()
        self.el(xpath="//input[@placeholder='请输入手机号码']") \
            .send_keys(self.phone)
        self.el(xpath="//input[@placeholder='请输入密码']") \
            .send_keys(self.password)
        elem_list = self.el(xpath="//span[@class='el-checkbox__input']")\
            .get_elements()
        for elem in elem_list:
            elem.click()
        self.el(xpath="//span[contains(text(), '立即登录')]") \
            .click()
        expect = '136****5335'
        actual = self.el(xpath="//span[@class='txt-line']").get_text()
        assert actual == expect, f'实际结果: {actual} != 预期结果: {expect}'
        self.screenshot('登录成功页')
