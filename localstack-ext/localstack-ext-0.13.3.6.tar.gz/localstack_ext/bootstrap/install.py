import logging
uYSaM=str
uYSaB=isinstance
uYSaA=False
uYSas=Exception
uYSam=None
uYSai=True
uYSaf=bool
import os
import re
import threading
import traceback
from typing import List,Union
import localstack
from localstack import constants
from localstack.services.install import(INSTALL_DIR_STEPFUNCTIONS,INSTALL_PATH_STEPFUNCTIONS_JAR,JAR_URLS,SFN_PATCH_URL_PREFIX,Installer,InstallerRepository,add_file_to_jar)
from localstack.utils.common import(download,file_exists_not_empty,in_docker,is_command_available,is_debian,now,rm_rf,run,save_file)
from localstack_ext.bootstrap.licensing import(api_key_configured,is_enterprise,prepare_environment)
from localstack_ext.constants import ARTIFACTS_REPO
LOG=logging.getLogger(__name__)
RULE_ENGINE_INSTALL_URL="https://github.com/whummer/serverless-iot-offline"
H2_DOWNLOAD_URL="http://www.h2database.com/h2-2019-10-14.zip"
SSL_CERT_URL="%s/raw/master/local-certs/server.key"%ARTIFACTS_REPO
SSL_CERT_URL_FALLBACK="{api_endpoint}/proxy/localstack.cert.key"
INFRA_DIR=os.path.join(os.path.dirname(localstack.__file__),"infra")
LOCALSTACK_DIR=os.path.dirname(localstack.__file__)
POSTGRES_LIB_FOLDER="/usr/lib/postgresql/11/lib"
SFN_PATCH_PRO_CLASS1="cloud/localstack/PersistenceAspect.class"
SFN_PATCH_PRO_CLASS2="cloud/localstack/PersistenceContext.class"
SFN_PATCH_PRO_CLASS3="cloud/localstack/PersistenceState.class"
SFN_PATCH_PRO_CLASS4="cloud/localstack/PersistenceRegionState.class"
SFN_PATCH_PRO_FILE_METAINF="META-INF/aop-pro.xml"
MAVEN_REPO="https://repo1.maven.org/maven2"
URL_KRYO=f"{MAVEN_REPO}/com/esotericsoftware/kryo/5.2.0/kryo-5.2.0.jar"
URL_OBJENESIS=f"{MAVEN_REPO}/org/objenesis/objenesis/3.2/objenesis-3.2.jar"
URL_MINLOG=f"{MAVEN_REPO}/com/esotericsoftware/minlog/1.3.1/minlog-1.3.1.jar"
URL_REFLECTASM=f"{MAVEN_REPO}/com/esotericsoftware/reflectasm/1.11.9/reflectasm-1.11.9.jar"
PRO_JAR_URLS=[URL_KRYO,URL_OBJENESIS,URL_MINLOG,URL_REFLECTASM]
INSTALL_LOCK=threading.RLock()
def install_libs():
 install_iot_rule_engine()
 install_postgres()
 install_timescaledb()
 install_redis()
 install_mqtt()
 install_stepfunctions()
def install_iot_rule_engine():
 target_dir=LOCALSTACK_DIR
 main_file=os.path.join(target_dir,"node_modules","serverless-iot-offline","query.js")
 if not os.path.exists(main_file):
  LOG.info("Installing IoT rule engine. This may take a while.")
  run("cd %s; npm install %s"%(target_dir,RULE_ENGINE_INSTALL_URL))
 return main_file
def install_postgres():
 if not in_docker():
  return
 check_or_install("psql","postgresql-11","RDS")
 check_or_install("pg_config",["postgresql-server-dev-11","libpq-dev"],"RDS")
 if not is_debian():
  return
 plpython_lib=f"{POSTGRES_LIB_FOLDER}/plpython3.so"
 if os.path.exists(plpython_lib):
  return
 install_package("postgresql-plpython3-11","RDS")
def install_timescaledb():
 if not in_docker():
  return
 if os.path.exists(f"{POSTGRES_LIB_FOLDER}/timescaledb.so"):
  return
 check_or_install("gcc",["cmake","gcc","git"],"Timestream")
 ts_dir="/tmp/timescaledb"
 tag="2.0.0-rc4"
 run("cd /tmp; git clone https://github.com/timescale/timescaledb.git")
 run("cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install"%(ts_dir,tag))
 rm_rf("/tmp/timescaledb")
def install_redis():
 check_or_install("redis-server","redis-server","ElastiCache")
 return "redis-server"
def install_mqtt():
 check_or_install("mosquitto","mosquitto","IoT")
 return "mosquitto"
def install_stepfunctions():
 classes=[SFN_PATCH_PRO_CLASS1,SFN_PATCH_PRO_CLASS2,SFN_PATCH_PRO_CLASS3,SFN_PATCH_PRO_CLASS4,SFN_PATCH_PRO_FILE_METAINF]
 for patch_class in classes:
  patch_url=f"{SFN_PATCH_URL_PREFIX}/{patch_class}"
  add_file_to_jar(patch_class,patch_url,target_jar=INSTALL_PATH_STEPFUNCTIONS_JAR)
 manifest_file=os.path.join(INSTALL_DIR_STEPFUNCTIONS,"META-INF","MANIFEST.MF")
 content=run(["unzip","-p",INSTALL_PATH_STEPFUNCTIONS_JAR,"META-INF/MANIFEST.MF"])
 content=re.sub("Main-Class: .+","Main-Class: cloud.localstack.StepFunctionsStarter",content)
 classpath=" ".join([os.path.basename(jar)for jar in[*PRO_JAR_URLS,*JAR_URLS]])
 content=re.sub(r"Class-Path: (.+ )\. ",f"Class-Path: {classpath} . ",content)
 save_file(manifest_file,content)
 run(["zip",INSTALL_PATH_STEPFUNCTIONS_JAR,"META-INF/MANIFEST.MF"],cwd=INSTALL_DIR_STEPFUNCTIONS)
 for jar_url in PRO_JAR_URLS:
  target=os.path.join(INSTALL_DIR_STEPFUNCTIONS,os.path.basename(jar_url))
  if not file_exists_not_empty(target):
   download(jar_url,target)
def install_package(packages:Union[List[uYSaM],uYSaM],api_name:uYSaM):
 if not(is_debian()and in_docker()):
  LOG.warning("Unable to install dependencies for %s API. Please install packages %s (or equivalent) on your system manually!",api_name,packages)
  return
 if uYSaB(packages,uYSaM):
  packages=packages.split()
 LOG.info("Downloading dependencies for %s API. This may take a while."%api_name)
 with INSTALL_LOCK:
  run(["apt-get","update"],shell=uYSaA)
  run(["apt-get","install","-y","--no-install-recommends"]+packages,shell=uYSaA)
def check_or_install(command:uYSaM,packages:Union[List[uYSaM],uYSaM],api:uYSaM):
 if not is_command_available(command):
  install_package(packages,api)
def setup_ssl_cert():
 from localstack.services import generic_proxy
 target_file=generic_proxy.get_cert_pem_file_path()
 if os.path.exists(target_file):
  if is_enterprise():
   LOG.debug("Avoiding to update SSL certificate.")
   return
  cache_duration_secs=6*60*60
  mod_time=os.path.getmtime(target_file)
  if mod_time>(now()-cache_duration_secs):
   LOG.debug("Using cached SSL certificate (less than 6hrs since last update).")
   return
 LOG.debug("Attempting to download local SSL certificate file")
 timeout_gh=3
 timeout_proxy=5
 try:
  return download_github_artifact(SSL_CERT_URL,target_file,timeout=timeout_gh)
 except uYSas:
  url=SSL_CERT_URL_FALLBACK.format(api_endpoint=constants.API_ENDPOINT)
  try:
   return download(url,target_file,timeout=timeout_proxy)
  except uYSas as e:
   LOG.info("Unable to download local test SSL certificate from %s to %s (using self-signed cert as fallback): %s",url,target_file,e)
   raise
def download_github_artifact(url:uYSaM,target_file:uYSaM,timeout:int=uYSam):
 def do_download(url,print_error=uYSaA):
  try:
   download(url,target_file,timeout=timeout)
   return uYSai
  except uYSas as e:
   if print_error:
    LOG.info("Unable to download Github artifact from from %s to %s: %s %s"%(url,target_file,e,traceback.format_exc()))
 result=do_download(url)
 if not result:
  url=url.replace("https://github.com","https://cdn.jsdelivr.net/gh")
  url=url.replace("/raw/master/","@master/")
  do_download(url,uYSai)
def install_azure():
 from localstack_ext.services.azure import api_specs
 api_specs.download_api_specs()
def install_ecr():
 from localstack_ext.services.ecr import registry
 registry.get_registry_binary()
def install_mysql():
 from localstack_ext.services.rds import db_utils
 db_utils.DBBackendMysql().install_mysql()
def install_pysiddhi():
 from localstack_ext.services.kinesisanalytics import query_utils
 query_utils.setup_siddhi()
def install_neptune():
 from localstack_ext.services.neptune import neptune_api
 neptune_api.install_graphdb()
def install_qldb():
 from localstack_ext.services.qldb import partiql
 partiql.install_partiql()
def install_k3d():
 from localstack_ext.services.eks import k8s_utils
 k8s_utils.KubeProviderK3S().initialize()
def install_kafka():
 from localstack_ext.services.kafka.kafka_api import download_kafka
 download_kafka()
class ExtInstallerRepository(InstallerRepository):
 name="ext"
 def should_load(self)->uYSaf:
  return api_key_configured()
 def load(self,*args,**kwargs):
  LOG.debug("Preparing Pro environment for LocalStack Package Manager.")
  with prepare_environment():
   LOG.debug("Pro environment has successfully been prepared.")
 def get_installer(self)->List[Installer]:
  return[("iot-rule-engine",install_iot_rule_engine),("postgres",install_postgres),("timescaledb",install_timescaledb),("redis",install_redis),("mqtt",install_mqtt),("azure",install_azure),("ecr",install_ecr),("mysql",install_mysql),("pysiddhi",install_pysiddhi),("neptune",install_neptune),("qldb",install_qldb),("k3d",install_k3d),("kafka",install_kafka),("stepfunctions",install_stepfunctions)]
# Created by pyminifier (https://github.com/liftoff/pyminifier)
