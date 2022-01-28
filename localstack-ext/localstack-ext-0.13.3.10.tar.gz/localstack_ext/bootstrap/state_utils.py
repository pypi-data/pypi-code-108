import logging
bGQdq=bool
bGQdU=hasattr
bGQdv=set
bGQdo=True
bGQdS=False
bGQdt=isinstance
bGQdc=dict
bGQdK=getattr
bGQdg=None
bGQdI=str
bGQdn=Exception
bGQdm=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
KINESIS_DIR="kinesis"
DYNAMODB_DIR="dynamodb"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[bGQdq,Set]:
 if bGQdU(obj,"__dict__"):
  visited=visited or bGQdv()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return bGQdo,visited
  visited.add(wrapper)
 return bGQdS,visited
def get_object_dict(obj):
 if bGQdt(obj,bGQdc):
  return obj
 obj_dict=bGQdK(obj,"__dict__",bGQdg)
 return obj_dict
def is_composite_type(obj):
 return bGQdt(obj,(bGQdc,OrderedDict))or bGQdU(obj,"__dict__")
def api_states_traverse(api_states_path:bGQdI,side_effect:Callable[...,bGQdg],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except bGQdn as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with bGQdm(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except bGQdn as e:
   LOG.debug("Unable to read pickled persistence file %s: %s",state_file,e)
def persist_object(obj,state_file):
 with bGQdm(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
