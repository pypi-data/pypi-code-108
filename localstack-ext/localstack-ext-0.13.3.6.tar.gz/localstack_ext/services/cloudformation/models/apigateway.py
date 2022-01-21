from localstack.services.cloudformation.service_models import GenericBaseModel
UsSvq=staticmethod
UsSvd=None
from localstack.utils.aws import aws_stack
class ApiGatewayAuthorizer(GenericBaseModel):
 @UsSvq
 def cloudformation_type():
  return "AWS::ApiGateway::Authorizer"
 def fetch_state(self,stack_name,resources):
  props=self.props
  client=aws_stack.connect_to_service("apigateway")
  api_id=self.resolve_refs_recursively(stack_name,props["RestApiId"],resources)
  auth_uri=self.resolve_refs_recursively(stack_name,props.get("AuthorizerUri"),resources)
  authorizers=client.get_authorizers(restApiId=api_id,limit=200)["items"]
  result=[a for a in authorizers if a["type"]==props.get("Type")and a.get("authorizerUri")==auth_uri]
  return(result or[UsSvd])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("id")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
