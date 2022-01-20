# -*- coding: utf-8 -*-

import time
import os
import json
import types

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_threadpool import SimpleThreadPool

from tikit.tencentcloud.common import credential
from tikit.tencentcloud.common.profile.client_profile import ClientProfile
from tikit.tencentcloud.common.profile.http_profile import HttpProfile
from tikit.tencentcloud.tione.v20211111 import tione_client
from tikit.tencentcloud.tione.v20211111 import models
from tikit.tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from .util import parse_cos_str
from .display_optimize import *

SCHEMA_INFO_VALUE_TYPES = ["TYPE_INT", "TYPE_STRING", "TYPE_BOOL", "TYPE_FLOAT"]
ANNOTATION_TYPES = ["ANNOTATION_TYPE_CLASSIFICATION",
                    "ANNOTATION_TYPE_DETECTION",
                    "ANNOTATION_TYPE_SEGMENTATION",
                    "ANNOTATION_TYPE_TRACKING",
                    "ANNOTATION_TYPE_OCR"]
ANNOTATION_FORMATS = ["ANNOTATION_FORMAT_TI",
                      "ANNOTATION_FORMAT_PASCAL",
                      "ANNOTATION_FORMAT_COCO",
                      "ANNOTATION_FORMAT_FILE"]
ALL_SUPPORT_TRAINING_MODES = ["PS_WORKER", "DDP", "MPI", "HOROVOD"]


class Client(object):
    # 临时秘钥使用，提前获取临时秘钥，避免访问的时候失败
    _secret_ahead_time = 60 * 5

    def __init__(self, secret_id=None, secret_key=None, region=None, token=None, proxies=None, tione_endpoint=None):
        """初始化，保存用户的信息

        :param secret_id:   秘钥SecretId
        :type secret_id:    str
        :param secret_key:  秘钥SecretKey
        :type secret_key:   str
        :param region:      地域信息
        :type region:       str
        :param token:       临时秘钥使用的token
        :type token:        str
        :param proxies:     使用代理来访问，内容如：{"https": "127.0.0.1:443"}.
        :type proxies:      dict
        """
        self._secret_id = secret_id
        self._secret_key = secret_key
        self._region = region if region is not None else os.getenv("REGION")
        self._token = token
        self._proxies = proxies

        self._cos_client = None
        self._tione_client = None
        # self._tione_client = tione_client.TioneClient(credential.Credential(secret_id, secret_key, token), self._region)

        self._expired_time = 0
        default_tione_enpoint = "tione.tencentcloudapi.com"
        if os.getenv("KUBERNETES_SERVICE_HOST") is not None and os.getenv("TI_INSTANCE_ID") is not None \
                and os.getenv("TI_TASK_ID") is not None:
            default_tione_enpoint = "tione.internal.tencentcloudapi.com"
        self._tione_endpoint = tione_endpoint if tione_endpoint is not None else default_tione_enpoint

        if secret_id is not None:
            self._init_client()

    def _init_client(self):
        config = CosConfig(Region=self._region, SecretId=self._secret_id, SecretKey=self._secret_key,
                           Token=self._token, Proxies=self._proxies)
        self._cos_client = CosS3Client(config)

        cred = credential.Credential(self._secret_id, self._secret_key, self._token)
        proxy = None if self._proxies is None else self._proxies.get("https", None)
        http_profile = HttpProfile(endpoint=self._tione_endpoint, proxy=proxy, keepAlive=True)
        client_profile = ClientProfile(httpProfile=http_profile)
        self._tione_client = tione_client.TioneClient(cred, self._region, client_profile)

    def _update_secret(self):
        # self._region = os.getenv("REGION")
        # # TODO 从环境变量的认证URL中获取临时认证信息
        # self._secret_id = os.getenv("SECRET_ID")
        # self._secret_key = os.getenv("SECRET_KEY")
        # self._token =
        # self._expired_time =
        raise Exception("auto authentication is not supported")

    def guarantee_valid(self):
        if self._expired_time - self._secret_ahead_time < int(time.time()):
            self._update_secret()
            self._init_client()

    def describe_cos_buckets(self):
        """列出所有bucket

        :return:    bucket列表
        :rtype:     dict
        返回的结果如：
        {
          "Owner": {
            "ID": "qcs::cam::uin/100011011262:uin/100011011262",
            "DisplayName": "100011011162"
          },
          "Buckets": {
            "Bucket": [
              {
                "Name": "bucket-58565",
                "Location": "ap-beijing-fsi",
                "CreationDate": "2021-07-21T11:06:00Z",
                "BucketType": "cos"
              },
              {
                "Name": "tai-1300158565",
                "Location": "ap-guangzhou",
                "CreationDate": "2021-10-22T11:04:40Z",
                "BucketType": "cos"
              }
            ]
          }
        }
        """
        return self._cos_client.list_buckets()

    def is_cos_dir(self, bucket, path):
        """判断目录是否为文件夹

        :param bucket:
        :type bucket:
        :param path:
        :type path:
        :return:
        :rtype:
        """
        objects = self._cos_client.list_objects(
            Bucket=bucket,
            Prefix=path.strip("/") + "/",
            MaxKeys=1
        )
        if "Contents" in objects and len(objects["Contents"]) > 0:
            return True
        return False

    def upload_to_cos(self, local_path, bucket, cos_path):
        """把本地路径下的文件或者目录上传到cos上

        :param local_path:  本地路径
        :type local_path:   str
        :param bucket:      cos上的桶
        :type bucket:       str
        :param cos_path:    cos上的路径
        :type cos_path:     str
        :return:            None. 错误信息通过 raise 给出。
        :rtype:
        """
        if not os.path.exists(local_path):
            raise Exception("local path is not exist, please check it.")

        if os.path.isfile(local_path):
            if cos_path.endswith("/"):
                cos_path = os.path.join(cos_path, os.path.basename(local_path))
            self._cos_client.upload_file(
                Bucket=bucket,
                LocalFilePath=local_path,
                Key=cos_path,
                EnableMD5=True
            )
            return

        local_path_length = len(local_path)
        if os.path.isdir(local_path):
            walk = os.walk(local_path)
            # 创建上传的线程池
            pool = SimpleThreadPool()
            base_path = cos_path
            if self.is_cos_dir(bucket, cos_path):
                base_path = os.path.join(base_path, os.path.basename(local_path))
            for path, dir_list, file_list in walk:
                pre_path = os.path.join(base_path, path[local_path_length:].strip('/'))
                for file_name in file_list:
                    src_key = os.path.join(path, file_name)
                    cos_object_key = os.path.join(pre_path, file_name).strip('/')
                    pool.add_task(self._cos_client.upload_file, bucket, cos_object_key, src_key)

            pool.wait_completion()
            result = pool.get_result()
            if not result['success_all']:
                raise Exception("failed to upload files to cos, please retry")
            return

    def describe_cos_path(self, bucket, path, maker="", max_keys=1000, encoding_type=""):
        """获取cos的目录的信息。目录下的内容最多显示1000个。要显示目录下的文件和文件夹，请以"/"结尾

        :param bucket:          cos的桶
        :type bucket:           str
        :param path:            路径
        :type path:             str
        :return:                目录信息
        :rtype:                 dict
        :param maker:           从marker开始列出条目
        :type maker:            str
        :param max_keys:        设置单次返回最大的数量,最大为1000.
        :type max_keys:         int
        :param encoding_type:   设置返回结果编码方式,只能设置为url.
        :type encoding_type:    str
        """
        return self._cos_client.list_objects(
            Bucket=bucket,
            Prefix=path,
            Delimiter="/",
            Marker=maker,
            MaxKeys=max_keys,
            EncodingType=encoding_type
        )

    def delete_cos_files(self, bucket, file_infos):
        """删除cos的一个或者多个文件

        :param bucket:
        :type bucket:
        :param file_infos:
        :type file_infos:
        :return:
        :rtype:
        """
        delete_list = []
        for file in file_infos:
            delete_list.append({"Key": file['Key']})

        response = self._cos_client.delete_objects(Bucket=bucket, Delete={"Object": delete_list})
        print(response)

    def delete_cos_path(self, bucket, delete_path):
        """删除cos目录。要删除目录下的文件和文件夹，请以"/"结尾，即：不带斜杠的，当成文件来删除；带斜杠的，当成文件夹来删除

        :param bucket:      cos的桶
        :type bucket:       str
        :param delete_path: 要删除的路径
        :type delete_path:  str
        """
        if not delete_path.endswith("/"):
            return self._cos_client.delete_object(
                Bucket=bucket,
                Key=delete_path,
            )
            return

        pool = SimpleThreadPool()
        marker = ""
        while True:
            file_infos = []
            response = self._cos_client.list_objects(Bucket=bucket, Prefix=delete_path, Marker=marker, MaxKeys=100)
            if "Contents" in response:
                contents = response.get("Contents")
                file_infos.extend(contents)
                pool.add_task(self.delete_cos_files, bucket, file_infos)
            # 列举完成，退出
            if response['IsTruncated'] == 'false':
                break

            # 列举下一页
            marker = response["NextMarker"]

        pool.wait_completion()
        result = pool.get_result()
        if not result['success_all']:
            raise Exception("failed to delete files, please retry")

    def download_from_cos(self, bucket, cos_path, local_path):
        """从cos上下载文件或者目录本地。
        注意：本地文件存在会直接覆盖。 cos_path为目录且local_path 为存在的目录的时候，cos_path的文件夹名会作为子目录保留。

        :param bucket:      cos上的桶
        :type bucket:       str
        :param cos_path:    cos上的路径
        :type cos_path:     str
        :param local_path:  本地路径
        :type local_path:   str
        :return:            None. 错误信息通过 raise 给出。
        :rtype:
        """
        file_infos = self.get_cos_sub_files(bucket, cos_path)
        # 下载文件
        if len(file_infos) == 1 and file_infos[0]["Key"] == cos_path:
            if os.path.isdir(local_path) or local_path.endswith("/"):
                local_name = os.path.join(local_path, os.path.basename(cos_path))
                self._cos_client.download_file(bucket, cos_path, local_name)
            else:
                local_dir = os.path.dirname(local_path)
                if local_dir != "" and not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                self._cos_client.download_file(bucket, cos_path, local_path)
            return

        # 下载目录
        if os.path.isfile(local_path):
            raise Exception("cannot download directory into file \"%s\"" % local_path)
        target_path = local_path
        # local_path 为存在的目录的时候
        if os.path.isdir(local_path):
            target_path = os.path.join(target_path, os.path.basename(cos_path))
        cos_path_length = len(cos_path)
        pool = SimpleThreadPool()
        for file in file_infos:
            # 文件下载 获取文件到本地
            file_cos_key = file["Key"]
            local_name = os.path.join(target_path, file_cos_key[cos_path_length:].strip('/'))

            # 如果本地目录结构不存在，递归创建
            local_dir = os.path.dirname(local_name)
            if local_dir != "" and not os.path.exists(local_dir):
                os.makedirs(local_dir)

            # skip dir, no need to download it
            if str(local_name).endswith("/"):
                continue

            # 使用线程池方式
            pool.add_task(self._cos_client.download_file, bucket, file_cos_key, local_name)

        pool.wait_completion()
        result = pool.get_result()
        if not result['success_all']:
            raise Exception("failed to download files, please retry")

    def get_cos_sub_files(self, bucket, prefix):
        """列出当前目录子节点，返回所有子节点信息

        :param bucket:
        :type bucket:
        :param prefix:
        :type prefix:
        :return:
        :rtype:
        """
        file_infos = []
        marker = ""
        while True:
            response = self._cos_client.list_objects(bucket, prefix, "", marker)
            if "Contents" in response:
                contents = response.get("Contents")
                file_infos.extend(contents)

            if "NextMarker" in response.keys():
                marker = response["NextMarker"]
            else:
                break

        sorted(file_infos, key=lambda file_info: file_info["Key"])
        # for file in file_infos:
        #     print(file)
        return file_infos

    def push_training_metrics(self, timestamp, value_map, task_id=None, epoch=None, total_steps=None, step=None):
        """上报训练自定义指标（单条）

        :param timestamp:   时间戳
        :type timestamp:    int
        :param value_map:   指标映射。 指标名称 -> 指标值
        :type value_map:    map: str -> float
        :param task_id:     任务ID。若为空，就当前取任务节点环境的 TI_TASK_ID 环境变量的值
        :type task_id:      str
        :param epoch:       epoch值
        :type epoch:        int
        :param total_steps: 总步数
        :type total_steps:  int
        :param step:        第几步
        :type step:         int
        :return:
        :rtype:             :class:`tikit.tencentcloud.tione.v20211111.models.PushTrainingMetricsResponse`

        client.push_training_metrics(int(time.time()), {"field1": 11, "field2": 12}, "task-id-00001", 3, 1000, 66)
        """
        try:
            metric = models.MetricData()
            if task_id:
                metric.TaskId = task_id
            else:
                metric.TaskId = os.getenv("TI_TASK_ID")
            if not metric.TaskId or len(metric.TaskId) == 0:
                raise TencentCloudSDKException(message="task id cannot be empty")

            metric.Timestamp = timestamp
            metric.Epoch = epoch
            metric.TotalSteps = total_steps
            metric.Step = step
            metric.Points = []
            for pair in value_map.items():
                metric.Points.append({"Name": pair[0], "Value": pair[1]})
            metric_list = [metric]
            req = models.PushTrainingMetricsRequest()
            req.Data = metric_list

            return self._tione_client.PushTrainingMetrics(req)

        except TencentCloudSDKException as err:
            raise

    def push_training_metrics_list(self, metric_list):
        """上报训练自定义指标（列表）

        :param metric_list: MetricData 数组。 若任务ID为空，就当前取任务节点环境的 TI_TASK_ID 环境变量的值
        :type metric_list:  list of :class:`tikit.tencentcloud.tione.v20211111.models.MetricData`
        :return:
        :rtype:             :class:`tikit.tencentcloud.tione.v20211111.models.PushTrainingMetricsResponse`
        """
        try:
            for i in range(len(metric_list)):
                if not metric_list[i].TaskId or len(metric_list[i].TaskId) == 0:
                    metric_list[i].TaskId = os.getenv("TI_TASK_ID")
                if not metric_list[i].TaskId or len(metric_list[i].TaskId) == 0:
                    raise TencentCloudSDKException(message="task id cannot be empty")

                if metric_list[i].Timestamp is None:
                    raise Exception("field Timestamp cannot be empty")

            req = models.PushTrainingMetricsRequest()
            req.Data = metric_list

            return self._tione_client.PushTrainingMetrics(req)

        except TencentCloudSDKException as err:
            raise

    def describe_training_metrics(self, task_id):
        """查询训练自定义指标

        :param task_id: 任务ID
        :type task_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingMetricsResponse`
        """
        try:
            req = models.DescribeTrainingMetricsRequest()
            req.TaskId = task_id
            return self._tione_client.DescribeTrainingMetrics(req)
        except TencentCloudSDKException as err:
            raise

    def describe_train_resource_groups(self, offset=0, limit=20, search_word="", tag_filters=None):
        """获取训练资源组列表

        :param offset: 偏移量，默认为0；分页查询起始位置，如：Limit为100，第一页Offset为0，第二页OffSet为100....即每页左边为开区间
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为20000；分页查询每页大小，最大20000
        :type limit: int
        :param search_word: 支持模糊查找资源组id和资源组名
        :type search_word: str
        :param tag_filters: 标签过滤
        :type tag_filters: list of tikit.tencentcloud.tione.v20211111.models.Tag
        :return:
        :rtype:    :class:`tikit.tencentcloud.tione.v20211111.models.DescribeBillingResourceGroupsResponse`
        """
        try:
            req = models.DescribeBillingResourceGroupsRequest()
            req.Type = "TRAIN"
            req.Offset = offset
            req.Limit = limit
            req.SearchWord = search_word
            req.TagFilters = tag_filters
            return self._tione_client.DescribeBillingResourceGroups(req)
        except TencentCloudSDKException as err:
            raise

    def describe_inference_resource_groups(self, offset=0, limit=20, search_word="", tag_filters=None):
        """获取推理训练组列表

        :param offset: 偏移量，默认为0；分页查询起始位置，如：Limit为100，第一页Offset为0，第二页OffSet为100....即每页左边为开区间
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为20000；分页查询每页大小，最大20000
        :type limit: int
        :param search_word: 支持模糊查找资源组id和资源组名
        :type search_word: str
        :param tag_filters: 标签过滤
        :type tag_filters: list of tikit.tencentcloud.tione.v20211111.models.Tag
        :return:
        :rtype:    :class:`tikit.tencentcloud.tione.v20211111.models.DescribeBillingResourceGroupsResponse`
        """
        try:
            req = models.DescribeBillingResourceGroupsRequest()
            req.Type = "INFERENCE"
            req.Offset = offset
            req.Limit = limit
            req.SearchWord = search_word
            req.TagFilters = tag_filters
            return self._tione_client.DescribeBillingResourceGroups(req)
        except TencentCloudSDKException as err:
            raise

    def describe_postpaid_training_price(self):
        """查询每种配置的每小时的价格，价格单位：元

        :rtype:     tikit.tencentcloud.tione.v20211111.models.DescribeBillingSpecsResponse
        """
        try:
            req = models.DescribeBillingSpecsRequest()
            req.TaskType = "TRAIN"
            req.ChargeType = "POSTPAID_BY_HOUR"
            specs = self._tione_client.DescribeBillingSpecs(req)

            price_req = models.DescribeBillingSpecsPriceRequest()
            price_req.SpecsParam = []
            for spec in specs.Specs:
                price_req.SpecsParam.append({"SpecName": spec.SpecName, "SpecCount": 1})
            price_result = self._tione_client.DescribeBillingSpecsPrice(price_req)
            for i in range(len(price_result.SpecsPrice)):
                specs.Specs[i].SpecId = str(price_result.SpecsPrice[i].RealTotalCost / 100.0)
            return specs
        except TencentCloudSDKException as err:
            raise

    def describe_training_tasks(self, filters=None, tag_filters=None, offset=0, limit=10000, order="DESC",
                                order_field="UpdateTime"):
        """获取训练任务列表

        :param filters:     过滤器，eg：[{ "Name": "TaskStatus", "Values": ["Running"] }]
        :type filters:      list of Filter
        :param tag_filters: 标签过滤器，eg：[{ "TagKey": "TagKeyA", "TagValue": ["TagValueA"] }]
        :type tag_filters:  list of TagFilter
        :param offset:      偏移量，默认为0
        :type offset:       int
        :param limit:       返回数量，默认为10000
        :type limit:        int
        :param order:       输出列表的排列顺序。取值范围：ASC：升序排列 DESC：降序排列
        :type order:        str
        :param order_field: 排序的依据字段， 取值范围 "CreateTime" "UpdateTime"
        :type order_field:  str
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingTasksResponse`
        """
        try:
            # 优化参数的显示
            req = models.DescribeTrainingTasksRequest()
            req.Filters = filters
            req.TagFilters = tag_filters
            req.Offset = offset
            req.Limit = limit
            req.Order = order
            req.OrderField = order_field
            return self._tione_client.DescribeTrainingTasks(req)
        except TencentCloudSDKException as err:
            raise

    def describe_training_task(self, task_id):
        """获取单个训练任务信息

        :param task_id: 训练任务ID
        :type task_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingTaskResponse`
        """
        try:
            # 优化参数的显示
            req = models.DescribeTrainingTaskRequest()
            req.Id = task_id
            # TODO 优化显示结果
            return self._tione_client.DescribeTrainingTask(req)
        except TencentCloudSDKException as err:
            raise

    def parse_cos_info(self, cos_str):
        """ 解析cos 字符串成结构体

        :param cos_str: 格式如： <bucket>/<cos path>/
        :type cos_str: str
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CosPathInfo`
        """
        cos_info = parse_cos_str(cos_str)
        cos_info.Region = self._region
        return cos_info

    def create_training_task(self,
                             name,
                             framework,
                             cos_output,
                             worker_resource,
                             ps_resource=None,
                             code_package_path=None,
                             input_data_config=None,
                             worker_start_cmd=None,
                             ps_start_cmd=None,
                             tags=None,
                             tuning_parameters_dict={},
                             resource_group_id="",
                             remark=None,
                             log_enable=False,
                             log_logset_id=None,
                             log_topic_id=None,
                             vpc_id=None,
                             sub_net_id=None):
        """创建训练任务

        :param name:        任务名称
        :type name:         str
        :param framework:   运行的框架环境
        :type framework:    :class:`tikit.models.FrameworkInfo`
        :param cos_output:          输出的cos信息
        :type cos_output:           str
        :param worker_resource:     worker节点的配置
        :type worker_resource:      :class:`tikit.models.ResourceConfigInfo`
        :param ps_resource:         ps节点的配置
        :type ps_resource:          :class:`tikit.models.ResourceConfigInfo`
        :param code_package_path:   代码的cos信息
        :type code_package_path:    str
        :param input_data_config:   输入的数据信息
        :type input_data_config:    :class:`tikit.models.TrainingDataConfig`
        :param worker_start_cmd:    worker的启动命令
        :type worker_start_cmd:     str
        :param ps_start_cmd:        ps节点的启动命令
        :type ps_start_cmd:         str
        :param tags:                标签
        :type tags:                 list of :class:`tikit.tencentcloud.tione.v20211111.models.Tag`
        :param tuning_parameters_dict:  调参字典
        :type tuning_parameters_dict:   dict
        :param resource_group_id:   预付费的资源组id
        :type resource_group_id:    str
        :param remark:              描述
        :type remark:               str
        :param log_enable:          日志开关
        :type log_enable:           bool
        :param log_logset_id:       日志集id
        :type log_logset_id:        str
        :param log_topic_id:        日志的topic id
        :type log_topic_id:         str
        :param vpc_id:              vpc的id
        :type vpc_id:               str
        :param sub_net_id:          子网id
        :type sub_net_id:           str
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateTrainingTaskResponse`
        """
        try:
            req = models.CreateTrainingTaskRequest()
            req.Name = name

            req.TrainingMode = framework.TrainingMode
            if framework.Name == "CUSTOM":
                req.ImageInfo = models.ImageInfo()
                req.ImageInfo.ImageType = framework.ImageType
                req.ImageInfo.ImageUrl = framework.ImageUrl
                req.ImageInfo.RegistryRegion = framework.RegistryRegion
                req.ImageInfo.RegistryId = framework.RegistryId
            else:
                req.FrameworkName = framework.Name
                req.FrameworkVersion = framework.FrameworkVersion

            if req.TrainingMode not in ALL_SUPPORT_TRAINING_MODES:
                raise TencentCloudSDKException(
                    message='only support these training modes {}'.format(ALL_SUPPORT_TRAINING_MODES))
            if req.TrainingMode == "PS_WORKER":
                if not ps_resource:
                    raise TencentCloudSDKException(message='PS_WORKER training mode, need the argument "ps_resource"')
                if worker_resource.ChargeType != ps_resource.ChargeType:
                    raise TencentCloudSDKException(
                        message='worker_resource charge type should be same with ps_resource')
            elif ps_resource:
                raise TencentCloudSDKException(message='only PS_WORKER training mode,need the argument "ps_resource"')

            req.ChargeType = worker_resource.ChargeType
            req.ResourceGroupId = resource_group_id

            worker_info = models.ResourceConfigInfo()
            worker_info.Role = "WORKER"
            worker_info.InstanceNum = worker_resource.InstanceNum
            worker_info.Cpu = worker_resource.Cpu
            worker_info.Memory = worker_resource.Memory
            worker_info.GpuType = worker_resource.GpuType
            worker_info.Gpu = worker_resource.Gpu
            worker_info.InstanceType = worker_resource.InstanceType
            req.ResourceConfigInfos = [worker_info]

            if ps_resource:
                ps_info = models.ResourceConfigInfo()
                ps_info.Role = "PS"
                ps_info.InstanceNum = ps_resource.InstanceNum
                ps_info.Cpu = ps_resource.Cpu
                ps_info.Memory = ps_resource.Memory
                ps_info.GpuType = ps_resource.GpuType
                ps_info.Gpu = ps_resource.Gpu
                req.ResourceConfigInfos.append(ps_info)

            req.Output = self.parse_cos_info(cos_output)
            req.Tags = tags
            req.CodePackagePath = self.parse_cos_info(code_package_path) if code_package_path else None
            req.StartCmdInfo = models.StartCmdInfo()
            req.StartCmdInfo.WorkerStartCmd = worker_start_cmd
            req.StartCmdInfo.PStartCmd = ps_start_cmd

            req.DataSource = input_data_config.DataSource
            req.DataConfigs = []
            if req.DataSource == "DATASET":
                for dataset_id in input_data_config.DataConfigDict:
                    data_config = models.DataConfig()
                    data_config.MappingPath = input_data_config.DataConfigDict[dataset_id]
                    data_config.Id = dataset_id
                    req.DataConfigs.append(data_config)
            if req.DataSource == "COS":
                for cos_str in input_data_config.DataConfigDict:
                    data_config = models.DataConfig()
                    data_config.MappingPath = input_data_config.DataConfigDict[cos_str]
                    data_config.StorageDataPath = self.parse_cos_info(cos_str)
                    req.DataConfigs.append(data_config)

            req.TuningParameters = json.dumps(tuning_parameters_dict)
            req.Remark = remark
            req.LogEnable = log_enable
            if log_enable:
                req.LogConfig = models.LogConfig()
                req.LogConfig.LogsetId = log_logset_id
                req.LogConfig.TopicId = log_topic_id

            req.VpcId = vpc_id
            req.SubnetId = sub_net_id

            return self._tione_client.CreateTrainingTask(req)
        except TencentCloudSDKException as err:
            raise

    def stop_training_task(self, task_id):
        """停止某个训练任务

        :param task_id: 训练任务ID
        :type task_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.StopTrainingTaskResponse`
        """
        try:
            req = models.StopTrainingTaskRequest()
            req.Id = task_id
            return self._tione_client.StopTrainingTask(req)
        except TencentCloudSDKException as err:
            raise

    def describe_training_frameworks(self):
        """查看训练框架

        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingFrameworksResponse`
        print返回的结果，输出如下：
        +------------+-------------------------+-------------------------+
        |  框架名称  |           版本          |         训练模式        |
        +------------+-------------------------+-------------------------+
        | TENSORFLOW |      1.15-py3.6-cpu     | PS_WORKER, MPI, HOROVOD |
        |            | 1.15-py3.6-cuda10.0-gpu |                         |
        |            |      2.4-py3.6-cpu      |                         |
        |            |  2.4-py3.6-cuda11.0-gpu |                         |
        |  PYTORCH   |  1.9-py3.6-cuda11.1-gpu |    DDP, MPI, HOROVOD    |
        |  PYSPARK   |     2.4.5-py3.6-cpu     |                         |
        |   LIGHT    |  3.0-py3.6-cuda11.0-gpu |    DDP, MPI, HOROVOD    |
        +------------+-------------------------+-------------------------+
        """
        try:
            req = models.DescribeTrainingFrameworksRequest()
            return self._tione_client.DescribeTrainingFrameworks(req)
        except TencentCloudSDKException as err:
            raise

    def delete_training_task(self, task_id):
        """删除某个训练任务

        :param task_id: 训练任务ID
        :type task_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DeleteTrainingTaskResponse`
        """
        try:
            req = models.DeleteTrainingTaskRequest()
            req.Id = task_id
            return self._tione_client.DeleteTrainingTask(req)
        except TencentCloudSDKException as err:
            raise

    def describe_training_task_pods(self, task_id):
        """获取训练任务的pod列表

        :param task_id: 训练任务ID
        :type task_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingTaskPodsResponse`
        """
        try:
            req = models.DescribeTrainingTaskPodsRequest()
            req.Id = task_id
            return self._tione_client.DescribeTrainingTaskPods(req)
        except TencentCloudSDKException as err:
            raise

    def _describe_logs(self, service, pod_name, start_time=None, end_time=None, limit=None, order=None,
                       context=None, filters=None):
        """查看pod的日志

        :param service: 查询哪种类型的日志。 TRAIN：训练任务； NOTEBOOK：Notebook服务； INFER：推理服务；
        :type service: str
        """
        try:
            req = models.DescribeLogsRequest()
            req.Service = service
            req.PodName = pod_name
            req.StartTime = start_time
            req.EndTime = end_time
            req.Limit = limit
            req.Order = order
            req.Context = context
            req.Filters = filters
            return self._tione_client.DescribeLogs(req)
        except TencentCloudSDKException as err:
            raise

    def describe_train_logs(self, pod_name, start_time=None, end_time=None, limit=None, order=None,
                            context=None, filters=None):
        """查看训练任务的日志

        :param pod_name: 查询哪个Pod的日志，支持通配符。查看某个训练任务的全部pod的日志可以填： "<task_id>*"，如：train-51cd6bf7ec1000*
        :type pod_name: str
        :param start_time: 日志查询开始时间。RFC3339格式的时间字符串，比如2021-12-16T13:20:24+08:00，默认值为当前时间的前一个小时
        :type start_time: str
        :param end_time: 日志查询结束时间。RFC3339格式的时间字符串，比如2021-12-16T13:20:24+08:00，默认值为当前时间
        :type end_time: str
        :param limit: 日志查询条数，默认值100，最大值100
        :type limit: int
        :param order: 排序方向。(ASC | DESC) 默认值为DESC
        :type order: str
        :param context: 分页的游标
        :type context: str
        :param filters: 过滤Filters
        :type filters: list of tikit.tencentcloud.tione.v20211111.models.Filter
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeLogsResponse`

            返回的对象如果非空，就会有 next() 方法，能不断地获取下一页的日志（如果有多页的话），如下：
            now_time = datetime.datetime.now(datetime.timezone.utc)
            now_time_str = now_time.isoformat()
            result = client.describe_train_logs("train-51cd6bf7ec1000-37c5p5nlr01s-launcher",
                                                "2021-12-10T09:32:03.823509+00:00",
                                                now_time_str,
                                                limit=30)
            print(result)
            print(result.next())
            print(result.next())
            print(result.next())
        """
        result = self._describe_logs("TRAIN", pod_name, start_time, end_time, limit, order, context, filters)

        def get_next_data(xx):
            if result.Context != "":
                next_result = self.describe_train_logs(pod_name, start_time, end_time, limit, order, result.Context, filters)
                result.Context = next_result.Context
                result.Content = next_result.Content
                result.RequestId = next_result.RequestId
                return result
            else:
                print("All logs are displayed! Return None.")
                return None

        result.next = types.MethodType(get_next_data, result)
        return result

    def create_text_dataset(self, dataset_name, storage_data_path, storage_label_path, dataset_tags=None):
        """创建文本数据集

        :param dataset_name: 数据集名称
        :type dataset_name: str
        :param storage_data_path: 数据源cos路径。格式：<bucket>/<cos path>/
        :type storage_data_path:  str
        :param storage_label_path: 数据集标签cos存储路径。格式：<bucket>/<cos path>/
        :type storage_label_path: str
        :param dataset_tags: 数据集标签
        :type dataset_tags: list of tikit.tencentcloud.tione.v20211111.models.Tag
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateDatasetResponse`
        """
        try:
            req = models.CreateDatasetRequest()
            req.DatasetName = dataset_name
            req.DatasetType = "TYPE_DATASET_TEXT"
            req.StorageDataPath = self.parse_cos_info(storage_data_path)
            req.StorageLabelPath = self.parse_cos_info(storage_label_path)
            req.DatasetTags = dataset_tags
            return self._tione_client.CreateDataset(req)
        except TencentCloudSDKException as err:
            raise

    def create_table_dataset(self, dataset_name, storage_data_path, storage_label_path, dataset_tags=None,
                             is_schema_existed=None, schema_info_dict=None):
        """创建表格数据集

        :param dataset_name: 数据集名称
        :type dataset_name: str
        :param storage_data_path: 数据源cos路径。格式：<bucket>/<cos path>/
        :type storage_data_path:  str
        :param storage_label_path: 数据集标签cos存储路径。格式：<bucket>/<cos path>/
        :type storage_label_path:  str
        :param dataset_tags: 数据集标签
        :type dataset_tags: list of tikit.tencentcloud.tione.v20211111.models.Tag
        :param is_schema_existed: 数据是否存在表头。
            若数据文件包含表头，则请您严格按照表格列名配置Schema信息，否则校验不通过会造成导入数据集失败；
            若数据文件不包含表头，则平台会根据您定义的Schema信息依次为您解析表格数据
        :type is_schema_existed: bool
        :param schema_info_dict: 表头信息。格式： 字段名称 -> 数据类型。字段的数据类型包括：
            TYPE_INT:       整型
            TYPE_STRING:    字符串
            TYPE_BOOL:      布尔型
            TYPE_FLOAT:     浮点型
        :type dict
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateDatasetResponse`
        """
        try:
            req = models.CreateDatasetRequest()
            req.DatasetName = dataset_name
            req.DatasetType = "TYPE_DATASET_TABLE"
            req.StorageDataPath = self.parse_cos_info(storage_data_path)
            req.StorageLabelPath = self.parse_cos_info(storage_label_path)
            req.DatasetTags = dataset_tags
            req.IsSchemaExisted = is_schema_existed
            req.SchemaInfos = []
            for field in schema_info_dict:
                schema_info = models.SchemaInfo()
                if field == "":
                    raise TencentCloudSDKException(message='schema_info.Name must be non-empty string')
                if schema_info_dict[field] not in SCHEMA_INFO_VALUE_TYPES:
                    raise TencentCloudSDKException(
                        message='schema_info.Type must in {}'.format(SCHEMA_INFO_VALUE_TYPES))
                schema_info.Name = field
                schema_info.Type = schema_info_dict[field]
                req.SchemaInfos.append(schema_info)
            return self._tione_client.CreateDataset(req)
        except TencentCloudSDKException as err:
            raise

    def create_image_dataset(self, dataset_name, storage_data_path, storage_label_path, dataset_tags=None,
                             with_annotation=False, annotation_type=None, annotation_format=None):
        """创建图片数据集

        :param dataset_name: 数据集名称
        :type dataset_name: str
        :param storage_data_path: 数据源cos路径。格式：<bucket>/<cos path>/
        :type storage_data_path:  str
        :param storage_label_path: 数据集标签cos存储路径。格式：<bucket>/<cos path>/
        :type storage_label_path:  str
        :param dataset_tags: 数据集标签
        :type dataset_tags: list of tikit.tencentcloud.tione.v20211111.models.Tag
        :param with_annotation: 是否已经标注
        :type with_annotation: bool
        :param annotation_type: 标注类型。可选值如下：
            ANNOTATION_TYPE_CLASSIFICATION: 图片分类
            ANNOTATION_TYPE_DETECTION:      目标检测
            ANNOTATION_TYPE_SEGMENTATION:   图片分割
            ANNOTATION_TYPE_TRACKING:       目标跟踪
            ANNOTATION_TYPE_OCR:            OCR识别
        :type annotation_type: str
        :param annotation_format: 标注格式。可选值如下：
            ANNOTATION_FORMAT_TI:       TI平台格式
            ANNOTATION_FORMAT_PASCAL:   Pascal Voc
            ANNOTATION_FORMAT_COCO:     COCO
            ANNOTATION_FORMAT_FILE:     文件目录结构
        :type annotation_format: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateDatasetResponse`
        """
        try:
            req = models.CreateDatasetRequest()
            req.DatasetName = dataset_name
            req.DatasetType = "TYPE_DATASET_IMAGE"
            req.StorageDataPath = self.parse_cos_info(storage_data_path)
            req.StorageLabelPath = self.parse_cos_info(storage_label_path)
            req.DatasetTags = dataset_tags
            req.AnnotationStatus = "STATUS_ANNOTATED" if with_annotation else "STATUS_NON_ANNOTATED"
            if with_annotation:
                if annotation_type not in ANNOTATION_TYPES:
                    raise TencentCloudSDKException(message='annotation_type must in {}'.format(ANNOTATION_TYPES))
                if annotation_format not in ANNOTATION_FORMATS:
                    raise TencentCloudSDKException(message='annotation_format must in {}'.format(ANNOTATION_FORMATS))
            req.AnnotationType = annotation_type
            req.AnnotationFormat = annotation_format
            return self._tione_client.CreateDataset(req)
        except TencentCloudSDKException as err:
            raise

    def create_other_dataset(self, dataset_name, storage_data_path, storage_label_path, dataset_tags=None):
        """创建其他类型的数据集

        :param dataset_name: 数据集名称
        :type dataset_name: str
        :param storage_data_path: 数据源cos路径。格式：<bucket>/<cos path>/
        :type storage_data_path:  str
        :param storage_label_path: 数据集标签cos存储路径。格式：<bucket>/<cos path>/
        :type storage_label_path:  str
        :param dataset_tags: 数据集标签
        :type dataset_tags: list of tikit.tencentcloud.tione.v20211111.models.Tag
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateDatasetResponse`
        """
        try:
            req = models.CreateDatasetRequest()
            req.DatasetName = dataset_name
            req.DatasetType = "TYPE_DATASET_OTHER"
            req.StorageDataPath = self.parse_cos_info(storage_data_path)
            req.StorageLabelPath = self.parse_cos_info(storage_label_path)
            req.DatasetTags = dataset_tags
            return self._tione_client.CreateDataset(req)
        except TencentCloudSDKException as err:
            raise

    def describe_datasets(self, dataset_ids=None, filters=None, tag_filters=None, order=None, order_field=None,
                          offset=None, limit=None):
        """查看数据集列表

        :param dataset_ids: 数据集id列表
        :type dataset_ids: list of str
        :param filters: 字段过滤条件
        :type filters: list of Filter
        :param tag_filters: 标签过滤条件
        :type tag_filters: list of TagFilter
        :param order: 排序值 Asc Desc
        :type order: str
        :param order_field: 排序字段
        :type order_field: str
        :param offset: 偏移值
        :type offset: int
        :param limit: 返回数据个数
        :type limit: int
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeDatasetsResponse`
        """
        try:
            req = models.DescribeDatasetsRequest()
            req.DatasetIds = dataset_ids
            req.Filters = filters
            req.TagFilters = tag_filters
            req.Order = order
            req.OrderField = order_field
            req.Offset = offset
            req.Limit = limit
            return self._tione_client.DescribeDatasets(req)
        except TencentCloudSDKException as err:
            raise

    def delete_dataset(self, dataset_id, delete_label_enable=False):
        """删除某个数据集

        :param dataset_id: 数据集id
        :type dataset_id: str
        :param delete_label_enable: 是否删除cos标签文件
        :type delete_label_enable: bool
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DeleteDatasetResponse`
        """
        try:
            req = models.DeleteDatasetRequest()
            req.DatasetId = dataset_id
            req.DeleteLabelEnable = delete_label_enable
            return self._tione_client.DeleteDataset(req)
        except TencentCloudSDKException as err:
            raise

    def describe_dataset_detail_structured(self, dataset_id, offset=None, limit=None):
        """查看结构化数据集的内容

        :param dataset_id: 数据集ID
        :type dataset_id: str
        :param offset: 偏移值
        :type offset: int
        :param limit: 返回数据条数
        :type limit: int
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeDatasetDetailStructuredResponse`
        """
        try:
            req = models.DescribeDatasetDetailStructuredRequest()
            req.DatasetId = dataset_id
            req.Offset = offset
            req.Limit = limit
            return self._tione_client.DescribeDatasetDetailStructured(req)
        except TencentCloudSDKException as err:
            raise

    def describe_dataset_detail_unstructured(self, dataset_id, offset=None, limit=None, label_list=[],
                                             annotation_status="STATUS_ALL"):
        """查看非结构化数据集的内容

        :param dataset_id: 数据集ID
        :type dataset_id: str
        :param offset: 偏移值
        :type offset: int
        :param limit: 返回数据条数
        :type limit: int
        :param label_list: 标签过滤参数
        :type label_list: list of str
        :param annotation_status: 标注状态过滤参数。
            STATUS_ANNOTATED:       已标注
            STATUS_NON_ANNOTATED:   未标注
            STATUS_ALL:             全部
        :type annotation_status: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeDatasetDetailUnstructuredResponse`
        """
        try:
            req = models.DescribeDatasetDetailUnstructuredRequest()
            req.DatasetId = dataset_id
            req.Offset = offset
            req.Limit = limit
            req.LabelList = label_list
            req.AnnotationStatus = annotation_status
            return self._tione_client.DescribeDatasetDetailUnstructured(req)
        except TencentCloudSDKException as err:
            raise

    def _get_model_index(self, task_id):
        req = models.DescribeLatestTrainingMetricsRequest()
        req.TaskId = task_id
        result = self._tione_client.DescribeLatestTrainingMetrics(req)
        indexs = []
        for metric in result.Metrics:
            indexs.append("{}={}".format(metric.MetricName, metric.Values[0].Value))
        return ",".join(indexs)

    def describe_system_reasoning_images(self):
        """获取平台内置的推理镜像

        :return:    推理镜像信息
        :rtype:     :class:`tikit.tencentcloud.tione.v20211111.models.DescribeInferTemplatesResponse`
        数据格式如：
        {
          "FrameworkTemplates": [
            {
              "Framework": "TENSORFLOW",
              "FrameworkVersion": "2.4",
              "Groups": [
                "TENSORFLOW",
                "LIGHT"
              ],
              "InferTemplates": [
                {
                  "InferTemplateId": "tf2.4-py38-cpu",
                  "InferTemplateImage": "ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-tensorflow-cpu:py38-tensorflow2.4-cpu-20211206"
                },
                {
                  "InferTemplateId": "tf2.4-py38-gpu",
                  "InferTemplateImage": "ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-tensorflow-gpu:py38-tensorflow2.4-cu110-20211206"
                }
              ]
            }
          ],
          "RequestId": "3654e19b-c2ba-4953-b131-d66495723008"
        }

        print的返回结果，输出如下：（镜像标识用来配置新模型的运行环境
        +------------+----------------+-------------------------+--------------------+------------------------------------------------------------------------------------------------------------+
        |  算法框架  | 算法框架版本号 |    支持的训练框架集合   |      镜像标识      |                                                  镜像url                                                   |
        +------------+----------------+-------------------------+--------------------+------------------------------------------------------------------------------------------------------------+
        | TENSORFLOW |      2.4       | ['TENSORFLOW', 'LIGHT'] |   tf2.4-py38-cpu   |  ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-tensorflow-cpu:py38-tensorflow2.4-cpu-20211206   |
        | TENSORFLOW |      2.4       | ['TENSORFLOW', 'LIGHT'] |   tf2.4-py38-gpu   | ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-tensorflow-gpu:py38-tensorflow2.4-cu110-20211206  |
        | TENSORFLOW |      1.15      | ['TENSORFLOW', 'LIGHT'] |  tf1.15-py36-cpu   |  ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-tensorflow-cpu:py36-tensorflow1.15-cpu-20211206  |
        | TENSORFLOW |      1.15      | ['TENSORFLOW', 'LIGHT'] |  tf1.15-py36-gpu   | ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-tensorflow-gpu:py36-tensorflow1.15-cu100-20211206 |
        |  PYTORCH   |      1.9       |   ['PYTORCH', 'LIGHT']  |  py1.9.0-py36-cpu  |     ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-pytorch-cpu:py36-torch1.9.0-cpu-20211206      |
        |  PYTORCH   |      1.9       |   ['PYTORCH', 'LIGHT']  | py1.9.0-py36-cu111 |    ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-pytorch-gpu:py36-torch1.9.0-cu111-20211206     |
        |  PYTORCH   |      1.9       |   ['PYTORCH', 'LIGHT']  | py1.9.0-py36-cu102 |    ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-pytorch-gpu:py36-torch1.9.0-cu102-20211206     |
        |    PMML    |     0.9.12     |   ['SPARK', 'PYSPARK']  |     pmml-py36      |              ccr.ccs.tencentyun.com/qcloud-ti-platform/ti-cloud-infer-pmml:py36-pmml-20211206              |
        +------------+----------------+-------------------------+--------------------+------------------------------------------------------------------------------------------------------------+
        """
        req = models.DescribeInferTemplatesRequest()
        result = self._tione_client.DescribeInferTemplates(req)
        return result

    def _get_model_new_version(self, training_model_id):
        versions = self.describe_training_model_versions(training_model_id)
        ret = "v1"
        for version in versions.TrainingModelVersions:
            new_length = len(version.TrainingModelVersion)
            if new_length > len(ret) or (new_length == len(ret) and version.TrainingModelVersion > ret):
                ret = version.TrainingModelVersion
        return "v%d" % (int(ret[1:]) + 1)

    def _set_reaoning_env(self, req, reasoning_env):
        req.ReasoningEnvironmentSource = reasoning_env.Source
        if reasoning_env.Source == "CUSTOM":
            req.ReasoningImageInfo = models.ImageInfo()
            req.ReasoningImageInfo.ImageType = reasoning_env.ImageType
            req.ReasoningImageInfo.ImageUrl = reasoning_env.ImageUrl
            req.ReasoningImageInfo.RegistryRegion = reasoning_env.RegistryRegion
            req.ReasoningImageInfo.RegistryId = reasoning_env.RegistryId
            return
        system_images = self.describe_system_reasoning_images()
        for framework_template in system_images.FrameworkTemplates:
            for image in framework_template.InferTemplates:
                if image.InferTemplateId == reasoning_env.ImageKey:
                    req.ReasoningEnvironment = image.InferTemplateImage
                    return
        raise TencentCloudSDKException(
            message='image key "{}" is invalid, please use "describe_system_images" to get image key list'.format(
                reasoning_env.ImageKey))

    def _create_model_by_task(self,
                              req,
                              training_job_id,
                              reasoning_env,
                              training_model_index=None,
                              delete_task_cos_model=True,
                              tags=None):
        try:
            req.TrainingJobId = training_job_id
            # get job info from task
            task = self.describe_training_task(training_job_id)
            req.TrainingJobName = task.TrainingTaskDetail.Name
            req.TrainingModelCosPath = task.TrainingTaskDetail.Output
            req.AlgorithmFramework = task.TrainingTaskDetail.FrameworkName

            # 训练指标优先使用参数里面的
            req.TrainingModelIndex = training_model_index
            if not training_model_index:
                req.TrainingModelIndex = self._get_model_index(training_job_id)

            self._set_reaoning_env(req, reasoning_env)

            req.ModelMoveMode = "CUT" if delete_task_cos_model else "COPY"
            req.Tags = tags
            return self._tione_client.CreateTrainingModel(req)

        except TencentCloudSDKException as err:
            raise

    def create_model_by_task(self,
                             training_model_name,
                             training_job_id,
                             reasoning_env,
                             training_model_index=None,
                             delete_task_cos_model=True,
                             tags=None):
        """使用现有的任务的结果来创建新的模型

        :param training_model_name: 模型名称
        :type training_model_name: str
        :param training_job_id: 训练任务id
        :type training_job_id: str
        :param reasoning_env: 推理的运行环境
        :type reasoning_env:  :class:`tikit.models.ReasoningEnvironment`
        :param training_model_index: 训练指标。非空时覆盖训练任务里面的值。
        :type training_model_index: str
        :param delete_task_cos_model: 是否删除任务的原来输出的模型文件
        :type delete_task_cos_model: bool
        :param tags: 标签配置
        :type tags: list of :class:`tikit.tencentcloud.tione.v20211111.models.Tag`
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateTrainingModelResponse`
        返回的内容如下：
        {
          "Id": "m-23054253294030848",
          "RequestId": "c8f9b70e-bf4d-4c34-9480-21d902d3b341"
        }
        """
        req = models.CreateTrainingModelRequest()
        req.ImportMethod = "MODEL"
        req.TrainingModelName = training_model_name
        return self._create_model_by_task(req,
                                          training_job_id,
                                          reasoning_env,
                                          training_model_index,
                                          delete_task_cos_model,
                                          tags)

    def create_model_by_cos(self,
                            training_model_name,
                            algorithm_framework,
                            model_cos_path,
                            model_index,
                            reasoning_env,
                            delete_task_cos_model=True,
                            tags=None):
        """使用现有的cos路径来创建新的模型

        :param training_model_name: 模型名称
        :type training_model_name: str
        :param algorithm_framework: 算法框架
        :type algorithm_framework: str
        :param model_cos_path: 模型cos目录，以/结尾。格式：<bucket>/<cos path>/
        :type model_cos_path:  str
        :param model_index: 训练指标。
        :type model_index: str
        :param reasoning_env: 推理的运行环境
        :type reasoning_env:  :class:`tikit.models.ReasoningEnvironment`
        :param delete_task_cos_model: 是否删除任务的原来输出的模型文件
        :type delete_task_cos_model: bool
        :param tags: 标签配置
        :type tags: list of :class:`tikit.tencentcloud.tione.v20211111.models.Tag`
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateTrainingModelResponse`
        返回的内容如下：
        {
          "Id": "m-23054253294030848",
          "RequestId": "c8f9b70e-bf4d-4c34-9480-21d902d3b341"
        }
        """
        try:
            req = models.CreateTrainingModelRequest()
            req.ImportMethod = "MODEL"
            req.TrainingModelName = training_model_name
            req.AlgorithmFramework = algorithm_framework
            req.TrainingModelCosPath = self.parse_cos_info(model_cos_path)
            req.TrainingModelIndex = model_index

            # 设置镜像
            self._set_reaoning_env(req, reasoning_env)

            req.ModelMoveMode = "CUT" if delete_task_cos_model else "COPY"
            req.Tags = tags
            return self._tione_client.CreateTrainingModel(req)
        except TencentCloudSDKException as err:
            raise

    def create_model_version_by_task(self,
                                     training_model_id,
                                     training_job_id,
                                     reasoning_env,
                                     training_model_index=None,
                                     delete_task_cos_model=True,
                                     tags=None):
        """使用现有的cos路径来创建新的模型版本

        :param training_model_id: 模型ID
        :type training_model_id: str
        :param training_job_id: 训练任务id
        :type training_job_id: str
        :param reasoning_env: 推理的运行环境
        :type reasoning_env:  :class:`tikit.models.ReasoningEnvironment`
        :param training_model_index: 训练指标。非空时覆盖训练任务里面的值。
        :type training_model_index: str
        :param delete_task_cos_model: 是否删除任务的原来输出的模型文件
        :type delete_task_cos_model: bool
        :param tags: 标签配置
        :type tags: list of :class:`tikit.tencentcloud.tione.v20211111.models.Tag`
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateTrainingModelResponse`
        返回的内容如下：
        {
          "Id": "m-23054253294030848",
          "RequestId": "c8f9b70e-bf4d-4c34-9480-21d902d3b341"
        }
        """
        try:
            req = models.CreateTrainingModelRequest()
            req.ImportMethod = "VERSION"
            req.TrainingModelId = training_model_id
            req.TrainingModelVersion = self._get_model_new_version(training_model_id)
            return self._create_model_by_task(req,
                                              training_job_id,
                                              reasoning_env,
                                              training_model_index,
                                              delete_task_cos_model,
                                              tags)
        except TencentCloudSDKException as err:
            raise

    def create_model_version_by_cos(self,
                                    training_model_id,
                                    algorithm_framework,
                                    model_cos_path,
                                    model_index,
                                    reasoning_env,
                                    delete_task_cos_model=True,
                                    tags=None):
        """使用现有的cos路径来创建新的模型版本

        :param training_model_id: 模型ID
        :type training_model_id: str
        :param algorithm_framework: 算法框架
        :type algorithm_framework: str
        :param model_cos_path: 模型cos目录，以/结尾。格式：<bucket>/<cos path>/
        :type model_cos_path:  str
        :param model_index: 训练指标。
        :type model_index: str
        :param reasoning_env: 推理的运行环境
        :type reasoning_env:  :class:`tikit.models.ReasoningEnvironment`
        :param delete_task_cos_model: 是否删除任务的原来输出的模型文件
        :type delete_task_cos_model: bool
        :param tags: 标签配置
        :type tags: list of :class:`tikit.tencentcloud.tione.v20211111.models.Tag`
        :return:
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CreateTrainingModelResponse`
        返回的内容如下：
        {
          "Id": "m-23054253294030848",
          "RequestId": "c8f9b70e-bf4d-4c34-9480-21d902d3b341"
        }
        """
        try:
            req = models.CreateTrainingModelRequest()
            req.ImportMethod = "VERSION"
            req.TrainingModelId = training_model_id
            req.TrainingModelVersion = self._get_model_new_version(training_model_id)
            req.AlgorithmFramework = algorithm_framework
            req.TrainingModelCosPath = self.parse_cos_info(model_cos_path)
            req.TrainingModelIndex = model_index

            req.ModelMoveMode = "CUT" if delete_task_cos_model else "COPY"

            self._set_reaoning_env(req, reasoning_env)

            req.Tags = tags
            return self._tione_client.CreateTrainingModel(req)
        except TencentCloudSDKException as err:
            raise

    def describe_training_models(self, filters=None, order_field=None, order=None, offset=None, limit=None,
                                 tag_filters=None):
        """查看模型列表

        :param filters: 过滤器
        :type filters: list of Filter
        :param order_field: 排序字段
        :type order_field: str
        :param order: 排序方式，ASC/DESC
        :type order: str
        :param offset: 偏移量
        :type offset: int
        :param limit: 返回结果数量
        :type limit: int
        :param tag_filters: 标签过滤
        :type tag_filters: list of TagFilter
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingModelsResponse`
        print返回的结果，输出如下：
        +---------------------+-----------------------+-------------------+----------------------+
        |        模型ID       |          名称         |        标签       |       创建时间       |
        +---------------------+-----------------------+-------------------+----------------------+
        | m-23054253294030848 | tikit-model-task-1227 |                   | 2021-12-27T14:22:43Z |
        | m-23054252760240128 |  tikit-model-cos-1227 |                   | 2021-12-27T14:22:35Z |
        | m-23054246746066944 |    tikit-model-task   |                   | 2021-12-27T14:21:03Z |
        | m-23037023501881344 |    tikit-model-cos    |                   | 2021-12-24T13:20:57Z |
        | m-23036973226987520 |   tikit-model-name-2  |                   | 2021-12-24T13:08:10Z |
        | m-23034443699064832 |      model_cos-2      |                   | 2021-12-24T02:24:52Z |
        | m-23028904650346496 |       model_cos       | tag_001:tag_v_001 | 2021-12-23T02:56:13Z |
        | m-23028894739075072 |       model_task      |                   | 2021-12-23T02:53:42Z |
        |  22997374387884032  |         xx004         |                   | 2021-12-17T13:17:39Z |
        |  22996889833377792  |         xx003         |                   | 2021-12-17T11:14:26Z |
        +---------------------+-----------------------+-------------------+----------------------+
        """
        try:
            req = models.DescribeTrainingModelsRequest()
            req.Filters = filters
            req.OrderField = order_field
            req.order = order
            req.Offset = offset
            req.Limit = limit
            req.TagFilters = tag_filters
            return self._tione_client.DescribeTrainingModels(req)
        except TencentCloudSDKException as err:
            raise

    def describe_training_model_versions(self, training_model_id):
        """查看模型各个版本的信息列表

        :param training_model_id: 模型id
        :type training_model_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingModelVersionsResponse`
        """
        try:
            req = models.DescribeTrainingModelVersionsRequest()
            req.TrainingModelId = training_model_id
            return self._tione_client.DescribeTrainingModelVersions(req)
        except TencentCloudSDKException as err:
            raise

    def describe_training_model_version(self, training_model_version_id):
        """查看单个版本的信息

        :param training_model_version_id: 模型版本id
        :type training_model_version_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingModelVersionResponse`
        """
        try:
            req = models.DescribeTrainingModelVersionRequest()
            req.TrainingModelVersionId = training_model_version_id
            return self._tione_client.DescribeTrainingModelVersion(req)
        except TencentCloudSDKException as err:
            raise

    def delete_training_model(self, training_model_id):
        """删除模型

        :param training_model_id: 模型id
        :type training_model_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DeleteTrainingModelResponse`
        """
        try:
            req = models.DeleteTrainingModelRequest()
            req.TrainingModelId = training_model_id
            return self._tione_client.DeleteTrainingModel(req)
        except TencentCloudSDKException as err:
            raise

    def delete_training_model_version(self, training_model_version_id):
        """删除模型版本

        :param training_model_version_id: 模型版本id
        :type training_model_version_id: str
        :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.DeleteTrainingModelVersionResponse`
        """
        try:
            req = models.DeleteTrainingModelVersionRequest()
            req.TrainingModelVersionId = training_model_version_id
            return self._tione_client.DeleteTrainingModelVersion(req)
        except TencentCloudSDKException as err:
            raise
