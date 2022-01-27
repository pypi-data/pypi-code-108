"""
Type annotations for ec2 service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_ec2 import EC2Client
    from mypy_boto3_ec2.paginator import (
        DescribeAddressesAttributePaginator,
        DescribeByoipCidrsPaginator,
        DescribeCapacityReservationFleetsPaginator,
        DescribeCapacityReservationsPaginator,
        DescribeCarrierGatewaysPaginator,
        DescribeClassicLinkInstancesPaginator,
        DescribeClientVpnAuthorizationRulesPaginator,
        DescribeClientVpnConnectionsPaginator,
        DescribeClientVpnEndpointsPaginator,
        DescribeClientVpnRoutesPaginator,
        DescribeClientVpnTargetNetworksPaginator,
        DescribeCoipPoolsPaginator,
        DescribeDhcpOptionsPaginator,
        DescribeEgressOnlyInternetGatewaysPaginator,
        DescribeExportImageTasksPaginator,
        DescribeFastLaunchImagesPaginator,
        DescribeFastSnapshotRestoresPaginator,
        DescribeFleetsPaginator,
        DescribeFlowLogsPaginator,
        DescribeFpgaImagesPaginator,
        DescribeHostReservationOfferingsPaginator,
        DescribeHostReservationsPaginator,
        DescribeHostsPaginator,
        DescribeIamInstanceProfileAssociationsPaginator,
        DescribeImportImageTasksPaginator,
        DescribeImportSnapshotTasksPaginator,
        DescribeInstanceCreditSpecificationsPaginator,
        DescribeInstanceEventWindowsPaginator,
        DescribeInstanceStatusPaginator,
        DescribeInstanceTypeOfferingsPaginator,
        DescribeInstanceTypesPaginator,
        DescribeInstancesPaginator,
        DescribeInternetGatewaysPaginator,
        DescribeIpamPoolsPaginator,
        DescribeIpamScopesPaginator,
        DescribeIpamsPaginator,
        DescribeIpv6PoolsPaginator,
        DescribeLaunchTemplateVersionsPaginator,
        DescribeLaunchTemplatesPaginator,
        DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginator,
        DescribeLocalGatewayRouteTableVpcAssociationsPaginator,
        DescribeLocalGatewayRouteTablesPaginator,
        DescribeLocalGatewayVirtualInterfaceGroupsPaginator,
        DescribeLocalGatewayVirtualInterfacesPaginator,
        DescribeLocalGatewaysPaginator,
        DescribeManagedPrefixListsPaginator,
        DescribeMovingAddressesPaginator,
        DescribeNatGatewaysPaginator,
        DescribeNetworkAclsPaginator,
        DescribeNetworkInsightsAccessScopeAnalysesPaginator,
        DescribeNetworkInsightsAccessScopesPaginator,
        DescribeNetworkInsightsAnalysesPaginator,
        DescribeNetworkInsightsPathsPaginator,
        DescribeNetworkInterfacePermissionsPaginator,
        DescribeNetworkInterfacesPaginator,
        DescribePrefixListsPaginator,
        DescribePrincipalIdFormatPaginator,
        DescribePublicIpv4PoolsPaginator,
        DescribeReplaceRootVolumeTasksPaginator,
        DescribeReservedInstancesModificationsPaginator,
        DescribeReservedInstancesOfferingsPaginator,
        DescribeRouteTablesPaginator,
        DescribeScheduledInstanceAvailabilityPaginator,
        DescribeScheduledInstancesPaginator,
        DescribeSecurityGroupRulesPaginator,
        DescribeSecurityGroupsPaginator,
        DescribeSnapshotTierStatusPaginator,
        DescribeSnapshotsPaginator,
        DescribeSpotFleetInstancesPaginator,
        DescribeSpotFleetRequestsPaginator,
        DescribeSpotInstanceRequestsPaginator,
        DescribeSpotPriceHistoryPaginator,
        DescribeStaleSecurityGroupsPaginator,
        DescribeStoreImageTasksPaginator,
        DescribeSubnetsPaginator,
        DescribeTagsPaginator,
        DescribeTrafficMirrorFiltersPaginator,
        DescribeTrafficMirrorSessionsPaginator,
        DescribeTrafficMirrorTargetsPaginator,
        DescribeTransitGatewayAttachmentsPaginator,
        DescribeTransitGatewayConnectPeersPaginator,
        DescribeTransitGatewayConnectsPaginator,
        DescribeTransitGatewayMulticastDomainsPaginator,
        DescribeTransitGatewayPeeringAttachmentsPaginator,
        DescribeTransitGatewayRouteTablesPaginator,
        DescribeTransitGatewayVpcAttachmentsPaginator,
        DescribeTransitGatewaysPaginator,
        DescribeTrunkInterfaceAssociationsPaginator,
        DescribeVolumeStatusPaginator,
        DescribeVolumesPaginator,
        DescribeVolumesModificationsPaginator,
        DescribeVpcClassicLinkDnsSupportPaginator,
        DescribeVpcEndpointConnectionNotificationsPaginator,
        DescribeVpcEndpointConnectionsPaginator,
        DescribeVpcEndpointServiceConfigurationsPaginator,
        DescribeVpcEndpointServicePermissionsPaginator,
        DescribeVpcEndpointServicesPaginator,
        DescribeVpcEndpointsPaginator,
        DescribeVpcPeeringConnectionsPaginator,
        DescribeVpcsPaginator,
        GetAssociatedIpv6PoolCidrsPaginator,
        GetGroupsForCapacityReservationPaginator,
        GetInstanceTypesFromInstanceRequirementsPaginator,
        GetIpamAddressHistoryPaginator,
        GetIpamPoolAllocationsPaginator,
        GetIpamPoolCidrsPaginator,
        GetIpamResourceCidrsPaginator,
        GetManagedPrefixListAssociationsPaginator,
        GetManagedPrefixListEntriesPaginator,
        GetSpotPlacementScoresPaginator,
        GetTransitGatewayAttachmentPropagationsPaginator,
        GetTransitGatewayMulticastDomainAssociationsPaginator,
        GetTransitGatewayPrefixListReferencesPaginator,
        GetTransitGatewayRouteTableAssociationsPaginator,
        GetTransitGatewayRouteTablePropagationsPaginator,
        GetVpnConnectionDeviceTypesPaginator,
        ListSnapshotsInRecycleBinPaginator,
        SearchLocalGatewayRoutesPaginator,
        SearchTransitGatewayMulticastGroupsPaginator,
    )

    client: EC2Client = boto3.client("ec2")

    describe_addresses_attribute_paginator: DescribeAddressesAttributePaginator = client.get_paginator("describe_addresses_attribute")
    describe_byoip_cidrs_paginator: DescribeByoipCidrsPaginator = client.get_paginator("describe_byoip_cidrs")
    describe_capacity_reservation_fleets_paginator: DescribeCapacityReservationFleetsPaginator = client.get_paginator("describe_capacity_reservation_fleets")
    describe_capacity_reservations_paginator: DescribeCapacityReservationsPaginator = client.get_paginator("describe_capacity_reservations")
    describe_carrier_gateways_paginator: DescribeCarrierGatewaysPaginator = client.get_paginator("describe_carrier_gateways")
    describe_classic_link_instances_paginator: DescribeClassicLinkInstancesPaginator = client.get_paginator("describe_classic_link_instances")
    describe_client_vpn_authorization_rules_paginator: DescribeClientVpnAuthorizationRulesPaginator = client.get_paginator("describe_client_vpn_authorization_rules")
    describe_client_vpn_connections_paginator: DescribeClientVpnConnectionsPaginator = client.get_paginator("describe_client_vpn_connections")
    describe_client_vpn_endpoints_paginator: DescribeClientVpnEndpointsPaginator = client.get_paginator("describe_client_vpn_endpoints")
    describe_client_vpn_routes_paginator: DescribeClientVpnRoutesPaginator = client.get_paginator("describe_client_vpn_routes")
    describe_client_vpn_target_networks_paginator: DescribeClientVpnTargetNetworksPaginator = client.get_paginator("describe_client_vpn_target_networks")
    describe_coip_pools_paginator: DescribeCoipPoolsPaginator = client.get_paginator("describe_coip_pools")
    describe_dhcp_options_paginator: DescribeDhcpOptionsPaginator = client.get_paginator("describe_dhcp_options")
    describe_egress_only_internet_gateways_paginator: DescribeEgressOnlyInternetGatewaysPaginator = client.get_paginator("describe_egress_only_internet_gateways")
    describe_export_image_tasks_paginator: DescribeExportImageTasksPaginator = client.get_paginator("describe_export_image_tasks")
    describe_fast_launch_images_paginator: DescribeFastLaunchImagesPaginator = client.get_paginator("describe_fast_launch_images")
    describe_fast_snapshot_restores_paginator: DescribeFastSnapshotRestoresPaginator = client.get_paginator("describe_fast_snapshot_restores")
    describe_fleets_paginator: DescribeFleetsPaginator = client.get_paginator("describe_fleets")
    describe_flow_logs_paginator: DescribeFlowLogsPaginator = client.get_paginator("describe_flow_logs")
    describe_fpga_images_paginator: DescribeFpgaImagesPaginator = client.get_paginator("describe_fpga_images")
    describe_host_reservation_offerings_paginator: DescribeHostReservationOfferingsPaginator = client.get_paginator("describe_host_reservation_offerings")
    describe_host_reservations_paginator: DescribeHostReservationsPaginator = client.get_paginator("describe_host_reservations")
    describe_hosts_paginator: DescribeHostsPaginator = client.get_paginator("describe_hosts")
    describe_iam_instance_profile_associations_paginator: DescribeIamInstanceProfileAssociationsPaginator = client.get_paginator("describe_iam_instance_profile_associations")
    describe_import_image_tasks_paginator: DescribeImportImageTasksPaginator = client.get_paginator("describe_import_image_tasks")
    describe_import_snapshot_tasks_paginator: DescribeImportSnapshotTasksPaginator = client.get_paginator("describe_import_snapshot_tasks")
    describe_instance_credit_specifications_paginator: DescribeInstanceCreditSpecificationsPaginator = client.get_paginator("describe_instance_credit_specifications")
    describe_instance_event_windows_paginator: DescribeInstanceEventWindowsPaginator = client.get_paginator("describe_instance_event_windows")
    describe_instance_status_paginator: DescribeInstanceStatusPaginator = client.get_paginator("describe_instance_status")
    describe_instance_type_offerings_paginator: DescribeInstanceTypeOfferingsPaginator = client.get_paginator("describe_instance_type_offerings")
    describe_instance_types_paginator: DescribeInstanceTypesPaginator = client.get_paginator("describe_instance_types")
    describe_instances_paginator: DescribeInstancesPaginator = client.get_paginator("describe_instances")
    describe_internet_gateways_paginator: DescribeInternetGatewaysPaginator = client.get_paginator("describe_internet_gateways")
    describe_ipam_pools_paginator: DescribeIpamPoolsPaginator = client.get_paginator("describe_ipam_pools")
    describe_ipam_scopes_paginator: DescribeIpamScopesPaginator = client.get_paginator("describe_ipam_scopes")
    describe_ipams_paginator: DescribeIpamsPaginator = client.get_paginator("describe_ipams")
    describe_ipv6_pools_paginator: DescribeIpv6PoolsPaginator = client.get_paginator("describe_ipv6_pools")
    describe_launch_template_versions_paginator: DescribeLaunchTemplateVersionsPaginator = client.get_paginator("describe_launch_template_versions")
    describe_launch_templates_paginator: DescribeLaunchTemplatesPaginator = client.get_paginator("describe_launch_templates")
    describe_local_gateway_route_table_virtual_interface_group_associations_paginator: DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginator = client.get_paginator("describe_local_gateway_route_table_virtual_interface_group_associations")
    describe_local_gateway_route_table_vpc_associations_paginator: DescribeLocalGatewayRouteTableVpcAssociationsPaginator = client.get_paginator("describe_local_gateway_route_table_vpc_associations")
    describe_local_gateway_route_tables_paginator: DescribeLocalGatewayRouteTablesPaginator = client.get_paginator("describe_local_gateway_route_tables")
    describe_local_gateway_virtual_interface_groups_paginator: DescribeLocalGatewayVirtualInterfaceGroupsPaginator = client.get_paginator("describe_local_gateway_virtual_interface_groups")
    describe_local_gateway_virtual_interfaces_paginator: DescribeLocalGatewayVirtualInterfacesPaginator = client.get_paginator("describe_local_gateway_virtual_interfaces")
    describe_local_gateways_paginator: DescribeLocalGatewaysPaginator = client.get_paginator("describe_local_gateways")
    describe_managed_prefix_lists_paginator: DescribeManagedPrefixListsPaginator = client.get_paginator("describe_managed_prefix_lists")
    describe_moving_addresses_paginator: DescribeMovingAddressesPaginator = client.get_paginator("describe_moving_addresses")
    describe_nat_gateways_paginator: DescribeNatGatewaysPaginator = client.get_paginator("describe_nat_gateways")
    describe_network_acls_paginator: DescribeNetworkAclsPaginator = client.get_paginator("describe_network_acls")
    describe_network_insights_access_scope_analyses_paginator: DescribeNetworkInsightsAccessScopeAnalysesPaginator = client.get_paginator("describe_network_insights_access_scope_analyses")
    describe_network_insights_access_scopes_paginator: DescribeNetworkInsightsAccessScopesPaginator = client.get_paginator("describe_network_insights_access_scopes")
    describe_network_insights_analyses_paginator: DescribeNetworkInsightsAnalysesPaginator = client.get_paginator("describe_network_insights_analyses")
    describe_network_insights_paths_paginator: DescribeNetworkInsightsPathsPaginator = client.get_paginator("describe_network_insights_paths")
    describe_network_interface_permissions_paginator: DescribeNetworkInterfacePermissionsPaginator = client.get_paginator("describe_network_interface_permissions")
    describe_network_interfaces_paginator: DescribeNetworkInterfacesPaginator = client.get_paginator("describe_network_interfaces")
    describe_prefix_lists_paginator: DescribePrefixListsPaginator = client.get_paginator("describe_prefix_lists")
    describe_principal_id_format_paginator: DescribePrincipalIdFormatPaginator = client.get_paginator("describe_principal_id_format")
    describe_public_ipv4_pools_paginator: DescribePublicIpv4PoolsPaginator = client.get_paginator("describe_public_ipv4_pools")
    describe_replace_root_volume_tasks_paginator: DescribeReplaceRootVolumeTasksPaginator = client.get_paginator("describe_replace_root_volume_tasks")
    describe_reserved_instances_modifications_paginator: DescribeReservedInstancesModificationsPaginator = client.get_paginator("describe_reserved_instances_modifications")
    describe_reserved_instances_offerings_paginator: DescribeReservedInstancesOfferingsPaginator = client.get_paginator("describe_reserved_instances_offerings")
    describe_route_tables_paginator: DescribeRouteTablesPaginator = client.get_paginator("describe_route_tables")
    describe_scheduled_instance_availability_paginator: DescribeScheduledInstanceAvailabilityPaginator = client.get_paginator("describe_scheduled_instance_availability")
    describe_scheduled_instances_paginator: DescribeScheduledInstancesPaginator = client.get_paginator("describe_scheduled_instances")
    describe_security_group_rules_paginator: DescribeSecurityGroupRulesPaginator = client.get_paginator("describe_security_group_rules")
    describe_security_groups_paginator: DescribeSecurityGroupsPaginator = client.get_paginator("describe_security_groups")
    describe_snapshot_tier_status_paginator: DescribeSnapshotTierStatusPaginator = client.get_paginator("describe_snapshot_tier_status")
    describe_snapshots_paginator: DescribeSnapshotsPaginator = client.get_paginator("describe_snapshots")
    describe_spot_fleet_instances_paginator: DescribeSpotFleetInstancesPaginator = client.get_paginator("describe_spot_fleet_instances")
    describe_spot_fleet_requests_paginator: DescribeSpotFleetRequestsPaginator = client.get_paginator("describe_spot_fleet_requests")
    describe_spot_instance_requests_paginator: DescribeSpotInstanceRequestsPaginator = client.get_paginator("describe_spot_instance_requests")
    describe_spot_price_history_paginator: DescribeSpotPriceHistoryPaginator = client.get_paginator("describe_spot_price_history")
    describe_stale_security_groups_paginator: DescribeStaleSecurityGroupsPaginator = client.get_paginator("describe_stale_security_groups")
    describe_store_image_tasks_paginator: DescribeStoreImageTasksPaginator = client.get_paginator("describe_store_image_tasks")
    describe_subnets_paginator: DescribeSubnetsPaginator = client.get_paginator("describe_subnets")
    describe_tags_paginator: DescribeTagsPaginator = client.get_paginator("describe_tags")
    describe_traffic_mirror_filters_paginator: DescribeTrafficMirrorFiltersPaginator = client.get_paginator("describe_traffic_mirror_filters")
    describe_traffic_mirror_sessions_paginator: DescribeTrafficMirrorSessionsPaginator = client.get_paginator("describe_traffic_mirror_sessions")
    describe_traffic_mirror_targets_paginator: DescribeTrafficMirrorTargetsPaginator = client.get_paginator("describe_traffic_mirror_targets")
    describe_transit_gateway_attachments_paginator: DescribeTransitGatewayAttachmentsPaginator = client.get_paginator("describe_transit_gateway_attachments")
    describe_transit_gateway_connect_peers_paginator: DescribeTransitGatewayConnectPeersPaginator = client.get_paginator("describe_transit_gateway_connect_peers")
    describe_transit_gateway_connects_paginator: DescribeTransitGatewayConnectsPaginator = client.get_paginator("describe_transit_gateway_connects")
    describe_transit_gateway_multicast_domains_paginator: DescribeTransitGatewayMulticastDomainsPaginator = client.get_paginator("describe_transit_gateway_multicast_domains")
    describe_transit_gateway_peering_attachments_paginator: DescribeTransitGatewayPeeringAttachmentsPaginator = client.get_paginator("describe_transit_gateway_peering_attachments")
    describe_transit_gateway_route_tables_paginator: DescribeTransitGatewayRouteTablesPaginator = client.get_paginator("describe_transit_gateway_route_tables")
    describe_transit_gateway_vpc_attachments_paginator: DescribeTransitGatewayVpcAttachmentsPaginator = client.get_paginator("describe_transit_gateway_vpc_attachments")
    describe_transit_gateways_paginator: DescribeTransitGatewaysPaginator = client.get_paginator("describe_transit_gateways")
    describe_trunk_interface_associations_paginator: DescribeTrunkInterfaceAssociationsPaginator = client.get_paginator("describe_trunk_interface_associations")
    describe_volume_status_paginator: DescribeVolumeStatusPaginator = client.get_paginator("describe_volume_status")
    describe_volumes_paginator: DescribeVolumesPaginator = client.get_paginator("describe_volumes")
    describe_volumes_modifications_paginator: DescribeVolumesModificationsPaginator = client.get_paginator("describe_volumes_modifications")
    describe_vpc_classic_link_dns_support_paginator: DescribeVpcClassicLinkDnsSupportPaginator = client.get_paginator("describe_vpc_classic_link_dns_support")
    describe_vpc_endpoint_connection_notifications_paginator: DescribeVpcEndpointConnectionNotificationsPaginator = client.get_paginator("describe_vpc_endpoint_connection_notifications")
    describe_vpc_endpoint_connections_paginator: DescribeVpcEndpointConnectionsPaginator = client.get_paginator("describe_vpc_endpoint_connections")
    describe_vpc_endpoint_service_configurations_paginator: DescribeVpcEndpointServiceConfigurationsPaginator = client.get_paginator("describe_vpc_endpoint_service_configurations")
    describe_vpc_endpoint_service_permissions_paginator: DescribeVpcEndpointServicePermissionsPaginator = client.get_paginator("describe_vpc_endpoint_service_permissions")
    describe_vpc_endpoint_services_paginator: DescribeVpcEndpointServicesPaginator = client.get_paginator("describe_vpc_endpoint_services")
    describe_vpc_endpoints_paginator: DescribeVpcEndpointsPaginator = client.get_paginator("describe_vpc_endpoints")
    describe_vpc_peering_connections_paginator: DescribeVpcPeeringConnectionsPaginator = client.get_paginator("describe_vpc_peering_connections")
    describe_vpcs_paginator: DescribeVpcsPaginator = client.get_paginator("describe_vpcs")
    get_associated_ipv6_pool_cidrs_paginator: GetAssociatedIpv6PoolCidrsPaginator = client.get_paginator("get_associated_ipv6_pool_cidrs")
    get_groups_for_capacity_reservation_paginator: GetGroupsForCapacityReservationPaginator = client.get_paginator("get_groups_for_capacity_reservation")
    get_instance_types_from_instance_requirements_paginator: GetInstanceTypesFromInstanceRequirementsPaginator = client.get_paginator("get_instance_types_from_instance_requirements")
    get_ipam_address_history_paginator: GetIpamAddressHistoryPaginator = client.get_paginator("get_ipam_address_history")
    get_ipam_pool_allocations_paginator: GetIpamPoolAllocationsPaginator = client.get_paginator("get_ipam_pool_allocations")
    get_ipam_pool_cidrs_paginator: GetIpamPoolCidrsPaginator = client.get_paginator("get_ipam_pool_cidrs")
    get_ipam_resource_cidrs_paginator: GetIpamResourceCidrsPaginator = client.get_paginator("get_ipam_resource_cidrs")
    get_managed_prefix_list_associations_paginator: GetManagedPrefixListAssociationsPaginator = client.get_paginator("get_managed_prefix_list_associations")
    get_managed_prefix_list_entries_paginator: GetManagedPrefixListEntriesPaginator = client.get_paginator("get_managed_prefix_list_entries")
    get_spot_placement_scores_paginator: GetSpotPlacementScoresPaginator = client.get_paginator("get_spot_placement_scores")
    get_transit_gateway_attachment_propagations_paginator: GetTransitGatewayAttachmentPropagationsPaginator = client.get_paginator("get_transit_gateway_attachment_propagations")
    get_transit_gateway_multicast_domain_associations_paginator: GetTransitGatewayMulticastDomainAssociationsPaginator = client.get_paginator("get_transit_gateway_multicast_domain_associations")
    get_transit_gateway_prefix_list_references_paginator: GetTransitGatewayPrefixListReferencesPaginator = client.get_paginator("get_transit_gateway_prefix_list_references")
    get_transit_gateway_route_table_associations_paginator: GetTransitGatewayRouteTableAssociationsPaginator = client.get_paginator("get_transit_gateway_route_table_associations")
    get_transit_gateway_route_table_propagations_paginator: GetTransitGatewayRouteTablePropagationsPaginator = client.get_paginator("get_transit_gateway_route_table_propagations")
    get_vpn_connection_device_types_paginator: GetVpnConnectionDeviceTypesPaginator = client.get_paginator("get_vpn_connection_device_types")
    list_snapshots_in_recycle_bin_paginator: ListSnapshotsInRecycleBinPaginator = client.get_paginator("list_snapshots_in_recycle_bin")
    search_local_gateway_routes_paginator: SearchLocalGatewayRoutesPaginator = client.get_paginator("search_local_gateway_routes")
    search_transit_gateway_multicast_groups_paginator: SearchTransitGatewayMulticastGroupsPaginator = client.get_paginator("search_transit_gateway_multicast_groups")
    ```
"""
import sys
from datetime import datetime
from typing import Generic, Iterator, Sequence, TypeVar, Union

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import (
    ArchitectureTypeType,
    InstanceTypeType,
    IpamResourceTypeType,
    LocationTypeType,
    OfferingClassTypeType,
    OfferingTypeValuesType,
    RIProductDescriptionType,
    TargetCapacityUnitTypeType,
    TenancyType,
    VirtualizationTypeType,
)
from .type_defs import (
    DescribeAddressesAttributeResultTypeDef,
    DescribeByoipCidrsResultTypeDef,
    DescribeCapacityReservationFleetsResultTypeDef,
    DescribeCapacityReservationsResultTypeDef,
    DescribeCarrierGatewaysResultTypeDef,
    DescribeClassicLinkInstancesResultTypeDef,
    DescribeClientVpnAuthorizationRulesResultTypeDef,
    DescribeClientVpnConnectionsResultTypeDef,
    DescribeClientVpnEndpointsResultTypeDef,
    DescribeClientVpnRoutesResultTypeDef,
    DescribeClientVpnTargetNetworksResultTypeDef,
    DescribeCoipPoolsResultTypeDef,
    DescribeDhcpOptionsResultTypeDef,
    DescribeEgressOnlyInternetGatewaysResultTypeDef,
    DescribeExportImageTasksResultTypeDef,
    DescribeFastLaunchImagesResultTypeDef,
    DescribeFastSnapshotRestoresResultTypeDef,
    DescribeFleetsResultTypeDef,
    DescribeFlowLogsResultTypeDef,
    DescribeFpgaImagesResultTypeDef,
    DescribeHostReservationOfferingsResultTypeDef,
    DescribeHostReservationsResultTypeDef,
    DescribeHostsResultTypeDef,
    DescribeIamInstanceProfileAssociationsResultTypeDef,
    DescribeImportImageTasksResultTypeDef,
    DescribeImportSnapshotTasksResultTypeDef,
    DescribeInstanceCreditSpecificationsResultTypeDef,
    DescribeInstanceEventWindowsResultTypeDef,
    DescribeInstancesResultTypeDef,
    DescribeInstanceStatusResultTypeDef,
    DescribeInstanceTypeOfferingsResultTypeDef,
    DescribeInstanceTypesResultTypeDef,
    DescribeInternetGatewaysResultTypeDef,
    DescribeIpamPoolsResultTypeDef,
    DescribeIpamScopesResultTypeDef,
    DescribeIpamsResultTypeDef,
    DescribeIpv6PoolsResultTypeDef,
    DescribeLaunchTemplatesResultTypeDef,
    DescribeLaunchTemplateVersionsResultTypeDef,
    DescribeLocalGatewayRouteTablesResultTypeDef,
    DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResultTypeDef,
    DescribeLocalGatewayRouteTableVpcAssociationsResultTypeDef,
    DescribeLocalGatewaysResultTypeDef,
    DescribeLocalGatewayVirtualInterfaceGroupsResultTypeDef,
    DescribeLocalGatewayVirtualInterfacesResultTypeDef,
    DescribeManagedPrefixListsResultTypeDef,
    DescribeMovingAddressesResultTypeDef,
    DescribeNatGatewaysResultTypeDef,
    DescribeNetworkAclsResultTypeDef,
    DescribeNetworkInsightsAccessScopeAnalysesResultTypeDef,
    DescribeNetworkInsightsAccessScopesResultTypeDef,
    DescribeNetworkInsightsAnalysesResultTypeDef,
    DescribeNetworkInsightsPathsResultTypeDef,
    DescribeNetworkInterfacePermissionsResultTypeDef,
    DescribeNetworkInterfacesResultTypeDef,
    DescribePrefixListsResultTypeDef,
    DescribePrincipalIdFormatResultTypeDef,
    DescribePublicIpv4PoolsResultTypeDef,
    DescribeReplaceRootVolumeTasksResultTypeDef,
    DescribeReservedInstancesModificationsResultTypeDef,
    DescribeReservedInstancesOfferingsResultTypeDef,
    DescribeRouteTablesResultTypeDef,
    DescribeScheduledInstanceAvailabilityResultTypeDef,
    DescribeScheduledInstancesResultTypeDef,
    DescribeSecurityGroupRulesResultTypeDef,
    DescribeSecurityGroupsResultTypeDef,
    DescribeSnapshotsResultTypeDef,
    DescribeSnapshotTierStatusResultTypeDef,
    DescribeSpotFleetInstancesResponseTypeDef,
    DescribeSpotFleetRequestsResponseTypeDef,
    DescribeSpotInstanceRequestsResultTypeDef,
    DescribeSpotPriceHistoryResultTypeDef,
    DescribeStaleSecurityGroupsResultTypeDef,
    DescribeStoreImageTasksResultTypeDef,
    DescribeSubnetsResultTypeDef,
    DescribeTagsResultTypeDef,
    DescribeTrafficMirrorFiltersResultTypeDef,
    DescribeTrafficMirrorSessionsResultTypeDef,
    DescribeTrafficMirrorTargetsResultTypeDef,
    DescribeTransitGatewayAttachmentsResultTypeDef,
    DescribeTransitGatewayConnectPeersResultTypeDef,
    DescribeTransitGatewayConnectsResultTypeDef,
    DescribeTransitGatewayMulticastDomainsResultTypeDef,
    DescribeTransitGatewayPeeringAttachmentsResultTypeDef,
    DescribeTransitGatewayRouteTablesResultTypeDef,
    DescribeTransitGatewaysResultTypeDef,
    DescribeTransitGatewayVpcAttachmentsResultTypeDef,
    DescribeTrunkInterfaceAssociationsResultTypeDef,
    DescribeVolumesModificationsResultTypeDef,
    DescribeVolumesResultTypeDef,
    DescribeVolumeStatusResultTypeDef,
    DescribeVpcClassicLinkDnsSupportResultTypeDef,
    DescribeVpcEndpointConnectionNotificationsResultTypeDef,
    DescribeVpcEndpointConnectionsResultTypeDef,
    DescribeVpcEndpointServiceConfigurationsResultTypeDef,
    DescribeVpcEndpointServicePermissionsResultTypeDef,
    DescribeVpcEndpointServicesResultTypeDef,
    DescribeVpcEndpointsResultTypeDef,
    DescribeVpcPeeringConnectionsResultTypeDef,
    DescribeVpcsResultTypeDef,
    FilterTypeDef,
    GetAssociatedIpv6PoolCidrsResultTypeDef,
    GetGroupsForCapacityReservationResultTypeDef,
    GetInstanceTypesFromInstanceRequirementsResultTypeDef,
    GetIpamAddressHistoryResultTypeDef,
    GetIpamPoolAllocationsResultTypeDef,
    GetIpamPoolCidrsResultTypeDef,
    GetIpamResourceCidrsResultTypeDef,
    GetManagedPrefixListAssociationsResultTypeDef,
    GetManagedPrefixListEntriesResultTypeDef,
    GetSpotPlacementScoresResultTypeDef,
    GetTransitGatewayAttachmentPropagationsResultTypeDef,
    GetTransitGatewayMulticastDomainAssociationsResultTypeDef,
    GetTransitGatewayPrefixListReferencesResultTypeDef,
    GetTransitGatewayRouteTableAssociationsResultTypeDef,
    GetTransitGatewayRouteTablePropagationsResultTypeDef,
    GetVpnConnectionDeviceTypesResultTypeDef,
    InstanceRequirementsRequestTypeDef,
    InstanceRequirementsWithMetadataRequestTypeDef,
    ListSnapshotsInRecycleBinResultTypeDef,
    PaginatorConfigTypeDef,
    RequestIpamResourceTagTypeDef,
    ScheduledInstanceRecurrenceRequestTypeDef,
    SearchLocalGatewayRoutesResultTypeDef,
    SearchTransitGatewayMulticastGroupsResultTypeDef,
    SlotDateTimeRangeRequestTypeDef,
    SlotStartTimeRangeRequestTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "DescribeAddressesAttributePaginator",
    "DescribeByoipCidrsPaginator",
    "DescribeCapacityReservationFleetsPaginator",
    "DescribeCapacityReservationsPaginator",
    "DescribeCarrierGatewaysPaginator",
    "DescribeClassicLinkInstancesPaginator",
    "DescribeClientVpnAuthorizationRulesPaginator",
    "DescribeClientVpnConnectionsPaginator",
    "DescribeClientVpnEndpointsPaginator",
    "DescribeClientVpnRoutesPaginator",
    "DescribeClientVpnTargetNetworksPaginator",
    "DescribeCoipPoolsPaginator",
    "DescribeDhcpOptionsPaginator",
    "DescribeEgressOnlyInternetGatewaysPaginator",
    "DescribeExportImageTasksPaginator",
    "DescribeFastLaunchImagesPaginator",
    "DescribeFastSnapshotRestoresPaginator",
    "DescribeFleetsPaginator",
    "DescribeFlowLogsPaginator",
    "DescribeFpgaImagesPaginator",
    "DescribeHostReservationOfferingsPaginator",
    "DescribeHostReservationsPaginator",
    "DescribeHostsPaginator",
    "DescribeIamInstanceProfileAssociationsPaginator",
    "DescribeImportImageTasksPaginator",
    "DescribeImportSnapshotTasksPaginator",
    "DescribeInstanceCreditSpecificationsPaginator",
    "DescribeInstanceEventWindowsPaginator",
    "DescribeInstanceStatusPaginator",
    "DescribeInstanceTypeOfferingsPaginator",
    "DescribeInstanceTypesPaginator",
    "DescribeInstancesPaginator",
    "DescribeInternetGatewaysPaginator",
    "DescribeIpamPoolsPaginator",
    "DescribeIpamScopesPaginator",
    "DescribeIpamsPaginator",
    "DescribeIpv6PoolsPaginator",
    "DescribeLaunchTemplateVersionsPaginator",
    "DescribeLaunchTemplatesPaginator",
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginator",
    "DescribeLocalGatewayRouteTableVpcAssociationsPaginator",
    "DescribeLocalGatewayRouteTablesPaginator",
    "DescribeLocalGatewayVirtualInterfaceGroupsPaginator",
    "DescribeLocalGatewayVirtualInterfacesPaginator",
    "DescribeLocalGatewaysPaginator",
    "DescribeManagedPrefixListsPaginator",
    "DescribeMovingAddressesPaginator",
    "DescribeNatGatewaysPaginator",
    "DescribeNetworkAclsPaginator",
    "DescribeNetworkInsightsAccessScopeAnalysesPaginator",
    "DescribeNetworkInsightsAccessScopesPaginator",
    "DescribeNetworkInsightsAnalysesPaginator",
    "DescribeNetworkInsightsPathsPaginator",
    "DescribeNetworkInterfacePermissionsPaginator",
    "DescribeNetworkInterfacesPaginator",
    "DescribePrefixListsPaginator",
    "DescribePrincipalIdFormatPaginator",
    "DescribePublicIpv4PoolsPaginator",
    "DescribeReplaceRootVolumeTasksPaginator",
    "DescribeReservedInstancesModificationsPaginator",
    "DescribeReservedInstancesOfferingsPaginator",
    "DescribeRouteTablesPaginator",
    "DescribeScheduledInstanceAvailabilityPaginator",
    "DescribeScheduledInstancesPaginator",
    "DescribeSecurityGroupRulesPaginator",
    "DescribeSecurityGroupsPaginator",
    "DescribeSnapshotTierStatusPaginator",
    "DescribeSnapshotsPaginator",
    "DescribeSpotFleetInstancesPaginator",
    "DescribeSpotFleetRequestsPaginator",
    "DescribeSpotInstanceRequestsPaginator",
    "DescribeSpotPriceHistoryPaginator",
    "DescribeStaleSecurityGroupsPaginator",
    "DescribeStoreImageTasksPaginator",
    "DescribeSubnetsPaginator",
    "DescribeTagsPaginator",
    "DescribeTrafficMirrorFiltersPaginator",
    "DescribeTrafficMirrorSessionsPaginator",
    "DescribeTrafficMirrorTargetsPaginator",
    "DescribeTransitGatewayAttachmentsPaginator",
    "DescribeTransitGatewayConnectPeersPaginator",
    "DescribeTransitGatewayConnectsPaginator",
    "DescribeTransitGatewayMulticastDomainsPaginator",
    "DescribeTransitGatewayPeeringAttachmentsPaginator",
    "DescribeTransitGatewayRouteTablesPaginator",
    "DescribeTransitGatewayVpcAttachmentsPaginator",
    "DescribeTransitGatewaysPaginator",
    "DescribeTrunkInterfaceAssociationsPaginator",
    "DescribeVolumeStatusPaginator",
    "DescribeVolumesPaginator",
    "DescribeVolumesModificationsPaginator",
    "DescribeVpcClassicLinkDnsSupportPaginator",
    "DescribeVpcEndpointConnectionNotificationsPaginator",
    "DescribeVpcEndpointConnectionsPaginator",
    "DescribeVpcEndpointServiceConfigurationsPaginator",
    "DescribeVpcEndpointServicePermissionsPaginator",
    "DescribeVpcEndpointServicesPaginator",
    "DescribeVpcEndpointsPaginator",
    "DescribeVpcPeeringConnectionsPaginator",
    "DescribeVpcsPaginator",
    "GetAssociatedIpv6PoolCidrsPaginator",
    "GetGroupsForCapacityReservationPaginator",
    "GetInstanceTypesFromInstanceRequirementsPaginator",
    "GetIpamAddressHistoryPaginator",
    "GetIpamPoolAllocationsPaginator",
    "GetIpamPoolCidrsPaginator",
    "GetIpamResourceCidrsPaginator",
    "GetManagedPrefixListAssociationsPaginator",
    "GetManagedPrefixListEntriesPaginator",
    "GetSpotPlacementScoresPaginator",
    "GetTransitGatewayAttachmentPropagationsPaginator",
    "GetTransitGatewayMulticastDomainAssociationsPaginator",
    "GetTransitGatewayPrefixListReferencesPaginator",
    "GetTransitGatewayRouteTableAssociationsPaginator",
    "GetTransitGatewayRouteTablePropagationsPaginator",
    "GetVpnConnectionDeviceTypesPaginator",
    "ListSnapshotsInRecycleBinPaginator",
    "SearchLocalGatewayRoutesPaginator",
    "SearchTransitGatewayMulticastGroupsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeAddressesAttributePaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeAddressesAttribute)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeaddressesattributepaginator)
    """

    def paginate(
        self,
        *,
        AllocationIds: Sequence[str] = ...,
        Attribute: Literal["domain-name"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeAddressesAttributeResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeAddressesAttribute.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeaddressesattributepaginator)
        """


class DescribeByoipCidrsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeByoipCidrs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describebyoipcidrspaginator)
    """

    def paginate(
        self, *, DryRun: bool = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeByoipCidrsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeByoipCidrs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describebyoipcidrspaginator)
        """


class DescribeCapacityReservationFleetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCapacityReservationFleets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecapacityreservationfleetspaginator)
    """

    def paginate(
        self,
        *,
        CapacityReservationFleetIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeCapacityReservationFleetsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCapacityReservationFleets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecapacityreservationfleetspaginator)
        """


class DescribeCapacityReservationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCapacityReservations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecapacityreservationspaginator)
    """

    def paginate(
        self,
        *,
        CapacityReservationIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeCapacityReservationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCapacityReservations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecapacityreservationspaginator)
        """


class DescribeCarrierGatewaysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCarrierGateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecarriergatewayspaginator)
    """

    def paginate(
        self,
        *,
        CarrierGatewayIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeCarrierGatewaysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCarrierGateways.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecarriergatewayspaginator)
        """


class DescribeClassicLinkInstancesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClassicLinkInstances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclassiclinkinstancespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        InstanceIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeClassicLinkInstancesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClassicLinkInstances.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclassiclinkinstancespaginator)
        """


class DescribeClientVpnAuthorizationRulesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnAuthorizationRules)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnauthorizationrulespaginator)
    """

    def paginate(
        self,
        *,
        ClientVpnEndpointId: str,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeClientVpnAuthorizationRulesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnAuthorizationRules.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnauthorizationrulespaginator)
        """


class DescribeClientVpnConnectionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnConnections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnconnectionspaginator)
    """

    def paginate(
        self,
        *,
        ClientVpnEndpointId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeClientVpnConnectionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnConnections.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnconnectionspaginator)
        """


class DescribeClientVpnEndpointsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnEndpoints)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnendpointspaginator)
    """

    def paginate(
        self,
        *,
        ClientVpnEndpointIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeClientVpnEndpointsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnEndpoints.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnendpointspaginator)
        """


class DescribeClientVpnRoutesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnRoutes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnroutespaginator)
    """

    def paginate(
        self,
        *,
        ClientVpnEndpointId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeClientVpnRoutesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnRoutes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpnroutespaginator)
        """


class DescribeClientVpnTargetNetworksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnTargetNetworks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpntargetnetworkspaginator)
    """

    def paginate(
        self,
        *,
        ClientVpnEndpointId: str,
        AssociationIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeClientVpnTargetNetworksResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeClientVpnTargetNetworks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeclientvpntargetnetworkspaginator)
        """


class DescribeCoipPoolsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCoipPools)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecoippoolspaginator)
    """

    def paginate(
        self,
        *,
        PoolIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeCoipPoolsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeCoipPools.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describecoippoolspaginator)
        """


class DescribeDhcpOptionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeDhcpOptions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describedhcpoptionspaginator)
    """

    def paginate(
        self,
        *,
        DhcpOptionsIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeDhcpOptionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeDhcpOptions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describedhcpoptionspaginator)
        """


class DescribeEgressOnlyInternetGatewaysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeEgressOnlyInternetGateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeegressonlyinternetgatewayspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        EgressOnlyInternetGatewayIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeEgressOnlyInternetGatewaysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeEgressOnlyInternetGateways.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeegressonlyinternetgatewayspaginator)
        """


class DescribeExportImageTasksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeExportImageTasks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeexportimagetaskspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ExportImageTaskIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeExportImageTasksResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeExportImageTasks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeexportimagetaskspaginator)
        """


class DescribeFastLaunchImagesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFastLaunchImages)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefastlaunchimagespaginator)
    """

    def paginate(
        self,
        *,
        ImageIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeFastLaunchImagesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFastLaunchImages.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefastlaunchimagespaginator)
        """


class DescribeFastSnapshotRestoresPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFastSnapshotRestores)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefastsnapshotrestorespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeFastSnapshotRestoresResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFastSnapshotRestores.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefastsnapshotrestorespaginator)
        """


class DescribeFleetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFleets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefleetspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        FleetIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeFleetsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFleets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefleetspaginator)
        """


class DescribeFlowLogsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFlowLogs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeflowlogspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        FlowLogIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeFlowLogsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFlowLogs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeflowlogspaginator)
        """


class DescribeFpgaImagesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFpgaImages)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefpgaimagespaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        FpgaImageIds: Sequence[str] = ...,
        Owners: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeFpgaImagesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeFpgaImages.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describefpgaimagespaginator)
        """


class DescribeHostReservationOfferingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeHostReservationOfferings)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describehostreservationofferingspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxDuration: int = ...,
        MinDuration: int = ...,
        OfferingId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeHostReservationOfferingsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeHostReservationOfferings.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describehostreservationofferingspaginator)
        """


class DescribeHostReservationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeHostReservations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describehostreservationspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        HostReservationIdSet: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeHostReservationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeHostReservations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describehostreservationspaginator)
        """


class DescribeHostsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeHosts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describehostspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        HostIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeHostsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeHosts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describehostspaginator)
        """


class DescribeIamInstanceProfileAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIamInstanceProfileAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeiaminstanceprofileassociationspaginator)
    """

    def paginate(
        self,
        *,
        AssociationIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeIamInstanceProfileAssociationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIamInstanceProfileAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeiaminstanceprofileassociationspaginator)
        """


class DescribeImportImageTasksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeImportImageTasks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeimportimagetaskspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ImportTaskIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeImportImageTasksResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeImportImageTasks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeimportimagetaskspaginator)
        """


class DescribeImportSnapshotTasksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeImportSnapshotTasks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeimportsnapshottaskspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ImportTaskIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeImportSnapshotTasksResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeImportSnapshotTasks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeimportsnapshottaskspaginator)
        """


class DescribeInstanceCreditSpecificationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceCreditSpecifications)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancecreditspecificationspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInstanceCreditSpecificationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceCreditSpecifications.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancecreditspecificationspaginator)
        """


class DescribeInstanceEventWindowsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceEventWindows)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstanceeventwindowspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        InstanceEventWindowIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInstanceEventWindowsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceEventWindows.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstanceeventwindowspaginator)
        """


class DescribeInstanceStatusPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceStatus)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancestatuspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        IncludeAllInstances: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInstanceStatusResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceStatus.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancestatuspaginator)
        """


class DescribeInstanceTypeOfferingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceTypeOfferings)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancetypeofferingspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        LocationType: LocationTypeType = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInstanceTypeOfferingsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceTypeOfferings.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancetypeofferingspaginator)
        """


class DescribeInstanceTypesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceTypes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancetypespaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        InstanceTypes: Sequence[InstanceTypeType] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInstanceTypesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstanceTypes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancetypespaginator)
        """


class DescribeInstancesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInstancesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInstances.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinstancespaginator)
        """


class DescribeInternetGatewaysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInternetGateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinternetgatewayspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        InternetGatewayIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeInternetGatewaysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeInternetGateways.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeinternetgatewayspaginator)
        """


class DescribeIpamPoolsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpamPools)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipampoolspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        IpamPoolIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeIpamPoolsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpamPools.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipampoolspaginator)
        """


class DescribeIpamScopesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpamScopes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipamscopespaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        IpamScopeIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeIpamScopesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpamScopes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipamscopespaginator)
        """


class DescribeIpamsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpams)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipamspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        IpamIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeIpamsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpams.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipamspaginator)
        """


class DescribeIpv6PoolsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpv6Pools)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipv6poolspaginator)
    """

    def paginate(
        self,
        *,
        PoolIds: Sequence[str] = ...,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeIpv6PoolsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeIpv6Pools.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeipv6poolspaginator)
        """


class DescribeLaunchTemplateVersionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLaunchTemplateVersions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelaunchtemplateversionspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        LaunchTemplateId: str = ...,
        LaunchTemplateName: str = ...,
        Versions: Sequence[str] = ...,
        MinVersion: str = ...,
        MaxVersion: str = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLaunchTemplateVersionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLaunchTemplateVersions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelaunchtemplateversionspaginator)
        """


class DescribeLaunchTemplatesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLaunchTemplates)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelaunchtemplatespaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        LaunchTemplateIds: Sequence[str] = ...,
        LaunchTemplateNames: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLaunchTemplatesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLaunchTemplates.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelaunchtemplatespaginator)
        """


class DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayroutetablevirtualinterfacegroupassociationspaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayRouteTableVirtualInterfaceGroupAssociationIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[
        DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResultTypeDef
    ]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayroutetablevirtualinterfacegroupassociationspaginator)
        """


class DescribeLocalGatewayRouteTableVpcAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayRouteTableVpcAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayroutetablevpcassociationspaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayRouteTableVpcAssociationIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLocalGatewayRouteTableVpcAssociationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayRouteTableVpcAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayroutetablevpcassociationspaginator)
        """


class DescribeLocalGatewayRouteTablesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayRouteTables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayroutetablespaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayRouteTableIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLocalGatewayRouteTablesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayRouteTables.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayroutetablespaginator)
        """


class DescribeLocalGatewayVirtualInterfaceGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayVirtualInterfaceGroups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayvirtualinterfacegroupspaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayVirtualInterfaceGroupIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLocalGatewayVirtualInterfaceGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayVirtualInterfaceGroups.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayvirtualinterfacegroupspaginator)
        """


class DescribeLocalGatewayVirtualInterfacesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayVirtualInterfaces)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayvirtualinterfacespaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayVirtualInterfaceIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLocalGatewayVirtualInterfacesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGatewayVirtualInterfaces.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayvirtualinterfacespaginator)
        """


class DescribeLocalGatewaysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayspaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeLocalGatewaysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeLocalGateways.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describelocalgatewayspaginator)
        """


class DescribeManagedPrefixListsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeManagedPrefixLists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describemanagedprefixlistspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PrefixListIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeManagedPrefixListsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeManagedPrefixLists.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describemanagedprefixlistspaginator)
        """


class DescribeMovingAddressesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeMovingAddresses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describemovingaddressespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PublicIps: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeMovingAddressesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeMovingAddresses.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describemovingaddressespaginator)
        """


class DescribeNatGatewaysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNatGateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenatgatewayspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        NatGatewayIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNatGatewaysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNatGateways.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenatgatewayspaginator)
        """


class DescribeNetworkAclsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkAcls)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkaclspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkAclIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkAclsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkAcls.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkaclspaginator)
        """


class DescribeNetworkInsightsAccessScopeAnalysesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsAccessScopeAnalyses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightsaccessscopeanalysespaginator)
    """

    def paginate(
        self,
        *,
        NetworkInsightsAccessScopeAnalysisIds: Sequence[str] = ...,
        NetworkInsightsAccessScopeId: str = ...,
        AnalysisStartTimeBegin: Union[datetime, str] = ...,
        AnalysisStartTimeEnd: Union[datetime, str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkInsightsAccessScopeAnalysesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsAccessScopeAnalyses.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightsaccessscopeanalysespaginator)
        """


class DescribeNetworkInsightsAccessScopesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsAccessScopes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightsaccessscopespaginator)
    """

    def paginate(
        self,
        *,
        NetworkInsightsAccessScopeIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkInsightsAccessScopesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsAccessScopes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightsaccessscopespaginator)
        """


class DescribeNetworkInsightsAnalysesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsAnalyses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightsanalysespaginator)
    """

    def paginate(
        self,
        *,
        NetworkInsightsAnalysisIds: Sequence[str] = ...,
        NetworkInsightsPathId: str = ...,
        AnalysisStartTime: Union[datetime, str] = ...,
        AnalysisEndTime: Union[datetime, str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkInsightsAnalysesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsAnalyses.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightsanalysespaginator)
        """


class DescribeNetworkInsightsPathsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsPaths)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightspathspaginator)
    """

    def paginate(
        self,
        *,
        NetworkInsightsPathIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkInsightsPathsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInsightsPaths.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinsightspathspaginator)
        """


class DescribeNetworkInterfacePermissionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInterfacePermissions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinterfacepermissionspaginator)
    """

    def paginate(
        self,
        *,
        NetworkInterfacePermissionIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkInterfacePermissionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInterfacePermissions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinterfacepermissionspaginator)
        """


class DescribeNetworkInterfacesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInterfaces)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinterfacespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkInterfaceIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeNetworkInterfacesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeNetworkInterfaces.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describenetworkinterfacespaginator)
        """


class DescribePrefixListsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribePrefixLists)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeprefixlistspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PrefixListIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribePrefixListsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribePrefixLists.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeprefixlistspaginator)
        """


class DescribePrincipalIdFormatPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribePrincipalIdFormat)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeprincipalidformatpaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Resources: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribePrincipalIdFormatResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribePrincipalIdFormat.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeprincipalidformatpaginator)
        """


class DescribePublicIpv4PoolsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribePublicIpv4Pools)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describepublicipv4poolspaginator)
    """

    def paginate(
        self,
        *,
        PoolIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribePublicIpv4PoolsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribePublicIpv4Pools.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describepublicipv4poolspaginator)
        """


class DescribeReplaceRootVolumeTasksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeReplaceRootVolumeTasks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describereplacerootvolumetaskspaginator)
    """

    def paginate(
        self,
        *,
        ReplaceRootVolumeTaskIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeReplaceRootVolumeTasksResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeReplaceRootVolumeTasks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describereplacerootvolumetaskspaginator)
        """


class DescribeReservedInstancesModificationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeReservedInstancesModifications)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describereservedinstancesmodificationspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        ReservedInstancesModificationIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeReservedInstancesModificationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeReservedInstancesModifications.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describereservedinstancesmodificationspaginator)
        """


class DescribeReservedInstancesOfferingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeReservedInstancesOfferings)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describereservedinstancesofferingspaginator)
    """

    def paginate(
        self,
        *,
        AvailabilityZone: str = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        IncludeMarketplace: bool = ...,
        InstanceType: InstanceTypeType = ...,
        MaxDuration: int = ...,
        MaxInstanceCount: int = ...,
        MinDuration: int = ...,
        OfferingClass: OfferingClassTypeType = ...,
        ProductDescription: RIProductDescriptionType = ...,
        ReservedInstancesOfferingIds: Sequence[str] = ...,
        DryRun: bool = ...,
        InstanceTenancy: TenancyType = ...,
        OfferingType: OfferingTypeValuesType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeReservedInstancesOfferingsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeReservedInstancesOfferings.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describereservedinstancesofferingspaginator)
        """


class DescribeRouteTablesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeRouteTables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeroutetablespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        RouteTableIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeRouteTablesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeRouteTables.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describeroutetablespaginator)
        """


class DescribeScheduledInstanceAvailabilityPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeScheduledInstanceAvailability)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describescheduledinstanceavailabilitypaginator)
    """

    def paginate(
        self,
        *,
        FirstSlotStartTimeRange: "SlotDateTimeRangeRequestTypeDef",
        Recurrence: "ScheduledInstanceRecurrenceRequestTypeDef",
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxSlotDurationInHours: int = ...,
        MinSlotDurationInHours: int = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeScheduledInstanceAvailabilityResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeScheduledInstanceAvailability.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describescheduledinstanceavailabilitypaginator)
        """


class DescribeScheduledInstancesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeScheduledInstances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describescheduledinstancespaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ScheduledInstanceIds: Sequence[str] = ...,
        SlotStartTimeRange: "SlotStartTimeRangeRequestTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeScheduledInstancesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeScheduledInstances.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describescheduledinstancespaginator)
        """


class DescribeSecurityGroupRulesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSecurityGroupRules)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesecuritygrouprulespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        SecurityGroupRuleIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSecurityGroupRulesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSecurityGroupRules.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesecuritygrouprulespaginator)
        """


class DescribeSecurityGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSecurityGroups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesecuritygroupspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        GroupIds: Sequence[str] = ...,
        GroupNames: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSecurityGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSecurityGroups.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesecuritygroupspaginator)
        """


class DescribeSnapshotTierStatusPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSnapshotTierStatus)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesnapshottierstatuspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSnapshotTierStatusResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSnapshotTierStatus.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesnapshottierstatuspaginator)
        """


class DescribeSnapshotsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSnapshots)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesnapshotspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        OwnerIds: Sequence[str] = ...,
        RestorableByUserIds: Sequence[str] = ...,
        SnapshotIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSnapshotsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSnapshots.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesnapshotspaginator)
        """


class DescribeSpotFleetInstancesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotFleetInstances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotfleetinstancespaginator)
    """

    def paginate(
        self,
        *,
        SpotFleetRequestId: str,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSpotFleetInstancesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotFleetInstances.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotfleetinstancespaginator)
        """


class DescribeSpotFleetRequestsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotFleetRequests)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotfleetrequestspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        SpotFleetRequestIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSpotFleetRequestsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotFleetRequests.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotfleetrequestspaginator)
        """


class DescribeSpotInstanceRequestsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotInstanceRequests)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotinstancerequestspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        SpotInstanceRequestIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSpotInstanceRequestsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotInstanceRequests.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotinstancerequestspaginator)
        """


class DescribeSpotPriceHistoryPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotPriceHistory)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotpricehistorypaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        AvailabilityZone: str = ...,
        DryRun: bool = ...,
        EndTime: Union[datetime, str] = ...,
        InstanceTypes: Sequence[InstanceTypeType] = ...,
        ProductDescriptions: Sequence[str] = ...,
        StartTime: Union[datetime, str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSpotPriceHistoryResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSpotPriceHistory.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describespotpricehistorypaginator)
        """


class DescribeStaleSecurityGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeStaleSecurityGroups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describestalesecuritygroupspaginator)
    """

    def paginate(
        self, *, VpcId: str, DryRun: bool = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeStaleSecurityGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeStaleSecurityGroups.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describestalesecuritygroupspaginator)
        """


class DescribeStoreImageTasksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeStoreImageTasks)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describestoreimagetaskspaginator)
    """

    def paginate(
        self,
        *,
        ImageIds: Sequence[str] = ...,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeStoreImageTasksResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeStoreImageTasks.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describestoreimagetaskspaginator)
        """


class DescribeSubnetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSubnets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesubnetspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        SubnetIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSubnetsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeSubnets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describesubnetspaginator)
        """


class DescribeTagsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTags)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetagspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTagsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTags.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetagspaginator)
        """


class DescribeTrafficMirrorFiltersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrafficMirrorFilters)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrafficmirrorfilterspaginator)
    """

    def paginate(
        self,
        *,
        TrafficMirrorFilterIds: Sequence[str] = ...,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTrafficMirrorFiltersResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrafficMirrorFilters.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrafficmirrorfilterspaginator)
        """


class DescribeTrafficMirrorSessionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrafficMirrorSessions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrafficmirrorsessionspaginator)
    """

    def paginate(
        self,
        *,
        TrafficMirrorSessionIds: Sequence[str] = ...,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTrafficMirrorSessionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrafficMirrorSessions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrafficmirrorsessionspaginator)
        """


class DescribeTrafficMirrorTargetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrafficMirrorTargets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrafficmirrortargetspaginator)
    """

    def paginate(
        self,
        *,
        TrafficMirrorTargetIds: Sequence[str] = ...,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTrafficMirrorTargetsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrafficMirrorTargets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrafficmirrortargetspaginator)
        """


class DescribeTransitGatewayAttachmentsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayAttachments)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayattachmentspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayAttachmentIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayAttachmentsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayAttachments.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayattachmentspaginator)
        """


class DescribeTransitGatewayConnectPeersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayConnectPeers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayconnectpeerspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayConnectPeerIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayConnectPeersResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayConnectPeers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayconnectpeerspaginator)
        """


class DescribeTransitGatewayConnectsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayConnects)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayconnectspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayAttachmentIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayConnectsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayConnects.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayconnectspaginator)
        """


class DescribeTransitGatewayMulticastDomainsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayMulticastDomains)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewaymulticastdomainspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayMulticastDomainIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayMulticastDomainsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayMulticastDomains.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewaymulticastdomainspaginator)
        """


class DescribeTransitGatewayPeeringAttachmentsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayPeeringAttachments)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewaypeeringattachmentspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayAttachmentIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayPeeringAttachmentsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayPeeringAttachments.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewaypeeringattachmentspaginator)
        """


class DescribeTransitGatewayRouteTablesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayRouteTables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayroutetablespaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayRouteTableIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayRouteTablesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayRouteTables.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayroutetablespaginator)
        """


class DescribeTransitGatewayVpcAttachmentsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayVpcAttachments)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayvpcattachmentspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayAttachmentIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewayVpcAttachmentsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGatewayVpcAttachments.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayvpcattachmentspaginator)
        """


class DescribeTransitGatewaysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTransitGatewaysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTransitGateways.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetransitgatewayspaginator)
        """


class DescribeTrunkInterfaceAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrunkInterfaceAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrunkinterfaceassociationspaginator)
    """

    def paginate(
        self,
        *,
        AssociationIds: Sequence[str] = ...,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTrunkInterfaceAssociationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeTrunkInterfaceAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describetrunkinterfaceassociationspaginator)
        """


class DescribeVolumeStatusPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVolumeStatus)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevolumestatuspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVolumeStatusResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVolumeStatus.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevolumestatuspaginator)
        """


class DescribeVolumesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVolumes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevolumespaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVolumesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVolumes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevolumespaginator)
        """


class DescribeVolumesModificationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVolumesModifications)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevolumesmodificationspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        VolumeIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVolumesModificationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVolumesModifications.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevolumesmodificationspaginator)
        """


class DescribeVpcClassicLinkDnsSupportPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcClassicLinkDnsSupport)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcclassiclinkdnssupportpaginator)
    """

    def paginate(
        self, *, VpcIds: Sequence[str] = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcClassicLinkDnsSupportResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcClassicLinkDnsSupport.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcclassiclinkdnssupportpaginator)
        """


class DescribeVpcEndpointConnectionNotificationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointConnectionNotifications)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointconnectionnotificationspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        ConnectionNotificationId: str = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcEndpointConnectionNotificationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointConnectionNotifications.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointconnectionnotificationspaginator)
        """


class DescribeVpcEndpointConnectionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointConnections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointconnectionspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcEndpointConnectionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointConnections.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointconnectionspaginator)
        """


class DescribeVpcEndpointServiceConfigurationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointServiceConfigurations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointserviceconfigurationspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        ServiceIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcEndpointServiceConfigurationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointServiceConfigurations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointserviceconfigurationspaginator)
        """


class DescribeVpcEndpointServicePermissionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointServicePermissions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointservicepermissionspaginator)
    """

    def paginate(
        self,
        *,
        ServiceId: str,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcEndpointServicePermissionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointServicePermissions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointservicepermissionspaginator)
        """


class DescribeVpcEndpointServicesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointServices)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointservicespaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        ServiceNames: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcEndpointServicesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpointServices.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointservicespaginator)
        """


class DescribeVpcEndpointsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpoints)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointspaginator)
    """

    def paginate(
        self,
        *,
        DryRun: bool = ...,
        VpcEndpointIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcEndpointsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcEndpoints.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcendpointspaginator)
        """


class DescribeVpcPeeringConnectionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcPeeringConnections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcpeeringconnectionspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        VpcPeeringConnectionIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcPeeringConnectionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcPeeringConnections.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcpeeringconnectionspaginator)
        """


class DescribeVpcsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcspaginator)
    """

    def paginate(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VpcIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeVpcsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.DescribeVpcs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#describevpcspaginator)
        """


class GetAssociatedIpv6PoolCidrsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetAssociatedIpv6PoolCidrs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getassociatedipv6poolcidrspaginator)
    """

    def paginate(
        self, *, PoolId: str, DryRun: bool = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetAssociatedIpv6PoolCidrsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetAssociatedIpv6PoolCidrs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getassociatedipv6poolcidrspaginator)
        """


class GetGroupsForCapacityReservationPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetGroupsForCapacityReservation)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getgroupsforcapacityreservationpaginator)
    """

    def paginate(
        self,
        *,
        CapacityReservationId: str,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetGroupsForCapacityReservationResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetGroupsForCapacityReservation.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getgroupsforcapacityreservationpaginator)
        """


class GetInstanceTypesFromInstanceRequirementsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetInstanceTypesFromInstanceRequirements)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getinstancetypesfrominstancerequirementspaginator)
    """

    def paginate(
        self,
        *,
        ArchitectureTypes: Sequence[ArchitectureTypeType],
        VirtualizationTypes: Sequence[VirtualizationTypeType],
        InstanceRequirements: "InstanceRequirementsRequestTypeDef",
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetInstanceTypesFromInstanceRequirementsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetInstanceTypesFromInstanceRequirements.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getinstancetypesfrominstancerequirementspaginator)
        """


class GetIpamAddressHistoryPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamAddressHistory)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipamaddresshistorypaginator)
    """

    def paginate(
        self,
        *,
        Cidr: str,
        IpamScopeId: str,
        DryRun: bool = ...,
        VpcId: str = ...,
        StartTime: Union[datetime, str] = ...,
        EndTime: Union[datetime, str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetIpamAddressHistoryResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamAddressHistory.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipamaddresshistorypaginator)
        """


class GetIpamPoolAllocationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamPoolAllocations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipampoolallocationspaginator)
    """

    def paginate(
        self,
        *,
        IpamPoolId: str,
        DryRun: bool = ...,
        IpamPoolAllocationId: str = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetIpamPoolAllocationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamPoolAllocations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipampoolallocationspaginator)
        """


class GetIpamPoolCidrsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamPoolCidrs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipampoolcidrspaginator)
    """

    def paginate(
        self,
        *,
        IpamPoolId: str,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetIpamPoolCidrsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamPoolCidrs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipampoolcidrspaginator)
        """


class GetIpamResourceCidrsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamResourceCidrs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipamresourcecidrspaginator)
    """

    def paginate(
        self,
        *,
        IpamScopeId: str,
        DryRun: bool = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        IpamPoolId: str = ...,
        ResourceId: str = ...,
        ResourceType: IpamResourceTypeType = ...,
        ResourceTag: "RequestIpamResourceTagTypeDef" = ...,
        ResourceOwner: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetIpamResourceCidrsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetIpamResourceCidrs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getipamresourcecidrspaginator)
        """


class GetManagedPrefixListAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetManagedPrefixListAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getmanagedprefixlistassociationspaginator)
    """

    def paginate(
        self,
        *,
        PrefixListId: str,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetManagedPrefixListAssociationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetManagedPrefixListAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getmanagedprefixlistassociationspaginator)
        """


class GetManagedPrefixListEntriesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetManagedPrefixListEntries)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getmanagedprefixlistentriespaginator)
    """

    def paginate(
        self,
        *,
        PrefixListId: str,
        DryRun: bool = ...,
        TargetVersion: int = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetManagedPrefixListEntriesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetManagedPrefixListEntries.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getmanagedprefixlistentriespaginator)
        """


class GetSpotPlacementScoresPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetSpotPlacementScores)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getspotplacementscorespaginator)
    """

    def paginate(
        self,
        *,
        TargetCapacity: int,
        InstanceTypes: Sequence[str] = ...,
        TargetCapacityUnitType: TargetCapacityUnitTypeType = ...,
        SingleAvailabilityZone: bool = ...,
        RegionNames: Sequence[str] = ...,
        InstanceRequirementsWithMetadata: "InstanceRequirementsWithMetadataRequestTypeDef" = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetSpotPlacementScoresResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetSpotPlacementScores.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getspotplacementscorespaginator)
        """


class GetTransitGatewayAttachmentPropagationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayAttachmentPropagations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayattachmentpropagationspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayAttachmentId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayAttachmentPropagationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayAttachmentPropagations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayattachmentpropagationspaginator)
        """


class GetTransitGatewayMulticastDomainAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayMulticastDomainAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewaymulticastdomainassociationspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayMulticastDomainId: str = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayMulticastDomainAssociationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayMulticastDomainAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewaymulticastdomainassociationspaginator)
        """


class GetTransitGatewayPrefixListReferencesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayPrefixListReferences)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayprefixlistreferencespaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayRouteTableId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayPrefixListReferencesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayPrefixListReferences.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayprefixlistreferencespaginator)
        """


class GetTransitGatewayRouteTableAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayRouteTableAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayroutetableassociationspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayRouteTableId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayRouteTableAssociationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayRouteTableAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayroutetableassociationspaginator)
        """


class GetTransitGatewayRouteTablePropagationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayRouteTablePropagations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayroutetablepropagationspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayRouteTableId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayRouteTablePropagationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetTransitGatewayRouteTablePropagations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#gettransitgatewayroutetablepropagationspaginator)
        """


class GetVpnConnectionDeviceTypesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetVpnConnectionDeviceTypes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getvpnconnectiondevicetypespaginator)
    """

    def paginate(
        self, *, DryRun: bool = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetVpnConnectionDeviceTypesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.GetVpnConnectionDeviceTypes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#getvpnconnectiondevicetypespaginator)
        """


class ListSnapshotsInRecycleBinPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.ListSnapshotsInRecycleBin)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#listsnapshotsinrecyclebinpaginator)
    """

    def paginate(
        self,
        *,
        SnapshotIds: Sequence[str] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListSnapshotsInRecycleBinResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.ListSnapshotsInRecycleBin.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#listsnapshotsinrecyclebinpaginator)
        """


class SearchLocalGatewayRoutesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.SearchLocalGatewayRoutes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#searchlocalgatewayroutespaginator)
    """

    def paginate(
        self,
        *,
        LocalGatewayRouteTableId: str,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[SearchLocalGatewayRoutesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.SearchLocalGatewayRoutes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#searchlocalgatewayroutespaginator)
        """


class SearchTransitGatewayMulticastGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.SearchTransitGatewayMulticastGroups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#searchtransitgatewaymulticastgroupspaginator)
    """

    def paginate(
        self,
        *,
        TransitGatewayMulticastDomainId: str = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[SearchTransitGatewayMulticastGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Paginator.SearchTransitGatewayMulticastGroups.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/paginators.html#searchtransitgatewaymulticastgroupspaginator)
        """
