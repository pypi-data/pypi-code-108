"""
responses(回应)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

# pip install pydantic[ujson, email]
from pydantic import ValidationError
from pydantic import BaseModel, Field, validator, Extra

from .enums import (
    AreaEnum,
    TypeEnum,
    StatusEnum,
    FinishStatusEnum,
    EnableStatusEnum,

    ContractsAttrEnum,
    ContractsStatusEnum,
    ContractsTypeEnum,
    ContractsWorkflowStatusEnum,

    SettlementATypeEnum,
    TmeSettlementATypeEnum,
    SettlementStatusEnum,
    SettlementCheckStatusEnum,
    MatchListStatusEnum,
    MatchListBStatusEnum,
    BStatusEnum,
    AuthorizationFormEnum,
    MQStatusEnum,
    MatchCheckStatusEnum,

    AccountTypeEnum,

    AuthRelationEnum,
    AuthorizedModeEnum,

    DeriveVersionEnum,
)

from .model import AlbumModel, SongModel


class PageData(BaseModel):
    """
    翻页数据
    """
    total: int = Field(None, title="总数")
    page: int = Field(None, title="当前第几页")


class IdName(BaseModel):
    """
    ID和名称
    """
    id: int = Field(None, title="ID")
    name: str = Field(None, title="名称", max_length=250)


##########################################################################################################

class IndexInfoResponses(BaseModel):
    """
    首页信息
    """
    document: str = Field(None, title="我的单据")
    upcoming: str = Field(None, title="我的待办")
    operation: str = Field(None, title="我的经办")
    contract_warn: str = Field(None, title="合同到期提醒")
    contract_perfect: str = Field(None, title="临时合同待完善")
    works_perfect: str = Field(None, title="作品信息待完善")
    works_auth_pur: int = Field(None, title="（采购）超授权上线作品数")
    works_auth_sale: int = Field(None, title="（销售）超授权上线作品数")
    crash_contact: str = Field(None, title="紧急联系")
    guidelines: str = Field(None, title="操作指引")

    class Config:
        extra = Extra.forbid  # 禁止额外属性(主要是为了检查是否有我们漏下的数据)


##########################################################################################################
class Company(BaseModel):
    """
    公司
    """
    id: int = Field(None, title="公司ID")
    name: str = Field(None, title="公司名称", max_length=250)


class CompanyResponses(BaseModel):
    """
    公司数据列表
    """
    list: List[Company] = Field(None, title="公司数据列表")


##########################################################################################################


class IcSigns(IdName):
    """
    签约主体
    """
    abbr_name: str = Field(None, title="简称", max_length=250)


class Authorize(BaseModel):
    """
    授权信息
    """
    id: int = Field(None, title="ID")
    name: str = Field(None, title="名称", max_length=250)
    type: str = Field(None, title="类型", max_length=250)
    parnt_id: int = Field(None, title="父ID")


class SigningAuthorizeResponses(BaseModel):
    """
    签约授权信息
    """
    icSigns: List[IcSigns] = Field(None, title="签约主体")
    supplier: List[IdName] = Field(None, title="采购签约主体")  # 他们签约主体（合同类型为采购）
    customer: List[IdName] = Field(None, title="销售签约主体")  # 他们签约主体（合同类型为销售）
    authorize: List[Authorize] = Field(None, title="授权信息")
    language: List[IdName] = Field(None, title="语种")


##########################################################################################################
class Artist(BaseModel):
    """
    歌手
    """
    singer_id: int = Field(None, title="艺人ID")
    singer_name: str = Field(None, title="艺人名称", max_length=250)
    trans_name: str = Field(None, title="艺人翻译名", max_length=250)
    area: AreaEnum = Field(None, title="艺人活跃地区")
    type: TypeEnum = Field(None, title="艺人类型")
    photo_url: str = Field(None, title="艺人图片", max_length=1024)
    album_list: List = Field([], title="艺人专辑")


class ArtistListResponses(PageData):
    """
    歌手列表数据
    """
    list: List[Artist] = Field([], title="列表数据")


##########################################################################################################


class Album(BaseModel):
    """
    专辑
    """
    id: int = Field(None, title="专辑ID")
    album_name: str = Field('', title="专辑名称", max_length=250)
    artist_name: str = Field(None, title="艺人", max_length=250)
    online_time: str = Field(None, title="上线时间", max_length=50)
    album_cover: str = Field(None, title="封面图", max_length=1024)
    status: StatusEnum = Field(0, title="状态")
    finish_status: FinishStatusEnum = Field(None, title="完善状态")
    copyright_company: str = Field(None, title="所属公司", max_length=250)


class AlbumResponses(PageData):
    """
    专辑列表数据
    """
    list: List[Album] = Field(None, title="列表数据")


##########################################################################################################
class AlbumDetailsResponses(AlbumModel):
    """
    专辑详情
    """
    ...


##########################################################################################################
class UserSubject(BaseModel):
    """
    专辑
    """
    id: str = Field(None, title="ID")
    name: str = Field('', title="签约主体名称")
    abbr_name: str = Field(None, title="简称")
    ic_id: str = Field(None, title="所属公司")
    status: EnableStatusEnum = Field(None, title="状态")
    user_id: str = Field(None, title="用户ID")
    user_name: str = Field(None, title="用户名称")
    set_uid: str = Field(None, title="修改用户ID")
    set_name: str = Field(None, title="修改用户名称")
    create_time: str = Field(None, title="创建时间")
    update_time: str = Field(None, title="更新时间")


class UserSubjectResponses(PageData):
    """
    歌手列表数据
    """
    list: List[UserSubject] = Field([], title="列表数据")


##########################################################################################################
class FileInfo(BaseModel):
    """
    专辑
    """
    width: str = Field(None, title="宽度")
    height: str = Field(None, title="长度")
    audio_check: str = Field(None, title="音频检查")
    duration: str = Field(None, title="持续时间")
    fileSize: str = Field(None, title="文件大小")
    origin_file_name: str = Field(None, title="原始文件名")


class AudioDetectionResponses(BaseModel):
    """
    音频检测
    """
    url: str = Field(None, title="链接")
    file_id: str = Field(None, title="文件ID")
    md5: str = Field(None, title="MD5")
    msg: str = Field(None, title="提示信息")
    file_info: FileInfo = Field(None, title="文件信息")


##########################################################################################################
class QuerySong(BaseModel):
    """
    作品查询
    """
    id: str = Field(None, title="ID")
    cms_id: str = Field(None, title="作品主键id", max_length=250)
    tme_id: str = Field(None, title="tme_id作品id", max_length=250)
    name: str = Field(None, title="作品名称", max_length=250)
    album_id: str = Field(None, title="专辑id", max_length=250)  # 可以用于查询歌曲专辑详情
    album_name: str = Field(None, title="专辑名称", max_length=250)
    artist_name: str = Field(None, title="表演者", max_length=250)
    wording: str = Field(None, title="词作者", max_length=250)
    composing: str = Field(None, title="曲作者", max_length=250)
    language_name: str = Field(None, title="语种", max_length=250)
    version: str = Field(None, title="版本")
    # 衍生版本（1：非；2：是；）
    derive_version: DeriveVersionEnum = Field(None, title="衍生版本")
    album_genre: str = Field(None, title="专辑流派", max_length=250)
    create_time: str = Field(None, title="录入时间", max_length=250)
    mainer: str = Field(None, title="作品业务负责人", max_length=250)
    cd_index: str = Field(None, title="CD索引")
    publish_time: str = Field(None, title="发行时间")
    online_time: str = Field(None, title="上线时间")
    pay_mode: str = Field(None, title="付费模式")
    cql_id: str = Field(None, title="cql_id")
    maker: str = Field(None, title="制作人")
    user_name: str = Field(None, title="用户名称")
    company: str = Field(None, title="所属公司")
    now_buy_contract_no: str = Field(None, title="now_buy_contract_no")
    signsubject: str = Field(None, title="签约主体")
    auth_relation: AuthRelationEnum = Field(None, title="授权关系")
    buy_contract_no: str = Field(None, title="采购合同编号", max_length=250)
    buy_authorized_start_date: str = Field(None, title="采购授权时间_开始", max_length=250)
    buy_authorized_end_date: str = Field(None, title="采购授权时间_结束", max_length=250)
    sell_contract_no: str = Field(None, title="销售合同编号", max_length=250)
    sell_authorized_start_date: str = Field(None, title="销售授权时间_开始", max_length=250)
    sell_authorized_end_date: str = Field(None, title="销售授权时间_结束", max_length=250)
    # authorized_mode: AuthorizedModeEnum = Field(None, title="授权形式")  # 1：代表独家；2：代表非独家
    authorized_mode: str = Field(None, title="授权形式", max_length=250)  # 授权形式(1：代表独家；2：代表非独家)
    authorized_mode_desc: str = Field(None, title="授权形式说明", max_length=250)
    word_share: str = Field(None, title="词权利比例", max_length=250)
    music_share: str = Field(None, title="曲权利比例", max_length=250)
    record_share: str = Field(None, title="录音权利比例", max_length=250)


class QuerySongResponses(PageData):
    """
    作品查询数据
    """
    list: List[QuerySong] = Field(None, title="列表数据")
    page: int = Field(None, title="当前第几页")
    total: int = Field(None, title="总数")


##########################################################################################################
class QueryContracts(BaseModel):
    """
    合同查询
    """
    inter_no: str = Field(None, title="内部合同编号", max_length=250)
    attr: ContractsAttrEnum = Field(None, title="合同属性")
    type: ContractsTypeEnum = Field(None, title="合同类型")
    status: ContractsStatusEnum = Field(None, title="合同状态")
    workflow_status: ContractsWorkflowStatusEnum = Field(None, title="审核状态")
    attr_desc: str = Field(None, title="合同属性value", max_length=250)
    type_desc: str = Field(None, title="合同类型value", max_length=250)
    status_desc: str = Field(None, title="合同状态value", max_length=250)
    workflow_status_desc: str = Field(None, title="审核状态value", max_length=250)
    works_count: int = Field(None, title="作品数量")
    works_real_count: int = Field(None, title="作品实际数量")
    my_signing_name: str = Field(None, title="我方签约主体", max_length=250)
    other_signing_name: str = Field(None, title="他方签约主体", max_length=250)
    guaranteed_balance: str = Field(None, title="保底金余额", max_length=250)
    uid: str = Field(None, title="合同创建人ID", max_length=250)
    user_name: str = Field(None, title="合同创建人姓名", max_length=250)
    principal: str = Field(None, title="责任人", max_length=250)
    effective_time: str = Field(None, title="合同生效时间", max_length=250)
    failure_time: str = Field(None, title="合同到期时间", max_length=250)
    authorized_start_date: str = Field(None, title="授权有效日期", max_length=250)
    authorized_end_date: str = Field(None, title="授权失效日期", max_length=250)
    expiration_time: str = Field(None, title="合同剩余到期时间", max_length=250)  # （单位：秒，负数代表已到期N秒）
    expiration_time_day: str = Field(None, title="合同剩余到期时间", max_length=250)  # （单位：天，负数代表已到期N天）
    company_name: str = Field(None, title="所属公司名称", max_length=250)
    create_time: str = Field(None, title="创建时间", max_length=250)
    # 没有在文档里面的内容
    asset_type: str = Field(None, title="资产类型", max_length=250)
    authorized_area: str = Field(None, title="授权区域", max_length=250)
    authorized_mode: str = Field(None, title="授权模式", max_length=250)
    authorized_note: str = Field(None, title="授权备注", max_length=2048)
    authorized_platform: str = Field(None, title="授权平台", max_length=250)
    authorized_products: str = Field(None, title="授权产品", max_length=250)
    cooperate_mode: str = Field(None, title="合作模式", max_length=250)
    exclude_tax_amount: str = Field(None, title="不含税金额", max_length=250)
    exter_no: str = Field(None, title="外部合同编号", max_length=250)
    guaranteed_amount: str = Field(None, title="保底金", max_length=250)
    ic_id: str = Field(None, title="所属公司", max_length=250)
    id: str = Field(None, title="合同ID", max_length=250)
    include_tax_amount: str = Field(None, title="含税金额", max_length=250)
    my_signing_id: str = Field(None, title="我方签约主体ID", max_length=250)
    note: str = Field(None, title="备注", max_length=250)
    # other_signing: str = Field(None, title="他方签约主体", max_length=250)  # 这个和 other_signing_name 是一样的
    other_signing_id: str = Field(None, title="他方签约主体ID", max_length=250)  # 他方签约主体ID，供应商或客户ID
    share_proportion: str = Field(None, title="分成比例", max_length=250)
    tax_rate: str = Field(None, title="税率", max_length=250)


class QueryContractsResponses(PageData):
    """
    合同查询数据
    """
    list: List[QueryContracts] = Field(None, title="列表数据")
    page: int = Field(None, title="当前第几页")
    total: int = Field(None, title="总数")


##########################################################################################################
class QueryCompanySettlement(BaseModel):
    """
    版权结算单查询
    """
    id: int = Field(None, title="结算单ID")
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    # 结算单类型（1：匹配结算单；2：补结算单）
    a_type: SettlementATypeEnum = Field(None, title="结算单类型")
    # 结算单状态（1：新建；2：审核中；3：审核完成；4：删除；5：审核驳回；）
    status: SettlementStatusEnum = Field(None, title="结算单状态")
    # 审核状态（1：待初审；2：业务审核；3：待复核；4：待财务审核；5：已驳回；6:已完成；）
    check_status: SettlementCheckStatusEnum = Field(None, title="审核状态")
    company: str = Field(None, title="所属公司", max_length=250)
    sup_name: str = Field(None, title="版权公司", max_length=250)
    name: str = Field(None, title="结算单名称", max_length=250)
    # 这个是一个字典类型数据
    condition: Dict = Field(None, title="生成条件")
    create_time: str = Field(None, title="创建时间", max_length=250)
    adminer: str = Field(None, title="操作人", max_length=250)
    # 这些文档里面没有
    inter_no: str = Field(None, title="内部合同编号", max_length=250)
    type: ContractsTypeEnum = Field('', title="合同类型")
    sn: str = Field(None, title="结算单编号", max_length=250)


class QueryCompanySettlementResponses(PageData):
    """
    版权结算单查询数据
    """
    list: List[QueryCompanySettlement] = Field(None, title="列表数据")
    page: int = Field(None, title="当前第几页")
    total: int = Field(None, title="总数")


##########################################################################################################
class QueryMatchList(BaseModel):
    """
    版权结算单查询
    """
    id: int = Field(None, title="结算单ID")
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    # 结算单类型（1：匹配结算单；2：补结算单）
    a_type: SettlementATypeEnum = Field(None, title="结算单类型")
    # 结算单状态（1：待确认；2：匹配中；3：匹配失败；4：匹配完成；5：确认无误；6：确认作废；）
    status: MatchListStatusEnum = Field(None, title="结算单状态")
    # 供应商绑定状态（1：未绑定；2：绑定中；3：绑定失败；4：绑定成功；）
    b_status: MatchListBStatusEnum = Field(None, title="供应商绑定状态")
    company: str = Field(None, title="所属公司", max_length=250)
    signer: str = Field(None, title="客户公司", max_length=250)
    # 授权形式（1：独家；2：非独）
    type: AuthorizationFormEnum = Field(None, title="授权形式")
    name: str = Field(None, title="结算单名称", max_length=250)
    create_time: str = Field(None, title="创建时间", max_length=250)
    # 文档没有的内容
    adminer: str = Field(None, title="操作人", max_length=250)
    sn: str = Field(None, title="结算单编号", max_length=250)
    inter_no: str = Field(None, title="内部合同编号", max_length=250)
    my_signing: str = Field(None, title="我方签约主体", max_length=250)
    other_signing: str = Field(None, title="他方签约主体", max_length=250)
    principal: str = Field(None, title="合同负责人", max_length=250)


class QueryMatchListResponses(PageData):
    """
    版权结算单查询数据
    """
    list: List[QueryMatchList] = Field(None, title="列表数据")
    page: int = Field(None, title="当前第几页")
    total: int = Field(None, title="总数")


##########################################################################################################
class QueryMatchMQList(BaseModel):
    """
    手工单任务查询
    """
    id: int = Field(None, title="任务ID")
    # 状态（1：进行中；2：已完成；3：处理失败）
    status: MQStatusEnum = Field(None, title="状态")
    create_time: str = Field(None, title="创建时间", max_length=250)
    code: str = Field('', title="作业标识", max_length=250)
    obj_sn: str = Field('', title="结算单编号", max_length=250)
    creater: str = Field(None, title="操作者", max_length=250)
    name: str = Field('', title="中文名", max_length=250)
    # 当 status 状态为 2 时，message 为结算单区间和编号 json，[‘sn’:[],’time’:[]]
    message: str = Field(None, title="消息", max_length=1024)
    # 文档没有的内容
    type: int = Field(None, title="类型")
    params: str = Field(None, title="参数", max_length=1024)


class QueryMatchMQListResponses(PageData):
    """
    手工单任务查询数据
    """
    list: List[QueryMatchMQList] = Field(None, title="列表数据")
    page: int = Field(None, title="当前第几页")
    total: int = Field(None, title="总数")


##########################################################################################################
class QueryMatchSearchList(BaseModel):
    """
    手工单选择条件查询
    """
    id: int = Field(None, title="列表ID")
    sing_id: int = Field(None, title="作品ID")
    sing_name: str = Field('', title="作品名称", max_length=250)
    album_name: str = Field('', title="专辑名", max_length=250)
    singer: str = Field('', title="表演者", max_length=250)
    wording: str = Field(None, title="词作者", max_length=250)
    composing: str = Field(None, title="曲作者", max_length=250)
    language: str = Field(None, title="语种", max_length=250)
    # 是否结算（1：未结算；2：已结算；3：结算中；）
    check_status: MatchCheckStatusEnum = Field(None, title="是否结算")
    inter_no: str = Field(None, title="采购合同编号", max_length=250)
    ac_sn: str = Field('', title="结算单编号", max_length=250)
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    plat_name: str = Field('', title="平台名称", max_length=250)


class QueryMatchSearchListResponses(PageData):
    """
    手工单选择条件查询数据
    """
    list: List[QueryMatchSearchList] = Field(None, title="列表数据")
    page: int = Field(None, title="当前第几页")
    total: int = Field(None, title="总数")


##########################################################################################################
class QueryTmeSettlement(BaseModel):
    """
    结算单查询列表
    """
    id: int = Field(None, title="结算单ID")
    inter_no: str = Field(None, title="TME合同号", max_length=250)
    # 授权形式（1：独家；2：非独）
    type: AuthorizationFormEnum = Field(None, title="类型")
    start_time: str = Field('', title="结算开始时间", max_length=250)
    end_time: str = Field('', title="结算结束时间", max_length=250)
    # 结算单类型（1：结算单；2：补结算单）
    a_type: TmeSettlementATypeEnum = Field(None, title="结算单类型")
    # 结算单状态（1：待确认；2：匹配中；3：匹配失败；4：匹配完成；5：确认无误；6：确认作废；）
    status: MatchListStatusEnum = Field(None, title="结算单状态")
    # 供应商绑定状态（1：未绑定；2：绑定中；3：绑定失败；4：绑定成功；）
    b_status: BStatusEnum = Field(None, title="供应商绑定状态")
    company: str = Field(None, title="所属公司", max_length=250)
    company_id: str = Field(None, title="所属公司ID", max_length=250)
    signer: str = Field(None, title="客户公司", max_length=250)
    other_signing: str = Field(None, title="他方签约主体", max_length=250)
    my_signing: str = Field(None, title="我方签约主体", max_length=250)
    sn: str = Field('', title="结算单编号", max_length=250)
    name: str = Field('', title="结算单名称", max_length=250)
    adminer: str = Field(None, title="经办人", max_length=250)
    principal: str = Field(None, title="合同负责人", max_length=250)
    create_time: str = Field(None, title="创建时间", max_length=250)


class QueryTmeSettlementResponses(PageData):
    """
    结算单查询列表数据
    """
    list: List[QueryTmeSettlement] = Field(None, title="列表数据")


##########################################################################################################
class AccountList(BaseModel):
    """
    手工单选择条件查询
    """
    id: int = Field(None, title="用户ID")
    name: str = Field('', title="中文名", max_length=250)
    # 1启用，2禁用
    status: EnableStatusEnum = Field(None, title="状态")
    avatar_url: str = Field('', title="头像地址", max_length=1024)
    employee_id: str = Field('', title="员工编号", max_length=250)
    created_time: str = Field('', title="创建时间", max_length=250)
    ic_name: str = Field(None, title="所属公司", max_length=250)
    # 账号类型: 1集团账号，2系统账号
    type: AccountTypeEnum = Field(None, title="账号类型")
    gid: str = Field(None, title="所属角色", max_length=250)
    role_name: str = Field(None, title="角色名称", max_length=250)
    department: str = Field('', title="部门", max_length=250)
    email: str = Field('', title="邮箱", max_length=250)


class AccountListResponses(PageData):
    """
    手工单选择条件查询数据
    """
    list: List[AccountList] = Field(None, title="列表数据")
