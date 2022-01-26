"""
requests(请求)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

# pip install pydantic[ujson, email]
from pydantic import ValidationError
from pydantic import BaseModel, Field, validator

from .enums import (
    AreaEnum,
    TypeEnum,
    StatusEnum,
    FinishStatusEnum,
    AlbumTypeEnum,
    RegionEnum,
    ContractsAttrEnum,
    ContractsStatusEnum,
    ContractsTypeEnum,
    ContractsWorkflowStatusEnum,
    SettlementStatusEnum,
    TmeSettlementStatusEnum,
    MatchListBStatusEnum,
    SettlementCheckStatusEnum,
    MQStatusEnum,
    MatchCheckStatusEnum,
    CheckMatchTypeEnum,
    EnableStatusEnum,
)

from .model import AlbumModel, SongModel, CopyrightData, ShowerModel


def convert_to_list_string(v):
    """

    转换字典为列表包含字典数据的字符串，例如：[{name:123, filename:456},]
    """
    # print(f'{cls.__name__} list_data_to_str', type(v), v)
    if not v:
        return None
        # v = {}
    elif isinstance(v, dict):
        if not v.get('name'):
            return None
            # v = {}
        if 'url' in v:
            del v['url']

    return json.dumps([v], ensure_ascii=False)


def convert_to_character_array_list(v, delimiter=','):
    """
    转换为用指定字符串分割数据的列表，例如：["id,name", "id2,name2"]
    """
    # print(f'{cls.__name__} list_data_to_str', type(v), v)
    if not v:
        v = []
    r = []
    for _data in v:
        r.append(f"{_data['id']}{delimiter}{_data['name']}")
    return r


##########################################################################################################
class ArtistSearchRequests(BaseModel):
    """
    艺人查询
    """
    singer_name: str = Field(None, title="艺人名", max_length=250)
    area: AreaEnum = Field(None, title="艺人活跃地区")
    type: TypeEnum = Field(None, title="艺人类型")
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class CreateShowerRequests(ShowerModel):
    """
    艺人创建
    """
    ...


##########################################################################################################
class AlbumSearchRequests(BaseModel):
    """
    专辑查询
    """
    page_size: int = Field(20, title="每页数量")
    page: int = Field(1, title="当前页码")
    song_name: str = Field('', title="歌曲名称", max_length=250)
    album_name: str = Field('', title="专辑名称", max_length=250)
    song_type: AlbumTypeEnum = Field(None, title="专辑类型")
    song_genre: int = Field(None, title="专辑流派")
    artist_name: str = Field('', title="艺人名", max_length=250)
    region: RegionEnum = Field(None, title="地区")
    language: int = Field(None, title="语言")
    status: StatusEnum = Field(0, title="状态")
    finish_status: FinishStatusEnum = Field(None, title="完善状态")
    copyright_company_id: int = Field(None, title="所属公司ID")
    signsubject_id: int = Field(None, title="签约主体ID")
    user_id: int = Field(None, title="用户ID")
    start_time: str = Field('', title="开始时间", max_length=20)
    end_time: str = Field('', title="结束时间", max_length=20)


class SaveSong(SongModel):
    """
    歌曲模型
    """
    artist: List[str] = Field(None, title="所属艺人")  # [{id,name}]
    text_lyrics: str = Field(None, title="文本歌词")  # 需要先获取上传文件的返回数据
    music: str = Field(None, title="音频")
    copyright_list: CopyrightData = Field(CopyrightData().dict(), title="录音版权")

    @validator('text_lyrics', 'music', pre=True)
    def list_data_to_str(cls, v):
        """
        转换列表数据为后端需要的json字符串
        """
        return convert_to_list_string(v)

    @validator('artist', pre=True, whole=True)
    def artist_data(cls, v):
        """
        转换保存专家需要的歌手数据
        """
        return convert_to_character_array_list(v)


class SaveAlbumRequests(AlbumModel):
    """
    专辑模型
    """
    artist: List[str] = Field(None, title="所属艺人")  # [{id,name}]
    album_cover: str = Field(None, title="专辑封面")  # 需要先获取上传文件的返回数据
    song_list: List[SaveSong] = Field([], title="歌曲列表")
    auth_file: str = Field(None, title="授权文件")

    @validator('album_cover', pre=True, always=True)
    def album_cover_data_to_str(cls, v):
        """
        转换数据为后端需要的字符串
        """
        # print(f'{cls.__name__} album_cover_data_to_str', type(v), v)
        if not v:
            v = {}
        elif isinstance(v, dict):
            if not v.get('name'):
                v = {}
            if 'url' in v:
                del v['url']
        elif isinstance(v, str):
            return v

        return json.dumps([v], ensure_ascii=False)

    @validator('auth_file', pre=True)
    def auth_file_data_to_str(cls, v):
        """
        转换数据为后端需要的字符串
        """
        # print(f'{cls.__name__} list_data_to_str', type(v), v)
        if not v:
            v = []
        r = []
        for file_data in v:
            if 'url' in file_data:
                del file_data['url']
            r.append(file_data)

        return json.dumps(r, ensure_ascii=False)

    @validator('artist', pre=True, whole=True)
    def artist_data(cls, v):
        """
        转换保存专家需要的歌手数据
        """
        # print(f'{cls.__name__} list_data_to_str', type(v), v)
        return convert_to_character_array_list(v, delimiter=',')


##########################################################################################################
class UserSubjectRequests(BaseModel):
    """
    艺人查询
    """
    name: str = Field(None, title="签约主体名称")
    ic_id: int = Field(None, title="所属公司ID")
    page_size: int = Field(None, title="每页数量")
    page: int = Field(None, title="当前页码")


##########################################################################################################
class AccountListRequests(BaseModel):
    """
    账号搜索
    """
    name: str = Field('', title="中文名")
    ic_id: int = Field('', title="所属公司ID")
    status: EnableStatusEnum = Field(None, title="用户状态")
    employee_id: str = Field('', title="员工编号")
    is_p: bool = Field(None, title="是否上下级所属公司下所有用户")
    page_size: int = Field(10, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class Check(BaseModel):
    """
    检查内容
    """
    id: str = Field(None, title="作品ID")
    name: str = Field(None, title="作品名称")
    album_name: str = Field(None, title="专辑名称")
    text_lyrics: str = Field(None, title="文本歌词")
    artist: str = Field(None, title="艺人id")
    composing: str = Field(None, title="曲作者")
    wording: str = Field(None, title="词作者")
    original_company: str = Field(None, title="原始版权公司")
    version: str = Field(None, title="作品版本")


class CheckRepeatRequests(BaseModel):
    """
    作品检测
    """
    check: List[Check] = Field([], title="作品列表")


##########################################################################################################


##########################################################################################################
class QuerySongRequests(BaseModel):
    """
    作品查询
    """
    cms_ids: List[int] = Field(None, title="作品主键id数组")  # [{id,name}]
    cql_ids: List[int] = Field(None, title="作品中央曲库id数组")
    company_id: int = Field(None, title="所属公司id")
    signsubject_id: int = Field(None, title="签约主体id")
    name: str = Field('', title="作品名称", max_length=250)
    album_name: str = Field('', title="专辑名称", max_length=250)
    tme_id: str = Field('', title="作品id", max_length=250)
    artist_name: str = Field('', title="表演者", max_length=250)
    buy_contract_no: str = Field('', title="采购合同编号", max_length=250)
    composing: str = Field('', title="曲作者", max_length=250)
    wording: str = Field('', title="词作者", max_length=250)
    language: str = Field('', title="语种", max_length=250)
    album_genre: str = Field('', title="专辑流派", max_length=250)
    sell_contract_no: str = Field('', title="销售合同编号", max_length=250)
    start_time: str = Field('', title="录入时间_开始", max_length=250)
    end_time: str = Field('', title="录入时间_结束", max_length=250)
    mainer: str = Field('', title="作品业务负责人", max_length=250)
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class QueryContractsRequests(BaseModel):
    """
    合同查询
    """
    work_id: str = Field(None, title="作品主键id")  # 通过作品主键id，查询包含该作品的合同
    ic_id: str = Field(None, title="所属公司id")
    inter_no: str = Field(None, title="内部合同编号", max_length=250)
    # 1：代表框架合同\普通合同；2：代表子合同；3：代表补充合同；4：代表转内部合同
    attr: ContractsAttrEnum = Field(None, title="合同属性")
    start_time: str = Field('', title="合同期限开始时间", max_length=250)
    end_time: str = Field('', title="合同期限结束时间", max_length=250)
    start_create_time: str = Field('', title="合同创建开始时间", max_length=250)
    end_create_time: str = Field('', title="合同创建结束时间", max_length=250)
    start_expiration_day: str = Field('', title="合同剩余到期时间开始", max_length=250)  # （单位：天）
    end_expiration_day: str = Field('', title="合同剩余到期时间结束", max_length=250)  # （单位：天）
    # 1：草稿；2：已驳回；3：审核中；4：变更中；5：审核完成；6：已终止
    status: ContractsStatusEnum = Field(None, title="合同状态", )
    # 1：代表采购合同；2：代表销售合同
    type: ContractsTypeEnum = Field('', title="合同类型")
    principal: str = Field('', title="责任人", max_length=250)
    other_signing: str = Field('', title="他方签约主体", max_length=250)
    uid: str = Field('', title="合同创建人ID", max_length=250)
    user_name: str = Field('', title="合同创建人姓名", max_length=250)
    # 1：待初审；2：业务审核；3：待复核；4：待财务审核；5：已驳回；6:已完成；
    workflow_status: ContractsWorkflowStatusEnum = Field(None, title="审核状态")
    # 1：获取所有当下歌曲绑定的合同；
    all_type: int = Field(1, title="获取方式")

    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class QueryCompanySettlementRequests(BaseModel):
    """
    版权结算单查询
    """

    company_id: int = Field(None, title="所属公司ID")
    copyright_id: int = Field(None, title="版权公司ID")
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    create_start_time: str = Field('', title="创建开始时间", max_length=250)
    create_end_time: str = Field('', title="创建结束时间", max_length=250)
    # 结算单状态（1：新建；2：审核中；3：审核完成；4：删除；5：审核驳回；）
    status: SettlementStatusEnum = Field(None, title="结算单状态")
    sn: int = Field(None, title="结算单编号")
    # 审核状态（1：待初审；2：业务审核；3：待复核；4：待财务审核；5：已驳回；6:已完成；）
    check_status: SettlementCheckStatusEnum = Field(None, title="审核状态")
    condition: str = Field(None, title="生成条件")
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class QueryMatchListRequests(BaseModel):
    """
    手工单查询
    """
    company_id: int = Field(None, title="所属公司ID")
    customer_id: int = Field(None, title="客户方公司ID")
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    name: str = Field('', title="结算单名称", max_length=250)
    sn: str = Field('', title="结算单编号", max_length=250)
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")
    # 文档没有的内容
    abbr_name: str = Field(None, title="简称")


##########################################################################################################
class QueryMatchMQListRequests(BaseModel):
    """
    手工单任务查询
    """
    obj_id: int = Field(None, title="手工单ID")
    # 状态（1：进行中；2：已完成；3：处理失败）
    status: MQStatusEnum = Field(None, title="状态")
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class QueryMatchSearchListRequests(BaseModel):
    """
    手工单选择条件查询
    """
    account_id: List[int] = Field(None, title="结算单ID")  # 列表
    copyright_id: int = Field(None, title="版权公司ID")
    inter_no: str = Field('', title="合同编号", max_length=250)
    language: int = Field(None, title="语种")
    album_name: str = Field('', title="专辑名", max_length=250)
    sing_name: str = Field('', title="作品名称", max_length=250)
    sing_id: List[int] = Field(None, title="作品ID")  # 列表
    singer: str = Field('', title="表演者", max_length=250)
    wording: str = Field('', title="词作者", max_length=250)
    composing: str = Field('', title="曲作者", max_length=250)
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    ac_sn: str = Field('', title="结算单编号", max_length=250)
    # 是否结算（1：未结算；2：已结算；3：结算中；）
    check_status: MatchCheckStatusEnum = Field(None, title="是否结算")
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")


##########################################################################################################
class QueryCheckMatchRequests(BaseModel):
    """
    手工单生成版权结算单
    """
    account_id: List[int] = Field(None, title="结算单ID")  # 列表
    check_id: List[int] = Field(None, title="确认结算的歌曲ID")  # 列表
    nocheck_id: List[int] = Field(None, title="确认不结算的歌曲ID")  # 列表
    # 查询条件来自 QueryMatchSearchListRequests，但是多了两个字段 type conditionType
    condition: Dict = Field(None, title="查询条件")
    copyright_id: int = Field(None, title="版权公司ID")
    inter_no: str = Field('', title="合同编号", max_length=250)
    language: int = Field(None, title="语种")
    album_name: str = Field('', title="专辑名", max_length=250)
    sing_name: str = Field('', title="作品名称", max_length=250)
    sing_id: List[int] = Field(None, title="作品ID")  # 列表
    singer: str = Field('', title="表演者", max_length=250)
    wording: str = Field('', title="词作者", max_length=250)
    composing: str = Field('', title="曲作者", max_length=250)
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    ac_sn: str = Field('', title="结算单编号", max_length=250)
    # 是否结算（1：未结算；2：已结算；3：结算中；）
    check_status: MatchCheckStatusEnum = Field(None, title="是否结算")
    # 类型（1：按条件生成；2：按作品生成；3：导入Excel生成；）
    type: CheckMatchTypeEnum = Field('', title="类型")


##########################################################################################################
class QueryTmeSettlementRequests(BaseModel):
    """
    结算单查询列表
    """
    name: str = Field('', title="结算单名称", max_length=250)
    sn: int = Field(None, title="结算单编号")
    signer: str = Field('', title="我方签约主体", max_length=250)
    adminer: str = Field('', title="经办人", max_length=250)
    inter_no: str = Field('', title="内部合同编号", max_length=250)
    start_time: str = Field('', title="结算单开始时间", max_length=250)
    end_time: str = Field('', title="结算单结束时间", max_length=250)
    company_id: int = Field(None, title="所属公司ID")
    # 结算单状态（1：待确认；2：匹配中；3：匹配失败；4：匹配完成；5：确认无误；6：确认作废）
    status: TmeSettlementStatusEnum = Field(None, title="结算单状态")
    page_size: int = Field(999, title="每页数量")
    page: int = Field(1, title="当前页码")

    # 供应商绑定状态（1：未绑定；2：绑定中；3：绑定失败；4：绑定成功；）
    b_status: MatchListBStatusEnum = Field(None, title="供应商绑定状态")


##########################################################################################################
if __name__ == '__main__':
    from ilds.time import Timer

    with Timer() as timer:
        try:
            a = ArtistSearchRequests(singer_name='喝喝')
            print(ArtistSearchRequests().json())
            a.area = AreaEnum.内地
            print(ArtistSearchRequests().parse_raw(a.json()))
        except ValidationError as e:
            # 如果验证失败，pydantic 会抛出一个错误，列出错误的原因
            print(e.json())

        print(UserSubjectRequests().json(exclude_none=True))
