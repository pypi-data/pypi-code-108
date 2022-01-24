from localstack.services.cloudformation.models import awslambda
bRJCp=staticmethod
bRJCY=super
bRJCy=None
bRJCB=int
bRJCG=len
bRJCi=classmethod
from localstack.services.cloudformation.service_models import REF_ARN_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
class LambdaLayerVersion(GenericBaseModel):
 @bRJCp
 def cloudformation_type():
  return "AWS::Lambda::LayerVersion"
 def get_cfn_attribute(self,attribute_name):
  if attribute_name in REF_ARN_ATTRS:
   version="$LATEST"
   return aws_stack.lambda_layer_arn(self.props["LayerName"],version=version)
  return bRJCY(LambdaLayerVersion,self).get_cfn_attribute(attribute_name)
 def fetch_state(self,stack_name,resources):
  layer_name=self.resolve_refs_recursively(stack_name,self.props.get("LayerName"),resources)
  client=aws_stack.connect_to_service("lambda")
  layers=client.list_layer_versions(LayerName=layer_name).get("LayerVersions",[])
  return layers[-1]if layers else bRJCy
 @bRJCp
 def get_deploy_templates():
  return{"create":{"function":"publish_layer_version"}}
class LambdaLayerVersionPermission(awslambda.LambdaPermission):
 @bRJCp
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
 @bRJCp
 def layer_name_and_version(params):
  layer_arn=params.get("LayerVersionArn","")
  parts=layer_arn.split(":")
  layer_name=parts[6]if ":" in layer_arn else layer_arn
  version_number=bRJCB(parts[7]if bRJCG(parts)>7 else 1)
  return layer_name,version_number
 @bRJCi
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
 @bRJCp
 def cloudformation_type():
  return "AWS::Lambda::Alias"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("lambda")
  props=self.props
  func_name=self.resolve_refs_recursively(stack_name,props.get("FunctionName"),resources)
  func_version=self.resolve_refs_recursively(stack_name,props.get("FunctionVersion"),resources)
  layers=client.list_aliases(FunctionName=func_name)["Aliases"]
  result=[lr for lr in layers if func_version in(bRJCy,lr.get("FunctionVersion"))]
  return(result or[bRJCy])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  repo_name=self.props.get("AliasArn")
  return repo_name
 @bRJCi
 def get_deploy_templates(cls):
  return{"create":{"function":"create_alias","parameters":["Description","FunctionName","FunctionVersion","Name"]}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
