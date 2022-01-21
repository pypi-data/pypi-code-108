import json
fiSQK=None
fiSQe=str
fiSQO=int
fiSQX=True
fiSQC=open
fiSQq=bool
fiSQJ=classmethod
fiSQG=False
fiSQT=Exception
fiSQz=staticmethod
fiSQd=bytes
import logging
import os
import zipfile
from typing import List,Union
from localstack import config as localstack_config
from localstack.utils.testutil import create_zip_file_python
from localstack_ext.bootstrap.auth import get_auth_cache
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_FILE,COMPRESSION_FORMAT,CPVCS_DIR,DEFAULT_POD_DIR,DELTA_LOG_DIR,HEAD_FILE,KNOWN_VER_FILE,MAX_VER_FILE,META_ZIP,METAMODELS_FILE,OBJ_STORE_DIR,REFS_DIR,REMOTE_FILE,REV_SUB_DIR,STATE_ZIP,VER_LOG_FILE,VER_LOG_STRUCTURE,VER_SUB_DIR,VERSION_SPACE_DIRS,VERSION_SPACE_FILES)
LOG=logging.getLogger(__name__)
class CPVCSConfigContext:
 default_instance=fiSQK
 def __init__(self,pod_root_dir:fiSQe):
  self.cpvcs_root_dir=pod_root_dir
  self.pod_root_dir=pod_root_dir
  self.user=fiSQK
 def get_pod_context(self)->fiSQe:
  return os.path.basename(self.pod_root_dir)
 def get_context_user(self)->fiSQe:
  return self.user
 def get_pod_root_dir(self)->fiSQe:
  return self.pod_root_dir
 def get_head_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,HEAD_FILE)
 def get_max_ver_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,MAX_VER_FILE)
 def get_known_ver_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,KNOWN_VER_FILE)
 def get_ver_log_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,VER_LOG_FILE)
 def get_obj_store_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,OBJ_STORE_DIR)
 def get_rev_obj_store_path(self)->fiSQe:
  return os.path.join(self.get_obj_store_path(),REV_SUB_DIR)
 def get_ver_obj_store_path(self)->fiSQe:
  return os.path.join(self.get_obj_store_path(),VER_SUB_DIR)
 def get_ver_refs_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,REFS_DIR,VER_SUB_DIR)
 def get_rev_refs_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,REFS_DIR,REV_SUB_DIR)
 def get_version_ref_file_path(self,version_ref:fiSQe)->fiSQe:
  return os.path.join(self.get_ver_refs_path(),version_ref)
 def get_delta_log_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,self.get_obj_store_path(),DELTA_LOG_DIR)
 def get_version_meta_archive_path(self,version:fiSQO,with_format:fiSQq=fiSQX)->fiSQe:
  version_meta_path=os.path.join(self.get_pod_root_dir(),META_ZIP.format(version_no=version))
  if not with_format:
   return version_meta_path
  return f"{version_meta_path}.{COMPRESSION_FORMAT}"
 def get_version_state_archive_path(self,version,with_format:fiSQq=fiSQX)->fiSQe:
  version_state_path=os.path.join(self.get_pod_root_dir(),STATE_ZIP.format(version_no=version))
  if not with_format:
   return version_state_path
  return f"{version_state_path}.{COMPRESSION_FORMAT}"
 def update_ver_log(self,author:fiSQe,ver_no:fiSQO,rev_id:fiSQe,rev_no:fiSQO):
  with fiSQC(self.get_ver_log_path(),"a")as fp:
   fp.write(f"{VER_LOG_STRUCTURE.format(author=author, ver_no=ver_no, rev_rid_no=f'{rev_id}_{rev_no}')}\n")
 def create_version_symlink(self,name:fiSQe,key:fiSQe=fiSQK)->fiSQe:
  return self._create_symlink(name,key,self.get_ver_refs_path())
 def create_revision_symlink(self,name:fiSQe,key:fiSQe=fiSQK)->fiSQe:
  return self._create_symlink(name,key,self.get_rev_refs_path())
 def is_initialized(self)->fiSQq:
  return self.pod_root_dir and os.path.isdir(self.pod_root_dir)
 def _create_symlink(self,name:fiSQe,key:fiSQe,path:fiSQe)->fiSQe:
  rel_path=os.path.relpath(path,start=self.get_pod_root_dir())
  rel_symlink=os.path.join(rel_path,name)
  if key:
   symlink=os.path.join(path,name)
   with fiSQC(symlink,"w")as fp:
    fp.write(key)
  return rel_symlink
 def _get_head_key(self)->fiSQe:
  return self._get_key(self.get_head_path())
 def get_max_ver_key(self)->fiSQe:
  return self._get_key(self.get_max_ver_path())
 def _get_key(self,path:fiSQe)->fiSQe:
  with fiSQC(path,"r")as fp:
   rel_key_path=fp.readline().strip()
  key_path=self.get_pod_absolute_path(rel_key_path)
  with fiSQC(key_path,"r")as fp:
   key=fp.readline()
   return key
 def get_pod_absolute_path(self,rel_path):
  return os.path.join(self.get_pod_root_dir(),rel_path)
 def get_obj_file_path(self,key:fiSQe)->fiSQe:
  return os.path.join(self.get_obj_store_path(),key)
 def get_remote_info_path(self)->fiSQe:
  return os.path.join(self.pod_root_dir,REMOTE_FILE)
 def is_remotly_managed(self,pod_name:fiSQe=fiSQK)->fiSQq:
  if pod_name:
   return os.path.isfile(os.path.join(self.cpvcs_root_dir,pod_name,REMOTE_FILE))
  else:
   return os.path.isfile(self.get_remote_info_path())
 def set_pod_context(self,pod_name:fiSQe):
  cache=get_auth_cache()
  user=cache.get("username","unknown")
  self.pod_root_dir=os.path.join(self.cpvcs_root_dir,pod_name)
  self.user=user
 def pod_exists_locally(self,pod_name:fiSQe)->fiSQq:
  return os.path.isdir(os.path.join(self.cpvcs_root_dir,pod_name))
 def rename_pod(self,new_pod_name:fiSQe):
  curr_name=self.get_pod_root_dir()
  new_name=os.path.join(self.cpvcs_root_dir,new_pod_name)
  os.rename(curr_name,new_name)
  self.set_pod_context(new_name)
 def get_pod_name(self)->fiSQe:
  return os.path.basename(self.get_pod_root_dir())
 def get_version_space_dir_paths(self)->List[fiSQe]:
  return[os.path.join(self.get_pod_root_dir(),directory)for directory in VERSION_SPACE_DIRS]
 def get_version_space_file_paths(self)->List[fiSQe]:
  return[os.path.join(self.get_pod_root_dir(),filename)for filename in VERSION_SPACE_FILES]
 @fiSQJ
 def get(cls):
  if not cls.default_instance:
   pod_root_dir=os.environ.get("POD_DIR")
   if not pod_root_dir:
    pod_root_dir=os.path.join(localstack_config.dirs.tmp,DEFAULT_POD_DIR)
   pod_root_dir=os.path.join(pod_root_dir,CPVCS_DIR)
   cls.default_instance=CPVCSConfigContext(pod_root_dir)
  return cls.default_instance
config_context=CPVCSConfigContext.get()
class PodFilePaths:
 @fiSQJ
 def metamodel_file(cls,revision:fiSQO,version:fiSQO=fiSQK,absolute=fiSQG)->fiSQe:
  if not revision:
   return METAMODELS_FILE
  result=f"metamodel_commit_{revision}.json"
  if absolute:
   if version is fiSQK:
    raise fiSQT("Missing pod version when constructing revision metamodel file path")
   os.path.join(cls.metadata_dir(version))
  return result
 @fiSQz
 def commit_metamodel_file(commit_no:fiSQO)->fiSQe:
  return COMMIT_FILE.format(commit_no=commit_no)
 @fiSQz
 def metadata_dir(version:fiSQO)->fiSQe:
  return os.path.join(config_context.get_pod_root_dir(),META_ZIP.format(version_no=version))
 @fiSQJ
 def metadata_zip_file(cls,version:fiSQO):
  return f"{cls.metadata_dir(version)}.{COMPRESSION_FORMAT}"
 @fiSQz
 def get_version_meta_archive(version:fiSQO)->fiSQe:
  version_meta_path=config_context.get_version_meta_archive_path(version)
  if os.path.isfile(version_meta_path):
   return version_meta_path
 @fiSQz
 def get_version_state_archive(version:fiSQO)->fiSQe:
  version_state_path=config_context.get_version_state_archive_path(version)
  if os.path.isfile(version_state_path):
   return version_state_path
def zip_directories(zip_dest:fiSQe,directories:List[fiSQe])->fiSQe:
 for version_space_dir in directories:
  create_zip_file_python(source_path=version_space_dir,content_root=os.path.basename(version_space_dir),base_dir=version_space_dir,zip_file=zip_dest,mode="a")
 return zip_dest
def add_file_to_archive(archive:fiSQe,entry_name:fiSQe,content:Union[fiSQe,fiSQd]):
 with zipfile.ZipFile(archive,"a")as zip_file:
  zip_file.writestr(entry_name,content)
def read_file_from_archive(archive_path:fiSQe,file_name:fiSQe)->fiSQe:
 try:
  with zipfile.ZipFile(archive_path)as archive:
   content=json.loads(archive.read(file_name))
   return json.dumps(content)
 except fiSQT as e:
  LOG.debug(f"Could not find {file_name} in archive {archive_path}: {e}")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
