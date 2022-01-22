from typing import Tuple
JDzdN=staticmethod
JDzdp=None
JDzdm=classmethod
JDzde=str
from localstack.services.cloudformation.deployment_utils import param_json_to_str
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone,select_attributes
from localstack_ext.services.cloudformation.service_models import LOG
class EC2VPCEndpoint(GenericBaseModel):
 @JDzdN
 def cloudformation_type():
  return "AWS::EC2::VPCEndpoint"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("ec2")
  result=client.describe_vpc_endpoints(Filters=[{"Name":"service-name","Values":[self.props["ServiceName"]]},{"Name":"vpc-id","Values":[self.props["VpcId"]]}])
  result=result["VpcEndpoints"]
  return(result or[JDzdp])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("VpcEndpointId")
 @JDzdN
 def get_deploy_templates():
  return{"create":{"function":"create_vpc_endpoint","parameters":{"ServiceName":"ServiceName","PolicyDocument":param_json_to_str("PolicyDocument"),"VpcId":"VpcId","SecurityGroupIds":"SecurityGroupIds","SubnetIds":"SubnetIds","RouteTableIds":"RouteTableIds","VpcEndpointType":"VpcEndpointType","PrivateDnsEnabled":"PrivateDnsEnabled"}}}
class EC2ElasticIP(GenericBaseModel):
 @JDzdN
 def cloudformation_type():
  return "AWS::EC2::EIP"
 def get_physical_resource_id(self,attribute=JDzdp,**kwargs):
  return self.props.get("PublicIp")
 def fetch_state(self,stack_name,resources):
  if self.get_physical_resource_id():
   return self.state
 @JDzdm
 def get_deploy_templates(cls):
  def allocate_address(resource_id,resources,resource_type,func,stack_name,*args,**kwargs):
   resource=cls(resources[resource_id])
   resource.fetch_and_update_state(stack_name,resources)
   client=aws_stack.connect_to_service("ec2")
   kwargs=select_attributes(resource.props,["Domain","PublicIpv4Pool"])
   result=client.allocate_address(**kwargs)
   resource.state.update(result)
   return result
  return{"create":{"function":allocate_address},"delete":{"function":"release_address","parameters":["PublicIp","AllocationId"]}}
class SubnetRouteTableAssociation(GenericBaseModel):
 @JDzdN
 def cloudformation_type():
  return "AWS::EC2::SubnetRouteTableAssociation"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("RouteTableAssociationId")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("ec2")
  props=self.props
  table_id=self.resolve_refs_recursively(stack_name,props["RouteTableId"],resources)
  subnet_id=self.resolve_refs_recursively(stack_name,props["SubnetId"],resources)
  tables=client.describe_route_tables(RouteTableIds=[table_id])["RouteTables"]
  tables=[t for t in tables if t["RouteTableId"]==table_id]
  if tables:
   associations=tables[0].get("Associations",[])
   matching=[a for a in associations if a.get("SubnetId")==subnet_id]
   return(matching or[JDzdp])[0]
 @JDzdN
 def get_deploy_templates():
  return{"create":{"function":"associate_route_table","parameters":{"RouteTableId":"RouteTableId","SubnetId":"SubnetId"}},"delete":{"function":"disassociate_route_table","parameters":{"AssociationId":"PhysicalResourceId"}}}
class SecurityGroupInOrEgress(GenericBaseModel):
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   props=self.props
   res_id="%s_%s_%s"%(props.get("IpProtocol"),props.get("FromPort"),props.get("ToPort"))
   return res_id
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("ec2")
  rp=self.props
  kwargs=({"GroupNames":[rp.get("GroupName")]}if rp.get("GroupName")else{"GroupIds":[rp["GroupId"]]})
  result=client.describe_security_groups(**kwargs)["SecurityGroups"]
  src_grp_name=rp.get("SourceSecurityGroupName")
  src_grp_id=rp.get("SourceSecurityGroupId")
  dst_grp_id=rp.get("DestinationSecurityGroupId")
  if not result:
   return
  perms=result[0].get("IpPermissions" if self.is_ingress()else "IpPermissionsEgress")
  for perm in perms:
   if JDzde(perm["IpProtocol"])!=JDzde(rp["IpProtocol"]):
    continue
   if perm.get("FromPort")!=rp.get("FromPort")or perm.get("ToPort")!=rp.get("ToPort"):
    continue
   if not self.is_ingress():
    return perm
   groups=perm.get("UserIdGroupPairs",[])
   groups=[g for g in groups if g.get("GroupId")in[src_grp_id,dst_grp_id]or g.get("GroupName")==src_grp_name]
   if groups:
    return perm
 @JDzdm
 def is_ingress(cls):
  return "Ingress" in cls.cloudformation_type()
 @JDzdm
 def get_vpc_and_name_for_security_group(cls,group_id:JDzde)->Tuple[JDzde,JDzde]:
  client=aws_stack.connect_to_service("ec2")
  groups=client.describe_security_groups(GroupIds=[group_id])["SecurityGroups"]
  vpc_id=groups and groups[0].get("VpcId")or JDzdp
  group_name=groups and groups[0]["GroupName"]or JDzdp
  return vpc_id,group_name
 @JDzdm
 def get_deploy_templates(cls):
  def create_params(params,**kwargs):
   result=clone(params)
   source_group_name=result.get("SourceSecurityGroupName")
   source_group_id=result.pop("SourceSecurityGroupId",JDzdp)
   vpc_id=JDzdp
   if cls.is_ingress()and source_group_id and not source_group_name:
    vpc_id,group_name=cls.get_vpc_and_name_for_security_group(source_group_id)
    result["SourceSecurityGroupName"]=group_name
   dst_group_id=result.pop("DestinationSecurityGroupId",JDzdp)
   if cls.is_ingress()and not dst_group_id:
    dst_group_id=result.get("GroupId")
    if dst_group_id and not vpc_id:
     vpc_id,_=cls.get_vpc_and_name_for_security_group(dst_group_id)
   if not cls.is_ingress()and not dst_group_id:
    LOG.info("TODO: Add support for DestinationPrefixListId for %s"%cls.cloudformation_type())
   if result.get("IpProtocol"):
    result["IpProtocol"]=JDzde(result.get("IpProtocol"))
   description=result.pop("Description",JDzdp)
   cidr_ipv6=result.pop("CidrIpv6",JDzdp)
   if cidr_ipv6 or vpc_id:
    cidr_ip=result.get("CidrIp")
    cidr_ip=cidr_ip or("127.0.0.1/32" if description else cidr_ip)
    ipv6_range={"CidrIpv6":cidr_ipv6,"Description":description}
    ip_range={"CidrIp":cidr_ip,"Description":description}
    groups=[]
    if source_group_id:
     groups.append({"GroupId":source_group_id,"GroupName":source_group_name,"Description":description,"VpcId":vpc_id})
    if dst_group_id:
     groups.append({"GroupId":dst_group_id,"Description":description,"VpcId":vpc_id})
    ip_perm={"IpProtocol":result.get("IpProtocol"),"UserIdGroupPairs":groups,"FromPort":result.get("FromPort"),"ToPort":result.get("ToPort")}
    ip_perm["IpRanges"]=cidr_ip and[ip_range]
    ip_perm["Ipv6Ranges"]=cidr_ipv6 and[ipv6_range]
    result["IpPermissions"]=[ip_perm]
   else:
    LOG.debug('Neither "VpcId" nor "CidrIpv6" found in CF params: %s'%params)
   return result
  func_name=("authorize_security_group_ingress" if cls.is_ingress()else "authorize_security_group_egress")
  return{"create":{"function":func_name,"parameters":create_params}}
class SecurityGroupEgress(SecurityGroupInOrEgress):
 @JDzdN
 def cloudformation_type():
  return "AWS::EC2::SecurityGroupEgress"
class SecurityGroupIngress(SecurityGroupInOrEgress):
 @JDzdN
 def cloudformation_type():
  return "AWS::EC2::SecurityGroupIngress"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
