import logging
AYBCh=bool
AYBCU=True
AYBCW=False
AYBCG=Exception
AYBCt=any
AYBCK=None
import os
from localstack import config
from localstack import config as localstack_config
from localstack.runtime import hooks
from localstack.utils import common
from localstack.utils.bootstrap import(API_DEPENDENCIES,LocalstackContainer,get_enabled_apis,is_api_enabled)
from localstack.utils.docker_utils import VolumeBind
from localstack_ext import config as config_ext
from localstack_ext.bootstrap import install,licensing,local_daemon
LOG=logging.getLogger(__name__)
EXTERNAL_PORT_APIS=("apigateway","apigatewayv2","athena","cloudfront","codecommit","ecs","ecr","elasticache","mediastore","rds","transfer","kafka","neptune","azure")
API_DEPENDENCIES.update({"amplify":["s3","appsync","cognito"],"apigateway":["apigatewayv2"],"athena":["emr"],"docdb":["rds"],"ecs":["ecr"],"elasticache":["ec2"],"elb":["elbv2"],"emr":["athena","s3"],"glacier":["s3"],"glue":["rds"],"iot":["iot-analytics","iot-data","iotwireless"],"kinesisanalytics":["kinesis","dynamodb"],"neptune":["rds"],"rds":["rds-data"],"redshift":["redshift-data"],"timestream":["timestream-write","timestream-query"],"transfer":["s3"]})
get_enabled_apis.cache_clear()
def api_key_configured()->AYBCh:
 return(AYBCU if os.environ.get("LOCALSTACK_API_KEY")and os.environ.get("LOCALSTACK_API_KEY").strip()else AYBCW)
def modify_edge_port_config():
 if os.environ.get("EDGE_PORT")and not localstack_config.EDGE_PORT_HTTP:
  LOG.warning(("!! Configuring EDGE_PORT={p} without setting EDGE_PORT_HTTP may lead "+"to issues; better leave the defaults, or set EDGE_PORT=443 and EDGE_PORT_HTTP={p}").format(p=localstack_config.EDGE_PORT))
 else:
  port=localstack_config.EDGE_PORT
  localstack_config.EDGE_PORT=443
  localstack_config.EDGE_PORT_HTTP=port
@hooks.install(should_load=api_key_configured)
def install_pro_libs():
 install.install_libs()
@hooks.prepare_host(priority=100,should_load=api_key_configured)
def activate_pro_key_on_host():
 with licensing.prepare_environment():
  LOG.debug("pro activation done")
@hooks.prepare_host(should_load=api_key_configured)
def create_dns_forward():
 try:
  from localstack_ext.services import dns_server
  dns_server.setup_network_configuration()
 except AYBCG as e:
  LOG.warning("Unable to start DNS: %s"%e)
@hooks.prepare_host(should_load=api_key_configured)
def start_ec2_daemon():
 try:
  if is_api_enabled("ec2")and config_ext.EC2_AUTOSTART_DAEMON:
   LOG.debug("Starting EC2 daemon...")
   local_daemon.start_in_background()
 except AYBCG as e:
  LOG.warning("Unable to start local daemon process: %s"%e)
@hooks.configure_localstack_container(priority=10,should_load=api_key_configured)
def configure_pro_container(container:LocalstackContainer):
 try:
  from localstack_ext.services import dns_server
  docker_flags=[]
  if config_ext.use_custom_dns():
   if not common.is_port_open(dns_server.DNS_PORT,protocols="tcp"):
    docker_flags+=["-p","{a}:{p}:{p}".format(a=config_ext.DNS_ADDRESS,p=dns_server.DNS_PORT)]
   if not common.is_port_open(dns_server.DNS_PORT,protocols="udp"):
    docker_flags+=["-p","{a}:{p}:{p}/udp".format(a=config_ext.DNS_ADDRESS,p=dns_server.DNS_PORT)]
  if AYBCt([is_api_enabled(api)for api in EXTERNAL_PORT_APIS]):
   docker_flags+=["-p","{start}-{end}:{start}-{end}".format(start=config.EXTERNAL_SERVICE_PORTS_START,end=config.EXTERNAL_SERVICE_PORTS_END)]
  container.additional_flags.extend(docker_flags)
 except AYBCG as e:
  LOG.warning("failed to configure DNS: %s",e)
 modify_edge_port_config()
 if is_api_enabled("eks"):
  kube_config=os.path.expanduser("~/.kube/config")
  if os.path.exists(kube_config):
   container.volumes.add(VolumeBind(kube_config,"/root/.kube/config"))
 if is_api_enabled("azure"):
  container.ports.add(5671)
 if os.environ.get("AZURE"):
  container.ports.add(config_ext.PORT_AZURE)
@hooks.on_infra_start(should_load=api_key_configured)
def setup_pro_infra():
 _setup_logging()
 install.setup_ssl_cert()
 modify_edge_port_config()
 with licensing.prepare_environment():
  try:
   from localstack_ext.services import dns_server
   dns_server.setup_network_configuration()
  except AYBCG as e:
   LOG.warning("error setting up dns server: %s",e)
  try:
   from localstack_ext.bootstrap.dashboard import dashboard_extended
   from localstack_ext.services import edge
   from localstack_ext.utils import persistence as persistence_ext
   from localstack_ext.utils.aws import aws_utils
   persistence_ext.enable_extended_persistence()
   dashboard_extended.patch_dashboard()
   edge.patch_start_edge()
   patch_start_infra()
   aws_utils.patch_aws_utils()
   set_default_providers_to_pro()
  except AYBCG as e:
   if LOG.isEnabledFor(level=logging.DEBUG):
    LOG.exception("error enabling pro code")
   else:
    LOG.error("error enabling pro code: %s",e)
def set_default_providers_to_pro():
 from localstack.services.plugins import SERVICE_PLUGINS
 pro_services=SERVICE_PLUGINS.apis_with_provider("pro")
 localstack_config.SERVICE_PROVIDER_CONFIG.bulk_set_provider_if_not_exists(pro_services,"pro")
 eager_services=["azure"]
 for service in eager_services:
  if not is_api_enabled(service):
   continue
  try:
   LOG.debug("loading service plugin for %s",service)
   SERVICE_PLUGINS.get_service_container(service).start()
  except AYBCG as e:
   LOG.error("error while loading service %s: %s",service,e)
def patch_start_infra():
 from localstack.services import infra
 try:
  from localstack_ext.utils.aws.metadata_service import start_metadata_service
 except AYBCG:
  start_metadata_service=AYBCK
 def do_start_infra(asynchronous,apis,is_in_docker,*args,**kwargs):
  if common.in_docker():
   try:
    start_metadata_service and start_metadata_service()
   except AYBCG:
    pass
  enforce_before=config_ext.ENFORCE_IAM
  try:
   config_ext.ENFORCE_IAM=AYBCW
   return do_start_infra_orig(asynchronous,apis,is_in_docker,*args,**kwargs)
  finally:
   config_ext.ENFORCE_IAM=enforce_before
 do_start_infra_orig=infra.do_start_infra
 infra.do_start_infra=do_start_infra
def _setup_logging():
 log_level=logging.DEBUG if localstack_config.DEBUG else logging.INFO
 logging.getLogger("localstack_ext").setLevel(log_level)
 logging.getLogger("botocore").setLevel(logging.INFO)
 logging.getLogger("kubernetes").setLevel(logging.INFO)
 logging.getLogger("pyftpdlib").setLevel(logging.INFO)
 logging.getLogger("pyhive").setLevel(logging.INFO)
 logging.getLogger("websockets").setLevel(logging.INFO)
 logging.getLogger("asyncio").setLevel(logging.INFO)
 logging.getLogger("hpack").setLevel(logging.INFO)
 logging.getLogger("jnius.reflect").setLevel(logging.INFO)
 logging.getLogger("dulwich").setLevel(logging.ERROR)
 logging.getLogger("kazoo").setLevel(logging.ERROR)
 logging.getLogger("postgresql_proxy").setLevel(logging.WARNING)
 logging.getLogger("intercept").setLevel(logging.WARNING)
 logging.getLogger("root").setLevel(logging.WARNING)
 logging.getLogger("").setLevel(logging.WARNING)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
