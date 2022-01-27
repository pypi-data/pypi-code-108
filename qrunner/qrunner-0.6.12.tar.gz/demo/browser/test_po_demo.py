# @Time    : 2022/1/27 10:19
# @Author  : kang.yang@qizhidao.com
# @File    : test_po_demo.py
import qrunner


class DemoPage(qrunner.Page):
    """
    测试po类
    """
    def __init__(self, driver):
        super().__init__(driver)
        # 元素定义
        self.url = 'https://www.qizhidao.com'
        self.login_entry = self.el(xpath="//span[contains(text(), '登录/注册')]")
        self.pwd_login_tab = self.el(xpath="//span[contains(text(), '帐号密码登录')]")
        self.phone_input = self.el(xpath="//input[@placeholder='请输入手机号码']")
        self.pwd_input = self.el(xpath="//input[@placeholder='请输入密码']")
        self.check_box = self.el(xpath="//span[@class='el-checkbox__input']")
        self.login_btn = self.el(xpath="//span[contains(text(), '立即登录')]")
        self.username = self.el(xpath="//span[@class='txt-line']")
        # 访问页面
        self.open(self.url)

    def login_by_pwd(self, phone, password):
        self.login_entry.click()
        self.pwd_login_tab.click()
        self.phone_input.send_keys(phone)
        self.pwd_input.send_keys(password)
        for el in self.check_box.get_elements():
            el.click()
        self.login_btn.click()

    def assert_login_suc(self, expect):
        actual = self.username.get_text()
        assert actual == expect, f'实际结果: {actual} != 预期结果: {expect}'
        self.screenshot('登录成功页')


class TestDemo(qrunner.TestCase):
    """
    测试demo类
    """
    def start(self):
        self.phone = '13652435335'
        self.password = 'wz123456'
        self.expect = '136****5335'

    def test_case_01(self):
        """
        账号密码登录
        @return:
        """
        self.set_title('账号密码登录')
        page = DemoPage(self.driver)
        page.login_by_pwd(self.phone, self.password)
        page.assert_login_suc(self.expect)
