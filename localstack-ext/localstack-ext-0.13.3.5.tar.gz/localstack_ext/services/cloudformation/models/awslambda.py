from localstack.services.cloudformation.models import awslambda
dbSNi=staticmethod
dbSNH=super
dbSNu=None
dbSNG=int
dbSNQ=len
dbSNn=classmethod
from localstack.services.cloudformation.service_models import REF_ARN_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
class LambdaLayerVersion(GenericBaseModel):
 @dbSNi
 def cloudformation_type():
  return "AWS::Lambda::LayerVersion"
 def get_cfn_attribute(self,attribute_name):
  if attribute_name in REF_ARN_ATTRS:
   version="$LATEST"
   return aws_stack.lambda_layer_arn(self.props["LayerName"],version=version)
  return dbSNH(LambdaLayerVersion,self).get_cfn_attribute(attribute_name)
 def fetch_state(self,stack_name,resources):
  layer_name=self.resolve_refs_recursively(stack_name,self.props.get("LayerName"),resources)
  client=aws_stack.connect_to_service("lambda")
  layers=client.list_layer_versions(LayerName=layer_name).get("LayerVersions",[])
  return layers[-1]if layers else dbSNu
 @dbSNi
 def get_deploy_templates():
  return{"create":{"function":"publish_layer_version"}}
class LambdaLayerVersionPermission(awslambda.LambdaPermission):
 @dbSNi
 def cloudformation_type():
  return "AWS::Lambda::LayerVersionPermission"
 def fetch_state(self,stack_name,resources):
  props=self.props
  props["LayerVersionArn"]=self.resolve_refs_recursively(stack_name,props["LayerVersionArn"],resources)
  layer_name,version_number=self.layer_name_and_version(props)
  layer_arn=aws_stack.lambda_layer_arn(layer_name)
  layer_arn_qualified="%s:%s"%(layer_arn,version_number)
  result=self.do_fetch_state(layer_name,layer_arn_qualified)
  return result
 @dbSNi
 def layer_name_and_version(params):
  layer_arn=params.get("LayerVersionArn","")
  parts=layer_arn.split(":")
  layer_name=parts[6]if ":" in layer_arn else layer_arn
  version_number=dbSNG(parts[7]if dbSNQ(parts)>7 else 1)
  return layer_name,version_number
 @dbSNn
 def get_deploy_templates(cls):
  def layer_permission_params(params,**kwargs):
   layer_name,version_number=cls.layer_name_and_version(params)
   result=select_attributes(params,["Action","Principal"])
   result["StatementId"]=short_uid()
   result["LayerName"]=layer_name
   result["VersionNumber"]=version_number
   return result
  return{"create":{"function":"add_layer_version_permission","parameters":layer_permission_params}}
class LambdaAlias(awslambda.LambdaPermission):
 @dbSNi
 def cloudformation_type():
  return "AWS::Lambda::Alias"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("lambda")
  props=self.props
  func_name=self.resolve_refs_recursively(stack_name,props.get("FunctionName"),resources)
  func_version=self.resolve_refs_recursively(stack_name,props.get("FunctionVersion"),resources)
  layers=client.list_aliases(FunctionName=func_name)["Aliases"]
  result=[lr for lr in layers if func_version in(dbSNu,lr.get("FunctionVersion"))]
  return(result or[dbSNu])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  repo_name=self.props.get("AliasArn")
  return repo_name
 @dbSNn
 def get_deploy_templates(cls):
  return{"create":{"function":"create_alias","parameters":["Description","FunctionName","FunctionVersion","Name"]}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
