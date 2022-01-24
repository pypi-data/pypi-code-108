from datetime import datetime
oGtfK=str
oGtfz=int
oGtfS=super
oGtfP=False
oGtfQ=isinstance
oGtfy=hash
oGtfU=bool
oGtfc=True
oGtfm=list
oGtfT=map
oGtfR=None
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class CPVCSObj:
 def __init__(self,hash_ref:oGtfK):
  self.hash_ref:oGtfK=hash_ref
class Serialization(Enum):
 MAIN=API_STATES_DIR
 DDB=DYNAMODB_DIR
 KINESIS=KINESIS_DIR
 serializer_root_lookup={oGtfK(MAIN):API_STATES_DIR,oGtfK(DDB):DYNAMODB_DIR,oGtfK(KINESIS):KINESIS_DIR}
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:oGtfK,rel_path:oGtfK,file_name:oGtfK,size:oGtfz,service:oGtfK,region:oGtfK,serialization:Serialization):
  oGtfS(StateFileRef,self).__init__(hash_ref)
  self.rel_path:oGtfK=rel_path
  self.file_name:oGtfK=file_name
  self.size:oGtfz=size
  self.service:oGtfK=service
  self.region:oGtfK=region
  self.serialization:Serialization=serialization
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path,serialization=self.serialization)
 def __eq__(self,other):
  if not other:
   return oGtfP
  if not oGtfQ(other,StateFileRef):
   return oGtfP
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return oGtfy((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->oGtfU:
  if not other:
   return oGtfP
  if not oGtfQ(other,StateFileRef):
   return oGtfP
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->oGtfU:
  for other in others:
   if self.congruent(other):
    return oGtfc
  return oGtfP
 def metadata(self)->oGtfK:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:oGtfK,state_files:Set[StateFileRef],parent_ptr:oGtfK):
  oGtfS(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:oGtfK=parent_ptr
 def state_files_info(self)->oGtfK:
  return "\n".join(oGtfm(oGtfT(lambda state_file:oGtfK(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:oGtfK,head_ptr:oGtfK,message:oGtfK,timestamp:oGtfK=oGtfK(datetime.now().timestamp()),delta_log_ptr:oGtfK=oGtfR):
  self.tail_ptr:oGtfK=tail_ptr
  self.head_ptr:oGtfK=head_ptr
  self.message:oGtfK=message
  self.timestamp:oGtfK=timestamp
  self.delta_log_ptr:oGtfK=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:oGtfK,to_node:oGtfK)->oGtfK:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:oGtfK,state_files:Set[StateFileRef],parent_ptr:oGtfK,creator:oGtfK,rid:oGtfK,revision_number:oGtfz,assoc_commit:Commit=oGtfR):
  oGtfS(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:oGtfK=creator
  self.rid:oGtfK=rid
  self.revision_number:oGtfz=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(oGtfT(lambda state_file:oGtfK(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:oGtfK,state_files:Set[StateFileRef],parent_ptr:oGtfK,creator:oGtfK,comment:oGtfK,active_revision_ptr:oGtfK,outgoing_revision_ptrs:Set[oGtfK],incoming_revision_ptr:oGtfK,version_number:oGtfz):
  oGtfS(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(oGtfT(lambda stat_file:oGtfK(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
