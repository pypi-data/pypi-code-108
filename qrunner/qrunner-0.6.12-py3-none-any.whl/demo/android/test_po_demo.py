# @Time    : 2022/1/26 9:35
# @Author  : kang.yang@qizhidao.com
# @File    : test_po_demo.py
import qrunner


class DemoPage(qrunner.Page):
    """
    demo页面
    """
    def __init__(self, driver):
        super().__init__(driver)
        # 元素定义
        self.el_ad = self.el(resourceId='id/bottom_btn')
        self.el_my = self.el(resourceId='id/bottom_view', index=3)
        self.el_order = self.el(text='我的订单')

    def go_my(self):
        """
        从首页进入我的页
        @return:
        """
        self.el_ad.click()
        self.el_my.click()

    def assert_my(self):
        """
        断言文案'我的订单'存在，以确定进入我的页
        @return:
        """
        assert self.el_order.exists(timeout=3), f'我的订单未找到'
        self.screenshot('我的页')


class TestDemo(qrunner.TestCase):
    """
    demo用例
    """
    def test_case_01(self):
        """
        测试从首页进入我的页
        @return:
        """
        self.set_title('安卓po模式用例')
        page = DemoPage(self.driver)
        page.go_my()
        page.assert_my()
