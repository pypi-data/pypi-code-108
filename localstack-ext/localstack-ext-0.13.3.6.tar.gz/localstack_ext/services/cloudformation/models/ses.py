from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
jWiSJ=staticmethod
jWiSv=None
jWiSl=all
jWiSb=super
jWiSn=str
jWiSd=classmethod
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class SESTemplate(GenericBaseModel):
 @jWiSJ
 def cloudformation_type():
  return "AWS::SES::Template"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("ses")
  template_name=self.props.get("Template",{}).get("TemplateName")
  tmpl_name=self.resolve_refs_recursively(stack_name,template_name,resources)
  templates=client.list_templates().get("TemplatesMetadata",[])
  template=[t for t in templates if t["Name"]==tmpl_name]
  return(template or[jWiSv])[0]
 def get_physical_resource_id(self,attribute=jWiSv,**kwargs):
  return self.props.get("Template",{}).get("TemplateName")
 def update_resource(self,new_resource,stack_name,resources):
  client=aws_stack.connect_to_service("ses")
  new_props=new_resource["Properties"]
  new_template=new_props.get("Template",{})
  template=client.get_template(TemplateName=new_template["TemplateName"])["Template"]
  if jWiSl(template.get(attr,"")==new_template.get(attr,"")for attr in["SubjectPart","TextPart","HtmlPart"]):
   return
  return client.update_template(**new_props)
 @jWiSJ
 def get_deploy_templates():
  return{"create":{"function":"create_template"},"delete":{"function":"delete_template","parameters":{"TemplateName":"TemplateName"}}}
class SESReceiptRuleSet(GenericBaseModel):
 @jWiSJ
 def cloudformation_type():
  return "AWS::SES::ReceiptRuleSet"
 def get_physical_resource_id(self,attribute=jWiSv,**kwargs):
  return self.props.get("RuleSetName")
 def get_cfn_attribute(self,attribute):
  return jWiSb(SESReceiptRuleSet,self).get_cfn_attribute(attribute)
 @jWiSJ
 def add_defaults(resource,stack_name:jWiSn):
  role=resource["Properties"]
  if not role.get("RuleSetName"):
   role["RuleSetName"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("ses")
  rule_set_name=self.props.get("RuleSetName")
  rule_set_name=self.resolve_refs_recursively(stack_name,rule_set_name,resources)
  rule_set=client.describe_receipt_rule_set(RuleSetName=rule_set_name)
  return rule_set or jWiSv
 @jWiSd
 def fetch_details(cls,rule_set_name):
  client=aws_stack.connect_to_service("ses")
  rule=client.describe_receipt_rule_set(RuleSetName=rule_set_name)
  return rule or jWiSv
 @jWiSJ
 def get_deploy_templates():
  return{"create":{"function":"create_receipt_rule_set"},"delete":{"function":"delete_receipt_rule_set"}}
class SESReceiptRule(GenericBaseModel):
 @jWiSJ
 def cloudformation_type():
  return "AWS::SES::ReceiptRule"
 def get_physical_resource_id(self,attribute=jWiSv,**kwargs):
  return self.props.get("Rule",{}).get("Name")
 def get_cfn_attribute(self,attribute):
  return jWiSb(SESReceiptRule,self).get_cfn_attribute(attribute)
 @jWiSd
 def fetch_details(cls,rule_set_name,rule_name):
  client=aws_stack.connect_to_service("ses")
  rule=client.describe_receipt_rule(RuleSetName=rule_set_name,RuleName=rule_name).get("Rule")
  return rule or jWiSv
 @jWiSJ
 def add_defaults(resource,stack_name:jWiSn):
  rule=resource["Properties"]["Rule"]
  if not rule.get("Name"):
   rule["Name"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 @jWiSJ
 def get_deploy_templates():
  return{"create":{"function":"create_receipt_rule"},"delete":{"function":"delete_receipt_rule","parameters":{"RuleSetName":"RuleSetName","RuleName":lambda params,**kwargs:params["Rule"]["Name"]}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
