from typing import Dict
xpLVS=staticmethod
xpLVw=None
xpLVo=str
xpLVr=super
xpLVU=int
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class RDSDBSubnetGroup(GenericBaseModel):
 @xpLVS
 def cloudformation_type():
  return "AWS::RDS::DBSubnetGroup"
 def get_physical_resource_id(self,attribute=xpLVw,**kwargs):
  return self.props.get("DBSubnetGroupName")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("rds")
  group_name=self.resolve_refs_recursively(stack_name,self.props.get("DBSubnetGroupName"),resources)
  group=client.describe_db_subnet_groups()["DBSubnetGroups"]
  match=[i for i in group if i["DBSubnetGroupName"]==group_name]
  return(match or[xpLVw])[0]
 @xpLVS
 def get_deploy_templates():
  return{"create":{"function":"create_db_subnet_group"},"delete":{"function":"delete_db_subnet_group","parameters":{"DBSubnetGroupName":"DBSubnetGroupName"}}}
class RDSDBCluster(GenericBaseModel):
 @xpLVS
 def cloudformation_type():
  return "AWS::RDS::DBCluster"
 @xpLVS
 def add_defaults(resource:Dict,stack_name:xpLVo):
  props=resource["Properties"]
  if not props.get("DBClusterIdentifier"):
   props["DBClusterIdentifier"]=f"dbc-{short_uid()}"
 def get_physical_resource_id(self,attribute=xpLVw,**kwargs):
  return self.props.get("DBClusterIdentifier")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("rds")
  clusters=client.describe_db_clusters().get("DBClusters",[])
  cluster_id=self.resolve_refs_recursively(stack_name,self.props.get("DBClusterIdentifier"),resources)
  match=[c for c in clusters if c["DBClusterIdentifier"]==cluster_id]
  return(match or[xpLVw])[0]
 def get_cfn_attribute(self,attribute):
  if attribute=="Endpoint.Address":
   return "localhost"
  props=self.props
  if attribute=="Endpoint.Port":
   return props.get("Port")or props.get("Endpoint",{}).get("Port")
  return xpLVr(RDSDBCluster,self).get_cfn_attribute(attribute)
 @xpLVS
 def get_deploy_templates():
  attrs=["AvailabilityZones","BackupRetentionPeriod","CharacterSetName","DatabaseName","DBClusterIdentifier","DBClusterParameterGroupName","VpcSecurityGroupIds","DBSubnetGroupName","Engine","EngineVersion","Port","MasterUsername","MasterUserPassword","OptionGroupName","PreferredBackupWindow","PreferredMaintenanceWindow","ReplicationSourceIdentifier","Tags","StorageEncrypted","KmsKeyId","PreSignedUrl","EnableIAMDatabaseAuthentication","BacktrackWindow","EnableCloudwatchLogsExports","EngineMode","ScalingConfiguration","DeletionProtection","GlobalClusterIdentifier","EnableHttpEndpoint","CopyTagsToSnapshot","Domain","DomainIAMRoleName","EnableGlobalWriteForwarding","SourceRegion"]
  def _params(params,**kwargs):
   params={k:v for k,v in params.items()if k in attrs}
   return params
  result={"create":{"function":"create_db_cluster","parameters":_params,"types":{"Port":xpLVU}},"delete":{"function":"delete_db_cluster","parameters":["DBClusterIdentifier"]}}
  return result
class RDSDBParameterGroup(GenericBaseModel):
 @xpLVS
 def cloudformation_type():
  return "AWS::RDS::DBParameterGroup"
 def get_physical_resource_id(self,attribute=xpLVw,**kwargs):
  return self.props.get("DBParameterGroupName")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("rds")
  props=self.props
  descr=self.resolve_refs_recursively(stack_name,props.get("Description"),resources)
  family=self.resolve_refs_recursively(stack_name,props.get("Family"),resources)
  groups=client.describe_db_parameter_groups()["DBParameterGroups"]
  match=[g for g in groups if g["Family"]==family and g["Description"]==descr]
  return(match or[xpLVw])[0]
 @xpLVS
 def get_deploy_templates():
  return{"create":{"function":"create_db_parameter_group","parameters":{"DBParameterGroupName":"DBParameterGroupName","DBParameterGroupFamily":"Family","Description":"Description","Tags":"Tags"}},"delete":{"function":"delete_db_parameter_group","parameters":["DBParameterGroupName"]}}
class RDSDBInstance(GenericBaseModel):
 @xpLVS
 def cloudformation_type():
  return "AWS::RDS::DBInstance"
 @xpLVS
 def add_defaults(resource:Dict,stack_name:xpLVo):
  props=resource["Properties"]
  if not props.get("DBInstanceIdentifier"):
   props["DBInstanceIdentifier"]=f"db-{short_uid()}"
 def get_physical_resource_id(self,attribute=xpLVw,**kwargs):
  return self.props.get("DBInstanceIdentifier")
 def get_cfn_attribute(self,attribute):
  if attribute=="Endpoint.Address":
   return "localhost"
  props=self.props
  if attribute=="Endpoint.Port":
   return props.get("Endpoint",{}).get("Port")or props.get("Port")
  return xpLVr(RDSDBInstance,self).get_cfn_attribute(attribute)
 def fetch_state(self,stack_name,resources):
  db_id=self.props.get("DBInstanceIdentifier")
  db_id=self.resolve_refs_recursively(stack_name,db_id,resources)
  client=aws_stack.connect_to_service("rds")
  instances=client.describe_db_instances()["DBInstances"]
  match=[i for i in instances if i["DBInstanceIdentifier"]==db_id]
  return(match or[xpLVw])[0]
 @xpLVS
 def get_deploy_templates():
  attrs=["DBName","DBInstanceIdentifier","AllocatedStorage","DBInstanceClass","Engine","MasterUsername","MasterUserPassword","DBSecurityGroups","AvailabilityZone","DBSubnetGroupName","PreferredMaintenanceWindow","DBParameterGroupName","BackupRetentionPeriod","PreferredBackupWindow","Port","MultiAZ","EngineVersion","AutoMinorVersionUpgrade","LicenseModel","Iops","OptionGroupName","CharacterSetName","NcharCharacterSetName","PubliclyAccessible","Tags","DBClusterIdentifier","StorageType","TdeCredentialArn","TdeCredentialPassword","StorageEncrypted","KmsKeyId","Domain","CopyTagsToSnapshot","MonitoringInterval","MonitoringRoleArn","DomainIAMRoleName","PromotionTier","Timezone","EnableIAMDatabaseAuthentication","EnablePerformanceInsights","PerformanceInsightsKMSKeyId","PerformanceInsightsRetentionPeriod","EnableCloudwatchLogsExports","ProcessorFeatures","DeletionProtection","MaxAllocatedStorage","EnableCustomerOwnedIp"]
  return{"create":{"function":"create_db_instance","parameters":attrs+[{"VpcSecurityGroupIds":"VPCSecurityGroups"}],"types":{"AllocatedStorage":xpLVU,"Port":xpLVU}},"delete":{"function":"delete_db_instance","parameters":["DBInstanceIdentifier"]}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
