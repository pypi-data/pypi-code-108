# @Time    : 2022/1/25 20:51
# @Author  : kang.yang@qizhidao.com
# @File    : test_demo.py
import qrunner


class TestDemo(qrunner.TestCase):
    """
    测试用例demo类
    """
    def test_case_01(self):
        """
        测试从首页进入我的页
        @return:
        """
        self.set_title('安卓过程式用例')
        self.el(resourceId='id/bottom_btn')\
            .click()
        self.el(resourceId='id/bottom_view', index=3)\
            .click()
        assert self.el(text='我的订单')\
            .exists(timeout=3)
        self.screenshot('我的页')
