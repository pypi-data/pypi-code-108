# -*- coding: utf-8 -*-
from prettytable import PrettyTable

from tikit.tencentcloud.tione.v20211111 import models


def group_resources_table(resource_groups):
    """

    :param resource_groups:
    :type resource_groups:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeBillingResourceGroupsResponse`
    :return:
    :rtype:
    """
    table = PrettyTable()
    table.field_names = [
        "资源组id",
        "资源组名称",
        "可用节点",
        "总节点",
        "已用/总资源",
        "标签"
    ]
    for resource in resource_groups.ResourceGroupSet:
        resource_detail = "CPU {}/{} 核\nMEM {}/{} GB\nGPU {}/{} 卡".format(
            resource.UsedResource.Cpu, resource.TotalResource.Cpu,
            resource.UsedResource.Memory, resource.TotalResource.Memory,
            resource.UsedResource.Gpu, resource.TotalResource.Gpu)
        tag_detail = "\n".join(map(lambda x: "%s:%s" % (x.TagKey, x.TagValue), resource.TagSet))
        table.add_row([resource.ResourceGroupId,
                       resource.ResourceGroupName,
                       resource.FreeInstance,
                       resource.TotalInstance,
                       resource_detail,
                       tag_detail])
    return table


def group_resources_table_str(self):
    return group_resources_table(self).get_string()


def group_resources_table_html(self):
    return group_resources_table(self).get_html_string()


models.DescribeBillingResourceGroupsResponse.__repr__ = group_resources_table_str
models.DescribeBillingResourceGroupsResponse._repr_html_ = group_resources_table_html
