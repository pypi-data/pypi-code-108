import hashlib
ordgt=str
ordgk=hex
ordgq=None
ordgI=open
ordgY=Exception
ordgs=int
ordgU=map
ordgN=isinstance
import logging
import os
import random
import zipfile
from typing import Optional
from localstack.utils.common import new_tmp_dir,rm_rf
from localstack_ext.bootstrap.cpvcs.models import Revision,Version
from localstack_ext.bootstrap.cpvcs.utils.common import config_context
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,api_states_traverse
LOG=logging.getLogger(__name__)
def random_hash()->ordgt:
 return ordgk(random.getrandbits(160))
def compute_file_hash(file_path:ordgt,accum=ordgq)->Optional[ordgt]:
 try:
  with ordgI(file_path,"rb")as fp:
   if accum:
    accum.update(fp.read())
   else:
    return hashlib.sha1(fp.read()).hexdigest()
 except ordgY as e:
  LOG.warning(f"Failed to open file and compute hash for file at {file_path}: {e}")
def compute_version_archive_hash(version_no:ordgs,state_archive:ordgt)->ordgt:
 def _compute_file_hash_func(**kwargs):
  dir_name=kwargs.get("dir_name")
  file_name=kwargs.get("fname")
  accum=kwargs.get("mutables")[0]
  file_path=os.path.join(dir_name,file_name)
  compute_file_hash(file_path,accum)
 tmp_state_dir=new_tmp_dir()
 with zipfile.ZipFile(state_archive)as archive:
  archive.extractall(tmp_state_dir)
 tmp_state_archive_api_states=os.path.join(tmp_state_dir,API_STATES_DIR)
 m=hashlib.sha1()
 api_states_traverse(tmp_state_archive_api_states,_compute_file_hash_func,[m])
 m.update(ordgt(version_no).encode("utf-8"))
 rm_rf(tmp_state_dir)
 return m.hexdigest()
def compute_revision_hash(cpvcs_node:Revision)->ordgt:
 if not cpvcs_node.state_files:
  return random_hash()
 state_file_keys=ordgU(lambda state_file:state_file.hash_ref,cpvcs_node.state_files)
 m=hashlib.sha1()
 for key in state_file_keys:
  try:
   with ordgI(os.path.join(config_context.get_obj_store_path(),key),"rb")as fp:
    m.update(fp.read())
  except ordgY as e:
   LOG.warning(f"Failed to open file and compute hash for {key}: {e}")
 if ordgN(cpvcs_node,Revision):
  m.update(cpvcs_node.rid.encode("utf-8"))
  m.update(ordgt(cpvcs_node.revision_number).encode("utf-8"))
 elif ordgN(cpvcs_node,Version):
  m.update(ordgt(cpvcs_node.version_number).encode("utf-8"))
 return m.hexdigest()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
