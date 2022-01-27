"""
Type annotations for ec2 service client waiters.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_ec2 import EC2Client
    from mypy_boto3_ec2.waiter import (
        BundleTaskCompleteWaiter,
        ConversionTaskCancelledWaiter,
        ConversionTaskCompletedWaiter,
        ConversionTaskDeletedWaiter,
        CustomerGatewayAvailableWaiter,
        ExportTaskCancelledWaiter,
        ExportTaskCompletedWaiter,
        ImageAvailableWaiter,
        ImageExistsWaiter,
        InstanceExistsWaiter,
        InstanceRunningWaiter,
        InstanceStatusOkWaiter,
        InstanceStoppedWaiter,
        InstanceTerminatedWaiter,
        InternetGatewayExistsWaiter,
        KeyPairExistsWaiter,
        NatGatewayAvailableWaiter,
        NetworkInterfaceAvailableWaiter,
        PasswordDataAvailableWaiter,
        SecurityGroupExistsWaiter,
        SnapshotCompletedWaiter,
        SpotInstanceRequestFulfilledWaiter,
        SubnetAvailableWaiter,
        SystemStatusOkWaiter,
        VolumeAvailableWaiter,
        VolumeDeletedWaiter,
        VolumeInUseWaiter,
        VpcAvailableWaiter,
        VpcExistsWaiter,
        VpcPeeringConnectionDeletedWaiter,
        VpcPeeringConnectionExistsWaiter,
        VpnConnectionAvailableWaiter,
        VpnConnectionDeletedWaiter,
    )

    client: EC2Client = boto3.client("ec2")

    bundle_task_complete_waiter: BundleTaskCompleteWaiter = client.get_waiter("bundle_task_complete")
    conversion_task_cancelled_waiter: ConversionTaskCancelledWaiter = client.get_waiter("conversion_task_cancelled")
    conversion_task_completed_waiter: ConversionTaskCompletedWaiter = client.get_waiter("conversion_task_completed")
    conversion_task_deleted_waiter: ConversionTaskDeletedWaiter = client.get_waiter("conversion_task_deleted")
    customer_gateway_available_waiter: CustomerGatewayAvailableWaiter = client.get_waiter("customer_gateway_available")
    export_task_cancelled_waiter: ExportTaskCancelledWaiter = client.get_waiter("export_task_cancelled")
    export_task_completed_waiter: ExportTaskCompletedWaiter = client.get_waiter("export_task_completed")
    image_available_waiter: ImageAvailableWaiter = client.get_waiter("image_available")
    image_exists_waiter: ImageExistsWaiter = client.get_waiter("image_exists")
    instance_exists_waiter: InstanceExistsWaiter = client.get_waiter("instance_exists")
    instance_running_waiter: InstanceRunningWaiter = client.get_waiter("instance_running")
    instance_status_ok_waiter: InstanceStatusOkWaiter = client.get_waiter("instance_status_ok")
    instance_stopped_waiter: InstanceStoppedWaiter = client.get_waiter("instance_stopped")
    instance_terminated_waiter: InstanceTerminatedWaiter = client.get_waiter("instance_terminated")
    internet_gateway_exists_waiter: InternetGatewayExistsWaiter = client.get_waiter("internet_gateway_exists")
    key_pair_exists_waiter: KeyPairExistsWaiter = client.get_waiter("key_pair_exists")
    nat_gateway_available_waiter: NatGatewayAvailableWaiter = client.get_waiter("nat_gateway_available")
    network_interface_available_waiter: NetworkInterfaceAvailableWaiter = client.get_waiter("network_interface_available")
    password_data_available_waiter: PasswordDataAvailableWaiter = client.get_waiter("password_data_available")
    security_group_exists_waiter: SecurityGroupExistsWaiter = client.get_waiter("security_group_exists")
    snapshot_completed_waiter: SnapshotCompletedWaiter = client.get_waiter("snapshot_completed")
    spot_instance_request_fulfilled_waiter: SpotInstanceRequestFulfilledWaiter = client.get_waiter("spot_instance_request_fulfilled")
    subnet_available_waiter: SubnetAvailableWaiter = client.get_waiter("subnet_available")
    system_status_ok_waiter: SystemStatusOkWaiter = client.get_waiter("system_status_ok")
    volume_available_waiter: VolumeAvailableWaiter = client.get_waiter("volume_available")
    volume_deleted_waiter: VolumeDeletedWaiter = client.get_waiter("volume_deleted")
    volume_in_use_waiter: VolumeInUseWaiter = client.get_waiter("volume_in_use")
    vpc_available_waiter: VpcAvailableWaiter = client.get_waiter("vpc_available")
    vpc_exists_waiter: VpcExistsWaiter = client.get_waiter("vpc_exists")
    vpc_peering_connection_deleted_waiter: VpcPeeringConnectionDeletedWaiter = client.get_waiter("vpc_peering_connection_deleted")
    vpc_peering_connection_exists_waiter: VpcPeeringConnectionExistsWaiter = client.get_waiter("vpc_peering_connection_exists")
    vpn_connection_available_waiter: VpnConnectionAvailableWaiter = client.get_waiter("vpn_connection_available")
    vpn_connection_deleted_waiter: VpnConnectionDeletedWaiter = client.get_waiter("vpn_connection_deleted")
    ```
"""
from typing import Sequence

from botocore.waiter import Waiter as Boto3Waiter

from .type_defs import FilterTypeDef, WaiterConfigTypeDef

__all__ = (
    "BundleTaskCompleteWaiter",
    "ConversionTaskCancelledWaiter",
    "ConversionTaskCompletedWaiter",
    "ConversionTaskDeletedWaiter",
    "CustomerGatewayAvailableWaiter",
    "ExportTaskCancelledWaiter",
    "ExportTaskCompletedWaiter",
    "ImageAvailableWaiter",
    "ImageExistsWaiter",
    "InstanceExistsWaiter",
    "InstanceRunningWaiter",
    "InstanceStatusOkWaiter",
    "InstanceStoppedWaiter",
    "InstanceTerminatedWaiter",
    "InternetGatewayExistsWaiter",
    "KeyPairExistsWaiter",
    "NatGatewayAvailableWaiter",
    "NetworkInterfaceAvailableWaiter",
    "PasswordDataAvailableWaiter",
    "SecurityGroupExistsWaiter",
    "SnapshotCompletedWaiter",
    "SpotInstanceRequestFulfilledWaiter",
    "SubnetAvailableWaiter",
    "SystemStatusOkWaiter",
    "VolumeAvailableWaiter",
    "VolumeDeletedWaiter",
    "VolumeInUseWaiter",
    "VpcAvailableWaiter",
    "VpcExistsWaiter",
    "VpcPeeringConnectionDeletedWaiter",
    "VpcPeeringConnectionExistsWaiter",
    "VpnConnectionAvailableWaiter",
    "VpnConnectionDeletedWaiter",
)


class BundleTaskCompleteWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.BundleTaskComplete)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#bundletaskcompletewaiter)
    """

    def wait(
        self,
        *,
        BundleIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.BundleTaskComplete.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#bundletaskcompletewaiter)
        """


class ConversionTaskCancelledWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ConversionTaskCancelled)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#conversiontaskcancelledwaiter)
    """

    def wait(
        self,
        *,
        ConversionTaskIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ConversionTaskCancelled.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#conversiontaskcancelledwaiter)
        """


class ConversionTaskCompletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ConversionTaskCompleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#conversiontaskcompletedwaiter)
    """

    def wait(
        self,
        *,
        ConversionTaskIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ConversionTaskCompleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#conversiontaskcompletedwaiter)
        """


class ConversionTaskDeletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ConversionTaskDeleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#conversiontaskdeletedwaiter)
    """

    def wait(
        self,
        *,
        ConversionTaskIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ConversionTaskDeleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#conversiontaskdeletedwaiter)
        """


class CustomerGatewayAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.CustomerGatewayAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#customergatewayavailablewaiter)
    """

    def wait(
        self,
        *,
        CustomerGatewayIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.CustomerGatewayAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#customergatewayavailablewaiter)
        """


class ExportTaskCancelledWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ExportTaskCancelled)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#exporttaskcancelledwaiter)
    """

    def wait(
        self,
        *,
        ExportTaskIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ExportTaskCancelled.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#exporttaskcancelledwaiter)
        """


class ExportTaskCompletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ExportTaskCompleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#exporttaskcompletedwaiter)
    """

    def wait(
        self,
        *,
        ExportTaskIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ExportTaskCompleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#exporttaskcompletedwaiter)
        """


class ImageAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ImageAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#imageavailablewaiter)
    """

    def wait(
        self,
        *,
        ExecutableUsers: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ImageIds: Sequence[str] = ...,
        Owners: Sequence[str] = ...,
        IncludeDeprecated: bool = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ImageAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#imageavailablewaiter)
        """


class ImageExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ImageExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#imageexistswaiter)
    """

    def wait(
        self,
        *,
        ExecutableUsers: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ImageIds: Sequence[str] = ...,
        Owners: Sequence[str] = ...,
        IncludeDeprecated: bool = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.ImageExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#imageexistswaiter)
        """


class InstanceExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instanceexistswaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instanceexistswaiter)
        """


class InstanceRunningWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceRunning)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instancerunningwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceRunning.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instancerunningwaiter)
        """


class InstanceStatusOkWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceStatusOk)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instancestatusokwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        DryRun: bool = ...,
        IncludeAllInstances: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceStatusOk.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instancestatusokwaiter)
        """


class InstanceStoppedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceStopped)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instancestoppedwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceStopped.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instancestoppedwaiter)
        """


class InstanceTerminatedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceTerminated)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instanceterminatedwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InstanceTerminated.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#instanceterminatedwaiter)
        """


class InternetGatewayExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InternetGatewayExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#internetgatewayexistswaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        InternetGatewayIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.InternetGatewayExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#internetgatewayexistswaiter)
        """


class KeyPairExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.KeyPairExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#keypairexistswaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        KeyNames: Sequence[str] = ...,
        KeyPairIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.KeyPairExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#keypairexistswaiter)
        """


class NatGatewayAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.NatGatewayAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#natgatewayavailablewaiter)
    """

    def wait(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxResults: int = ...,
        NatGatewayIds: Sequence[str] = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.NatGatewayAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#natgatewayavailablewaiter)
        """


class NetworkInterfaceAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.NetworkInterfaceAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#networkinterfaceavailablewaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkInterfaceIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.NetworkInterfaceAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#networkinterfaceavailablewaiter)
        """


class PasswordDataAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.PasswordDataAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#passworddataavailablewaiter)
    """

    def wait(
        self, *, InstanceId: str, DryRun: bool = ..., WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.PasswordDataAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#passworddataavailablewaiter)
        """


class SecurityGroupExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SecurityGroupExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#securitygroupexistswaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        GroupIds: Sequence[str] = ...,
        GroupNames: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SecurityGroupExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#securitygroupexistswaiter)
        """


class SnapshotCompletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SnapshotCompleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#snapshotcompletedwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        OwnerIds: Sequence[str] = ...,
        RestorableByUserIds: Sequence[str] = ...,
        SnapshotIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SnapshotCompleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#snapshotcompletedwaiter)
        """


class SpotInstanceRequestFulfilledWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SpotInstanceRequestFulfilled)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#spotinstancerequestfulfilledwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        SpotInstanceRequestIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SpotInstanceRequestFulfilled.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#spotinstancerequestfulfilledwaiter)
        """


class SubnetAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SubnetAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#subnetavailablewaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        SubnetIds: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SubnetAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#subnetavailablewaiter)
        """


class SystemStatusOkWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SystemStatusOk)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#systemstatusokwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        DryRun: bool = ...,
        IncludeAllInstances: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.SystemStatusOk.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#systemstatusokwaiter)
        """


class VolumeAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VolumeAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#volumeavailablewaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VolumeAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#volumeavailablewaiter)
        """


class VolumeDeletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VolumeDeleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#volumedeletedwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VolumeDeleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#volumedeletedwaiter)
        """


class VolumeInUseWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VolumeInUse)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#volumeinusewaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VolumeInUse.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#volumeinusewaiter)
        """


class VpcAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcavailablewaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VpcIds: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcavailablewaiter)
        """


class VpcExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcexistswaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VpcIds: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcexistswaiter)
        """


class VpcPeeringConnectionDeletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcPeeringConnectionDeleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcpeeringconnectiondeletedwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        VpcPeeringConnectionIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcPeeringConnectionDeleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcpeeringconnectiondeletedwaiter)
        """


class VpcPeeringConnectionExistsWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcPeeringConnectionExists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcpeeringconnectionexistswaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        VpcPeeringConnectionIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpcPeeringConnectionExists.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpcpeeringconnectionexistswaiter)
        """


class VpnConnectionAvailableWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpnConnectionAvailable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpnconnectionavailablewaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VpnConnectionIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpnConnectionAvailable.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpnconnectionavailablewaiter)
        """


class VpnConnectionDeletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpnConnectionDeleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpnconnectiondeletedwaiter)
    """

    def wait(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VpnConnectionIds: Sequence[str] = ...,
        DryRun: bool = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Waiter.VpnConnectionDeleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/waiters.html#vpnconnectiondeletedwaiter)
        """
