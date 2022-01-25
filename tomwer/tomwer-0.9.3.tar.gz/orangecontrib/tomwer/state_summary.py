from orangewidget.utils.signals import summarize, PartialSummary
from tomwer.core.cluster import SlurmClusterConfiguration
from tomwer.core.scan.blissscan import BlissScan
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.futurescan import FutureTomwerScan


@summarize.register(object)  # noqa F811
def summarize_(Object: object):
    return PartialSummary("any object", "an oject of any type")


@summarize.register(dict)  # noqa F811
def summarize_(configuration: dict):
    return PartialSummary(
        "any configuration", "any configuration that can be provided to a process"
    )


@summarize.register(SlurmClusterConfiguration)  # noqa F811
def summarize_(cluster_config: SlurmClusterConfiguration):
    return PartialSummary(
        "cluster configuration",
        "cluster configuration to launch some remote processing",
    )


@summarize.register(TomwerScanBase)  # noqa F811
def summarize_(data: TomwerScanBase):
    return PartialSummary(
        "dataset with processing history",
        "core object used to ship dataset and history of processing done on this dataset",
    )


@summarize.register(FutureTomwerScan)  # noqa F811
def summarize_(future_data: FutureTomwerScan):
    return PartialSummary(
        "dataset with pending processing",
        "object used when there is some pending processing (asyncio.future). Can be convert back to `data`",
    )


@summarize.register(BlissScan)  # noqa F811
def summarize_(bliss_scan: BlissScan):
    return PartialSummary(
        "raw dataset from bliss",
        "object used when debug some processing relative to bliss",
    )
