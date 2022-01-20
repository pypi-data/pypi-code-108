# -*- coding: utf-8 -*-
"""
更新日期:2021/8/27
作者: D.Z.zhong
用途: 图片管道文件实现异步下载上传至阿里云oss
运行环境：win10 64/linux + python3.9 + scrapy2.4.1
选择目录位置:{python}\Lib\site-packages\scrapy\pipelines
需要配置的settings参数:
FILES_STORE <阿里云域名> eg:'https://xcc2.oss-cn-shenzhen.aliyuncs.com'
FILES_OSS_FILE <Oss文件目录> eg:'default/files'
FILES_OSS_URLS_FIELD <读取pdf字段链接> eg:'raw_pdf_url'(该字段多个用|分割)
FILES_OSS_RESULT_FIELD <转存阿里云链接字段> eg:'pdf_url'
# FILES_OSS_URLS_FIELD = FILES_OSS_RESULT_FIELD = 'raw_pdf_url' #表示将raw_pdf_url字段替换成阿里云链接
RESOURCE_CLASSNAME <需要下载资源的item类名> eg:"FactoryMaterialItem"
ITEM_PIPELINES = {
   'scrapy.pipelines.ossfiles.OSSFilesPipeline': 300,
}
OSS_USER = xxxxxxxxxxxxxxxxxxxxxxxx
OSS_PASSWORD = xxxxxxxxxxxxxxxxxxxxxxxx
"""
import functools
import hashlib
import logging
import mimetypes
import os
import time
from collections import defaultdict
from contextlib import suppress
from ftplib import FTP
from io import BytesIO
from urllib.parse import urlparse

from itemadapter import ItemAdapter
from twisted.internet import defer, threads

from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.http import Request
from scrapy.pipelines.media import MediaPipeline
from scrapy.settings import Settings
from scrapy.utils.log import failure_to_exc_info
from scrapy.utils.misc import md5sum
from scrapy.utils.python import to_bytes
from scrapy.utils.request import referer_str
from scrapy.pipelines.files import FileException, FilesPipeline

import oss2
import magic

logger = logging.getLogger(__name__)

class OSSFilesStore:
    def __init__(self, uri):
        if not uri.startswith("https://xcc2.oss"):
            raise ValueError(f"Incorrect URI scheme in {uri}, expected '阿里云对象存储域名'")
        u = urlparse(uri)
        self.basedir = uri.rstrip('/')
        self.auth = oss2.Auth(self.OSS_USERNAME, self.OSS_PASSWORD)
        self._bucket = oss2.Bucket(self.auth, 'oss-cn-shenzhen.aliyuncs.com', 'xcc2')


    def persist_file(self, path, buf, info, meta=None, headers=None):
        relative_path = path.replace(f"{self.basedir}/","")
        self._bucket.put_object(relative_path,buf.getvalue(), progress_callback=None)

    def stat_file(self, path, info):
        return {}

class OssFilesPipeline(MediaPipeline):
    MEDIA_NAME = "ossfile"
    EXPIRES = 90
    STORE_SCHEMES = {
        'https': OSSFilesStore #新增阿里云文件存储类
    }
    DEFAULT_FILES_OSS_URLS_FIELD = 'file_urls'
    DEFAULT_FILES_OSS_RESULT_FIELD = 'files'
    DEFAULT_OSS_DOMAIN = 'https://xcc2.oss-cn-shenzhen.aliyuncs.com'
    FILES_OSS_FILE = 'default/files'
    FILTER_EMPTY_ITEM = False # 过滤字段urlimg为空的item
    def __init__(self, store_uri, download_func=None, settings=None):
        if not store_uri:
            raise NotConfigured

        if isinstance(settings, dict) or settings is None:
            settings = Settings(settings)

        cls_name = "FilesPipeline"
        self.store = self._get_store(store_uri)
        resolve = functools.partial(self._key_for_pipe,
                                    base_class_name=cls_name,
                                    settings=settings)
        self.expires = settings.getint(
            resolve('FILES_EXPIRES'), self.EXPIRES
        )
        if not hasattr(self, "FILES_OSS_URLS_FIELD"):
            self.FILES_OSS_URLS_FIELD = self.DEFAULT_FILES_OSS_URLS_FIELD
        if not hasattr(self, "FILES_OSS_RESULT_FIELD"):
            self.FILES_OSS_RESULT_FIELD = self.DEFAULT_FILES_OSS_RESULT_FIELD
        if not hasattr(self, "OSS_DOMAIN"):
            logging.warning("At settings.py missing 'OSS_DOMAIN'")
            self.OSS_DOMAIN = self.DEFAULT_OSS_DOMAIN
        if not hasattr(self, "FILES_OSS_FILE"):
            logging.warning("At settings.py missing 'FILES_OSS_FILE'")
            self.FILES_OSS_FILE = self.DEFAULT_FILES_OSS_FILE
        if not hasattr(self, "FILTER_EMPTY_ITEM"):
            logging.warning("At settings.py missing 'FILTER_EMPTY_ITEM'")
            self.FILTER_EMPTY_ITEM = self.FILTER_EMPTY_ITEM

        self.files_oss_urls_field = settings.get(
            resolve('FILES_OSS_URLS_FIELD'), self.FILES_OSS_URLS_FIELD
        )
        self.files_oss_result_field = settings.get(
            resolve('FILES_OSS_RESULT_FIELD'), self.FILES_OSS_RESULT_FIELD
        )
        self.oss_domain = settings.get(
            resolve('OSS_DOMAIN'), self.OSS_DOMAIN
        )
        self.files_oss_file = settings.get(
            resolve('FILES_OSS_FILE'), self.FILES_OSS_FILE
        )
        self.filter_empty_item = settings.get(
            resolve('FILTER_EMPTY_ITEM'), self.FILTER_EMPTY_ITEM
        )
        # FIX: 出现未配置错误
        self.if_feed = settings.get('FEEDS').attributes 
        self.need_download_classname = settings.get('RESOURCE_CLASSNAME')
        super().__init__(download_func=download_func, settings=settings)

    @classmethod
    def from_settings(cls, settings):
        oss_store = cls.STORE_SCHEMES['https']
        oss_store.OSS_USERNAME = settings['OSS_USER']
        oss_store.OSS_PASSWORD = settings['OSS_PASSWORD']

        store_uri = settings['FILES_STORE']
        return cls(store_uri, settings=settings)

    def _get_store(self, uri):
        '''
        判断uri
        '''
        if os.path.isabs(uri):  # to support win32 paths like: C:\\some\dir
            scheme = 'file'
        else:
            scheme = urlparse(uri).scheme
        if scheme != 'https':
            raise NotConfigured # FILES_STORE不是阿里云域名的
        store_cls = self.STORE_SCHEMES[scheme]
        return store_cls(uri)

    def media_to_download(self, request, info, *, item=None):
        def _onsuccess(result):
            if not result:
                return  # returning None force download

            last_modified = result.get('last_modified', None)
            if not last_modified:
                return  # returning None force download

            age_seconds = time.time() - last_modified
            age_days = age_seconds / 60 / 60 / 24
            if age_days > self.expires:
                return  # returning None force download

            referer = referer_str(request)
            logger.debug(
                'File (uptodate): Downloaded %(medianame)s from %(request)s '
                'referred in <%(referer)s>',
                {'medianame': self.MEDIA_NAME, 'request': request,
                 'referer': referer},
                extra={'spider': info.spider}
            )
            # self.inc_stats(info.spider, 'uptodate')

            checksum = result.get('checksum', None)
            return {'url': request.url, 'path': path, 'checksum': checksum, 'status': 'uptodate'}

        path = self.file_path(request, info=info, item=item) #调用了存放位置的路径函数
        dfd = defer.maybeDeferred(self.store.stat_file, path, info)
        dfd.addCallbacks(_onsuccess, lambda _: None)
        dfd.addErrback(
            lambda f:
            logger.error(self.__class__.__name__ + '.store.stat_file',
                         exc_info=failure_to_exc_info(f),
                         extra={'spider': info.spider})
        )
        return dfd

    def media_downloaded(self, response, request, info, *, item=None):
        referer = referer_str(request)

        if response.status != 200:
            logger.warning(
                'File (code: %(status)s): Error downloading file from '
                '%(request)s referred in <%(referer)s>',
                {'status': response.status,
                 'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('download-error')

        if not response.body:
            logger.warning(
                'File (empty-content): Empty file from %(request)s referred '
                'in <%(referer)s>: no-content',
                {'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        logger.debug(
            'File (%(status)s): Downloaded file from %(request)s referred in '
            '<%(referer)s>',
            {'status': status, 'request': request, 'referer': referer},
            extra={'spider': info.spider}
        )
        # self.inc_stats(info.spider, status)

        try:
            path = self.file_path(request, response=response, info=info, item=item)
            checksum = self.file_downloaded(response, request, info, item=item)
        except FileException as exc:
            logger.warning(
                'File (error): Error processing file from %(request)s '
                'referred in <%(referer)s>: %(errormsg)s',
                {'request': request, 'referer': referer, 'errormsg': str(exc)},
                extra={'spider': info.spider}, exc_info=True
            )
            raise
        except Exception as exc:
            logger.error(
                'File (unknown-error): Error processing file from %(request)s '
                'referred in <%(referer)s>',
                {'request': request, 'referer': referer},
                exc_info=True, extra={'spider': info.spider}
            )
            raise FileException(str(exc))

        return {'url': request.url, 'path': path, 'checksum': checksum, 'status': status}

    # Overridable Interface
    def get_media_requests(self, item, info):
        # TEST:item出入多种类型时
        if self.need_download_classname.lower() in item.__class__.__name__.lower():
            # TODO: 由于字段长度限制,是否判断限制传入url长度
            urls = ItemAdapter(item).get(self.files_oss_urls_field, '').split("|") \
                if not ItemAdapter(item).get(self.files_oss_urls_field, '').split("|")==[''] else []
            return [Request(u) for u in urls]


    def file_downloaded(self, response, request, info, *, item=None):
        path = self.file_path(request, response=response, info=info, item=item)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        self.store.persist_file(path, buf, info)
        return checksum

    def item_completed(self, results, item, info):
        with suppress(KeyError):
            ItemAdapter(item)[self.files_oss_result_field] = '|'.join([x['path'] for ok, x in results if ok])
        # TAG: 如果决定资源字段返回为空不存表,修改 FILTER_EMPTY_ITEM = True
        if not item[self.files_oss_urls_field] and self.filter_empty_item:
            if self.if_feed :
                return {}
            else:return
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]
        # Handles empty and wild extensions by trying to guess the
        # mime type then extension or default to empty string otherwise
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        if not media_ext:
            with suppress(AttributeError):
                kind = magic.from_buffer(response.body, mime=True).split('/')[-1]
                # 若为html文件
            with suppress(NameError):
                if kind =='html':
                    logging.warning("下载文件为html,请确认是否下载成功")
                media_ext = '.'+kind if not kind.startswith(".") else kind
        return f'{self.oss_domain}/{self.files_oss_file}/{media_guid}{media_ext}'

    def inc_stats(self, spider, status):
        spider.crawler.stats.inc_value('file_count', spider=spider)
        spider.crawler.stats.inc_value(f'file_status_count/{status}', spider=spider)
