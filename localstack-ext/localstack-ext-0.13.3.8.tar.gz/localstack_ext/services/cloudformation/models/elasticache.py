from localstack.services.cloudformation.service_models import GenericBaseModel
mVrgN=staticmethod
mVrgc=None
mVrgH=super
mVrgu=Exception
mVrgO=len
mVrgM=str
mVrgF=classmethod
mVrgo=int
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import(lambda_convert_types,lambda_rename_attributes)
class ElastiCacheSubnetGroup(GenericBaseModel):
 @mVrgN
 def cloudformation_type():
  return "AWS::ElastiCache::SubnetGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_cache_subnet_groups().get("CacheSubnetGroups",[])
  grp_name=self.resolve_refs_recursively(stack_name,self.props["CacheSubnetGroupName"],resources)
  result=[e for e in groups if e["CacheSubnetGroupName"]==grp_name]
  return(result or[mVrgc])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("CacheSubnetGroupName")
 @mVrgN
 def get_deploy_templates():
  return{"create":{"function":"create_cache_subnet_group","parameters":{"CacheSubnetGroupName":"CacheSubnetGroupName","CacheSubnetGroupDescription":"Description","SubnetIds":"SubnetIds","Tags":"Tags"}},"delete":{"function":"delete_cache_subnet_group","parameters":["CacheSubnetGroupName"]}}
class ElastiCacheReplicationGroup(GenericBaseModel):
 @mVrgN
 def cloudformation_type():
  return "AWS::ElastiCache::ReplicationGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_replication_groups().get("ReplicationGroups",[])
  grp_desc=self.resolve_refs_recursively(stack_name,self.props["ReplicationGroupDescription"],resources)
  result=[e for e in groups if e.get("Description")==grp_desc]
  return(result or[mVrgc])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("ReplicationGroupId")
 @mVrgN
 def get_deploy_templates():
  return{"create":{"function":"create_replication_group"},"delete":{"function":"delete_replication_group","parameters":["ReplicationGroupId"]}}
class ElastiCacheSecurityGroup(GenericBaseModel):
 @mVrgN
 def cloudformation_type():
  return "AWS::ElastiCache::SecurityGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_cache_security_groups().get("CacheSecurityGroups",[])
  grp_desc=self.resolve_refs_recursively(stack_name,self.props["Description"],resources)
  result=[e for e in groups if e["Description"]==grp_desc]
  return(result or[mVrgc])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("CacheSecurityGroupName")
 @mVrgN
 def get_deploy_templates():
  return{"create":{"function":"create_cache_security_group"},"delete":{"function":"delete_cache_security_group","parameters":["CacheSecurityGroupName"]}}
class ElastiCacheParameterGroup(GenericBaseModel):
 @mVrgN
 def cloudformation_type():
  return "AWS::ElastiCache::ParameterGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_cache_parameter_groups().get("CacheParameterGroups",[])
  grp_name=self.resolve_refs_recursively(stack_name,self.props["CacheParameterGroupName"],resources)
  result=[e for e in groups if e["CacheParameterGroupName"]==grp_name]
  return(result or[mVrgc])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("CacheParameterGroupName")
 @mVrgN
 def get_deploy_templates():
  def _param_values(params,**kwargs):
   props_dict=params.get("Properties")or{}
   return[{"ParameterName":n,"ParameterValue":v}for n,v in props_dict.items()]
  return{"create":[{"function":"create_cache_parameter_group","parameters":["CacheParameterGroupName","CacheParameterGroupFamily","Description","Tags"]},{"function":"modify_cache_parameter_group","parameters":{"CacheParameterGroupName":"CacheParameterGroupName","ParameterNameValues":_param_values}}],"delete":{"function":"delete_cache_parameter_group","parameters":["CacheParameterGroupName"]}}
class ElastiCacheCluster(GenericBaseModel):
 @mVrgN
 def cloudformation_type():
  return "AWS::ElastiCache::CacheCluster"
 def get_cfn_attribute(self,attribute_name):
  try:
   result=mVrgH(ElastiCacheCluster,self).get_cfn_attribute(attribute_name)
   assert result is not mVrgc
   return result
  except mVrgu:
   props=self.props
   if attribute_name in["Port","Address"]:
    attribute_name="RedisEndpoint.%s"%attribute_name
   parts=attribute_name.split(".")
   candidates=["ConfigurationEndpoint","RedisEndpoint","Endpoint"]
   if parts[0]in candidates and mVrgO(parts)>1:
    key_name="ConfigurationEndpoint"
    if not props.get(key_name):
     self.state=self.fetch_details(props.get("ClusterName"))
    parent_obj=self.state.get(parts[0])or self.state.get(key_name)or{}
    result=parent_obj.get(parts[1])or props.get(parts[1])
    return mVrgM(result)
   return props.get(attribute_name)
 @mVrgF
 def fetch_details(cls,cluster_name):
  client=aws_stack.connect_to_service("elasticache")
  clusters=client.describe_cache_clusters(MaxRecords=500).get("CacheClusters",[])
  match=[c for c in clusters if c.get("CacheClusterId")==cluster_name]
  return(match or[mVrgc])[0]
 @mVrgN
 def get_deploy_templates():
  return{"create":{"function":"create_cache_cluster","parameters":lambda_convert_types(lambda_rename_attributes({"ClusterName":"CacheClusterId","VpcSecurityGroupIds":"SecurityGroupIds"}),{"NumCacheNodes":mVrgo})},"delete":{"function":"delete_cache_cluster","parameters":{"CacheClusterId":"ClusterName"}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
