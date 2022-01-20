from elasticsearch_dsl import InnerDoc, field

__all__ = [
    'EnterpriseIndustryInnerDoc',
    'EnterpriseInfoDoc',
]


class EnterpriseIndustryInnerDoc(InnerDoc):
    """企业行业信息"""

    industry_category = field.Keyword()  # 行业门类名称
    industry_category_code = field.Keyword()  # 行业门类代码
    industry_first_class = field.Keyword()  # 行业大类名称
    industry_first_class_code = field.Keyword()  # 行业大类代码
    industry_second_class = field.Keyword()  # 行业中类名称
    industry_second_class_code = field.Keyword()  # 行业中类代码
    industry_third_class = field.Keyword()  # 行业小类名称
    industry_third_class_code = field.Keyword()  # 行业小类代码


class EnterpriseInfoDoc(InnerDoc):
    """企业库信息

    行业分类标准[国标]: http://www.stats.gov.cn/tjsj/tjbz/hyflbz/201905/P020190716349644060705.pdf
    Github 2017国家行业标准数据: https://github.com/ramwin/china-public-data/blob/master/%E5%9B%BD%E6%B0%91%E7%BB%8F%E6%B5%8E%E8%A1%8C%E4%B8%9A%E5%88%86%E7%B1%BB/%E5%9B%BD%E6%B0%91%E7%BB%8F%E6%B5%8E%E8%A1%8C%E4%B8%9A%E5%88%86%E7%B1%BB_2017.json
    国标分类：门类，大类，中类，小类 共4类
    和工业互联网标准保持一致
    """

    # ************ 企业共享基础信息 ************
    name = field.Keyword()  # 公司名称
    enterprise_type = field.Keyword()  # 企业类型，包括重点企业，建议设为枚举类型，key表示重点企业
    industry_info = field.Object(EnterpriseIndustryInnerDoc)  # 企业行业信息
    province = field.Keyword()  # 所在省份
    city = field.Keyword()  # 所在市
    district = field.Keyword()  # 所在区县
    park = field.Keyword()  # 所在园区
    address = field.Text(fields={'keyword': field.Keyword()})  # 详细地址
    public_network = field.IpRange()  # 公网网段，公网IP地址段类型，如：1.1.1.1/32
    domain = field.Keyword()  # 域名
    website = field.Keyword()  # 网址
