import contextlib
Jyxtp=None
Jyxtd=isinstance
JyxtD=list
JyxtO=all
Jyxtz=dict
Jyxtb=tuple
Jyxta=set
JyxtS=True
JyxtN=type
JyxtL=Exception
Jyxtq=str
Jyxtj=getattr
Jyxts=len
JyxtQ=range
JyxtA=map
JyxtW=bool
JyxtH=False
JyxtT=open
import inspect
import json
import logging
import os
import pickle
import sqlite3
from shutil import copyfile
from typing import Any,Dict,Set,Type
from localstack.services.dynamodb.dynamodb_starter import restart_dynamodb
from localstack.utils.common import ArbitraryAccessObj
from moto.s3.models import FakeBucket
from moto.sqs.models import Queue
from localstack_ext.bootstrap.state_utils import(check_already_visited,get_object_dict,is_composite_type)
LOG=logging.getLogger(__name__)
DDB_PREDEF_TABLES=("dm","cf","sm","ss","tr","us")
def _merge_helper_three_way(current,injecting,common_ancestor,visited:Set=Jyxtp):
 if Jyxtd(current,JyxtD)and Jyxtd(injecting,JyxtD):
  current.extend(injecting)
  return
 if(not is_composite_type(current)or not is_composite_type(injecting)or not is_composite_type(common_ancestor)):
  return
 cycle,visited=check_already_visited(injecting,visited)
 if cycle:
  return
 cur_dict=get_object_dict(current)
 inj_dict=get_object_dict(injecting)
 ancestor_dict=get_object_dict(common_ancestor)
 for key in cur_dict.keys()&inj_dict.keys()&ancestor_dict.keys():
  if JyxtO(Jyxtd(d.get(key),Jyxtz)for d in(cur_dict,inj_dict,ancestor_dict)):
   cur_dict[key]=inj_dict[key]=ancestor_dict[key]=_merge_helper_three_way(cur_dict[key],inj_dict[key],ancestor_dict[key])
 for d in cur_dict,inj_dict,ancestor_dict:
  for k,v in d.items():
   if Jyxtd(v,Jyxtz):
    d[k]=Jyxtb(v.items())
 set_cur,set_inj,set_ancestor=(Jyxta((k,pickle.dumps(v))for k,v in d.items())for d in(cur_dict,inj_dict,ancestor_dict))
 for k in Jyxta(k for k,_ in set_cur^set_ancestor)&Jyxta(k for k,_ in set_inj^set_ancestor):
  if cur_dict.get(k)!=inj_dict.get(k)or(k in cur_dict)^(k in inj_dict):
   LOG.debug("Found update-update conflict")
   cur_dict[k]=inj_dict[k]
 d=Jyxtz(set_cur&set_inj&set_ancestor|set_cur-set_ancestor|set_inj-set_ancestor)
 for k,v in d.items():
  v=pickle.loads(v)
  if Jyxtd(v,Jyxtb):
   d[k]=Jyxtz(v)
  else:
   d[k]=v
 return d
def _merge_helper(current,injecting,merge_strategy=Jyxtp,visited:Set=Jyxtp):
 if Jyxtd(current,JyxtD)and Jyxtd(injecting,JyxtD):
  current.extend(injecting)
  return
 if not is_composite_type(current)or not is_composite_type(injecting):
  return
 cycle,visited=check_already_visited(injecting,visited)
 if cycle:
  return
 cur_dict=get_object_dict(current)
 inj_dict=get_object_dict(injecting)
 for field_name,inj_field_value in inj_dict.items():
  cur_field_value=cur_dict.get(field_name)
  if cur_field_value is not Jyxtp:
   if is_composite_type(cur_field_value):
    _merge_helper(cur_field_value,inj_field_value,merge_strategy=merge_strategy,visited=visited)
   elif cur_field_value!=inj_field_value:
    LOG.debug("Overwriting existing value with new state: '%s' <> '%s'"%(cur_field_value,inj_field_value))
    cur_dict[field_name]=inj_field_value
  else:
   cur_dict[field_name]=inj_field_value
 return cur_dict
def merge_object_state(current,injecting,common_ancestor=Jyxtp,merge_strategy=Jyxtp):
 if not current or not injecting:
  return current
 is_special_case=handle_special_case(current,injecting)
 if is_special_case:
  return current
 if common_ancestor:
  _merge_helper_three_way(current,injecting,common_ancestor)
 else:
  _merge_helper(current,injecting)
 add_missing_attributes(current)
 return current
def handle_special_case(current,injecting):
 if Jyxtd(injecting,Queue):
  current.queues[injecting.name]=injecting
  return JyxtS
 elif Jyxtd(injecting,FakeBucket):
  current["global"].buckets[injecting.name]=injecting
  return JyxtS
def add_missing_attributes(obj:Any,safe:JyxtW=JyxtS,visited:Set=Jyxtp):
 try:
  obj_dict=get_object_dict(obj)
  if obj_dict is Jyxtp:
   return
  cycle,visited=check_already_visited(obj,visited)
  if cycle:
   return
  for attr_value in obj_dict.values():
   add_missing_attributes(attr_value,safe=safe,visited=visited)
  class_inst_attrs=infer_class_attributes(JyxtN(obj))
  for key,value in class_inst_attrs.items():
   if key not in obj_dict:
    LOG.debug("Add missing attribute '%s' to state object of type %s"%(key,JyxtN(obj)))
    obj_dict[key]=value
 except JyxtL as e:
  if not safe:
   raise
  LOG.warning("Unable to add missing attributes to persistence state object %s: %s",(obj,e))
def infer_class_attributes(clazz:Type)->Dict[Jyxtq,Any]:
 if clazz in[JyxtD,Jyxtz]or not inspect.isclass(clazz)or clazz.__name__=="function":
  return{}
 constructor=Jyxtj(clazz,"__init__",Jyxtp)
 if not constructor:
  return{}
 try:
  sig_args=inspect.getfullargspec(constructor)
  def get_default_arg_value(arg_name,arg_index=-1):
   arg_defaults=sig_args.defaults or[]
   num_non_default_args=Jyxts(sig_args.args or[])-Jyxts(arg_defaults)
   offset=arg_index-num_non_default_args
   if offset in JyxtQ(Jyxts(arg_defaults)):
    return arg_defaults[offset]
   kwargs_defaults=sig_args.kwonlydefaults or{}
   if arg_name in kwargs_defaults:
    return kwargs_defaults[arg_name]
   return ArbitraryAccessObj()
  args=[]
  kwargs={}
  for arg_idx in JyxtQ(1,Jyxts(sig_args.args)):
   args.append(get_default_arg_value(sig_args.args[arg_idx],arg_index=arg_idx))
  for arg in sig_args.kwonlyargs:
   kwargs[arg]=get_default_arg_value(arg)
  instance=clazz(*args,**kwargs)
  result=Jyxtz(instance.__dict__)
  return result
 except JyxtL:
  return{}
def merge_dynamodb(path_dest:Jyxtq,path_src:Jyxtq):
 db_files=os.listdir(path_dest)
 for region_file in os.listdir(path_src):
  datadir_dynamodb_reg=os.path.join(path_dest,region_file)
  tmp_dir_dynamodb_reg=os.path.join(path_src,region_file)
  if region_file in db_files:
   merge_sqllite_dbs(datadir_dynamodb_reg,tmp_dir_dynamodb_reg)
  else:
   copyfile(tmp_dir_dynamodb_reg,datadir_dynamodb_reg)
   LOG.info(f"Copied state from previously non-existing region file {region_file}")
 restart_dynamodb()
def merge_sqllite_dbs(file_dest:Jyxtq,file_src:Jyxtq)->Jyxtp:
 def _merge_table(table_name:Jyxtq,cursor_a,cursor_b)->Jyxtp:
  tmp_table_name=f"'{table_name}_new'"
  table_name=f"'{table_name}'"
  select_query=f"SELECT * FROM {table_name}"
  if table_name=="'cf'":
   return
  schema=Jyxtb(JyxtA(lambda x:x[1],cursor_b.execute(f"PRAGMA table_info({table_name})")))
  params=f"({('?,' * len(schema))[:-1]})"
  insert_str=f"INSERT INTO {tmp_table_name} {str(schema)} values {params}"
  if table_name=="'dm'":
   excl_tables=(Jyxtq(JyxtD(JyxtA(lambda x:x[0],cursor_a.execute(f"SELECT TableName FROM {table_name}")))).replace("[","(",1).replace("]",")",1))
   select_query+=f"AS O_T WHERE O_T.TableName NOT IN {excl_tables}"
  cursor_a.execute(f"CREATE TABLE IF NOT EXISTS {tmp_table_name} AS SELECT * FROM {table_name}")
  for row in cursor_b.execute(select_query):
   cursor_a.execute(insert_str,row)
  cursor_a.execute(f"DROP TABLE IF EXISTS {table_name}")
  cursor_a.execute(f"ALTER TABLE {tmp_table_name} RENAME TO {table_name}")
 with contextlib.closing(sqlite3.connect(file_dest))as db_src,contextlib.closing(sqlite3.connect(file_src))as db_target:
  cursor_dest=db_src.cursor()
  cursor_src=db_target.cursor()
  table_names=JyxtD(JyxtA(lambda x:x[0],cursor_dest.execute("SELECT name FROM sqlite_master WHERE type='table'")))
  if Jyxta(table_names)=={"cf","dm","ss","tr","us","sm"}:
   copyfile(file_src,file_dest)
   return
  for current_table in table_names:
   try:
    _merge_table(current_table,cursor_dest,cursor_src)
   except sqlite3.OperationalError as e:
    LOG.warning(f"Failed to merge table {current_table}: {e}")
    cursor_dest.execute(f"DROP TABLE IF EXISTS '{current_table}'")
    db_src.rollback()
    return
  db_src.commit()
  LOG.debug(f"Successfully merged db at {file_src} into {file_dest}")
def merge_kinesis_state(path_dest:Jyxtq,path_src:Jyxtq)->JyxtW:
 state_file="kinesis-data.json"
 datadir_statefile=os.path.join(path_dest,state_file)
 tmp_dir_statefile=os.path.join(path_src,state_file)
 if not os.path.isfile(datadir_statefile):
  LOG.info(f"Could not find statefile in path destination {path_dest}")
  return JyxtH
 if not os.path.isfile(tmp_dir_statefile):
  LOG.info(f"Could not find statefile in path source {path_src}")
  return JyxtH
 with JyxtT(datadir_statefile)as datadir_kinesis_file,JyxtT(tmp_dir_statefile)as tmp_dir_kinesis_file:
  datadir_kinesis_json=json.load(datadir_kinesis_file)
  tmp_dir_kinesis_json=json.load(tmp_dir_kinesis_file)
  datadir_streams=datadir_kinesis_json.get("streams",[])
  tmp_dir_streams=tmp_dir_kinesis_json.get("streams",[])
  if Jyxts(tmp_dir_streams)>0:
   datadir_stream_names=datadir_streams.keys()
   for stream in tmp_dir_streams:
    if stream not in datadir_stream_names:
     datadir_streams[stream]=tmp_dir_streams.get(stream)
     LOG.debug(f"Copied state from stream {stream}")
   with JyxtT(datadir_statefile,"w")as mutated_datadir_kinesis_file:
    mutated_datadir_kinesis_file.write(json.dumps(datadir_kinesis_json))
   return JyxtS
 return JyxtH
# Created by pyminifier (https://github.com/liftoff/pyminifier)
