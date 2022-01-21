# coding=utf-8
from cStringIO import StringIO
from tornado import gen
from sevencow import Cow
from base64 import urlsafe_b64encode
from magic_numbers import *
import hashlib

"""
This is a use example, you can copy to your project and rewrite.
"""

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


PIL_INSTALLED = False
try:
    from PIL import Image

    PIL_INSTALLED = True
except ImportError:
    raise


class Qiniu(Cow):
    def __init__(self, **kwargs):
        super(Qiniu, self).__init__(**kwargs)

    def generate_filename(self, data, name=None):

        if name:
            filename = check_name(name)
        else:
            # filename = random_string(10)
            filename = hashlib.md5(data).hexdigest()

        return filename

    @gen.coroutine
    def save_store_img(self, data):
        '''
        上传商城详情和主图图片
        :param data:
        :return:
        '''
        bucket, prefix = BUCKET_MAP[FILE_TYPE_STORE]
        task, filenames = [], []

        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))
        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_avatar(self, data, bucket, prefix):
        task, filenames = [], []

        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket,
                                 self.make_thumb(i, THUMB_SIZE[MAX]) if PIL_INSTALLED else i["body"],
                                 filename="/".join([prefix, filename]),
                                 content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_local_avatar(self, filePath):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_AVATAR]
        task, filenames = [], []
        with open(filePath, 'rb', encoding='utf-8') as f:
            data = f.read()
        filename = self.generate_filename(data)
        filenames.append(filename)
        task.append(self.put(bucket, data, filename="/".join([prefix, filename]), content_type='image/jpeg'))
        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_backimg(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_BACKIMG]

        task, filenames = [], []

        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_post(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_POST]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_cover(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_COVER]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(data=i['body'])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_local_cover(self, filePath):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_COVER]
        task, filenames = [], []
        with open(filePath, 'rb', encoding='utf-8') as f:
            data = f.read()
        filename = self.generate_filename(data)
        filenames.append(filename)
        task.append(self.put(bucket, data, filename="/".join([prefix, filename]), content_type='image/jpeg'))
        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_ad(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_AD]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(data=i['body'])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_audio(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_AUDIO]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            if i["content_type"] != 'audio/mp3':
                i["content_type"] = 'audio/mp3'
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_video(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_VIDEO]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_pack(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_PACK]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    @gen.coroutine
    def save_replay(self, data):
        bucket, prefix = BUCKET_MAP[FILE_TYPE_REPLAY]
        task, filenames = [], []
        for i in data:
            filename = self.generate_filename(i["body"])
            filenames.append(filename)
            task.append(self.put(bucket, i["body"], filename="/".join([prefix, filename]), content_type=i["content_type"]))

        yield task
        raise gen.Return(filenames)

    def make_thumb(self, upload_file, size=(240, 240), info=False):
        """生成缩略图"""

        try:
            thumb = Image.open(StringIO(upload_file["body"]))
        except IOError as e:
            raise e

        width, height = thumb.size
        if width > size[0] or height > size[1]:
            thumb.thumbnail(size, Image.ANTIALIAS)

        output = StringIO()
        thumb.save(output, thumb.format, quality=80)
        if not info:
            return output.getvalue()
        width, height = thumb.size
        return output.getvalue(), width, height

    def make_crop_thumb(self, upload_file, size=(128, 128), info=False):
        """生成带裁剪的缩略图"""
        im = Image.open(StringIO(upload_file["body"]))
        width, height = im.size
        if width <= height:
            offset = int((height - width) * 0.25)
            box = (0, offset, width, offset + width)
            region = im.crop(box)
        else:
            offset = int((width - height) / 2)
            box = (offset, 0, height + offset, height)
            region = im.crop(box)

        croped_width, croped_height = region.size

        if croped_width > size[0] or croped_height > size[1]:
            region.thumbnail(size, Image.ANTIALIAS)

        output = StringIO()
        region.save(output, im.format, quality=80)

        if not info:
            return output.getvalue()

        width, height = region.size
        return output.getvalue(), width, height

    def get_upload_token(self, filt_type, filename):
        """上传token"""
        bucket, prefix = BUCKET_MAP[int(filt_type)]
        token = self.generate_upload_token('%s:%s/%s' % (bucket, prefix, filename))
        return token, '%s/%s' % (prefix, filename)

    def get_upload_video_token(self, filename, cut_img, offset=1, watermark_media=None):
        """watermark_media: 上传策略
        1、上传后是否加水印
        2、播放时是否有限播放带水印的视频
        3、视频截图尺寸
        4、预处理使用的队列
        5、回调地址
        预处理规则：avthumb/mp4/vb/1.25m/wmImage/%s|saveas/%s;vframe/jpg/offset/%s/w/1024/h/950|saveas/%s
        解释：上传视频成功后 1、转为mp4且加上水印，然后保存到指定地方；2、取视频第n秒的截图，缩放为1024*950尺寸的jpg图片，保存在iguitar-image空间，保存名称为cover/filename
            1 和 2 顺序不能颠倒
        """
        bucket, prefix = BUCKET_MAP[FILE_TYPE_VIDEO]
        cover_bucket, cover_prefix = BUCKET_MAP[FILE_TYPE_COVER]    

        ops = dict()
        avthumbOps = ''
        if watermark_media.get('wmImage', True):
            avthumbOps = 'avthumb/mp4/vb/1.25m/wmImage/%s/rotate/auto|saveas/%s' % (urlsafe_b64encode(watermark_media["wmImageUrl"]),
                                                                        urlsafe_b64encode('%s:%s/%s' % (bucket, prefix, filename + '_wmImage')))
            ops['persistentNotifyUrl'] = watermark_media["NotifyUrl"]


        if watermark_media.get('cutjpg_w') and watermark_media.get('cutjpg_h'):
            vframeOps = 'vframe/jpg/offset/%s/w/%s/h/%s|saveas/%s' % (offset, watermark_media.get('cutjpg_w'), watermark_media.get('cutjpg_h'),
                                                                     urlsafe_b64encode('%s:%s/%s' % (cover_bucket, cover_prefix, cut_img)))
        else:
            # rotate/auto 会导致图片或视频翻转，原理不清
            # vframeOps = 'vframe/jpg/offset/%s/rotate/auto|saveas/%s' % (get_second(duration), urlsafe_b64encode('%s:%s/%s' % (cover_bucket, cover_prefix, cut_img)))
            vframeOps = 'vframe/jpg/offset/%s|saveas/%s' % (offset, urlsafe_b64encode('%s:%s/%s' % (cover_bucket, cover_prefix, cut_img)))

        if avthumbOps:
            persistentOps = avthumbOps + ';' + vframeOps
        else:
            persistentOps = vframeOps

        ops['persistentOps'] = persistentOps
        ops['persistentPipeline'] = watermark_media["Pipeline"]

        scope = '%s:%s/%s' % (bucket, prefix, filename)
        token = self.generate_upload_token(scope, ops=ops)
        return token, '%s/%s' % (prefix, filename)

