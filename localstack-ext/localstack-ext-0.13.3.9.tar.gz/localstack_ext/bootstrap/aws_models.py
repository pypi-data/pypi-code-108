from localstack.utils.aws import aws_models
QawHt=super
QawHi=None
QawHo=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  QawHt(LambdaLayer,self).__init__(arn)
  self.cwd=QawHi
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.QawHo.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(RDSDatabase,self).__init__(QawHo,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(RDSCluster,self).__init__(QawHo,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(AppSyncAPI,self).__init__(QawHo,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(AmplifyApp,self).__init__(QawHo,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(ElastiCacheCluster,self).__init__(QawHo,env=env)
class TransferServer(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(TransferServer,self).__init__(QawHo,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(CloudFrontDistribution,self).__init__(QawHo,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,QawHo,env=QawHi):
  QawHt(CodeCommitRepository,self).__init__(QawHo,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
