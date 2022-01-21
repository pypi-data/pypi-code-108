from typing import Dict
BLgqX=staticmethod
BLgqm=None
BLgqd=str
BLgqz=False
from localstack.services.cloudformation.deployment_utils import(generate_default_name_without_stack,params_list_to_dict)
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class QLDBLedger(GenericBaseModel):
 @BLgqX
 def cloudformation_type():
  return "AWS::QLDB::Ledger"
 def get_physical_resource_id(self,attribute=BLgqm,**kwargs):
  return self.props.get("Name")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("qldb")
  ledger_name=self.resolve_refs_recursively(stack_name,self.props.get("Name"),resources)
  result=client.describe_ledger(Name=ledger_name)
  return result
 @BLgqX
 def add_defaults(resource:Dict,stack_name:BLgqd):
  props=resource["Properties"]
  if not props.get("Name"):
   props["Name"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 @BLgqX
 def get_deploy_templates():
  def _delete_ledger(resource_id,resources,*args,**kwargs):
   qldb=aws_stack.connect_to_service("qldb")
   props=resources[resource_id]["Properties"]
   ledger_name=props.get("Name")
   qldb.update_ledger(Name=ledger_name,DeletionProtection=BLgqz)
   qldb.delete_ledger(Name=ledger_name)
  return{"create":{"function":"create_ledger","parameters":["KmsKey","DeletionProtection","Name","PermissionsMode",{"Tags":params_list_to_dict("Tags")}]},"delete":{"function":_delete_ledger}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
