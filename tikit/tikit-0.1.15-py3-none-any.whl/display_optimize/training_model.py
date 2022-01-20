# -*- coding: utf-8 -*-
from prettytable import PrettyTable

from tikit.tencentcloud.tione.v20211111 import models


def infer_templates_table(infer_templates):
    """

    :param infer_templates:
    :type infer_templates:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeInferTemplatesResponse`
    :return:
    :rtype:
    """
    table = PrettyTable()
    table.field_names = [
        "算法框架",
        "算法框架版本号",
        "支持的训练框架集合",
        "镜像标识",
        "镜像url"
    ]
    for framework_template in infer_templates.FrameworkTemplates:
        for image in framework_template.InferTemplates:
            table.add_row([
                framework_template.Framework,
                framework_template.FrameworkVersion,
                framework_template.Groups,
                image.InferTemplateId,
                image.InferTemplateImage
            ])
    return table


def infer_templates_table_str(self):
    return infer_templates_table(self).get_string()


def infer_templates_table_html(self):
    return infer_templates_table(self).get_html_string()


def training_model_table(training_models):
    """

    :param training_models:
    :type training_models:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingModelsResponse`
    :return:
    :rtype:
    """
    table = PrettyTable()
    table.field_names = [
        "模型ID",
        "名称",
        "标签",
        "创建时间"
    ]
    for model in training_models.TrainingModels:
        tag_detail = "\n".join(map(lambda x: "%s:%s" % (x.TagKey, x.TagValue), model.Tags))
        table.add_row([
            model.TrainingModelId,
            model.TrainingModelName,
            tag_detail,
            model.CreateTime
        ])
    return table


def training_model_table_str(self):
    return training_model_table(self).get_string()


def training_model_table_html(self):
    return training_model_table(self).get_html_string()


def training_model_version_table(training_model_versions):
    """

    :param training_model_versions:
    :type training_model_versions:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeTrainingModelVersionsResponse`
    :return:
    :rtype:
    """
    table = PrettyTable()
    table.field_names = [
        "版本ID",
        "模型版本",
        "算法框架",
        "运行环境来源",
        "运行环境",
        "模型指标",
        "COS 路径",
        "创建时间"
    ]
    for version in training_model_versions.TrainingModelVersions:
        reasoning_source = "内置"
        reasoning_env = version.ReasoningEnvironment
        if version.ReasoningEnvironmentSource == "custom" or version.ReasoningEnvironmentSource == "CUSTOM":
            reasoning_source = "自定义"
            reasoning_env = version.ReasoningImageInfo.ImageUrl
        table.add_row([
            version.TrainingModelVersionId,
            version.TrainingModelVersion,
            version.AlgorithmFramework,
            reasoning_source,
            reasoning_env,
            version.TrainingModelIndex,
            version.TrainingModelCosPath,
            version.TrainingModelCreateTime
        ])
    return table


def training_model_version_table_str(self):
    return training_model_version_table(self).get_string()


def training_model_version_table_html(self):
    return training_model_version_table(self).get_html_string()


models.DescribeInferTemplatesResponse.__repr__ = infer_templates_table_str
models.DescribeInferTemplatesResponse._repr_html_ = infer_templates_table_html

models.DescribeTrainingModelsResponse.__repr__ = training_model_table_str
models.DescribeTrainingModelsResponse._repr_html_ = training_model_table_html

models.DescribeTrainingModelVersionsResponse.__repr__ = training_model_version_table_str
models.DescribeTrainingModelVersionsResponse._repr_html_ = training_model_version_table_html
