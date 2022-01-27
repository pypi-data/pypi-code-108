"""
pyape.http.cdn
~~~~~~~~~~~~~~~~~~~

工具类
处理CDN
"""

from pyape.app import logger


class CDN(object):

    def __init__(self, cdn_cfg):
        self.cdn_cfg = cdn_cfg
        self.cdn_vendor = cdn_cfg.get('vendor')

    def delfile(self, file_path):
        raise NotImplementedError('delfile is not implemented')

    def getlist(self, dir_path, limit=None, begin=None):
        """
        获取 CDN 文件列表
        :param dir_path: 文件夹地址
        :param limit: 分页限制
        :param order: 排序，默认 asc
        :return: {file: [], iter: str, siteurl: str, path: str}
        """
        raise NotImplementedError('getlist is not implemented')
        
    def upload2cdn(self, file_path, content):
        """ 上传文件到 CDN
        :param file_path:
        :param content: 可以是 file object
        :return:
        """
        raise NotImplementedError('upload2cdn is not implemented')


class Upyun(CDN):

    def _build_upyun(self):
        import upyun
        return upyun.UpYun(self.cdn_cfg.get('bucket'), self.cdn_cfg.get('username'), self.cdn_cfg.get('password'))

    def delfile(self, file_path):
        message = None
        try:
            up = self._build_upyun()
            up.delete(file_path)
            return True,  message
        except Exception as e:
            message = 'upyun delfile exception:%s' % str(e)
            logger.error(message)
        return None, message

    def getlist(self, dir_path, limit=None, begin=None):
        """ 获取 CDN 文件列表
        :param dir_path: 文件夹地址
        :param limit: 分页限制
        :param order: 排序，默认 asc
        :return: {file: [], iter: str, siteurl: str, path: str}
        """
        message = None
        try:
            up = self._build_upyun()
            res = up.get_list_with_iter(dir_path, limit, begin=begin)
            res['siteurl'] = self.cdn_cfg.get('siteurl')
            res['path'] = dir_path
            return True,  res
        except Exception as e:
            message = 'upyun getlist exception:%s' % str(e)
            logger.error(message)
        return None, message

    def upload2cdn(self, file_path, content):
        """ 上传文件到 CDN
        :param file_path:
        :param content: 可以是 file object
        :return:
        """
        message = None
        try:
            up = self._build_upyun()
            res = up.put(file_path, content, checksum=True)
            logger.info('upyun upload file_path:%s res:%s' % (file_path, res))
            return True, self.cdn_cfg.get('siteurl') + file_path
        except Exception as e:
            message = 'upyun upload exception:%s' % str(e)
            logger.error(message)
        return None, message
