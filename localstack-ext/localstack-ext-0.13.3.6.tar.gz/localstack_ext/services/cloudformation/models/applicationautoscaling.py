from localstack.utils.aws import aws_stack
Fbnmj=staticmethod
Fbnmp=None
FbnmQ=classmethod
from localstack.utils.common import select_attributes
from localstack_ext.services.cloudformation.models.servicediscovery import ServiceDiscoveryNamespace
class ApplicationAutoScalingPolicy(ServiceDiscoveryNamespace):
 @Fbnmj
 def cloudformation_type():
  return "AWS::ApplicationAutoScaling::ScalingPolicy"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("application-autoscaling")
  props=self.props
  service_ns=props.get("ServiceNamespace")
  target_id=props.get("ScalingTargetId")
  if target_id:
   service_ns=target_id.split("|")[-1]
  pol_name=self.resolve_refs_recursively(stack_name,props["PolicyName"],resources)
  service_ns=self.resolve_refs_recursively(stack_name,service_ns,resources)
  policies=client.describe_scaling_policies(ServiceNamespace=service_ns)["ScalingPolicies"]
  policy=[p for p in policies if p["PolicyName"]==pol_name]
  return(policy or[Fbnmp])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("PolicyARN")
 @FbnmQ
 def get_deploy_templates(cls):
  def get_scaling_policy_params(params,**kwargs):
   attrs=("PolicyName","ServiceNamespace","ResourceId","ScalableDimension","PolicyType","StepScalingPolicyConfiguration","TargetTrackingScalingPolicyConfiguration")
   result=select_attributes(params,attrs)
   target_id=params.get("ScalingTargetId")
   if target_id:
    parts=target_id.split("|")
    result.setdefault("ResourceId",parts[0])
    result.setdefault("ScalableDimension",parts[1])
    result.setdefault("ServiceNamespace",parts[2])
   return result
  return{"create":{"function":"put_scaling_policy","parameters":get_scaling_policy_params},"delete":{"function":"delete_scaling_policy","parameters":["PolicyName","ServiceNamespace","ResourceId","ScalableDimension"]}}
class ApplicationAutoScalingScalableTarget(ServiceDiscoveryNamespace):
 @Fbnmj
 def cloudformation_type():
  return "AWS::ApplicationAutoScaling::ScalableTarget"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("application-autoscaling")
  props=self.props
  resource_id=self.resolve_refs_recursively(stack_name,props["ResourceId"],resources)
  scal_dim=self.resolve_refs_recursively(stack_name,props["ScalableDimension"],resources)
  service_ns=self.resolve_refs_recursively(stack_name,props["ServiceNamespace"],resources)
  services=client.describe_scalable_targets(ServiceNamespace=service_ns)["ScalableTargets"]
  service=[s for s in services if s["ResourceId"]==resource_id and s["ScalableDimension"]==scal_dim and s["ServiceNamespace"]==service_ns]
  return(service or[Fbnmp])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  if not self.state:
   return
  props=self.props
  return "service/%s|%s|%s"%(props["ResourceId"],props["ScalableDimension"],props["ServiceNamespace"])
 @FbnmQ
 def get_deploy_templates(cls):
  return{"create":{"function":"register_scalable_target","parameters":["ServiceNamespace","ResourceId","ScalableDimension","MinCapacity","MaxCapacity","RoleARN","SuspendedState"]},"delete":{"function":"deregister_scalable_target","parameters":["ServiceNamespace","ResourceId","ScalableDimension"]}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
