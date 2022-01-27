# @Time    : 2022/1/27 13:47
# @Author  : kang.yang@qizhidao.com
# @File    : test_demo.py
import qrunner
from qrunner.case import H5Driver, wel


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
        self.el(resourceId='id/bottom_btn')\
            .click()
        self.el(text='查企业').\
            click()
        driver = H5Driver()
        wel(driver, xpath="//div[@class='searchBox']")\
            .click()
        wel(driver, id_="serchInput").\
            send_keys(keyword)
        wel(driver, className="searchBtn").\
            click()
        assert wel(driver, xpath=f"//div[@class='cardTitleBox']//div[contains(text(), {expect})]")\
            .exists(timeout=5), f'未搜到: {expect}'
        self.screenshot('搜索结果页')
