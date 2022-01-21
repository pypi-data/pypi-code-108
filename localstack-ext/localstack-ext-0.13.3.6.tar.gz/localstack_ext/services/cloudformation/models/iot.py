from localstack.services.cloudformation.service_models import GenericBaseModel
OlPTt=staticmethod
OlPTR=classmethod
from localstack.utils.aws import aws_stack
class IoTCertificate(GenericBaseModel):
 @OlPTt
 def cloudformation_type():
  return "AWS::IoT::Certificate"
 def fetch_state(self,stack_name,resources):
  return self.state.get("certificateId")
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("certificateId")
 @OlPTR
 def get_deploy_templates(cls):
  def create_certificate_from_csr(resource_id,resources,*args,**kwargs):
   client=aws_stack.connect_to_service("iot")
   resource=cls(resources[resource_id])
   sign_req=resource.props.get("CertificateSigningRequest")
   response=client.create_certificate_from_csr(certificateSigningRequest=sign_req)
   resource.state["certificateId"]=response.get("certificateId")
   return response
  return{"create":{"function":create_certificate_from_csr}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
