import logging
HguVi=bool
HguVb=hasattr
HguVG=set
HguVd=True
HguVB=False
HguVN=isinstance
HguVO=dict
HguVp=getattr
HguVc=None
HguVQ=str
HguVX=Exception
HguVT=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
KINESIS_DIR="kinesis"
DYNAMODB_DIR="dynamodb"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[HguVi,Set]:
 if HguVb(obj,"__dict__"):
  visited=visited or HguVG()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return HguVd,visited
  visited.add(wrapper)
 return HguVB,visited
def get_object_dict(obj):
 if HguVN(obj,HguVO):
  return obj
 obj_dict=HguVp(obj,"__dict__",HguVc)
 return obj_dict
def is_composite_type(obj):
 return HguVN(obj,(HguVO,OrderedDict))or HguVb(obj,"__dict__")
def api_states_traverse(api_states_path:HguVQ,side_effect:Callable[...,HguVc],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except HguVX as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with HguVT(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except HguVX as e:
   LOG.debug("Unable to read pickled persistence file %s: %s",state_file,e)
def persist_object(obj,state_file):
 with HguVT(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
