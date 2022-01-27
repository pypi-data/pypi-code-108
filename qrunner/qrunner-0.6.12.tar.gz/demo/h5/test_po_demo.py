# @Time    : 2022/1/27 15:22
# @Author  : kang.yang@qizhidao.com
# @File    : test_po_demo.py
import qrunner
from qrunner.case import H5Driver


class NativePage(qrunner.Page):
    """
    原生po类demo
    """
    def __init__(self, driver):
        super().__init__(driver)
        # 元素定义
        self.close_ad_btn = self.el(resourceId='id/bottom_btn')
        self.ent_entry = self.el(text='查企业')

    def go_ent_search(self):
        self.close_ad_btn.click()
        self.ent_entry.click()


class H5Page(qrunner.H5Page):
    """
    H5po类demo
    """
    def __init__(self, driver):
        super().__init__(driver)
        # 元素定义
        self.search_entry = self.el(xpath="//div[@class='searchBox']")
        self.search_input = self.el(id_="serchInput")
        self.search_confirm = self.el(className="searchBtn")

    def search_by_key(self, keyword):
        self.search_entry.click()
        self.search_input.send_keys(keyword)
        self.search_confirm.click()

    def assert_result(self, expect):
        assert self.el(xpath=f"//div[@class='cardTitleBox']//div[contains(text(), {expect})]")\
            .exists(timeout=10)
        self.screenshot('搜索结果页')


class TestDemo(qrunner.TestCase):
    """
    测试用例demo
    """
    def test_case_01(self):
        """
        通过关键词查询企业详情信息
        @return:
        """
        keyword = '华为'
        expect = '华为技术有限公司'
        self.set_title('查询企业信息')

        native_page = NativePage(self.driver)
        native_page.go_ent_search()
        h5_page = H5Page(H5Driver())
        h5_page.search_by_key(keyword)
        h5_page.assert_result(expect)
