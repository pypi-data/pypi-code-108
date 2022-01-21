# coding=utf-8
from magic_numbers import *


PIL_INSTALLED = False
try:
    from PIL import Image

    PIL_INSTALLED = True
except ImportError:
    raise

def check_name(name):
    try:
        name = name.encode('utf-8')
    except UnicodeDecodeErroras e:
        pass
    name = name.replace(' ', '') \
        .replace('.', '') \
        .replace('-', '') \
        .replace('_', '') \
        .replace('（', '(') \
        .replace('）', ')') \
        .replace(',', '') \
        .replace('+', '')

    try:
        name = name.decode('utf-8')
    except UnicodeDecodeErroras e:
        pass

    return name


def get_store_goods_img_url(filename, size=1):
    '''
    获取商城商品图片url
    :param filename:
    :param size: 图片大小预留
    :return:
    '''
    return "%sstore/%s" % (QINIU_IMAGE, filename)


def get_backimg_url(filename, size=1):
    if size == RAW:
        return "%sback/%s" % (QINIU_IMAGE, filename)
    return "%sback/%s-%s" % (QINIU_IMAGE, filename, THUMB_MAP[size]) if filename else ""


def get_avatar_url(filename, size=1):
    if not filename:
        return ""
    if size == RAW:
        return "%savatar/%s" % (QINIU_IMAGE, filename)
    return "%savatar/%s-%s" % (QINIU_IMAGE, filename, THUMB_MAP[size])


def get_post_url(filename, size=1):
    if not filename:
        return ""
    # if size == RAW:
    #     return "%simage/%s" % (QINIU_IMAGE, filename)
    return "%simage/%s-%s" % (QINIU_IMAGE, filename, THUMB_MAP[size])


def get_audio_url(filename):
    if not filename:
        return ""
    return "%saudio/%s" % (QINIU_AUDIO, filename)


def get_video_url(filename):
    if not filename:
        return ""
    return "%svideo/%s" % (QINIU_MEDIA, filename)


def get_cover_url(filename, size=1):
    if not filename:
        return ""
    if isinstance(filename, list):
        for i in filename[::-1]:
            if i:
                filename = i
                break
    # if size == RAW:
    #     return "%scover/%s" % (QINIU_IMAGE, filename)
    return "%scover/%s-%s" % (QINIU_IMAGE, filename, THUMB_MAP[size])


def mget_cover_url(filename, size=1):
    pics = []
    if not filename:
        return pics
    if isinstance(filename, list):
        for i in filename:
            if not i:
                continue
            if size == RAW:
                # i = "%scover/%s" % (QINIU_IMAGE, i)
                i = "%scover/%s-%s" % (QINIU_IMAGE, i, THUMB_MAP[size])
            else:
                i = "%scover/%s-%s" % (QINIU_IMAGE, i, THUMB_MAP[size])
            pics.append(i)
    return pics


def get_bgt_url(filename):
    if not filename:
        return ""

    return "%sbgt/%s" % (QINIU_BGT, filename)


def get_version_url(filename):
    if not filename:
        return ""

    return "%spack/%s" % (QINIU_BGT, filename)


def get_post_media_url(type, media):
    if type == 0:
        return get_audio_url(media)
    return get_video_url(media)


def get_works_thumb_url(thumb, t=WORKS):
    if thumb == '':
        thumb = 'moren@3x.png'
    elif thumb == [''] or thumb == []:
        thumb = ['moren@3x.png']

    if not isinstance(thumb, list):
        return [get_cover_url(thumb, t)]
    return [get_cover_url(i, t) for i in thumb]


def get_ad_url(filename, size=6):
    if not filename:
        return ""
    if isinstance(filename, list):
        for i in filename[::-1]:
            if i:
                filename = i
                break
    # if size == RAW:
    #     return "%scover/%s" % (QINIU_IMAGE, filename)
    return "%sad/%s-%s" % (QINIU_IMAGE, filename, THUMB_MAP[size])


def get_replay_url(filename):
    if not filename:
        return ""

    return "%sreplay/%s" % (QINIU_REPLAY, filename)


def get_replay_img_url(filename):
    if not filename:
        return ""

    return "%simage/%s" % (QINIU_REPLAY, filename)


def get_replay_ppt_url(filename):
    if not filename:
        return ""

    return "%sppt/%s" % (QINIU_REPLAY, filename)


def get_replay_lyric_url(filename):
    if not filename:
        return ""

    return "%slyric/%s" % (QINIU_REPLAY, filename)