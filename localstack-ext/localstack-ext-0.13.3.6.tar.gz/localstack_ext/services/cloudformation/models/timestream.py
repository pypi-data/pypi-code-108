from typing import Dict
uBwpP=staticmethod
uBwph=str
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class TimestreamDatabase(GenericBaseModel):
 @uBwpP
 def cloudformation_type():
  return "AWS::Timestream::Database"
 @uBwpP
 def add_defaults(resource:Dict,stack_name:uBwph):
  props=resource["Properties"]
  if not props.get("DatabaseName"):
   props["DatabaseName"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("timestream-write")
  db_name=self.resolve_refs_recursively(stack_name,self.props.get("DatabaseName"),resources)
  result=client.describe_database(DatabaseName=db_name)
  return result["Database"]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("DatabaseName")
 @uBwpP
 def get_deploy_templates():
  return{"create":{"function":"create_database"},"delete":{"function":"delete_database","parameters":["DatabaseName"]}}
class TimestreamTable(GenericBaseModel):
 @uBwpP
 def cloudformation_type():
  return "AWS::Timestream::Table"
 @uBwpP
 def add_defaults(resource:Dict,stack_name:uBwph):
  props=resource["Properties"]
  if not props.get("TableName"):
   props["TableName"]=f"t{short_uid()}"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("timestream-write")
  db_name=self.resolve_refs_recursively(stack_name,self.props.get("DatabaseName"),resources)
  table_name=self.resolve_refs_recursively(stack_name,self.props.get("TableName"),resources)
  if not db_name:
   return
  result=client.describe_table(DatabaseName=db_name,TableName=table_name)
  return result["Table"]
 def get_physical_resource_id(self,attribute,**kwargs):
  props=self.props
  return f"{props.get('DatabaseName')}|{props.get('TableName')}"
 @uBwpP
 def get_deploy_templates():
  return{"create":{"function":"create_table"},"delete":{"function":"delete_table","parameters":["DatabaseName","TableName"]}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
