import enum
import ipaddress
import typing

from pydantic import BaseModel, root_validator
from wisdoms_dapr import data

__all__ = ['EnterpriseTypeEnum', 'EnterpriseIndustryInfoSchema', 'EnterpriseInfoSchema']


class EnterpriseTypeEnum(str, enum.Enum):
    """企业类型枚举"""

    key = 'key'  # 重点企业类型


class EnterpriseIndustryInfoSchema(BaseModel):
    """Enterprise Industry Info"""

    industry_category: str  # 行业门类名称
    industry_category_code: str  # 行业门类代码
    industry_first_class: str  # 行业大类名称
    industry_first_class_code: str  # 行业大类代码
    industry_second_class: str  # 行业中类名称
    industry_second_class_code: str  # 行业中类代码
    industry_third_class: str  # 行业小类名称
    industry_third_class_code: str  # 行业小类代码

    @root_validator
    def load_data(cls, values):
        """验证数据"""

        category = values.get('industry_category')
        if not category:
            return values
        if category not in data.CHINA_INDUSTRY_INFO:
            raise ValueError(f"{category} is not in china industry info")
        category_info = data.CHINA_INDUSTRY_INFO[category]
        values['industry_category_code'] = category_info['code']

        first_class = values.get('industry_first_class')
        if not first_class:
            return values
        if first_class not in category_info['children']:
            raise ValueError(f"{first_class} is not in china industry category class info")
        first_class_info = category_info['children'][first_class]
        values['industry_first_class_code'] = first_class_info['code']

        second_class = values.get('industry_second_class')
        if not second_class:
            return values
        if second_class not in first_class_info['children']:
            raise ValueError(f"{second_class} is not in china industry first class info")
        second_class_info = first_class_info['children'][second_class]
        values['industry_second_class_code'] = second_class_info['code']

        third_class = values.get('industry_third_class')
        if not third_class:
            return values
        if third_class not in second_class_info['children']:
            raise ValueError(f"{third_class} is not in china industry second class info")
        third_class_info = second_class_info['children'][third_class]
        values['industry_third_class_code'] = third_class_info['code']


class EnterpriseInfoSchema(BaseModel):
    """基础企业信息"""

    id: str  # ID
    name: str  # 公司名称
    enterprise_type: typing.Optional[EnterpriseTypeEnum]  # 企业类型，包括重点企业，建议设为枚举类型，key表示重点企业
    industry_info: typing.Optional[EnterpriseIndustryInfoSchema]  # 行业信息
    province: typing.Optional[str]  # 所在省份
    city: typing.Optional[str]  # 所在市
    district: typing.Optional[str]  # 所在区县
    park: typing.Optional[str]  # 所在园区
    address: typing.Optional[str]  # 详细地址
    public_network: typing.Optional[ipaddress.IPv4Network]  # 公网网段，公网IP地址段类型，如：1.1.1.1/32
    domain: typing.Optional[str]  # 域名
    website: typing.Optional[str]  # 网址

    @root_validator
    def load_data(cls, values):
        """Validate data"""

        # validate administrative division
        province = values.get('province')
        if province:
            city = values.get('city')
            if city:
                if city not in data.CHINA_ADMINISTRATIVE_DIVISION[province]:
                    raise ValueError(f"{city} not in {province} province")
                else:
                    distinct = values.get('distinct')
                    if distinct and distinct not in data.CHINA_ADMINISTRATIVE_DIVISION[province][city]:
                        raise ValueError(f"{distinct} not in {province} province {city} city")
        else:
            if province not in data.CHINA_ADMINISTRATIVE_DIVISION:
                raise ValueError(f"invalid province {province}")

        return values
