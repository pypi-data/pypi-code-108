from localstack.services.cloudformation.service_models import GenericBaseModel
NJOhE=staticmethod
NJOhu=None
NJOhs=classmethod
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone
class KafkaCluster(GenericBaseModel):
 @NJOhE
 def cloudformation_type():
  return "AWS::MSK::Cluster"
 def get_physical_resource_id(self,attribute=NJOhu,**kwargs):
  return self.props.get("ClusterArn")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("kafka")
  cluster_name=self.resolve_refs_recursively(stack_name,self.props["ClusterName"],resources)
  clusters=client.list_clusters()["ClusterInfoList"]
  clusters=[c for c in clusters if c["ClusterName"]==cluster_name]
  return(clusters or[NJOhu])[0]
 @NJOhs
 def get_deploy_templates(cls):
  def _create_params(params,resource_id,resources,**kwargs):
   resource=cls(resources[resource_id])
   props=clone(resource.props)
   storage_info=props.get("BrokerNodeGroupInfo",{}).get("StorageInfo",{})
   if "EBSStorageInfo" in storage_info:
    storage_info["EbsStorageInfo"]=storage_info.pop("EBSStorageInfo")
   return props
  def _delete_params(params,resource_id,resources,**kwargs):
   resource=cls(resources[resource_id])
   return{"ClusterArn":resource.props.get("ClusterArn")}
  return{"create":{"function":"create_cluster","parameters":_create_params},"delete":{"function":"delete_cluster","parameters":_delete_params}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
