from localstack.services.cloudformation.service_models import GenericBaseModel
jTtUs=staticmethod
jTtUG=None
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class RedshiftClusterParameterGroup(GenericBaseModel):
 @jTtUs
 def cloudformation_type():
  return "AWS::Redshift::ClusterParameterGroup"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self._get_name()
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("redshift")
  group_name=self.resolve_refs_recursively(stack_name,self._get_name(),resources)
  groups=client.describe_cluster_parameter_groups(ParameterGroupName=group_name)
  groups=groups.get("ParameterGroups")
  return(groups or[jTtUG])[0]
 def _get_name(self):
  props=self.properties
  result=props["ParameterGroupName"]=(props.get("ParameterGroupName")or "cf-pg-%s"%short_uid())
  return result
 @jTtUs
 def get_deploy_templates():
  def _group_name(resource_props,resources,resource_id,*args,**kwargs):
   resource=RedshiftClusterParameterGroup(resources[resource_id])
   return resource._get_name()
  return{"create":[{"function":"create_cluster_security_group","parameters":{"ParameterGroupName":_group_name,"ParameterGroupFamily":"ParameterGroupFamily","Description":"Description","Tags":"Tags"}},{"function":"modify_cluster_parameter_group","parameters":{"ParameterGroupName":_group_name,"Parameters":"Parameters"}}],"delete":{"function":"delete_cluster_parameter_group","parameters":{"ParameterGroupName":_group_name}}}
class RedshiftClusterSecurityGroup(GenericBaseModel):
 @jTtUs
 def cloudformation_type():
  return "AWS::Redshift::ClusterSecurityGroup"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self._get_name()
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("redshift")
  group_name=self.resolve_refs_recursively(stack_name,self._get_name(),resources)
  groups=client.describe_cluster_security_groups(ClusterSecurityGroupName=group_name)
  groups=groups.get("ClusterSecurityGroups")
  return(groups or[jTtUG])[0]
 def _get_name(self):
  props=self.properties
  result=props["SecurityGroupName"]=(props.get("SecurityGroupName")or "cf-sg-%s"%short_uid())
  return result
 @jTtUs
 def get_deploy_templates():
  def _group_name(resource_props,resources,resource_id,*args,**kwargs):
   resource=RedshiftClusterSecurityGroup(resources[resource_id])
   return resource._get_name()
  return{"create":{"function":"create_cluster_security_group","parameters":{"ClusterSecurityGroupName":_group_name,"Description":"Description"}},"delete":{"function":"delete_cluster_security_group","parameters":{"ClusterSecurityGroupName":_group_name}}}
class RedshiftClusterSubnetGroup(GenericBaseModel):
 @jTtUs
 def cloudformation_type():
  return "AWS::Redshift::ClusterSubnetGroup"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self._get_name()
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("redshift")
  group_name=self.resolve_refs_recursively(stack_name,self._get_name(),resources)
  groups=client.describe_cluster_subnet_groups(ClusterSubnetGroupName=group_name)["ClusterSubnetGroups"]
  return(groups or[jTtUG])[0]
 def _get_name(self):
  return "-".join(self.props["SubnetIds"])
 @jTtUs
 def get_deploy_templates():
  def _group_name(resource_props,*args,**kwargs):
   return "-".join(resource_props["SubnetIds"])
  return{"create":{"function":"create_cluster_subnet_group","parameters":{"ClusterSubnetGroupName":_group_name,"Description":"Description","SubnetIds":"SubnetIds","Tags":"Tags"}},"delete":{"function":"delete_cluster_subnet_group","parameters":{"ClusterSubnetGroupName":_group_name}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
