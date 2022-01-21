from localstack.services.cloudformation.deployment_utils import(lambda_keys_to_lower,params_list_to_dict)
aeLOq=staticmethod
aeLOH=None
aeLOh=super
aeLOJ=classmethod
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.utils.aws import aws_utils
class AmplifyBranch(GenericBaseModel):
 @aeLOq
 def cloudformation_type():
  return "AWS::Amplify::Branch"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("amplify")
  props=self.props
  app_id=self.resolve_refs_recursively(stack_name,props["AppId"],resources)
  branch_name=self.resolve_refs_recursively(stack_name,props["BranchName"],resources)
  branches=client.list_branches(appId=app_id)["branches"]
  branch=[b for b in branches if b["branchName"]==branch_name]
  return(branch or[aeLOH])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("BranchName")
 @aeLOq
 def get_deploy_templates():
  def get_amplify_branch_params(params,**kwargs):
   params=lambda_keys_to_lower()(params,**kwargs)
   auth_config=params.pop("basicAuthConfig",{})
   if auth_config:
    params["enableBasicAuth"]=auth_config["EnableBasicAuth"]
    params["basicAuthCredentials"]="%s:%s"%(auth_config["Username"],auth_config["Password"])
   params["tags"]=params_list_to_dict("tags",key_attr_name="key",value_attr_name="value")(params,**kwargs)
   return params
  return{"create":{"function":"create_branch","parameters":get_amplify_branch_params}}
class AmplifyApp(GenericBaseModel):
 @aeLOq
 def cloudformation_type():
  return "AWS::Amplify::App"
 def get_cfn_attribute(self,attribute_name):
  if attribute_name=="DefaultDomain":
   return "default.example.com"
  if attribute_name in REF_ID_ATTRS:
   return self.get_physical_resource_id(attribute_name)
  if attribute_name in["Arn"]:
   return self.props.get("appArn")
  return aeLOh(AmplifyApp,self).get_cfn_attribute(attribute_name)
 def get_physical_resource_id(self,attribute,**kwargs):
  props=self.props
  app_id=props.get("appId")
  if not app_id:
   return
  if attribute in REF_ID_ATTRS:
   return app_id
  return props.get("appArn")or aws_utils.amplify_app_arn(app_id)
 @aeLOJ
 def fetch_details(self,app_name):
  client=aws_stack.connect_to_service("amplify")
  apps=client.list_apps()["apps"]
  apps=[a for a in apps if a["name"]==app_name]
  return(apps or[aeLOH])[0]
 def fetch_state(self,stack_name,resources):
  app_name=self.resolve_refs_recursively(stack_name,self.props["Name"],resources)
  return self.fetch_details(app_name)
 @aeLOq
 def get_deploy_templates():
  def get_amplify_app_params(params,**kwargs):
   if "IAMServiceRole" in params:
    params["iamServiceRoleArn"]=params.pop("IAMServiceRole")
   params=lambda_keys_to_lower()(params,**kwargs)
   params["tags"]=params_list_to_dict("tags",key_attr_name="key",value_attr_name="value")(params,**kwargs)
   return params
  return{"create":{"function":"create_app","parameters":get_amplify_app_params}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
