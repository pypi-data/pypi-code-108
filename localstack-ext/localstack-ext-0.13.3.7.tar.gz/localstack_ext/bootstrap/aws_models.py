from localstack.utils.aws import aws_models
yvFMi=super
yvFMJ=None
yvFMp=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  yvFMi(LambdaLayer,self).__init__(arn)
  self.cwd=yvFMJ
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.yvFMp.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(RDSDatabase,self).__init__(yvFMp,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(RDSCluster,self).__init__(yvFMp,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(AppSyncAPI,self).__init__(yvFMp,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(AmplifyApp,self).__init__(yvFMp,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(ElastiCacheCluster,self).__init__(yvFMp,env=env)
class TransferServer(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(TransferServer,self).__init__(yvFMp,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(CloudFrontDistribution,self).__init__(yvFMp,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,yvFMp,env=yvFMJ):
  yvFMi(CodeCommitRepository,self).__init__(yvFMp,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
