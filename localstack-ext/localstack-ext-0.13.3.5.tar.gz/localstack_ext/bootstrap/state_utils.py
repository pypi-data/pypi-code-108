import logging
pRugv=bool
pRugn=hasattr
pRugS=set
pRugX=True
pRugJ=False
pRugj=isinstance
pRugY=dict
pRugL=getattr
pRugo=None
pRugN=str
pRugf=Exception
pRugr=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
KINESIS_DIR="kinesis"
DYNAMODB_DIR="dynamodb"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[pRugv,Set]:
 if pRugn(obj,"__dict__"):
  visited=visited or pRugS()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return pRugX,visited
  visited.add(wrapper)
 return pRugJ,visited
def get_object_dict(obj):
 if pRugj(obj,pRugY):
  return obj
 obj_dict=pRugL(obj,"__dict__",pRugo)
 return obj_dict
def is_composite_type(obj):
 return pRugj(obj,(pRugY,OrderedDict))or pRugn(obj,"__dict__")
def api_states_traverse(api_states_path:pRugN,side_effect:Callable[...,pRugo],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except pRugf as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with pRugr(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except pRugf as e:
   LOG.debug("Unable to read pickled persistence file %s: %s"%(state_file,e))
def persist_object(obj,state_file):
 with pRugr(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
