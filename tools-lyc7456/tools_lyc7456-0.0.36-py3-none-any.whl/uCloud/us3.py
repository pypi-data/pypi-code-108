import os
from ufile import logger                # 设置日志文件
from ufile import config                # 设置参数
from ufile import filemanager           # 普通上传
from ufile import multipartuploadufile  # 分片上传

# update by lyc at 2021-12-30

class US3():
    '''优刻得US3封装：https://github.com/ucloud/ufile-sdk-python'''
    def __init__(self, key, locallogname=False, use_inner_upload_domain=False, use_inner_download_domain=False):
        self.public_key = key['US3']['public_key']
        self.private_key = key['US3']['private_key']
        self.project_id = key['project_id']
        self.region = key['region']

        # 设置运行日志
        if locallogname:
            logger.set_log_file(locallogname)  
        
        # 以下两项如果不设置，则默认设为'.cn-bj.ufileos.com'，即使用公网上传或下载
        if use_inner_upload_domain:
            # 设置上传host后缀,外网可用后缀形如 .cn-bj.ufileos.com（cn-bj为北京地区，其他地区具体后缀可见控制台：对象存储-单地域空间管理-存储空间域名）
            config.set_default(uploadsuffix='.ufile.cn-north-04.ucloud.cn') 
        if use_inner_download_domain:
            # 设置下载host后缀，普通下载后缀即上传后缀，CDN下载后缀为 .ufile.ucloud.com.cn
            config.set_default(downloadsuffix='.ufile.cn-north-04.ucloud.cn')
        
        config.set_default(connection_timeout=60)   # 设置请求连接超时时间，单位为秒
        config.set_default(expires=60)              # 设置私有bucket下载链接有效期,单位为秒
        config.set_default(md5=True)                # 设置上传文件是否校验md5



    def __upload_common(self, bucket='', put_key='', localfile='', type_key='STANDARD'):
        '''
        普通上传。小于50M文件上传用。
        :param bucket: ufile空间名称
        :param put_key: 上传文件在空间中的名称
        :param localfile: 本地文件名
        :param type_key: 'STANDARD'-标准文件类型（默认），'IA'-低频文件类型，'ARCHIVE'-归档文件类型
        :return: 200 成功
        '''
        try:
            header = dict() # 设置 header
            header['X-Ufile-Storage-Class'] = type_key
            putufile_handler = filemanager.FileManager(self.public_key, self.private_key)       # 签名
            ret, resp = putufile_handler.putfile(bucket, put_key, localfile, header=None)
            return resp.status_code
        
        except Exception as err:
            # print(err)
            return err



    def __upload_multipart(self, bucket='', put_key='', localfile='', type_key='STANDARD'):
        '''
        分片上传。大于50M文件上传用。
        :param bucket: ufile空间名称
        :param put_key: 上传文件在空间中的名称
        :param localfile: 本地文件名
        :param type_key: 'STANDARD'-标准文件类型，'IA'-低频文件类型，'ARCHIVE'-归档文件类型
        :return: 200 成功
        '''
        try:
            header = dict()     # 设置 header
            header['X-Ufile-Storage-Class'] = type_key
            multipartuploadufile_handler = multipartuploadufile.MultipartUploadUFile(self.public_key, self.private_key)     # 签名
            ret, resp = multipartuploadufile_handler.uploadfile(bucket, put_key, localfile, maxthread=8,header=header)
            while True:
                if resp.status_code == 200:     # 分片上传成功
                    break
                elif resp.status_code == -1:    # 网络连接问题，续传
                    ret, resp = multipartuploadufile_handler.resumeuploadfile()
                else:                           # 服务或者客户端错误
                    print(resp.error)
                    break
            return resp.status_code

        except Exception as err:
            # print(err)
            return err



    def upload_file(self, bucket='',put_key='', localfile='', type_key="STANDARD"):
        '''
        上传ufile-接口类：自动识别上传文件来选择普通上传方法或分块上传方法
        :param bucket: ufile空间名称
        :param put_key: 上传文件在空间中的名称
        :param localfile: 本地文件名
        :param type_key: 'STANDARD'-标准文件类型，'IA'-低频文件类型，'ARCHIVE'-归档文件类型
        :return: int 200 上传成功
        '''
        if os.path.getsize(localfile) <= 52428800:      #  普通上传 < 50M < 分片上传
            return self.__upload_common(bucket=bucket, put_key=put_key, localfile=localfile, type_key=type_key)
        else:
            return self.__upload_multipart(bucket=bucket, put_key=put_key, localfile=localfile, type_key=type_key)



    # def getFileList(self, bucket='', marker=""):
    #     '''
    #     获取bucket下文件列表，写到本地文件。递归函数。
    #     :param bucket: ufile空间名称
    #     :param marker: 文件列表起始位置
    #     :return:
    #     '''
    #     try:
    #         # self.getfilelist_hander.set_keys(self.public_key, self.private_key)     # 重新设置aksk，签名
    #         prefix = ''     # 文件前缀
    #         limit = 1000    # 文件列表数目
    #         ret, resp = self.getfilelist_hander.getfilelist(bucket, prefix=prefix, limit=limit, marker=marker)
    #         for item in ret['DataSet']:
    #             self.logger_fl.info(item['FileName'])
    #         marker = ret['NextMarker']
    #         if marker:
    #             self.getFileList(bucket, marker)    # 递归调用自己
    #         else:
    #             return 0

    #     except Exception as err:
    #         # print(err)
    #         return err



    def delete_file(self, bucket='', key_name=''):
        '''
        删除空间一个文件。
        :param bucket: ufile空间名称
        :param key_name: 文件在空间中的名称
        :return: int 204 删除成功
        '''
        try:
            deleteufile_handler = filemanager.FileManager(self.public_key, self.private_key)
            ret, resp = deleteufile_handler.deletefile(bucket, key_name)
            return resp.status_code
        
        except Exception as err:
            # print(err)
            return err



    def classswitch_file(self, bucket='', key_name='', type_key='STANDARD'):
        '''
        转换空间中的一个文件的存储类型。
        :param bucket: ufile空间名称
        :param key_name: 文件在空间中的名称
        :param type_key: 'STANDARD'-标准文件类型，'IA'-低频文件类型，'ARCHIVE'-归档文件类型
        :return: int 200 成功
        '''
        try:
            classswitch_handler = filemanager.FileManager(self.public_key, self.private_key)
            # classswitch_handler.set_keys(self.public_key, self.private_key)           # 重新设置aksk，签名
            ret, resp = classswitch_handler.class_switch_file(bucket, key_name, type_key)
            return resp.status_code

        except Exception as err:
            # print(err)
            return err



    def restore_file(self, bucket='', key_name=''):
        '''
        解冻空间中的一个ARCHIVE归档型类型的文件。
        :param bucket: ufile空间名称
        :param key_name: 文件在空间中的名称
        :return: int 200 成功
        '''
        try:
            restorefile_handler = filemanager.FileManager(self.public_key, self.private_key)
            # restorefile_handler.set_keys(self.public_key, self.private_key)           # 重新设置aksk，签名
            ret, resp = restorefile_handler.restore_file(bucket, key_name)
            return resp.status_code

        except Exception as err:
            # print(err)
            return err

