from datetime import datetime
fzSiy=str
fzSie=int
fzSir=super
fzSiK=False
fzSih=isinstance
fzSiH=hash
fzSid=bool
fzSix=True
fzSiE=list
fzSia=map
fzSiJ=None
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class CPVCSObj:
 def __init__(self,hash_ref:fzSiy):
  self.hash_ref:fzSiy=hash_ref
class Serialization(Enum):
 MAIN=API_STATES_DIR
 DDB=DYNAMODB_DIR
 KINESIS=KINESIS_DIR
 serializer_root_lookup={fzSiy(MAIN):API_STATES_DIR,fzSiy(DDB):DYNAMODB_DIR,fzSiy(KINESIS):KINESIS_DIR}
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:fzSiy,rel_path:fzSiy,file_name:fzSiy,size:fzSie,service:fzSiy,region:fzSiy,serialization:Serialization):
  fzSir(StateFileRef,self).__init__(hash_ref)
  self.rel_path:fzSiy=rel_path
  self.file_name:fzSiy=file_name
  self.size:fzSie=size
  self.service:fzSiy=service
  self.region:fzSiy=region
  self.serialization:Serialization=serialization
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path,serialization=self.serialization)
 def __eq__(self,other):
  if not other:
   return fzSiK
  if not fzSih(other,StateFileRef):
   return fzSiK
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return fzSiH((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->fzSid:
  if not other:
   return fzSiK
  if not fzSih(other,StateFileRef):
   return fzSiK
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->fzSid:
  for other in others:
   if self.congruent(other):
    return fzSix
  return fzSiK
 def metadata(self)->fzSiy:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:fzSiy,state_files:Set[StateFileRef],parent_ptr:fzSiy):
  fzSir(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:fzSiy=parent_ptr
 def state_files_info(self)->fzSiy:
  return "\n".join(fzSiE(fzSia(lambda state_file:fzSiy(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:fzSiy,head_ptr:fzSiy,message:fzSiy,timestamp:fzSiy=fzSiy(datetime.now().timestamp()),delta_log_ptr:fzSiy=fzSiJ):
  self.tail_ptr:fzSiy=tail_ptr
  self.head_ptr:fzSiy=head_ptr
  self.message:fzSiy=message
  self.timestamp:fzSiy=timestamp
  self.delta_log_ptr:fzSiy=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:fzSiy,to_node:fzSiy)->fzSiy:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:fzSiy,state_files:Set[StateFileRef],parent_ptr:fzSiy,creator:fzSiy,rid:fzSiy,revision_number:fzSie,assoc_commit:Commit=fzSiJ):
  fzSir(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:fzSiy=creator
  self.rid:fzSiy=rid
  self.revision_number:fzSie=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(fzSia(lambda state_file:fzSiy(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:fzSiy,state_files:Set[StateFileRef],parent_ptr:fzSiy,creator:fzSiy,comment:fzSiy,active_revision_ptr:fzSiy,outgoing_revision_ptrs:Set[fzSiy],incoming_revision_ptr:fzSiy,version_number:fzSie):
  fzSir(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(fzSia(lambda stat_file:fzSiy(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
