# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-05-19 10:33:52
:LastEditTime: 2022-01-18 19:24:56
:LastEditors: ChenXiaolei
:Description: ufile传输
"""
from abc import get_cache_token
from ufile.filemanager import *
import traceback
import multiprocessing


class UFileHelper(FileManager):
    def __init__(self,
                 public_key,
                 private_key,
                 bucket=None,
                 connection_timeout=300,
                 upload_suffix=None,
                 download_suffix=None,
                 expires=None,
                 user_agent=None,
                 md5=None,
                 cdn_prefix=None,
                 src_prefix=None):
        """
        :Description: 初始化 PutUFile 实例
        :param public_key: string类型, 账户API公私钥中的公钥
        :param private_key: string类型, 账户API公私钥中的私钥
        :param bucket: ufile空间名称
        :param connection_timeout: integer类型，网络请求超时时间
        :param upload_suffix: string类型，上传地址后缀
        :param download_suffix: string类型，下载地址后缀
        :param expires: integer类型，文件下载链接失效时间
        :param user_agent: string类型 user_agent
        @md5: 布尔类型，上传文件是否携带MD5
        :return: None，如果为非法的公私钥，则抛出ValueError异常
        """
        super(UFileHelper, self).__init__(public_key, private_key)
        self.public_key = public_key
        self.private_key = private_key
        self.bucket = bucket
        if cdn_prefix:
            self.cdn_prefix = cdn_prefix
        if src_prefix:
            self.src_prefix = src_prefix

        import ufile.config
        ufile.config.set_default(connection_timeout=connection_timeout,
                                 expires=expires,
                                 user_agent=user_agent,
                                 uploadsuffix=upload_suffix,
                                 downloadsuffix=download_suffix,
                                 md5=md5)

    def _get_bucket(self, bucket=None):
        """
        :Description: 获取ufile bucket
        :param bucket: ufile空间名称
        :return: bucket
        :last_editors: ChenXiaolei
        """
        if bucket and bucket != "":
            return bucket
        elif hasattr(self, "bucket") and self.bucket != "":
            return self.bucket
        else:
            raise Exception("ufile bucket is not configured")

    def put_file(self, put_key, localfile, header=None, bucket=None):
        """
        :Description: 上传文件至ufile
        :param put_key: string 类型，上传文件在空间中的名称
        :param localfile: string类型，本地文件名称
        :param header: dict类型，http 请求header，键值对类型分别为string，比如{'User-Agent': 'Google Chrome'}
        :param bucket: string类型，上传空间名称 初始化参数和此函数参数二选一传递
        :return: 字典类型,包含源文件=>src_url和cdn文件=>cdn_url
        :last_editors: ChenXiaolei
        """
        ret, resp = self.putfile(self._get_bucket(bucket),
                                 put_key,
                                 localfile,
                                 header=header)

        result = {}

        if resp.status_code == 200:
            if hasattr(self, "src_prefix") and self.src_prefix != "":
                result["src_url"] = self.src_prefix.rstrip('/') + "/" + put_key
            else:
                result["src_url"] = "/" + put_key

            if hasattr(self, "cdn_prefix") and self.cdn_prefix != "":
                result["cdn_url"] = self.cdn_prefix.rstrip('/') + "/" + put_key
            else:
                result["cdn_url"] = "/" + put_key

        return result

    def download_file(self,
                      key,
                      localfile,
                      isprivate=False,
                      content_range=None,
                      header=None,
                      bucket=None):
        """
        下载UFile文件并且保存为本地文件

        :param key: string类型， 下载文件在空间中的名称
        :param localfile: string类型，要保存的本地文件名称
        :param isprivate: boolean类型，如果为私有空间则为True
        :param content_range: tuple类型，元素为两个整型
        :param header: dict类型，http 请求header，键值对类型分别为string，比如{'User-Agent': 'Google Chrome'}
        :param bucket: string类型, UFile空间名称
        :return: ret: 如果http状态码为[200, 204, 206]之一则返回None，否则如果服务器返回json信息则返回dict类型，键值对类型分别为string, unicode string类型，否则返回空的dict
        :return: ResponseInfo: 响应的具体信息，UCloud UFile 服务器返回信息或者网络链接异常
        """
        bucket = self._get_bucket(bucket)

        return super().download_file(bucket,
                                     key,
                                     localfile,
                                     isprivate=isprivate,
                                     content_range=content_range,
                                     header=header)


class KS3Helper():
    """
    :description: 金山云存储二次封装
    :last_editors: ChenXiaolei
    """
    ACCESS_KEY = ''
    SECRET_KEY = ''
    REGION_ENDPOINT = ""

    def __init__(self, access_key, secret_key, host):
        from ks3.connection import Connection
        self.ACCESS_KEY = access_key
        self.SECRET_KEY = secret_key
        self.HOST = host
        self.KS3_CONNECTION = Connection(self.ACCESS_KEY,
                                         self.SECRET_KEY,
                                         host=self.HOST,
                                         is_secure=False,
                                         domain_mode=False)

    def get_file_info(self, bucket_name, key_name):
        """
        :Description: 获取文件信息
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 文件信息  异常返回None
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)
        try:
            key_info = bucket.get_key(key_name)
            return key_info
        except:
            raise

    def get_file_contents(self, bucket_name, key_name):
        """
        :Description: 获取指定文件的字符串内容
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 文件字符串内容
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)
        try:
            key = bucket.get_key(key_name)
            contents = key.get_contents_as_string().decode()
            print(contents)
            return contents
        except:
            raise

    def save_file(self, bucket_name, key_name, saved_file_path):
        """
        :Description: 保存指定存储文件到本地
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :param saved_file_path: 保存文件的本地路径
        :return 成功返回True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)
        try:
            key = bucket.get_key(key_name)
            contents = key.get_contents_to_filename(saved_file_path)
            print(contents)
            return True
        except:
            raise

    def put_file_from_file_path(self,
                                bucket_name,
                                key_name,
                                source_file_path,
                                policy="public-read"):
        """
        :Description: 
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :param source_file_contents: 本地文件路径
        #param policy: 文件政策 私有:'private'   公共读:'public-read'
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            bucket = self.__get_bucket(bucket_name)
            key = bucket.new_key(key_name)
            ret = key.set_contents_from_filename(source_file_path,
                                                 policy=policy)
            if ret and ret.status == 200:
                print("金山存储文件上传成功")
                return True
        except:
            raise

        return False

    def put_file_from_contents(self,
                               bucket_name,
                               key_name,
                               source_file_contents,
                               policy="public-read"):
        """
        :Description: 通过文件流上传文件
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :param source_file_contents: 文件流字符串
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        try:
            bucket = self.__get_bucket(bucket_name)
            key = bucket.new_key(key_name)
            ret = key.set_contents_from_string(source_file_contents,
                                               policy=policy)
            if ret and ret.status == 200:
                print("金山存储文件上传成功")
                return True
        except:
            raise
        return False

    def del_file(
        self,
        bucket_name,
        key_name,
    ):
        """
        :Description: 删除文件
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            bucket = self.__get_bucket(bucket_name)
            bucket.delete_key(key_name)
            return True
        except:
            raise

    def multi_put_file(self,
                       bucket_name,
                       key_name,
                       source_file_path,
                       thread_num=5,
                       retry_times=3):
        """
        :Description: 分片上传
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :param source_file_path: 本地文件路径
        :param thread_num: 线程数量
        :param retry_times: 重试次数
        :return 成功返回True 异常抛出异常
        :last_editors: ChenXiaolei
        """
        import math
        import threadpool

        bucket = self.__get_bucket(bucket_name)
        f_size = os.stat(source_file_path).st_size
        mp = bucket.initiate_multipart_upload(key_name)
        if not mp:
            raise RuntimeError("%s init multiupload error" % key_name)
        print(f"{key_name} begin multipart upload,uploadid={mp.id}")
        chunk_size = 104857600
        chunk_count = int(math.ceil(f_size / float(chunk_size)))
        pool_args_list = []
        try:
            for i in range(chunk_count):
                offset = chunk_size * i
                bs = min(chunk_size, f_size - offset)
                part_num = i + 1
                pool_args_list.append(([
                    mp, source_file_path, key_name, offset, bs, part_num,
                    retry_times
                ], None))
            pool = threadpool.ThreadPool(thread_num)
            requests = threadpool.makeRequests(self.__upload_part_task,
                                               pool_args_list)
            [pool.putRequest(req) for req in requests]
            pool.wait()
            if len(multi_task_result) != chunk_count:
                raise RuntimeError(
                    "%s part miss,expect=%d,actual=%d" %
                    (key_name, chunk_count, len(multi_task_result)))
            for item in multi_task_result.keys():
                if not multi_task_result[item]:
                    raise RuntimeError("%s part upload has fail" % key_name)
            mp.complete_upload()
            print(f"{key_name} multipart upload success")
            return True
        except:
            print(f"{key_name} multipart upload fail")
            if mp:
                mp.cancel_upload()
            return False

    def __upload_part_task(self, mp, source_file_path, key_name, offset,
                           chunk_size, part_num, retry_times):
        """
        :Description: 分片上传任务
        :last_editors: ChenXiaolei
        """
        from filechunkio import FileChunkIO
        global multi_task_result
        multi_task_result = {}
        cur_task_ret = False
        try:
            for i in range(retry_times):
                try:
                    with FileChunkIO(source_file_path,
                                     'rb',
                                     offset=offset,
                                     bytes=chunk_size) as fp:
                        mp.upload_part_from_file(fp, part_num=part_num)
                    cur_task_ret = True
                    print(f"{key_name} part {part_num} upload success")
                    break
                except:
                    print(
                        f"{key_name} part {part_num} fail,uploadid={mp.id},error={traceback.format_exc()}"
                    )
                    if i + 1 >= retry_times:
                        print(f"{key_name} part {part_num} upload fail")
                        raise

        except:
            cur_task_ret = False
        finally:
            multi_task_result[part_num] = cur_task_ret

    def get_bucket_objects(self, bucket_name, prefix=None):
        """
        :Description: 列举Bucket内的文件或者目录
        :param bucket_name: bucket名称
        :param prefix: 指定前缀
        :return: 文件列表，目录列表
        :last_editors: ChenXiaolei
        """
        from ks3.prefix import Prefix
        from ks3.key import Key

        result_list = []
        result_dir = []

        try:
            bucket = self.__get_bucket(bucket_name)
            if prefix and prefix != "":
                keys = bucket.list(prefix=prefix)
            else:
                keys = bucket.list(delimiter='/')
            for key in keys:
                if isinstance(key, Key):
                    result_list.append(key.name)
                elif isinstance(key, Prefix):
                    result_dir.append(key.name)
        except:
            raise

        return result_list, result_dir

    def __get_bucket(self, bucket_name):
        """
        :Description: 获取bucket
        :param bucket_name: bucket名称
        :return bucket对象
        :last_editors: ChenXiaolei
        """
        return self.KS3_CONNECTION.get_bucket(bucket_name)


class OSS2Helper():
    """
    文件上传方法中的data参数
    ------------------------
    诸如 :func:`put_object <Bucket.put_object>` 这样的上传接口都会有 `data` 参数用于接收用户数据。`data` 可以是下述类型
        - unicode类型（对于Python3则是str类型）：内部会自动转换为UTF-8的bytes
        - bytes类型：不做任何转换
        - file-like object：对于可以seek和tell的file object，从当前位置读取直到结束。其他类型，请确保当前位置是文件开始。
        - 可迭代类型：对于无法探知长度的数据，要求一定是可迭代的。此时会通过Chunked Encoding传输。

    Bucket配置修改方法中的input参数
    -----------------------------
    诸如 :func:`put_bucket_cors <Bucket.put_bucket_cors>` 这样的Bucket配置修改接口都会有 `input` 参数接收用户提供的配置数据。
    `input` 可以是下述类型
    - Bucket配置信息相关的类，如 `BucketCors`
    - unicode类型（对于Python3则是str类型）
    - 经过utf-8编码的bytes类型
    - file-like object
    - 可迭代类型，会通过Chunked Encoding传输
    也就是说 `input` 参数可以比 `data` 参数多接受第一种类型的输入。

    返回值
    ------
    :class:`Service` 和 :class:`Bucket` 类的大多数方法都是返回 :class:`RequestResult <oss2.models.RequestResult>`
    及其子类。`RequestResult` 包含了HTTP响应的状态码、头部以及OSS Request ID，而它的子类则包含用户真正想要的结果。例如，
    `ListBucketsResult.buckets` 就是返回的Bucket信息列表；`GetObjectResult` 则是一个file-like object，可以调用 `read()` 来获取响应的
    HTTP包体。

    :class:`CryptoBucket`:
    加密接口
    -------
    CryptoBucket仅提供上传下载加密数据的接口，诸如`get_object` 、 `put_object` ，返回值与Bucket相应接口一致。


    异常
    ----
    一般来说Python SDK可能会抛出三种类型的异常，这些异常都继承于 :class:`OssError <oss2.exceptions.OssError>` ：
        - :class:`ClientError <oss2.exceptions.ClientError>` ：由于用户参数错误而引发的异常；
        - :class:`ServerError <oss2.exceptions.ServerError>` 及其子类：OSS服务器返回非成功的状态码，如4xx或5xx；
        - :class:`RequestError <oss2.exceptions.RequestError>` ：底层requests库抛出的异常，如DNS解析错误，超时等；
    当然，`Bucket.put_object_from_file` 和 `Bucket.get_object_to_file` 这类函数还会抛出文件相关的异常。


    .. _byte_range:

    指定下载范围
    ------------
    诸如 :func:`get_object <Bucket.get_object>` 以及 :func:`upload_part_copy <Bucket.upload_part_copy>` 这样的函数，可以接受
    `byte_range` 参数，表明读取数据的范围。该参数是一个二元tuple：(start, last)。这些接口会把它转换为Range头部的值，如：
        - byte_range 为 (0, 99) 转换为 'bytes=0-99'，表示读取前100个字节
        - byte_range 为 (None, 99) 转换为 'bytes=-99'，表示读取最后99个字节
        - byte_range 为 (100, None) 转换为 'bytes=100-'，表示读取第101个字节到文件结尾的部分（包含第101个字节）


    分页罗列
    -------
    罗列各种资源的接口，如 :func:`list_buckets <Service.list_buckets>` 、 :func:`list_objects <Bucket.list_objects>` 都支持
    分页查询。通过设定分页标记（如：`marker` 、 `key_marker` ）的方式可以指定查询某一页。首次调用将分页标记设为空（缺省值，可以不设），
    后续的调用使用返回值中的 `next_marker` 、 `next_key_marker` 等。每次调用后检查返回值中的 `is_truncated` ，其值为 `False` 说明
    已经到了最后一页。

    .. _line_range:

    指定查询CSV文件范围
    ------------
    诸如 :func:`select_object <Bucket.select_object>` 以及 :func:`select_object_to_file <Bucket.select_object_to_file>` 这样的函数的select_csv_params参数，可以接受
    `LineRange` 参数，表明读取CSV数据的范围。该参数是一个二元tuple：(start, last):
        - LineRange 为 (0, 99) 表示读取前100行
        - LineRange 为 (None, 99) 表示读取最后99行
        - LineRange 为 (100, None) 表示读取第101行到文件结尾的部分（包含第101行）

    .. _split_range:

    指定查询CSV文件范围
    ------------
    split可以认为是切分好的大小大致相等的csv行簇。每个Split大小大致相等，这样以便更好的做到负载均衡。
    诸如 :func:`select_object <Bucket.select_object>` 以及 :func:`select_object_to_file <Bucket.select_object_to_file>` 这样的函数的select_csv_params参数，可以接受
    `SplitRange` 参数，表明读取CSV数据的范围。该参数是一个二元tuple：(start, last):
        - SplitRange 为 (0, 9) 表示读取前10个Split
        - SplitRange 为 (None, 9) 表示读取最后9个split
        - SplitRange 为 (10, None) 表示读取第11个split到文件结尾的部分（包含第11个Split）

    分页查询
    -------
    和create_csv_object_meta配合使用，有两种方法：
        - 方法1：先获取文件总的行数(create_csv_object_meta返回)，然后把文件以line_range分成若干部分并行查询
        - 方法2：先获取文件总的Split数(create_csv_object_meta返回), 然后把文件分成若干个请求，每个请求含有大致相等的Split

    .. _progress_callback:

    上传下载进度
    -----------
    上传下载接口，诸如 `get_object` 、 `put_object` 、`resumable_upload`，都支持进度回调函数，可以用它实现进度条等功能。

    `progress_callback` 的函数原型如下 ::

        def progress_callback(bytes_consumed, total_bytes):
            '''进度回调函数。

            :param int bytes_consumed: 已经消费的字节数。对于上传，就是已经上传的量；对于下载，就是已经下载的量。
            :param int total_bytes: 总长度。
            '''

    其中 `total_bytes` 对于上传和下载有不同的含义：
        - 上传：当输入是bytes或可以seek/tell的文件对象，那么它的值就是总的字节数；否则，其值为None
        - 下载：当返回的HTTP相应中有Content-Length头部，那么它的值就是Content-Length的值；否则，其值为None


    .. _unix_time:

    Unix Time
    ---------
    OSS Python SDK会把从服务器获得时间戳都转换为自1970年1月1日UTC零点以来的秒数，即Unix Time。
    参见 `Unix Time <https://en.wikipedia.org/wiki/Unix_time>`_

    OSS中常用的时间格式有
        - HTTP Date格式，形如 `Sat, 05 Dec 2015 11:04:39 GMT` 这样的GMT时间。
        用在If-Modified-Since、Last-Modified这些HTTP请求、响应头里。
        - ISO8601格式，形如 `2015-12-05T00:00:00.000Z`。
        用在生命周期管理配置、列举Bucket结果中的创建时间、列举文件结果中的最后修改时间等处。

    `http_date` 函数把Unix Time转换为HTTP Date；而 `http_to_unixtime` 则做相反的转换。如 ::

        >>> import oss2, time
        >>> unix_time = int(time.time())             # 当前UNIX Time，设其值为 1449313829
        >>> date_str = oss2.http_date(unix_time)     # 得到 'Sat, 05 Dec 2015 11:10:29 GMT'
        >>> oss2.http_to_unixtime(date_str)          # 得到 1449313829

    .. note::

        生成HTTP协议所需的日期（即HTTP Date）时，请使用 `http_date` ， 不要使用 `strftime` 这样的函数。因为后者是和locale相关的。
        比如，`strftime` 结果中可能会出现中文，而这样的格式，OSS服务器是不能识别的。

    `iso8601_to_unixtime` 把ISO8601格式转换为Unix Time；`date_to_iso8601` 和 `iso8601_to_date` 则在ISO8601格式的字符串和
    datetime.date之间相互转换。如 ::

        >>> import oss2
        >>> d = oss2.iso8601_to_date('2015-12-05T00:00:00.000Z')  # 得到 datetime.date(2015, 12, 5)
        >>> date_str = oss2.date_to_iso8601(d)                    # 得到 '2015-12-05T00:00:00.000Z'
        >>> oss2.iso8601_to_unixtime(date_str)                    # 得到 1449273600

    .. _select_params:

        指定OSS Select的文件格式。
        对于Csv文件，支持如下Keys:
        >>> CsvHeaderInfo: None|Use|Ignore   #None表示没有CSV Schema头，Use表示启用CSV Schema头，可以在Select语句中使用Name，Ignore表示有CSV Schema头，但忽略它（Select语句中不可以使用Name)
                            默认值是None
        >>> CommentCharacter: Comment字符,默认值是#,不支持多个字符
        >>> RecordDelimiter: 行分隔符，默认是\n,最多支持两个字符分隔符（比如:\r\n)
        >>> FieldDelimiter: 列分隔符，默认是逗号(,), 不支持多个字符
        >>> QuoteCharacter: 列Quote字符，默认是双引号("),不支持多个字符。注意转义符合Quote字符相同。
        >>> LineRange: 指定查询CSV文件的行范围，参见 `line_range`。
        >>> SplitRange: 指定查询CSV文件的Split范围，参见 `split_range`.
            注意LineRange和SplitRange两种不能同时指定。若同时指定LineRange会被忽略。
        >>> CompressionType: 文件的压缩格式，默认值是None, 支持GZIP。
        >>> OutputRawData: 指定是响应Body返回Raw数据，默认值是False.
        >>> SkipPartialDataRecord: 当CSV行数据不完整时(select语句中出现的列在该行为空)，是否跳过该行。默认是False。
        >>> OutputHeader:是否输出CSV Header，默认是False.
        >>> EnablePayloadCrc:是否启用对Payload的CRC校验,默认是False. 该选项不能和OutputRawData:True混用。
        >>> MaxSkippedRecordsAllowed: 允许跳过的最大行数。默认值是0表示一旦有一行跳过就报错。当下列两种情况下该行CSV被跳过:1）当SkipPartialDataRecord为True时且该行不完整时 2）当该行的数据类型和SQL不匹配时
        对于Json 文件, 支持如下Keys:
        >>> Json_Type: DOCUMENT | LINES . DOCUMENT就是指一般的Json文件，LINES是指每一行是一个合法的JSON对象，文件由多行Json对象组成，整个文件本身不是合法的Json对象。
        >>> LineRange: 指定查询JSON LINE文件的行范围，参见 `line_range`。注意该参数仅支持LINES类型
        >>> SplitRange: 指定查询JSON LINE文件的Split范围，参见 `split_range`.注意该参数仅支持LINES类型
        >>> CompressionType: 文件的压缩格式，默认值是None, 支持GZIP。
        >>> OutputRawData: 指定是响应Body返回Raw数据，默认值是False. 
        >>> SkipPartialDataRecord: 当一条JSON记录数据不完整时(select语句中出现的Key在该对象为空)，是否跳过该Json记录。默认是False。
        >>> EnablePayloadCrc:是否启用对Payload的CRC校验,默认是False. 该选项不能和OutputRawData:True混用。
        >>> MaxSkippedRecordsAllowed: 允许跳过的最大Json记录数。默认值是0表示一旦有一条Json记录跳过就报错。当下列两种情况下该JSON被跳过:1）当SkipPartialDataRecord为True时且该条Json记录不完整时 2）当该记录的数据类型和SQL不匹配时
        >>> ParseJsonNumberAsString: 将Json文件中的数字解析成字符串。使用场景是当Json文件中的浮点数精度较高时，系统默认的浮点数精度无法达到要求，当解析成字符串时将完整保留原始数据精度，在Sql中使用Cast可以将字符串无精度损失地转成decimal.
        >>> AllowQuotedRecordDelimiter: 允许CSV中的列包含转义过的换行符。默认为true。当值为False时，select API可以用Range：bytes来设置选取目标对象内容的范围
        ‘
    .. _select_meta_params:

        create_select_object_meta参数集合，支持如下Keys:
        - RecordDelimiter: CSV换行符，最多支持两个字符
        - FieldDelimiter: CSV列分隔符，最多支持一个字符
        - QuoteCharacter: CSV转移Quote符，最多支持一个字符
        - OverwriteIfExists: true|false. true表示重新获得csv meta，并覆盖原有的meta。一般情况下不需要使用

    """
    ACCESS_KEY_ID = ""
    ACCESS_KEY_SECRET = ""
    END_POINT = ""

    def __init__(self, access_key_id, access_key_secret, end_point):
        import oss2
        self.ACCESS_KEY_ID = access_key_id
        self.ACCESS_KEY_SECRET = access_key_secret
        self.END_POINT = end_point

        self.AUTH = oss2.Auth(self.ACCESS_KEY_ID, self.ACCESS_KEY_SECRET)

    def __get_bucket(self, bucket_name):
        import oss2
        return oss2.Bucket(self.AUTH, self.END_POINT, bucket_name)

    def get_file_info(self, bucket_name, object_name):
        """
        :description: 获取文件信息
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 成功返回对象信息 失败则抛出异常
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)

        try:
            object_info = bucket.get_object_meta(object_name)
            return object_info
        except:
            raise

    def get_file_stream(self, bucket_name, object_name):
        bucket = self.__get_bucket(bucket_name)

        try:
            object_stream = bucket.get_object('<yourObjectName>')

            if object_stream.client_crc != object_stream.server_crc:
                raise Exception(
                    "The CRC checksum between client and server is inconsistent!"
                )
            return object_stream
        except:
            raise

    def save_file(self, bucket_name, object_name, local_file):
        """
        :description: 将指定的OSS文件下载到本地文件
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :param local_file: 由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        :return 成功返回True 如果文件不存在，则抛出 :class:`NoSuchKey <oss2.exceptions.NoSuchKey>` ；还可能抛出其他异常
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)

        try:
            bucket.get_object_to_file(object_name, local_file)

            return True
        except:
            raise

    def put_file_from_file_path(self, bucket_name, object_name, local_file):
        """
        :description: 
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功 True 其他:class:`PutObjectResult <oss2.models.PutObjectResult>`
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)

        try:
            bucket.put_object_from_file(object_name, local_file)
            return True
        except:
            raise

    def put_file(self, bucket_name, object_name, source_file_object):
        """
        :description: 
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param source_file_object: 上传文件对象 支持字符串/byte/unicode/网络流
        :return 成功 True 其他:class:`PutObjectResult <oss2.models.PutObjectResult>`
        :last_editors: ChenXiaolei
        """
        bucket = self.__get_bucket(bucket_name)

        try:
            # 上传文件。
            # 如果需要上传文件时设置文件存储类型（x-oss-storage-class）与访问权限（x-oss-object-acl），请在put_object中设置相关Header，示例如下。
            # headers = dict()
            # headers["x-oss-storage-class"] = "Standard"
            # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
            # 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
            # result = bucket.put_object('<yourObjectName>', 'content of object', headers=headers)
            result = bucket.put_object(object_name, source_file_object)

            # HTTP返回码。
            print('http status: {0}'.format(result.status))
            # 请求ID。请求ID是请求的唯一标识，强烈建议在程序日志中添加此参数。
            print('request_id: {0}'.format(result.request_id))
            # ETag是put_object方法返回值特有的属性，用于标识一个Object的内容。
            print('ETag: {0}'.format(result.etag))
            # HTTP响应头部。
            print('date: {0}'.format(result.headers['date']))
            if result.status == 200:
                return True
            else:
                return False
        except:
            raise

    def del_file(
        self,
        bucket_name,
        object_name,
    ):
        """
        :Description: 删除文件
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            bucket = self.__get_bucket(bucket_name)
            bucket.delete_object(object_name)
            return True
        except:
            raise

    def multi_put_file(self, bucket_name, object_name, local_file):
        """
        :description: 分片上传,自动计算分片
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        import os
        from oss2 import SizedFileAdapter, determine_part_size
        from oss2.models import PartInfo

        bucket = self.__get_bucket(bucket_name)

        try:
            total_size = os.path.getsize(local_file)
            # determine_part_size方法用于确定分片大小。
            part_size = determine_part_size(total_size,
                                            preferred_size=100 * 1024)

            # 初始化分片。
            # 如需在初始化分片时设置文件存储类型，请在init_multipart_upload中设置相关headers，参考如下。
            # headers = dict()
            # headers["x-oss-storage-class"] = "Standard"
            # upload_id = bucket.init_multipart_upload(key, headers=headers).upload_id
            upload_id = bucket.init_multipart_upload(object_name).upload_id
            parts = []

            # 逐个上传分片。
            with open(local_file, 'rb') as fileobj:
                part_number = 1
                offset = 0
                while offset < total_size:
                    num_to_upload = min(part_size, total_size - offset)
                    # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                    result = bucket.upload_part(
                        object_name, upload_id, part_number,
                        SizedFileAdapter(fileobj, num_to_upload))
                    parts.append(PartInfo(part_number, result.etag))

                    offset += num_to_upload
                    part_number += 1

            # 完成分片上传。
            # 如需在完成分片上传时设置文件访问权限ACL，请在complete_multipart_upload函数中设置相关headers，参考如下。
            # headers = dict()
            # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
            # bucket.complete_multipart_upload(key, upload_id, parts, headers=headers)
            bucket.complete_multipart_upload(object_name, upload_id, parts)

            # 验证分片上传。
            with open(local_file, 'rb') as fileobj:
                assert bucket.get_object(object_name).read() == fileobj.read()
        except:
            raise

        return True

    def get_bucket_objects(self, bucket_name, prefix='', delimiter=''):
        """
        :description: 列举bucket下的文件和文件夹信息
        :param bucket_name: bucket名称
        :param prefix: bucket目录 例如"fun/"
        :param delimiter: 对文件名称进行分组的字符 例如"/"
        :return 文件列表，目录列表
        :last_editors: ChenXiaolei
        """
        import oss2

        bucket = self.__get_bucket(bucket_name)

        objects = []
        dirs = []

        try:
            for obj in oss2.ObjectIteratorV2(bucket,
                                             prefix=prefix,
                                             delimiter=delimiter):
                # 判断obj为文件夹。
                if obj.is_prefix():
                    dirs.append(obj)
                # 判断obj为文件。
                else:
                    objects.append(obj)
        except:
            raise

        return objects, dirs


class COSHelper():
    """
    :description: 腾讯云对象存储帮助类
    :last_editors: ChenXiaolei
    """
    SECRET_ID = ""
    SECRET_KEY = ""
    REGION = ""

    def __init__(self, secret_id, secret_key, region, **other_config):
        """
        :description: 腾讯云对象存储(COS)初始化
        :param Appid(string): 用户APPID.
        :param Region(string): 地域信息.
        :param SecretId(string): 秘钥SecretId.
        :param SecretKey(string): 秘钥SecretKey.
        :param Token(string): 临时秘钥使用的token.
        :param Scheme(string): http/https
        :param Timeout(int): http超时时间.
        :param Access_id(string): 秘钥AccessId(兼容).
        :param Access_key(string): 秘钥AccessKey(兼容).
        :param Secret_id(string): 秘钥SecretId(兼容).
        :param Secret_key(string): 秘钥SecretKey(兼容).
        :param Endpoint(string): endpoint.
        :param IP(string): 访问COS的ip
        :param Port(int):  访问COS的port
        :param Anonymous(bool):  是否使用匿名访问COS
        :param UA(string):  使用自定义的UA来访问COS
        :param Proxies(dict):  使用代理来访问COS
        :param Domain(string):  使用自定义的域名来访问COS
        :param ServiceDomain(string):  使用自定义的域名来访问cos service
        :param PoolConnections(int):  连接池个数
        :param PoolMaxSize(int):      连接池中最大连接数
        :last_editors: ChenXiaolei
        """
        from qcloud_cos import CosConfig
        from qcloud_cos import CosS3Client
        self.SECRET_ID = secret_id
        self.SECRET_KEY = secret_key
        self.REGION = region

        self.COS_CONFIG = CosConfig(Region=region,
                                    SecretId=secret_id,
                                    SecretKey=secret_key,
                                    **other_config)
        self.COS_CLIENT = CosS3Client(self.COS_CONFIG)

    def get_file_info(self, bucket_name, object_name):
        """
        :description: 获取对象信息
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 成功返回对象信息 失败则抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            return self.COS_CLIENT.head_object(bucket_name, object_name)
        except:
            raise

    def get_object(self, bucket_name, object_name):
        """
        :description: 获取对象数据流
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 对象数据流
        :last_editors: ChenXiaolei
        """
        try:
            return self.COS_CLIENT.get_object(bucket_name, object_name)
        except:
            raise

    def save_file(self, bucket_name, object_name, local_file):
        """
        :description: 将指定的OSS文件下载到本地文件
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :param local_file: 由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        :return 成功返回True 如果文件不存在，则抛出异常
        :last_editors: ChenXiaolei
        """

        try:
            response = self.get_object(bucket_name, object_name)

            response['Body'].get_stream_to_file(local_file)

            return True
        except:
            raise

    def put_file_from_file_path(self, bucket_name, object_name, local_file):
        """
        :description: 通过文件路径上传文件
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功 True 异常抛出异常
        :last_editors: ChenXiaolei
        """
        with open(local_file, 'rb') as file_byte:
            file_bytes = file_byte.read()

        return self.put_file(bucket_name, object_name, file_bytes)

    def put_file(self, bucket_name, object_name, source_file_object):
        """
        :description: 上传文件
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param source_file_object: 上传文件对象
        :return 成功 True 其他异常
        :last_editors: ChenXiaolei
        """
        try:
            self.COS_CLIENT.put_object(bucket_name, source_file_object,
                                       object_name)

            return True
        except:
            raise

    def del_file(
        self,
        bucket_name,
        object_name,
    ):
        """
        :Description: 删除文件
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            self.COS_CLIENT.delete_object(bucket_name, object_name)
            return True
        except:
            raise

    def multi_put_file(self, bucket_name, object_name, local_file):
        """
        :description: 分片上传,自动计算分片
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """

        try:
            self.COS_CLIENT.upload_file(bucket_name, object_name, local_file)
        except:
            raise

        return True

    def get_bucket_objects(self, bucket_name, prefix="", delimiter=""):
        """
        :description: 列举bucket下的文件和文件夹信息
        :param bucket_name: bucket名称
        :param prefix: bucket目录 例如"fun/"
        :param delimiter: 对文件名称进行分组的字符 例如"/"
        :return 文件列表，目录列表
        :last_editors: ChenXiaolei
        """

        objects = []
        dirs = []

        try:
            object_list = self.COS_CLIENT.list_objects(bucket_name,
                                                       Prefix=prefix,
                                                       Delimiter=delimiter)

            if not object_list or "Contents" not in object_list or len(
                    object_list["Contents"]) == 0:
                return objects, dirs
            for obj in object_list["Contents"]:
                if obj["Key"].find('/') > -1 and obj["Key"].split(
                        '/')[::2] not in dirs:
                    dirs.append(obj["Key"].split('/')[::2])

                objects.append(obj)
        except:
            raise

        return objects, dirs


class BOSHelper():
    """
    :description: 百度云存储
    :last_editors: ChenXiaolei
    """
    BOS_HOST = ""
    ACCESS_KEY_ID = ""
    SECRET_ACCESS_KEY = ""

    def __init__(self, access_key_id, secret_access_key, bos_host="bj.bcebos.com", bos_media_host="http://media.bj.baidubce.com", **other_config):
        """
        :description: 百度云存储(BOS)初始化
        :param access_key_id: 百度云后台密钥id
        :param secret_access_key: 百度云后台密钥key
        :param bos_host: 指定百度云存储节点host
        :last_editors: ChenXiaolei
        """
        from baidubce.bce_client_configuration import BceClientConfiguration
        from baidubce.auth.bce_credentials import BceCredentials
        from baidubce import exception
        from baidubce.services import bos
        from baidubce.services.bos import canned_acl
        from baidubce.services.bos.bos_client import BosClient
        from baidubce.services import media
        from baidubce.services.media.media_client import MediaClient

        # 创建BceClientConfiguration
        self.bos_config = BceClientConfiguration(credentials=BceCredentials(
            access_key_id, secret_access_key), endpoint=bos_host, **other_config)
        # 创建BOS客户端
        self.bos_client = BosClient(self.bos_config)

        self.bos_media_config = BceClientConfiguration(credentials=BceCredentials(
            access_key_id, secret_access_key), endpoint=bos_media_host, **other_config)
        self.bos_media_client = MediaClient(self.bos_media_config)

    def get_file_info(self, bucket_name, object_name):
        """
        :description: 获取对象信息
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 成功返回对象信息 失败则抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            return self.bos_client.get_object_meta_data(bucket_name=bucket_name, key=object_name)
        except:
            raise

    def get_object(self, bucket_name, object_name):
        """
        :description: 获取对象数据流
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 对象数据流
        :last_editors: ChenXiaolei
        """
        try:
            return self.bos_client.get_object(bucket_name, object_name)
        except:
            raise

    def save_file(self, bucket_name, object_name, local_file):
        """
        :description: 将指定的OSS文件下载到本地文件
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :param local_file: 由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        :return HTTP Response
        :last_editors: ChenXiaolei
        """

        try:
            return self.bos_client.get_object_to_file(bucket_name, object_name, local_file)
        except:
            raise

    def put_file_from_file_path(self, bucket_name, object_name, local_file):
        """
        :description: 通过文件路径上传文件
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功 True 异常抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            self.bos_client.put_object_from_file(
                bucket_name, object_name, local_file)

            return True
        except:
            raise

    def put_file(self, bucket_name, object_name, source_file_object):
        """
        :description: 
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param source_file_object: 上传文件对象
        :return 成功 True 其他异常
        :last_editors: ChenXiaolei
        """
        try:
            self.bos_client.put_object_from_string(
                bucket_name, object_name, source_file_object)

            return True
        except:
            raise

    def put_file_stream(self, bucket_name, object_name, data, content_length, content_md5):
        """
        :description: 以数据流形式上传Object
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param data: file stream
        :param content_length: 对象MD5值,计算方法是对数据执行md5算法获取128位二进制数据
        :param content_md5: 对象MD5值
        :return 成功 True 其他异常
        :last_editors: ChenXiaolei
        """
        try:
            self.bos_client.put_object(
                bucket_name, object_name, data, content_length, content_md5)

            return True
        except:
            raise

    def del_file(
        self,
        bucket_name,
        object_name,
    ):
        """
        :Description: 删除文件
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            self.bos_client.delete_object(bucket_name, object_name)
            return True
        except:
            raise

    def multi_put_file(self, bucket_name, object_name, local_file, chunk_size=5, thread_num=multiprocessing.cpu_count()):
        """
        :description: 分片上传,自动计算分片
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """

        try:
            self.bos_client.put_super_obejct_from_file(
                bucket_name, object_name, local_file, chunk_size=chunk_size, thread_num=thread_num)
        except:
            raise

        return True

    def get_bucket_objects(self, bucket_name, prefix="", delimiter=""):
        """
        :description: 列举bucket下的文件和文件夹信息
        :param bucket_name: bucket名称
        :param prefix: bucket目录 例如"fun/"
        :param delimiter: 对文件名称进行分组的字符 例如"/"
        :return 文件列表，目录列表
        :last_editors: ChenXiaolei
        """

        objects = []
        dirs = []

        try:
            object_list = self.bos_client.list_objects(bucket_name,
                                                       prefix=prefix,
                                                       delimiter=delimiter)

            if not object_list or not hasattr(object_list, "contents") or len(
                    object_list.contents) == 0:
                return objects, dirs
            for obj in object_list.contents:
                if obj.key.find('/') > -1 and obj.key.split(
                        '/')[::2] not in dirs:
                    dirs.append(obj.key.split('/')[::2])

                objects.append(obj)
        except:
            raise

        return objects, dirs

    def get_media_info(self, bucket_name, object_name):
        """
        :description: 百度云MCP音视频获取媒体信息
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :return 媒体信息
        :last_editors: ChenXiaolei
        """        
        return self.bos_media_client.get_mediainfo_of_file(bucket_name, object_name)


class LocalFileHelper():
    """
    :description: 本地文件读写操作
    :last_editors: ChenXiaolei
    """
    @classmethod
    def get_file_content(self, file_path):
        """
        :description: 获取文件内容
        :param path:文件路径
        :return 文件内容
        :last_editors: ChenXiaolei
        """
        if not file_path or not self.check_file_exists(file_path):
            return ""
        with open(file_path) as file_object:
            file_content = file_object.read()
            return file_content

    @classmethod
    def get_file_content_array(self, file_path):
        """
        :description: 获取文件内容,按行构造为数组
        :param file_path: 文件路径
        :return 文件内容按行转换后的数组
        :last_editors: ChenXiaolei
        """
        if not file_path:
            return None
        file_content = self.get_file_content(file_path)

        return self._content_array(file_content)

    @classmethod
    def _content_to_array(self, file_content):
        """
        :description: 将文件内容按行转为数组
        :param file_content:文件内容
        :return 文件内容按行转换后的数组
        :last_editors: ChenXiaolei
        """
        contents_arr_new = []

        contents_arr = str(file_content).split(']')

        for i in range(len(contents_arr)):

            if (contents_arr[i].__contains__('[')):
                index = contents_arr[i].rfind('[')
                temp_str = contents_arr[i][index + 1:]

                if temp_str.__contains__('"'):

                    contents_arr_new.append(temp_str.replace('"', ''))

        return contents_arr_new

    @classmethod
    def write_file(self, file_path, content, mode="w", encoding='utf8'):
        """
        :description: 文件写入
        :param file_path: 文件路径
        :param content: 写入内容
        :return {*}
        :last_editors: ChenXiaolei
        """
        # 打开文件
        file = open(file_path, mode, encoding=encoding)
        # 写入文件内容
        file.write(content)
        # 关闭文件
        file.close()

    @classmethod
    def check_file_exists(self, file_path):
        """
        :description: 判断文件是否存在
        :param file_path: 文件路径
        :return 存在则返回True 不存在返回False
        :last_editors: ChenXiaolei
        """
        return os.path.exists(file_path)


class S3Helper():
    """
    :description: AWS S3存储
    :last_editors: ChenXiaolei
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, **other_config):
        """
        :description: AWS存储(BOS)初始化
        :param access_key_id: AWS S后台密钥id
        :param secret_access_key: AWS S3后台密钥key
        :param region_name: 指定AWS S3存储节点host
        :last_editors: ChenXiaolei
        """
        import boto3
        session = boto3.session.Session(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=region_name)
        self.s3_resource = session.resource('s3')
        self.s3_client = session.client('s3')

    def get_file_info(self, bucket_name, object_name):
        """
        :description: 获取对象信息
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 成功返回对象信息 失败则抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            return self.s3_client.get_object(Bucket=bucket_name, Key=object_name)
        except:
            raise

    def get_object(self, bucket_name, object_name):
        """
        :description: 获取对象数据流
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :return 对象数据流
        :last_editors: ChenXiaolei
        """
        try:
            return self.s3_client.download_fileobj(bucket_name, object_name)
        except:
            raise

    def save_file(self, bucket_name, object_name, local_file):
        """
        :description: 将指定的OSS文件下载到本地文件
        :param bucket_name: bucket名称
        :param object_name: 表示下载的OSS文件的完整名称，即包含文件后缀在内的完整路径，例如abc/efg/123.jpg
        :param local_file: 由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        :return HTTP Response
        :last_editors: ChenXiaolei
        """

        try:
            return self.s3_client.download_file(bucket_name, object_name, local_file)
        except:
            raise

    def put_file_from_file_path(self, bucket_name, object_name, local_file):
        """
        :description: 通过文件路径上传文件
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
        :return 成功 True 异常抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            self.s3_client.upload_file(
                Bucket=bucket_name, Key=object_name, Filename=local_file)

            return True
        except:
            raise

    def put_file(self, bucket_name, object_name, source_file_object):
        """
        :description: 
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param source_file_object: 上传文件对象
        :return 成功 True 其他异常
        :last_editors: ChenXiaolei
        """
        try:
            self.s3_client.upload_file(
                Bucket=bucket_name, Key=object_name, Filename=source_file_object)

            return True
        except:
            raise

    def put_file_stream(self, bucket_name, object_name, data):
        """
        :description: 以数据流形式上传Object
        :param bucket_name: bucket名称
        :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
        :param data: file stream
        :param content_length: 对象MD5值,计算方法是对数据执行md5算法获取128位二进制数据
        :param content_md5: 对象MD5值
        :return 成功 True 其他异常
        :last_editors: ChenXiaolei
        """
        try:
            self.s3_client.upload_fileobj(
                Bucket=bucket_name, Key=object_name, Body=data)

            return True
        except:
            raise

    def del_file(
        self,
        bucket_name,
        object_name,
    ):
        """
        :Description: 删除文件
        :param bucket_name: bucket名称
        :param key_name: 存储对象名称
        :return 成功True 失败抛出异常
        :last_editors: ChenXiaolei
        """
        try:
            self.s3_client.delete_object(bucket_name, object_name)
            return True
        except:
            raise

    # def multi_put_file(self, bucket_name, object_name, local_file, chunk_size=5, thread_num=multiprocessing.cpu_count()):
    #     """
    #     :description: 分片上传,自动计算分片
    #     :param bucket_name: bucket名称
    #     :param object_name: 表示不包含Bucket名称在内的Object的完整路径，例如example/folder/abc.jpg。
    #     :param local_file: 表示本地文件的完整路径，例如/users/local/abc.jpg。
    #     :return 成功True 失败抛出异常
    #     :last_editors: ChenXiaolei
    #     """

    #     try:
    #         self.s3_client.put_super_obejct_from_file(
    #             bucket_name, object_name, local_file, chunk_size=chunk_size, thread_num=thread_num)
    #     except:
    #         raise

    #     return True

    def get_bucket_objects(self, bucket_name, prefix="", delimiter=""):
        """
        :description: 列举bucket下的文件和文件夹信息
        :param bucket_name: bucket名称
        :param prefix: bucket目录 例如"fun/"
        :param delimiter: 对文件名称进行分组的字符 例如"/"
        :return 文件列表，目录列表
        :last_editors: ChenXiaolei
        """

        objects = []
        dirs = []

        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            if not bucket.objects.all():
                return objects, dirs
            for obj in bucket.objects.all():
                if obj.key.find('/') > -1 and obj.key.split(
                        '/')[::2] not in dirs:
                    dirs.append(obj.key.split('/')[::2])

                objects.append(obj)
        except:
            raise

        return objects, dirs