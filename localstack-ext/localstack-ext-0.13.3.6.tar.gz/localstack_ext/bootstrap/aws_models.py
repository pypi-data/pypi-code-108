from localstack.utils.aws import aws_models
NBmxn=super
NBmxF=None
NBmxR=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  NBmxn(LambdaLayer,self).__init__(arn)
  self.cwd=NBmxF
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.NBmxR.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(RDSDatabase,self).__init__(NBmxR,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(RDSCluster,self).__init__(NBmxR,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(AppSyncAPI,self).__init__(NBmxR,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(AmplifyApp,self).__init__(NBmxR,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(ElastiCacheCluster,self).__init__(NBmxR,env=env)
class TransferServer(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(TransferServer,self).__init__(NBmxR,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(CloudFrontDistribution,self).__init__(NBmxR,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,NBmxR,env=NBmxF):
  NBmxn(CodeCommitRepository,self).__init__(NBmxR,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
