import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

import requests
# pip install pydantic[ujson, email]
from pydantic import ValidationError
from pydantic import BaseModel, Field, validator

from .enums import (
    AuthFormEnum,
    AuthTransferEnum,
    AuthRelationEnum,
    IsEnum,
    StatusEnum,
    FinishStatusEnum,
    AlbumTypeEnum,
    RegionEnum,
    LanguageEnum,
    AreaEnum,
    TypeEnum,
    DeriveVersionEnum,
    ContractTypeEnum,
    CanLegalRightsEnum,
    CanCoverEnum,
)


class FileData(BaseModel):
    """
    文件数据
    """
    name: str = Field(None, title="文件名称", max_length=250)
    file_name: str = Field(None, title="原文件名称", max_length=250)
    url: str = Field(None, title="文件链接", max_length=1024)

    def save_file(self, file_dir, file_name=None, skip_existing_file=False):
        """
        保存文件
        """
        if not self.url:
            print('没有下载链接', self.file_name, self.name)
            return
        if file_name is None:
            if self.file_name:
                file_name = self.file_name
            elif self.name:
                file_name = self.name
            else:
                file_name = os.path.basename(self.url)
        file = os.path.join(file_dir, file_name)
        if skip_existing_file and os.path.exists(file):
            return
        kwargs = {'stream': True}
        req = requests.get(self.url, **kwargs)
        with(open(file, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


class TmeFileInfo(BaseModel):
    """
    Tme文件信息
    """
    audio_check: str = Field(None, title="音频检查", max_length=250)
    duration: int = Field(None, title="时长")
    origin_file_name: str = Field(None, title="原始文件名", max_length=250)
    fileSize: int = Field(None, title="文件大小")


class TmeFileData(BaseModel):
    """
    Tme文件数据
    """
    url: str = Field(None, title="文件链接", max_length=1024)
    file_info: TmeFileInfo = Field(None, title="文件信息")
    file_id: str = Field(None, title="文件ID", max_length=250)
    msg: str = Field(None, title="消息", max_length=512)
    md5: str = Field(None, title="MD5", max_length=100)


class MusicData(FileData):
    """
    音频文件数据
    """
    tme: TmeFileData = Field(None, title="tme")


class ArtistData(BaseModel):
    """
    艺人数据
    """
    id: int = Field(None, title="艺人ID")
    name: str = Field(None, title="艺人名称", max_length=250)


class CopyrightData(BaseModel):
    """
    授权数据
    """
    original_company: str = Field(None, title="原始版权公司", max_length=250)
    auth_start_time: str = Field(None, title="授权开始时间", max_length=50)
    auth_end_time: str = Field(None, title="授权结束时间", max_length=50)
    share: float = Field(100, title="份额")
    copyright_source: int = Field(None, title="版权来源")
    oversea_proxy: IsEnum = Field(None, title="海外总代理")
    auth_form: AuthFormEnum = Field(None, title="授权形式")
    auth_transfer: AuthTransferEnum = Field(None, title="可否转授权")
    auth_relation: AuthRelationEnum = Field(None, title="授权关系")
    type: str = Field(None, title="type", max_length=50)
    contract_type: ContractTypeEnum = Field(None, title="签约类型")
    # （1：未确定；2：可维权；3：不可维权）
    can_legal_rights: CanLegalRightsEnum = Field(None, title="可维权")
    # （1：否；2：是；）
    can_cover: CanCoverEnum = Field(None, title="可翻唱")
    auth_area: str = Field(None, title="授权区域", max_length=250)  # （ID，”,”分割）


##########################################################################################################
class SongModel(BaseModel):
    """
    歌曲模型
    """
    id: int = Field(0, title="歌曲ID")  # 新增则等于0
    name: str = Field('', title="歌曲名", max_length=250)
    subtitle: str = Field(None, title="副标题", max_length=250)
    tran_name: str = Field(None, title="翻译名", max_length=250)
    artist: List[ArtistData] = Field(None, title="所属艺人")  # [{id,name}]
    cd_index: int = Field(None, title="CD索引")  # （默认CD1）这个有时候为空
    language: int = Field(None, title="语言")
    album_genre: str = Field(None, title="流派", max_length=250)  # （名称，竖杠分割）
    version: str = Field(None, title="版本", max_length=250)
    derive_version: DeriveVersionEnum = Field(None, title="衍生版本")
    isrc: str = Field(None, title="ISRC编号", max_length=250)
    iswc: str = Field(None, title="ISWC编号", max_length=250)
    publish_time: str = Field(None, title="发行时间", max_length=50)
    online_time: str = Field(None, title="上线时间", max_length=50)
    pay_mode: int = Field(None, title="付费模式")  # （默认付费1.0）
    wording: str = Field(None, title="作词", max_length=250)
    composing: str = Field(None, title="作曲", max_length=250)
    arranging: str = Field(None, title="编曲", max_length=250)
    maker: str = Field(None, title="制作人", max_length=250)
    text_lyrics: List[FileData] = Field([], title="文本歌词")  # 需要先获取上传文件的返回数据
    music: MusicData = Field(None, title="音频")
    music_tme: str = Field(None, title="TME音频url", max_length=4096)
    mainer: str = Field(None, title="负责人", max_length=250)
    mainer_id: str = Field(None, title="负责人ID", max_length=50)
    location: int = Field(None, title="排序")  # 排序（默认1，升序）
    tme_id: str = Field(None, title="tme_id")
    cql_id: str = Field(None, title="cql_id")
    copyright_list: CopyrightData = Field(None, title="录音版权")
    word_copyright_list: CopyrightData = Field(None, title="词版权")
    music_copyright_list: CopyrightData = Field(None, title="曲版权")

    @validator('music', pre=True)
    def get_dictionary_contents_in_list(cls, v):
        """
        获取列表中的字典内容
        """
        if not v:
            return None
        if isinstance(v, list) and len(v) == 1:
            return v[0]
        elif isinstance(v, dict):
            return v
        raise ValueError(f'music 字段, 不能转换为字典 {v}')

    # @validator('artist', pre=True, whole=True)
    # def blank_character_to_none(cls, v):
    #     """
    #     空白字符的时候返回 None
    #     """
    #     # print('SongModel character_to_none', type(v), v)
    #     if not v:
    #         return None
    #     return v

    @validator('artist', pre=True, whole=True)
    def artist_to_list(cls, v):
        """
        如果内容不为真，那么我们返回空列表
        """
        # print('SongModel artist_to_list', type(v), v)
        if not v:
            return []
        return v

    @validator('text_lyrics', pre=True, whole=True)
    def text_lyrics_to_list(cls, v):
        """
        """
        # print('SongModel text_lyrics_to_list', type(v), v)
        if not v:
            return []
        return v


##########################################################################################################
class AlbumModel(BaseModel):
    """
    专辑模型
    """
    id: int = Field(None, title="专辑ID")  # （首次创建为空）
    album_name: str = Field('', title="专辑名称", max_length=250)
    tran_name: str = Field(None, title="翻译名称", max_length=250)
    album_cover: FileData = Field(None, title="专辑封面")  # 需要先获取上传文件的返回数据
    artist: List[ArtistData] = Field(None, title="所属艺人")  # [{id,name}]
    album_type: AlbumTypeEnum = Field(-1, title="专辑类型")
    region: RegionEnum = Field(None, title="地区")
    language: str = Field(None, title="语言", max_length=250)  # （ID，”,”分割）
    album_genre: str = Field(None, title="专辑流派", max_length=250)  # （名称，竖杠分割）
    album_upc: str = Field(None, title="专辑UPC", max_length=250)
    version: str = Field(None, title="专辑版本", max_length=250)
    brand_company: str = Field(None, title="外显厂牌公司", max_length=250)
    publish_time: str = Field(None, title="发行时间", max_length=50)
    online_time: str = Field(None, title="上线时间", max_length=50)
    is_number: IsEnum = Field(None, title="是否数专")
    pre_time: str = Field(None, title="预售时间", max_length=50)
    sale_start_time: str = Field(None, title="售卖开始时间", max_length=50)
    sale_end_time: str = Field(None, title="售卖结束时间", max_length=50)
    price: str = Field(None, title="售卖价格", max_length=50)
    auth_file: List[FileData] = Field(None, title="授权文件")
    album_summary: str = Field(None, title="专辑简介", max_length=8192)
    album_id_tme: int = Field(None, title="TME专辑ID")  # 保存草稿无  # 保存的时候不需要
    copyright_company_id: int = Field(None, title="所属公司ID")  # 保存的时候不需要
    copyright_company: str = Field(None, title="所属公司", max_length=250)  # 保存的时候不需要
    signsubject_id: int = Field(None, title="签约主体ID")
    signsubject: str = Field(None, title="签约主体名称", max_length=250)  # 保存的时候不需要
    status: StatusEnum = Field(0, title="状态")  # 保存的时候不需要
    finish_status: FinishStatusEnum = Field(None, title="完善状态")  # 自动判断   # 保存的时候不需要，获取专辑详情的时候也没有了
    song_list: List[SongModel] = Field([], title="歌曲列表")

    @validator('artist', pre=True, whole=True)
    def artist_to_none(cls, v):
        # print('artist_to_none', type(v), v)
        if not v:
            # print('artist_to_none return None')
            return None
        return v

    @validator('auth_file', pre=True, whole=True)
    def auth_file_to_none(cls, v):
        # print('auth_file_to_none', type(v), v)
        if not v:
            # print('auth_file_to_none return None')
            return None
        return v

    @validator('song_list', pre=True, whole=True)
    def song_list_to_list(cls, v):
        # print('song_list_to_list', type(v), v)
        if not v:
            # print('song_list_to_list return None')
            return []
        return v

    # class Config:
    #     extra = Extra.forbid  # 禁止额外属性(主要是为了检查是否有我们漏下的数据)


##########################################################################################################
class ShowerModel(BaseModel):
    """
    艺人模型
    """
    singer_name: str = Field(..., title="艺人名", max_length=250)
    trans_name: str = Field(None, title="艺人翻译名", max_length=250)
    area: AreaEnum = Field(..., title="艺人活跃地区")
    type: TypeEnum = Field(..., title="艺人类型")
    singer_desc: str = Field(..., title="艺人简介")  # 是
    singer_photo_list: List[FileData] = Field([], title="艺人图片")  # [{name(文件名称),url(文件url)}]

    # class Config:
    #     extra = Extra.forbid  # 禁止额外属性(主要是为了检查是否有我们漏下的数据)
