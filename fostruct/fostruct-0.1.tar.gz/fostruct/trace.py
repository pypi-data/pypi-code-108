import json
import glob

import os

class Trace:
  '''
  Trace structure manager
  
  Build and destruct folder structure
  '''
  
  def __init__(self, folder: str) -> None:
    self.__folder = folder + "\**"
    self.__folder_name = folder.split("\\")[-1]
  
  def _create_file(self, filepath: str, content: "str | None" = None) -> None:
    file_name = filepath.split("\\")[-1]
    folder_path = filepath.replace(file_name, "")
    
    if not os.path.exists(folder_path):
      os.makedirs(folder_path)
      
    with open(filepath, "w") as f:
      f.write(content if content else "")
    
    return filepath + file_name
  
  def build(self, output: str) -> None:
    '''
    Convert folders to JSON trace format
    
    Arguments:
      @output - output file to discharge trace contents
    '''
    
    result = {
      "files": []
    }
    
    files = {}
    
    for file in [f if os.path.isfile(f) else "" for f in glob.glob(self.__folder, recursive=True)]:
      if not file:
        continue
      
      relative_path = file.split(self.__folder_name, 1)[-1]
      
      with open(file, "r") as f:
        content = f.read()
      
      files[relative_path] = content
      
    result["files"] = files
      
    with open(output, "w") as file:
      file.write(json.dumps(result))
  
  def construct_from_json(self, input_path: str, output_path: str):
    '''
    Construct trace files to folder structure
    
    Arguments:
      @input_path - input trace file to read content
      from
    
      @output_path - folder to discharge trace folder
      structure content
    '''
    
    output_path = os.path.abspath(output_path)
    
    with open(input_path, "r") as file:
      trace = json.loads(file.read())
    
    folder = trace['files']
    
    for file in folder:
      self._create_file(output_path + file, folder[file])
      
  def construct_from_dict(self, input_dict: dict, output_path: str) -> None:
    '''
    Construct dictionary to folder structure
    
    Arguments:
      @input_dict - input dict format 
      [relative filepath: file content]
      
      @output_path - folder to discharge folder 
      structure and content
    '''
    
    for file_name in input_dict.keys():
      self._create_file(output_path + file_name, input_dict[file_name])
  
if __name__ == '__main__':
  PATH = "D:\dev\langauges\photon\photon\\trace"
  
  trace = Trace(PATH)
  
  trace.build("hello.trace.json")
  trace.construct("hello.trace.json", "D:\dev\langauges\photon\output")