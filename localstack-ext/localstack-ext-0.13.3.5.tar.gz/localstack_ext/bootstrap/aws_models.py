from localstack.utils.aws import aws_models
bROjE=super
bROjQ=None
bROja=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  bROjE(LambdaLayer,self).__init__(arn)
  self.cwd=bROjQ
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.bROja.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(RDSDatabase,self).__init__(bROja,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(RDSCluster,self).__init__(bROja,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(AppSyncAPI,self).__init__(bROja,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(AmplifyApp,self).__init__(bROja,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(ElastiCacheCluster,self).__init__(bROja,env=env)
class TransferServer(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(TransferServer,self).__init__(bROja,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(CloudFrontDistribution,self).__init__(bROja,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,bROja,env=bROjQ):
  bROjE(CodeCommitRepository,self).__init__(bROja,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
