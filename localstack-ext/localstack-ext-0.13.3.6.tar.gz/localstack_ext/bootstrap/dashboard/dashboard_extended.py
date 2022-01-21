import os
QiXKk=Exception
QiXKz=hasattr
from localstack import config
from localstack.dashboard import infra as dashboard_infra
from localstack.utils.aws import aws_stack
from localstack.utils.aws.request_context import MARKER_APIGW_REQUEST_REGION,THREAD_LOCAL
from localstack.utils.bootstrap import is_api_enabled
from localstack.utils.common import run_safe,short_uid
from localstack_ext.bootstrap.aws_models import(AmplifyApp,AppSyncAPI,CloudFrontDistribution,CodeCommitRepository,ElastiCacheCluster,RDSCluster,RDSDatabase,TransferServer)
get_graph_orig=dashboard_infra.get_graph
def get_resources(fetch_func):
 try:
  result=[]
  fetch_func(result)
  return result
 except QiXKk:
  pass
 return[]
def get_rds_databases(name_filter,pool,env):
 if not is_api_enabled("rds"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("rds")
  dbs=client.describe_db_instances()
  for inst in dbs["DBInstances"]:
   obj=RDSDatabase(id=inst["DBInstanceArn"])
   result.append(obj)
 return get_resources(fetch_func)
def get_rds_clusters(name_filter,pool,env):
 if not is_api_enabled("rds"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("rds")
  clusters=client.describe_db_clusters()
  for cluster in clusters["DBClusters"]:
   obj=RDSCluster(id=cluster["DBClusterArn"])
   result.append(obj)
 return get_resources(fetch_func)
def get_appsync_apis(name_filter,pool,env):
 if not is_api_enabled("appsync"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("appsync")
  apis=client.list_graphql_apis()
  for api in apis["graphqlApis"]:
   obj=AppSyncAPI(id=api["apiId"])
   result.append(obj)
 return get_resources(fetch_func)
def get_amplify_apps(name_filter,pool,env):
 if not is_api_enabled("amplify"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("amplify")
  apps=client.list_apps()
  for app in apps["apps"]:
   obj=AmplifyApp(id=app["appId"])
   result.append(obj)
 return get_resources(fetch_func)
def get_elasticache_clusters(name_filter,pool,env):
 if not is_api_enabled("elasticache"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("elasticache")
  clusters=client.describe_cache_clusters()
  for cluster in clusters["CacheClusters"]:
   obj=ElastiCacheCluster(id=cluster["CacheClusterId"])
   result.append(obj)
 return get_resources(fetch_func)
def get_transfer_servers(name_filter,pool,env):
 if not is_api_enabled("transfer"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("transfer")
  servers=client.list_servers()
  for server in servers["Servers"]:
   obj=TransferServer(id=server["ServerId"])
   result.append(obj)
 return get_resources(fetch_func)
def get_cloudfront_distributions(name_filter,pool,env):
 if not is_api_enabled("cloudfront"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("cloudfront")
  distros=client.list_distributions()
  for distro in distros["DistributionList"]["Items"]:
   obj=CloudFrontDistribution(id=distro["ARN"])
   result.append(obj)
 return get_resources(fetch_func)
def get_codecommit_repos(name_filter,pool,env):
 if not is_api_enabled("codecommit"):
  return[]
 def fetch_func(result):
  client=aws_stack.connect_to_service("codecommit")
  repos=client.list_repositories()
  for repo in repos["repositories"]:
   obj=CodeCommitRepository(id=repo["repositoryId"])
   result.append(obj)
 return get_resources(fetch_func)
def get_graph(*args,**kwargs):
 os.environ["AWS_ACCESS_KEY_ID"]=os.environ.get("AWS_ACCESS_KEY_ID")or "foobar"
 os.environ["AWS_SECRET_ACCESS_KEY"]=os.environ.get("AWS_SECRET_ACCESS_KEY")or "foobar"
 if QiXKz(THREAD_LOCAL,"request_context"):
  region=kwargs.get("region")or config.DEFAULT_REGION
  THREAD_LOCAL.request_context.headers[MARKER_APIGW_REQUEST_REGION]=region
 result=run_safe(get_graph_orig,*args,**kwargs)or{"nodes":[],"edges":[]}
 env=kwargs.get("env")
 name_filter=kwargs.get("name_filter")
 pool={}
 node_ids={}
 databases=get_rds_databases(name_filter,pool=pool,env=env)
 rds_clusters=get_rds_clusters(name_filter,pool=pool,env=env)
 appsync_apis=get_appsync_apis(name_filter,pool=pool,env=env)
 amplify_apps=get_amplify_apps(name_filter,pool=pool,env=env)
 elasticache_clusters=get_elasticache_clusters(name_filter,pool=pool,env=env)
 transfer_servers=get_transfer_servers(name_filter,pool=pool,env=env)
 cloudfront_distributions=get_cloudfront_distributions(name_filter,pool=pool,env=env)
 codecommit_repos=get_codecommit_repos(name_filter,pool=pool,env=env)
 resources={"rds_db":databases,"rds_cluster":rds_clusters,"appsync_api":appsync_apis,"amplify_app":amplify_apps,"elasticache_cluster":elasticache_clusters,"transfer_server":transfer_servers,"cloudfront_distr":cloudfront_distributions,"codecommit_repo":codecommit_repos}
 for res_type,res_list in resources.items():
  for res in res_list:
   uid=short_uid()
   node_ids[res.id]=uid
   result["nodes"].append({"id":uid,"arn":res.id,"name":res.name(),"type":res_type})
 return result
def patch_dashboard():
 dashboard_infra.get_graph=get_graph
# Created by pyminifier (https://github.com/liftoff/pyminifier)
