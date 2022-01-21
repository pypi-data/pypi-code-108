# -*- coding:utf8 -*-

# 七牛上传类型
FILE_TYPE_AVATAR = 1
FILE_TYPE_BACKIMG = 2
FILE_TYPE_POST = 3  # 以后所有新增的类型,都用这个,不在添加新类型
FILE_TYPE_AUDIO = 4
FILE_TYPE_VIDEO = 5
FILE_TYPE_COVER = 6
FILE_TYPE_PACK = 7
FILE_TYPE_AD = 8
FILE_TYPE_REPLAY = 9
FILE_TYPE_REPLAY_IMG = 10
FILE_TYPE_REPLAY_PPT = 11
FILE_TYPE_REPLAY_LYRIC = 12
FILE_TYPE_STORE = 13  # 商城图片

# 本地TYPE上传类型
LOCAL_TYPE_AUDIO = 0
LOCAL_TYPE_VIDEO = 1
LOCAL_TYPE_COVER = 2
LOCAL_TYPE_AVATAR = 4
LOCAL_TYPE_BACKIMG = 5
LOCAL_TYPE_REPLAY = 6

# 图片尺寸约定
MICRO = 0
SMALL = 1
BIG = 2
SLIDE = 3
WORKS = 4
CHANLLENGE = 5
LARGE = 6
HOME = 7
MAX = 8
RAW = 9
NEW_CHALLENGE = 10
NEW_CHALLENGE2 = 11
AD_START = 12
ALBUM_COVER = 13  # 推荐专辑列表封面图,400*200

# 上传类型对应bucket:(空间名, 域名路径目录)
BUCKET_MAP = {FILE_TYPE_AVATAR: ("iguitar-image", "avatar"),
              FILE_TYPE_BACKIMG: ("iguitar-image", "back"),
              FILE_TYPE_COVER: ("iguitar-image", "cover"),
              FILE_TYPE_POST: ("iguitar-image", "image"),
              FILE_TYPE_STORE: ("iguitar-image", "store"),  # 商城图片
              FILE_TYPE_AUDIO: ("iguitar-audio", "audio"),
              FILE_TYPE_VIDEO: ("iguitar-media", "video"),
              FILE_TYPE_PACK: ("iguitar-bgt-apk", "pack"),
              FILE_TYPE_AD: ("iguitar-image", "ad"),
              FILE_TYPE_REPLAY: ("iguitar-replay", "replay"),
              FILE_TYPE_REPLAY_IMG: ("iguitar-replay", "image"),
              }


# 缩略图尺寸,先缩略再上传
THUMB_SIZE = {MICRO: (100, 100),
              SMALL: (120, 120),
              BIG: (240, 240),
              LARGE: (750, 750),
              SLIDE: (750, 280),
              WORKS: (750, 450),
              CHANLLENGE: (750, 320),
              MAX: (1024, 1024),
              HOME: (750, 580),
              }

QINIU_IMAGE = "http://img.iguitar.immusician.com/"    # "http://7xlomp.com1.z0.glb.clouddn.com/"
QINIU_MEDIA = "http://media.iguitar.immusician.com/"      # "http://7xlizu.com5.z0.glb.clouddn.com/"
QINIU_AUDIO = "http://audio.iguitar.immusician.com/"  # "http://7xloms.com5.z0.glb.clouddn.com/"
QINIU_BGT = "http://bgt.iguitar.immusician.com/"       # "http://7xlomr.com5.z0.glb.clouddn.com/"
QINIU_REPLAY = "http://replay.iguitar.immusician.com/"  # "http://7xrxp6.com1.z0.glb.clouddn.com/"


THUMB_MAP = {MICRO: "micro",
             SMALL: "small",
             BIG: "big",
             LARGE: "large",
             SLIDE: "slide",
             WORKS: "works",
             CHANLLENGE: "chanllenge",
             NEW_CHALLENGE: "newchallenge",
             NEW_CHALLENGE2: 'newchallenge2',
             HOME: "home",
             RAW: "raw",
             AD_START: 'adstart',      # 750*1334
             ALBUM_COVER: 'albumcover'  # # 推荐专辑列表封面图,40*200
             }

