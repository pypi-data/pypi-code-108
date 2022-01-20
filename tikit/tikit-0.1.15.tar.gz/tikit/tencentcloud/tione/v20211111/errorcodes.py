# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# CAM签名/鉴权错误。
AUTHFAILURE = 'AuthFailure'

# CAM系统异常。
AUTHFAILURE_CAMEXCEPTION = 'AuthFailure.CamException'

# 未授权操作。
AUTHFAILURE_UNAUTHORIZEDOPERATION = 'AuthFailure.UnauthorizedOperation'

# 操作失败。
FAILEDOPERATION = 'FailedOperation'

# 调用集群失败。
FAILEDOPERATION_CALLCLUSTERFAIL = 'FailedOperation.CallClusterFail'

# 尚未开通CLS日志服务，请开前往开通。
FAILEDOPERATION_CLSSERVICENOTACTIVED = 'FailedOperation.ClsServiceNotActived'

# 数据库执行错误。
FAILEDOPERATION_EXECDATABASEFAIL = 'FailedOperation.ExecDatabaseFail'

# 标签操作失败。
FAILEDOPERATION_EXECTAGFAIL = 'FailedOperation.ExecTagFail'

# 数据库查询错误。
FAILEDOPERATION_QUERYDATABASEFAIL = 'FailedOperation.QueryDatabaseFail'

# 内部错误。
INTERNALERROR = 'InternalError'

# cos client 内部错误。
INTERNALERROR_DCCOSCLIENTERR = 'InternalError.DCCosClientErr'

# 创建内部异步任务失败。
INTERNALERROR_DCCREATEASYNCTASKERROR = 'InternalError.DCCreateAsyncTaskError'

# 创建cos client 失败。
INTERNALERROR_DCCREATEUSERCOSCLIENTERR = 'InternalError.DCCreateUserCosClientErr'

# 数据仓库 rpc 内部错误。
INTERNALERROR_DCDATAREPORPCERR = 'InternalError.DCDatarepoRpcErr'

# 数据集状态未恢复。
INTERNALERROR_DCDATASETSTATUSNOTREADY = 'InternalError.DCDatasetStatusNotReady'

# 获取用户临时秘钥失败。
INTERNALERROR_DCGETUSERTEMPLATESECURITERR = 'InternalError.DCGetUserTemplateSecuritErr'

# 数据序列化错误。
INTERNALERROR_DCMARSHALDATAERR = 'InternalError.DCMarshalDataErr'

# 数据集获取文件内容异常。
INTERNALERROR_DCQUERYDATASETCONTENTERR = 'InternalError.DCQueryDatasetContentErr'

# 数据反序列化错误。
INTERNALERROR_DCUNMARSHALDATAERR = 'InternalError.DCUnmarshalDataErr'

# 参数错误。
INVALIDPARAMETER = 'InvalidParameter'

# 请求参数校验失败。
INVALIDPARAMETER_VALIDATEERROR = 'InvalidParameter.ValidateError'

# 参数取值错误。
INVALIDPARAMETERVALUE = 'InvalidParameterValue'

# 不支持的标注类型。
INVALIDPARAMETERVALUE_DCANNOTATIONTYPE = 'InvalidParameterValue.DCAnnotationType'

# 存储桶参数错误。
INVALIDPARAMETERVALUE_DCCOSPATHINFO = 'InvalidParameterValue.DCCosPathInfo'

# 数据集标注状态不匹配。
INVALIDPARAMETERVALUE_DCDATASETANNOTATIONNOTMATCH = 'InvalidParameterValue.DCDatasetAnnotationNotMatch'

# 数据集Id不存在。
INVALIDPARAMETERVALUE_DCDATASETIDNOTEXIST = 'InvalidParameterValue.DCDatasetIdNotExist'

# 数据集重名已存在。
INVALIDPARAMETERVALUE_DCDATASETNAMEEXIST = 'InvalidParameterValue.DCDatasetNameExist'

# 不支持的数据集类型。
INVALIDPARAMETERVALUE_DCDATASETTYPE = 'InvalidParameterValue.DCDatasetType'

# 不支持的过滤参数。
INVALIDPARAMETERVALUE_DCFILTERVALUES = 'InvalidParameterValue.DCFilterValues'

# 缺少参数错误。
MISSINGPARAMETER = 'MissingParameter'

# 未知参数错误。
UNKNOWNPARAMETER = 'UnknownParameter'

# 操作不支持。
UNSUPPORTEDOPERATION = 'UnsupportedOperation'
