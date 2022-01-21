from localstack import config
hdQbD=staticmethod
hdQbw=None
hdQbk=classmethod
hdQbS=str
hdQbr=False
hdQbq=True
hdQbJ=super
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone,items_equivalent
from localstack_ext import config as ext_config
from localstack_ext.services.cloudformation.service_models import LOG
class ELBV2TargetGroup(GenericBaseModel):
 @hdQbD
 def cloudformation_type():
  return "AWS::ElasticLoadBalancingV2::TargetGroup"
 def get_physical_resource_id(self,attribute=hdQbw,**kwargs):
  return self.props.get("TargetGroupArn")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elbv2")
  group_name=self.resolve_refs_recursively(stack_name,self.props.get("Name"),resources)
  result=client.describe_target_groups()["TargetGroups"]
  result=[g for g in result if g.get("TargetGroupName")==group_name]
  return(result or[hdQbw])[0]
 @hdQbk
 def get_deploy_templates(cls):
  def register_targets(resource_id,resources,resource_type,func,stack_name,*args,**kwargs):
   resource=cls(resources[resource_id])
   resource.fetch_and_update_state(stack_name,resources)
   props=resource.props
   targets=props.get("Targets")
   if targets:
    client=aws_stack.connect_to_service("elbv2")
    group_arn=props.get("TargetGroupArn")
    client.register_targets(TargetGroupArn=group_arn,Targets=targets)
  def modify_target_group_attributes(resource_id,resources,*args,**kwargs):
   resource=cls(resources[resource_id])
   props=resource.props
   attrs=props.get("TargetGroupAttributes")
   if attrs:
    client=aws_stack.connect_to_service("elbv2")
    group_arn=props.get("TargetGroupArn")
    for attr in attrs:
     attr["Value"]=hdQbS(attr.get("Value",""))
    client.modify_target_group_attributes(TargetGroupArn=group_arn,Attributes=attrs)
  param_names=["Name","Protocol","ProtocolVersion","Port","VpcId","HealthCheckProtocol","HealthCheckPort","HealthCheckEnabled","HealthCheckPath","HealthCheckIntervalSeconds","HealthCheckTimeoutSeconds","HealthyThresholdCount","UnhealthyThresholdCount","Matcher","TargetType","Tags"]
  return{"create":[{"function":"create_target_group","parameters":param_names},{"function":register_targets},{"function":modify_target_group_attributes}]}
class ELBV2ListenerRule(GenericBaseModel):
 @hdQbD
 def cloudformation_type():
  return "AWS::ElasticLoadBalancingV2::ListenerRule"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("RuleArn")
 def fetch_state(self,stack_name,resources):
  def actions_match(rule):
   def _matches(action,_action):
    auth_config=action.get("AuthenticateCognitoConfig",{})
    for f in["Type","Order"]:
     if action.get(f)!=_action.get(f):
      return hdQbr
    _auth_config=_action.get("AuthenticateCognitoConfig",{})
    for f in["UserPoolArn","UserPoolClientId","UserPoolDomain"]:
     if auth_config.get(f)!=_auth_config.get(f):
      return hdQbr
    return hdQbq
   actions1=rule.get("Actions",[])
   return items_equivalent(actions,actions1,_matches)
  def conditions_match(rule):
   def _matches(cond,_cond):
    cond_values_wrapper=([cond.get(a)for a in candidate_attrs if cond.get(a)]+[cond])[0]
    if cond.get("Field")!=_cond.get("Field"):
     return hdQbr
    for cand in candidate_attrs:
     _cond=_cond.get(cand)or _cond
    cond_values=cond_values_wrapper.get("Values",[])
    if cond_values!=_cond.get("Values"):
     return hdQbr
    return hdQbq
   conditions1=rule.get("Conditions",[])
   candidate_attrs=["HostHeaderConfig","HttpHeaderConfig","HttpRequestMethodConfig","PathPatternConfig","QueryStringConfig","SourceIpConfig"]
   return items_equivalent(conditions,conditions1,_matches)
  client=aws_stack.connect_to_service("elbv2")
  rp=self.props
  conditions=rp.get("Conditions",[])
  actions=rp.get("Actions",[])
  list_arn=self.resolve_refs_recursively(stack_name,rp.get("ListenerArn"),resources)
  result=client.describe_rules(ListenerArn=list_arn)["Rules"]
  result=[r for r in result if actions_match(r)and conditions_match(r)]
  return(result or[hdQbw])[0]
 @hdQbD
 def get_deploy_templates():
  return{"create":{"function":"create_rule"}}
class ELBV2Listener(GenericBaseModel):
 @hdQbD
 def cloudformation_type():
  return "AWS::ElasticLoadBalancingV2::Listener"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("ListenerArn")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elbv2")
  props=self.props
  lb_arn=self.resolve_refs_recursively(stack_name,props.get("LoadBalancerArn"),resources)
  proto=self.resolve_refs_recursively(stack_name,props.get("Protocol"),resources)
  port=self.resolve_refs_recursively(stack_name,props.get("Port"),resources)
  result=client.describe_listeners(LoadBalancerArn=lb_arn)["Listeners"]
  port_candidates=[hdQbS(config.EDGE_PORT),hdQbS(config.EDGE_PORT_HTTP)]
  result_filtered=[ls for ls in result if ls.get("LoadBalancerArn")==lb_arn and(hdQbS(port or "")in[hdQbS(ls.get("Port")),""]or hdQbS(ls.get("Port"))in port_candidates)and ls.get("Protocol")==proto]
  if result and not result_filtered:
   LOG.debug("No matching entry when filtering ELBv2 listeners %s for props %s"%(result,props))
  return(result_filtered or[hdQbw])[0]
 @hdQbD
 def get_deploy_templates():
  def create_params(params,**kwargs):
   result=clone(params)
   for action in result.get("DefaultActions",[]):
    config=action.get("RedirectConfig",{})
    config["StatusCode"]=config.get("StatusCode")or "HTTP_301"
    config["Port"]=config.get("Port")and hdQbS(config["Port"])
   return result
  return{"create":{"function":"create_listener","parameters":create_params}}
class ELBV2LoadBalancer(GenericBaseModel):
 @hdQbD
 def cloudformation_type():
  return "AWS::ElasticLoadBalancingV2::LoadBalancer"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("LoadBalancerArn")
 def fetch_state(self,stack_name,resources):
  bal_name=self.props.get("Name")
  bal_name=self.resolve_refs_recursively(stack_name,bal_name,resources)
  client=aws_stack.connect_to_service("elbv2")
  result=client.describe_load_balancers()["LoadBalancers"]
  result=[bal for bal in result if bal["LoadBalancerName"]==bal_name]
  return(result or[hdQbw])[0]
 def get_cfn_attribute(self,attribute_name):
  if attribute_name=="DNSName":
   lb_arn=self.props.get("LoadBalancerArn")
   return "%s.elb.%s"%(lb_arn.split("/")[2],ext_config.RESOURCES_BASE_DOMAIN_NAME)
  return hdQbJ(ELBV2LoadBalancer,self).get_cfn_attribute(attribute_name)
 @hdQbD
 def get_deploy_templates():
  def get_elbv2_loadbalancer_params(params,**kwargs):
   result=clone(params)
   result.pop("LoadBalancerAttributes",[])
   result["Name"]=result.get("Name")or kwargs.get("resource_id")
   return result
  def get_elbv2_loadbalancer_attrs_params(params,**kwargs):
   lb_name=params.get("Name")or kwargs.get("resource_id")
   result=aws_stack.connect_to_service("elbv2").describe_load_balancers()["LoadBalancers"]
   result=[bal for bal in result if bal["LoadBalancerName"]==lb_name]
   result={"LoadBalancerArn":result and result[0]["LoadBalancerArn"]or lb_name,"Attributes":params.get("LoadBalancerAttributes",[])}
   return result
  return{"create":[{"function":"create_load_balancer","parameters":get_elbv2_loadbalancer_params},{"function":"modify_load_balancer_attributes","parameters":get_elbv2_loadbalancer_attrs_params}]}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
