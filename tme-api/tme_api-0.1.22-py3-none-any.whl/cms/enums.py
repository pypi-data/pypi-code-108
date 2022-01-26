from enum import Enum, IntEnum  # 字符的时候用 (str, Enum)


class AreaEnum(IntEnum):
    """艺人活跃地区"""
    港台 = 0
    内地 = 1
    日韩 = 2
    欧美 = 3
    其他 = 4
    东南亚 = 5
    未知 = 6


class TypeEnum(IntEnum):
    """艺人类型"""
    男 = 0
    女 = 1
    组合 = 2
    虚拟 = 3
    其他 = 4
    未知5 = 5
    未知 = 6


class AccountTypeEnum(IntEnum):
    """账号类型"""
    集团账号 = 1
    系统账号 = 2


class StatusEnum(IntEnum):
    """状态"""
    隐藏 = 0
    待上架 = 1
    已下架 = 2
    审核中 = 3
    审核不通过 = 4
    已上架 = 5
    草稿 = 6
    删除 = 7
    未知55 = 55


class FinishStatusEnum(IntEnum):
    """完善状态"""
    待完善 = 1
    已完善 = 2


class IsNumberEnum(IntEnum):
    """是否数专"""
    是 = 1
    否 = 2


class IsEnum(IntEnum):
    """是否"""
    未知 = 0
    是 = 1
    否 = 2


class AuthFormEnum(IntEnum):
    """授权形式"""
    未知 = 0
    非总代理 = 1
    总代理 = 2


class AuthTransferEnum(IntEnum):
    """可否转授权"""
    未知 = 0
    可转 = 1
    不可转 = 2


class AuthRelationEnum(IntEnum):
    """授权关系"""
    未知 = 0
    自有 = 1
    代理 = 2


class AuthorizedModeEnum(IntEnum):
    """授权形式"""
    独家 = 1
    非独家 = 2


class EnableStatusEnum(IntEnum):
    """启用状态"""
    未知 = 0
    启用 = 1
    禁用 = 2


class AlbumTypeEnum(IntEnum):
    """专辑类型"""
    未知 = -1
    录音室专辑 = 0
    演唱会 = 1
    影视 = 2
    动漫 = 3
    游戏 = 4
    舞曲 = 5
    纯音乐 = 6
    相声评书 = 7
    戏曲 = 8
    有声书籍 = 9
    Single = 10
    EP = 11
    古典作品 = 12
    同人音乐 = 13
    广播剧 = 14
    人声音频 = 15
    有声资讯 = 16
    综艺娱乐 = 17
    儿童教育 = 18
    音乐节目 = 19
    脱口秀 = 20
    搞笑段子 = 21
    情感生活 = 22
    其他 = 23


class RegionEnum(IntEnum):
    """地区"""
    港台 = 17
    内地 = 18
    日韩 = 19
    欧美 = 20
    其他 = 21
    东南亚 = 22
    未知 = 23


class LanguageEnum(IntEnum):
    """语言"""
    国语 = 0
    粤语 = 1
    台语 = 2
    日语 = 3
    韩语 = 4
    英语 = 5
    法语 = 6
    其他 = 7
    拉丁 = 8
    纯音乐 = 9
    德语 = 10
    俄语 = 11
    印度语 = 12
    泰语 = 13
    印尼语 = 14
    菲律宾语 = 15
    西班牙语 = 16
    印第安语 = 17
    葡萄牙语 = 18
    意大利语 = 19
    瑞典语 = 20
    波兰语 = 21
    丹麦语 = 22
    芬兰语 = 23
    越南语 = 24
    藏语 = 25
    马来语 = 26
    阿拉伯语 = 27
    客家语 = 28
    潮汕语 = 29
    维语 = 30
    冰岛语 = 31
    挪威语 = 32
    希腊语 = 33
    荷兰语 = 34
    捷克语 = 35
    乌克兰语 = 36
    蒙语 = 37
    哈萨克语 = 38
    缅甸语 = 39
    格鲁吉亚语 = 40
    罗马尼亚语 = 41


class GenreEnum(str, Enum):
    """流派"""
    Pop = "Pop",
    Classical = "Classical",
    Jazz = "Jazz",
    Blues = "Blues",
    Children_s = "Children's",
    Country = "Country",
    Dance = "Dance",
    Easy = "Easy",
    Listening = "Listening",
    Electronic = "Electronic",
    Folk = "Folk",
    Holiday = "Holiday",
    Latin = "Latin",
    Metal = "Metal",
    New = "New",
    Age = "Age",
    R_B = "R&b",
    Soul = "Soul",
    Rap_hip = "Rap/hip",
    Hop = "Hop",
    Reggae = "Reggae",
    Rock = "Rock",
    Soundtrack = "Soundtrack",
    World = "World",
    Music = "Music",
    Punk = "Punk",
    Alternative = "Alternative",
    Experimental = "Experimental",
    Spoken_audio = "Spoken&audio",
    Religious = "Religious",


class ContractsAttrEnum(IntEnum):
    """合同属性"""
    框架合同_普通合同 = 1
    子合同 = 2
    补充合同 = 3
    转内部合同 = 4


class ContractsStatusEnum(IntEnum):
    """合同状态"""
    草稿 = 1
    已驳回 = 2
    审核中 = 3
    变更中 = 4
    审核完成 = 5
    已终止 = 6


class ContractsTypeEnum(IntEnum):
    """合同类型"""
    采购合同 = 1
    销售合同 = 2


class ContractsWorkflowStatusEnum(IntEnum):
    """合同审核状态"""
    待初审 = 1
    业务审核 = 2
    待复核 = 3
    待财务审核 = 4
    已驳回 = 5
    已完成 = 6


class SettlementStatusEnum(IntEnum):
    """结算单状态"""
    新建 = 1
    审核中 = 2
    审核完成 = 3
    删除 = 4
    审核驳回 = 5


class TmeSettlementStatusEnum(IntEnum):
    """结算单状态"""
    待确认 = 1
    匹配中 = 2
    匹配失败 = 3
    匹配完成 = 4
    确认无误 = 5
    确认作废 = 6


class SettlementCheckStatusEnum(IntEnum):
    """审核状态"""
    无 = 0
    待初审 = 1
    业务审核 = 2
    待复核 = 3
    待财务审核 = 4
    已驳回 = 5
    已完成 = 6


class SettlementATypeEnum(IntEnum):
    """结算单类型"""
    匹配结算单 = 1
    补结算单 = 2


class TmeSettlementATypeEnum(IntEnum):
    """结算单类型"""
    结算单 = 1
    补结算单 = 2


class MatchListStatusEnum(IntEnum):
    """手工单查询状态"""
    # 无 = 0
    待确认 = 1
    匹配中 = 2
    匹配失败 = 3
    匹配完成 = 4
    确认无误 = 5
    确认作废 = 6


class MatchListBStatusEnum(IntEnum):
    """供应商绑定状态"""
    # 无 = 0
    未绑定 = 1
    绑定中 = 2
    绑定失败 = 3
    绑定成功 = 4


class BStatusEnum(IntEnum):
    """绑定状态"""
    # 无 = 0
    未绑定 = 1
    绑定中 = 2
    绑定失败 = 3
    绑定成功 = 4


class AuthorizationFormEnum(IntEnum):
    """供应商绑定状态"""
    独家 = 1
    非独 = 2


class MQStatusEnum(IntEnum):
    """手工单任务状态"""
    无 = 0
    进行中 = 1
    已完成 = 2
    处理失败 = 3


class MatchCheckStatusEnum(IntEnum):
    """是否结算"""
    # 无 = 0
    未结算 = 1
    已结算 = 2
    结算中 = 3


class CheckMatchTypeEnum(IntEnum):
    """手工单生成版权类型"""
    # 无 = 0
    按条件生成 = 1
    按作品生成 = 2
    导入Excel生成 = 3


class DeriveVersionEnum(IntEnum):
    """衍生版本"""
    # 无 = 0
    非 = 1
    是 = 2


class ContractTypeEnum(IntEnum):
    """签约类型"""
    未确定 = 1
    词曲签约 = 2
    录音自带词曲 = 3


class CanLegalRightsEnum(IntEnum):
    """可维权"""
    未确定 = 1
    可维权 = 2
    不可维权 = 3


class CanCoverEnum(IntEnum):
    """可翻唱"""
    否 = 1
    是 = 2

# 资产类型：代理 自有 外部定制 其他 免费 推广 演出
