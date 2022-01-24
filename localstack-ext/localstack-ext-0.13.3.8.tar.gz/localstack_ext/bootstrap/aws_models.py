from localstack.utils.aws import aws_models
Eqvdi=super
EqvdJ=None
Eqvdk=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  Eqvdi(LambdaLayer,self).__init__(arn)
  self.cwd=EqvdJ
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.Eqvdk.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(RDSDatabase,self).__init__(Eqvdk,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(RDSCluster,self).__init__(Eqvdk,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(AppSyncAPI,self).__init__(Eqvdk,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(AmplifyApp,self).__init__(Eqvdk,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(ElastiCacheCluster,self).__init__(Eqvdk,env=env)
class TransferServer(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(TransferServer,self).__init__(Eqvdk,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(CloudFrontDistribution,self).__init__(Eqvdk,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,Eqvdk,env=EqvdJ):
  Eqvdi(CodeCommitRepository,self).__init__(Eqvdk,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
