from localstack.utils.aws import aws_models
tqyXM=super
tqyXb=None
tqyXU=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  tqyXM(LambdaLayer,self).__init__(arn)
  self.cwd=tqyXb
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.tqyXU.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(RDSDatabase,self).__init__(tqyXU,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(RDSCluster,self).__init__(tqyXU,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(AppSyncAPI,self).__init__(tqyXU,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(AmplifyApp,self).__init__(tqyXU,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(ElastiCacheCluster,self).__init__(tqyXU,env=env)
class TransferServer(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(TransferServer,self).__init__(tqyXU,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(CloudFrontDistribution,self).__init__(tqyXU,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,tqyXU,env=tqyXb):
  tqyXM(CodeCommitRepository,self).__init__(tqyXU,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
