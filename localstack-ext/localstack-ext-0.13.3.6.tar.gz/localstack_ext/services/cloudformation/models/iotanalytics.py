from localstack.services.cloudformation.deployment_utils import lambda_keys_to_lower
pWQhj=staticmethod
pWQhg=None
pWQhf=classmethod
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import lambda_rename_attributes
class IoTAnalyticsChannel(GenericBaseModel):
 @pWQhj
 def cloudformation_type():
  return "AWS::IoTAnalytics::Channel"
 def fetch_state(self,stack_name,resources):
  channel_name=self.resolve_refs_recursively(stack_name,self.props.get("ChannelName"),resources)
  client=aws_stack.connect_to_service("iotanalytics")
  channels=client.list_channels(maxResults=500)["channelSummaries"]
  match=[c for c in channels if c.get("channelName")==channel_name]
  return(match or[pWQhg])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("ChannelName")
 @pWQhf
 def get_deploy_templates(cls):
  return{"create":{"function":"create_channel","parameters":{"channelName":"ChannelName","channelStorage":"ChannelStorage","retentionPeriod":"RetentionPeriod","tags":lambda_keys_to_lower("Tags")}},"delete":{"function":"delete_channel","parameters":{"channelName":"ChannelName"}}}
class IoTAnalyticsDataset(GenericBaseModel):
 @pWQhj
 def cloudformation_type():
  return "AWS::IoTAnalytics::Dataset"
 def fetch_state(self,stack_name,resources):
  dataset_name=self.resolve_refs_recursively(stack_name,self.props.get("DatasetName"),resources)
  client=aws_stack.connect_to_service("iotanalytics")
  datasets=client.list_datasets(maxResults=500)["datasetSummaries"]
  match=[d for d in datasets if d.get("datasetName")==dataset_name]
  return(match or[pWQhg])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("DatasetName")
 @pWQhf
 def get_deploy_templates(cls):
  return{"create":{"function":"create_dataset","parameters":lambda_rename_attributes({"scheduleExpression":"expression"},func=lambda_keys_to_lower())},"delete":{"function":"delete_dataset","parameters":{"datasetName":"DatasetName"}}}
class IoTAnalyticsPipeline(GenericBaseModel):
 @pWQhj
 def cloudformation_type():
  return "AWS::IoTAnalytics::Pipeline"
 def fetch_state(self,stack_name,resources):
  pipeline_name=self.resolve_refs_recursively(stack_name,self.props.get("PipelineName"),resources)
  client=aws_stack.connect_to_service("iotanalytics")
  pipelines=client.list_pipelines(maxResults=500)["pipelineSummaries"]
  match=[p for p in pipelines if p.get("pipelineName")==pipeline_name]
  return(match or[pWQhg])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("PipelineName")
 @pWQhf
 def get_deploy_templates(cls):
  return{"create":{"function":"create_pipeline","parameters":{"pipelineName":"PipelineName","pipelineActivities":lambda_keys_to_lower("PipelineActivities"),"tags":lambda_keys_to_lower("Tags")}},"delete":{"function":"delete_pipeline","parameters":{"pipelineName":"PipelineName"}}}
class IoTAnalyticsDatastore(GenericBaseModel):
 @pWQhj
 def cloudformation_type():
  return "AWS::IoTAnalytics::Datastore"
 def fetch_state(self,stack_name,resources):
  datastore_name=self.resolve_refs_recursively(stack_name,self.props.get("DatastoreName"),resources)
  client=aws_stack.connect_to_service("iotanalytics")
  datastores=client.list_datastores(maxResults=500)["datastoreSummaries"]
  match=[d for d in datastores if d.get("datastoreName")==datastore_name]
  return(match or[pWQhg])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("DatastoreName")
 @pWQhf
 def get_deploy_templates(cls):
  return{"create":{"function":"create_datastore","parameters":lambda_keys_to_lower()},"delete":{"function":"delete_datastore","parameters":{"datastoreName":"DatastoreName"}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
