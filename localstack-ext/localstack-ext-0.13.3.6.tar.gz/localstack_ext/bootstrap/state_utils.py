import logging
tzATL=bool
tzATX=hasattr
tzATj=set
tzATe=True
tzATS=False
tzATw=isinstance
tzATi=dict
tzATC=getattr
tzATb=None
tzATl=str
tzATN=Exception
tzATD=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
KINESIS_DIR="kinesis"
DYNAMODB_DIR="dynamodb"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[tzATL,Set]:
 if tzATX(obj,"__dict__"):
  visited=visited or tzATj()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return tzATe,visited
  visited.add(wrapper)
 return tzATS,visited
def get_object_dict(obj):
 if tzATw(obj,tzATi):
  return obj
 obj_dict=tzATC(obj,"__dict__",tzATb)
 return obj_dict
def is_composite_type(obj):
 return tzATw(obj,(tzATi,OrderedDict))or tzATX(obj,"__dict__")
def api_states_traverse(api_states_path:tzATl,side_effect:Callable[...,tzATb],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except tzATN as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with tzATD(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except tzATN as e:
   LOG.debug("Unable to read pickled persistence file %s: %s",state_file,e)
def persist_object(obj,state_file):
 with tzATD(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
