import inspect
PxnRT=False
PxnRF=type
PxnRy=str
PxnRl=None
PxnRM=open
PxnRv=NotImplementedError
PxnRC=staticmethod
PxnRw=classmethod
PxnRO=int
PxnRA=range
PxnRY=object
PxnRN=isinstance
PxnRr=dict
PxnRX=getattr
PxnRJ=Exception
PxnRu=list
PxnRK=len
import json
import logging
import os
import shutil
import zipfile
from enum import Enum
from typing import Any,Dict,List,Optional,Set,Tuple,Type
from deepdiff import DeepDiff
from localstack.utils.common import json_safe,merge_recursive,mkdir,new_tmp_dir,rm_rf,to_str
from localstack.utils.generic.singleton_utils import SubtypesInstanceManager
from localstack_ext.bootstrap.cpvcs.constants import(COMPRESSION_FORMAT,METAMODELS_FILE,VERSION_SERVICE_INFO_FILE)
from localstack_ext.bootstrap.cpvcs.models import StateFileRef,Version
from localstack_ext.bootstrap.cpvcs.obj_storage import default_storage as object_storage
from localstack_ext.bootstrap.cpvcs.utils.common import(PodFilePaths,add_file_to_archive,config_context,read_file_from_archive)
from localstack_ext.bootstrap.cpvcs.utils.hash_utils import compute_file_hash,random_hash
from localstack_ext.bootstrap.state_utils import(API_STATES_DIR,api_states_traverse,check_already_visited,get_object_dict,load_persisted_object)
LOG=logging.getLogger(__name__)
CAPTURE_METAMODEL_SEPARATELY=PxnRT
PLACEHOLDER_NO_CHANGE={"_meta_":"no-change"}
class MetamodelDeltaMethod(Enum):
 SIMPLE="simple"
 DEEP_DIFF="deepdiff"
class MetamodelDelta(SubtypesInstanceManager):
 def create_delta_for_state_files(self,sf1:StateFileRef,sf2:StateFileRef):
  if sf1 and sf2:
   if sf1.hash_ref==sf2.hash_ref:
    return PLACEHOLDER_NO_CHANGE
   else:
    backend1=load_persisted_object(config_context.get_obj_file_path(sf1.hash_ref))
    backend2=load_persisted_object(config_context.get_obj_file_path(sf2.hash_ref))
    return self.create_delta_json(backend1,backend2)
  if not sf1:
   backend2=load_persisted_object(config_context.get_obj_file_path(sf2.hash_ref))
   clazz=PxnRF(backend2)
   backend1=_infer_backend_init(clazz,sf2)
  else:
   backend1=load_persisted_object(config_context.get_obj_file_path(sf1.hash_ref))
   clazz=PxnRF(backend1)
   backend2=_infer_backend_init(clazz,sf1)
  diff=self.create_delta_json(backend1,backend2)
  return diff
 def create_delta_log(self,state_from:Set[StateFileRef],state_to:Set[StateFileRef])->PxnRy:
  state_files_from=_filter_special_cases(state_from)
  state_files_from_regular=state_files_from[0]
  state_files_from_s3=state_files_from[1]
  state_files_from_sqs=state_files_from[2]
  state_files_to=_filter_special_cases(state_to)
  state_files_to_regular=state_files_to[0]
  state_files_to_s3=state_files_to[1]
  state_files_to_sqs=state_files_to[2]
  def _create_sf_lookup(state_files:Set[StateFileRef])->Dict[PxnRy,StateFileRef]:
   return{os.path.join(sf.rel_path,sf.file_name):sf for sf in state_files}
  result={}
  state_files_to_lookup=_create_sf_lookup(state_files_to_regular)
  for state_file_from in state_files_from_regular:
   result_region=result.setdefault(state_file_from.region,{})
   result_service=result_region.setdefault(state_file_from.service,{})
   if state_file_from.any_congruence(state_files_to_regular):
    key=os.path.join(state_file_from.rel_path,state_file_from.file_name)
    state_file_to=state_files_to_lookup.pop(key)
    diff_json=self.create_delta_for_state_files(state_file_from,state_file_to)
   else:
    diff_json=self.create_delta_for_state_files(state_file_from,PxnRl)
   result_service[state_file_from.file_name]=diff_json
  for state_files_to in state_files_to_lookup.values():
   result_region=result.setdefault(state_files_to.region,{})
   result_service=result_region.setdefault(state_files_to.service,{})
   diff_json=self.create_delta_for_state_files(PxnRl,state_files_to)
   result_service[state_files_to.file_name]=diff_json
  def _handle_special_case_containers(service,sf_from,sf_to):
   region_containers_from={}
   region_containers_to={}
   for container_file_from in sf_from:
    region=container_file_from.region
    region_container=region_containers_from.setdefault(region,{})
    container=load_persisted_object(object_storage.get_state_file_location_by_key(container_file_from.hash_ref))
    if container:
     region_container[container.name]=container
   for container_file_to in sf_to:
    region=container_file_to.region
    region_container=region_containers_to.setdefault(region,{})
    container=load_persisted_object(object_storage.get_state_file_location_by_key(container_file_to.hash_ref))
    if container:
     region_container[container.name]=container
   for region,region_queues_from in region_containers_from.items():
    region_queues_to=region_containers_to.pop(region,{})
    container_result_region=result.setdefault(region,{})
    region_diff=self.create_delta_json(region_queues_from,region_queues_to)
    container_result_region[service]=region_diff
   for region,region_queues_to in region_containers_to.items():
    container_result_region=result.setdefault(region,{})
    region_diff=self.create_delta_json({},region_queues_to)
    container_result_region[service]=region_diff
  _handle_special_case_containers("sqs",state_files_from_sqs,state_files_to_sqs)
  _handle_special_case_containers("s3",state_files_from_s3,state_files_to_s3)
  tmp_dest=os.path.join(config_context.get_delta_log_path(),random_hash())
  result=json_safe(result)
  with PxnRM(tmp_dest,"w")as fp:
   json.dump(result,fp,indent=1)
  key=compute_file_hash(tmp_dest)
  dest=os.path.join(config_context.get_delta_log_path(),key)
  os.rename(tmp_dest,dest)
  return key
 def create_delta_json(self,state1:Any,state2:Any)->Dict:
  raise PxnRv
class MetamodelDeltaDeepDiff(MetamodelDelta):
 @PxnRC
 def impl_name():
  return MetamodelDeltaMethod.DEEP_DIFF
 def create_delta_json(self,state1:Any,state2:Any)->Dict:
  return DeepDiff(state1,state2).to_json()
class MetamodelDeltaSimple(MetamodelDelta):
 @PxnRC
 def impl_name():
  return MetamodelDeltaMethod.SIMPLE
 def create_delta_json(self,state1:Any,state2:Any)->Dict:
  metamodel1=_create_metamodel_helper(state1)or{}
  metamodel2=_create_metamodel_helper(state2)or{}
  if metamodel1==metamodel2:
   return PLACEHOLDER_NO_CHANGE
  return metamodel2
class CommitMetamodelUtils:
 @PxnRw
 def create_metadata_archive(cls,version:Version,delete_reference:bool=PxnRT,overwrite:bool=PxnRT,metamodels_file:PxnRy=PxnRl):
  revision_node=object_storage.get_revision_or_version_by_key(version.active_revision_ptr if overwrite else version.incoming_revision_ptr)
  revision_number=revision_node.revision_number
  metadata_dir=PodFilePaths.metadata_dir(version.version_number)
  mkdir(metadata_dir)
  if metamodels_file:
   archive_path=PodFilePaths.metadata_zip_file(version.version_number)
   if os.path.isfile(archive_path):
    with zipfile.ZipFile(archive_path)as archive:
     archive.extractall(metadata_dir)
  while revision_node:
   assoc_commit=revision_node.assoc_commit
   if not assoc_commit:
    break
   delta_ptr=assoc_commit.delta_log_ptr
   if delta_ptr:
    src=object_storage.get_delta_file_by_key(delta_ptr)
    if not src:
     continue
    dst_name=PodFilePaths.commit_metamodel_file(revision_node.revision_number+1)
    dst=os.path.join(config_context.get_pod_root_dir(),metadata_dir,dst_name)
    shutil.copy(src,dst)
    if delete_reference:
     os.remove(src)
   next_revision=assoc_commit.head_ptr if overwrite else revision_node.parent_ptr
   revision_node=object_storage.get_revision_by_key(next_revision)
  metamodels,service_info=cls.create_delta_metamodel_file(version.version_number,revision_number)
  if CAPTURE_METAMODEL_SEPARATELY:
   metamodels_file=metamodels_file or METAMODELS_FILE
   metamodels_dest=os.path.join(metadata_dir,metamodels_file)
   with PxnRM(metamodels_dest,"w")as fp:
    json.dump(metamodels,fp)
  service_info_dest=os.path.join(metadata_dir,VERSION_SERVICE_INFO_FILE)
  with PxnRM(service_info_dest,"w")as fp:
   json.dump(service_info,fp,indent=1)
  shutil.make_archive(metadata_dir,COMPRESSION_FORMAT,root_dir=metadata_dir)
  rm_rf(metadata_dir)
 @PxnRw
 def create_metamodel_from_state_files(cls,version:PxnRO)->Tuple[Dict,Dict]:
  tmp_states_dir=new_tmp_dir()
  version_state_archive=PodFilePaths.get_version_state_archive(version=version)
  if not version_state_archive:
   return
  with zipfile.ZipFile(version_state_archive)as archive:
   archive.extractall(tmp_states_dir)
  tmp_states_dir_api_states=os.path.join(tmp_states_dir,API_STATES_DIR)
  metamodels={}
  service_info={}
  api_states_traverse(api_states_path=tmp_states_dir_api_states,side_effect=_metadata_create_func,mutables=[metamodels,service_info])
  rm_rf(tmp_states_dir)
  metamodels=json_safe(metamodels)
  return metamodels,service_info
 @PxnRw
 def get_metamodel_delta(cls,prev_metamodel:Dict,this_metamodel:Dict)->Dict:
  if not prev_metamodel:
   return this_metamodel
  def _service_region_changed(prev_service_state,service_state):
   return service_state!=prev_service_state
  result={}
  this_metamodel=this_metamodel or{}
  for region,services in this_metamodel.items():
   result[region]=result_region={}
   prev_region=prev_metamodel.get(region)or{}
   for service_name,service_details in services.items():
    result_region[service_name]=PLACEHOLDER_NO_CHANGE
    prev_service_details=prev_region.get(service_name)
    if _service_region_changed(prev_service_details,service_details):
     result_region[service_name]=service_details
  return result
 @PxnRw
 def create_delta_metamodel_file(cls,version:PxnRO,revision:PxnRO,store_to_zip=PxnRT)->Tuple[Dict,Dict]:
  this_metamodel,service_info=cls.create_metamodel_from_state_files(version=version)
  metadata_zip=PodFilePaths.metadata_zip_file(version=version)
  metamodel_file=PodFilePaths.metamodel_file(revision=revision)
  if revision<=1:
   if store_to_zip:
    add_file_to_archive(metadata_zip,entry_name=metamodel_file,content=json.dumps(this_metamodel))
   return this_metamodel,service_info
  metamodel_delta=PxnRl
  if CAPTURE_METAMODEL_SEPARATELY:
   prev_metamodel=cls.reconstruct_metamodel(version=version,revision=revision-1)
   metamodel_delta=cls.get_metamodel_delta(prev_metamodel,this_metamodel)
   if store_to_zip:
    add_file_to_archive(metadata_zip,entry_name=metamodel_file,content=json.dumps(metamodel_delta))
  return metamodel_delta,service_info
 @PxnRw
 def reconstruct_metamodel(cls,version:PxnRO,revision:PxnRO=PxnRl)->Dict:
  result={}
  for rev in PxnRA(1,revision+1):
   metamodel=cls.get_version_metamodel(version=version,revision=rev)
   if not metamodel:
    return{}
   for service,service_details in metamodel.items():
    if service not in result:
     result[service]=service_details
     continue
    for region,region_details in service_details.items():
     if region_details==PLACEHOLDER_NO_CHANGE:
      continue
     result[service][region]=region_details
  return result
 @PxnRw
 def get_version_metamodel(cls,version:PxnRO,revision:PxnRO=PxnRl)->Dict:
  meta_archive=PodFilePaths.get_version_meta_archive(version)
  if meta_archive:
   metamodels_file=PodFilePaths.metamodel_file(revision=revision)
   result=read_file_from_archive(meta_archive,metamodels_file)
   return json.loads(result)
 @PxnRw
 def get_commit_diff(cls,version_no:PxnRO,commit_no:PxnRO)->Optional[Dict]:
  archive_path=PodFilePaths.get_version_meta_archive(version_no)
  if not archive_path:
   LOG.warning(f"No metadata found for version {version_no}")
   return
  file_name=PodFilePaths.commit_metamodel_file(commit_no)
  result=read_file_from_archive(archive_path=archive_path,file_name=file_name)
  result=json.loads(to_str(result or "{}"))
  return result
def _infer_backend_init(clazz:Type,sf:StateFileRef)->PxnRY:
 if PxnRN(clazz,PxnRr):
  return{}
 constructor=PxnRX(clazz,"__init__",PxnRl)
 sig_args=inspect.getfullargspec(constructor)
 if "region" in sig_args.args:
  backend=clazz(region=sf.region)
 elif "region_name" in sig_args.args:
  backend=clazz(region_name=sf.region)
 else:
  backend=clazz()
 return backend
def _filter_special_cases(state_files:Set[StateFileRef])->Tuple[List[StateFileRef],List[StateFileRef],List[StateFileRef]]:
 regular_refs,s3_bucket_refs,sqs_queue_refs=[],[],[]
 for state_file in state_files:
  if state_file.service=="sqs":
   sqs_queue_refs.append(state_file)
  elif state_file.service=="s3":
   s3_bucket_refs.append(state_file)
  else:
   regular_refs.append(state_file)
 return regular_refs,s3_bucket_refs,sqs_queue_refs
def _metadata_create_func(**kwargs):
 try:
  dir_name=kwargs.get("dir_name")
  file_name=kwargs.get("fname")
  region=kwargs.get("region")
  service_name=kwargs.get("service_name")
  mutables=kwargs.get("mutables")
  metamodels=mutables[0]
  file_path=os.path.join(dir_name,file_name)
  backend_state=load_persisted_object(file_path)
  service_metamodel=_create_metamodel_helper(backend_state)or{}
  region_metamodels=metamodels[region]=metamodels.get(region)or{}
  region_service_models=region_metamodels[service_name]=(region_metamodels.get(service_name)or{})
  service_info=mutables[1]
  merge_recursive(service_metamodel,region_service_models)
  service_region_info=service_info.setdefault(region,{})
  service_info=service_region_info.setdefault(service_name,{})
  service_info["size"]=service_info.get("size",0)+os.path.getsize(file_path)
 except PxnRJ as e:
  LOG.exception(f"Unable to create metamodel for state object {kwargs} : {e}")
def _create_metamodel_helper(obj,width=25,visited:set=PxnRl):
 if obj is PxnRl:
  return obj
 cycle,visited=check_already_visited(obj,visited)
 if cycle:
  return obj
 obj_dict=get_object_dict(obj)
 result=obj=obj_dict if obj_dict is not PxnRl else obj
 if PxnRN(obj,PxnRr):
  result=PxnRr(result)
  for field_name,field_value in result.items():
   result[field_name]=_create_metamodel_helper(field_value,width=width,visited=visited)
 elif PxnRN(obj,PxnRu):
  result=[_create_metamodel_helper(o,width=width,visited=visited)for o in obj]
  if PxnRK(result)>width:
   result={"size":PxnRK(result),"items":result[:width]}
 return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
