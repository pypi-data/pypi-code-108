from typing import Optional, List, Dict
import fnmatch
import os
import re
import json

import numpy as np
import pandas as pd

import ROOT

from quickstats.utils.root_utils import declare_expression

class RooProcBaseAction(object):
    def __init__(self, **params):
        self._params = params
        self.executed = False
        self.status   = None
    
    def get_formatted_parameters(self, global_vars:Optional[Dict]=None):
        if global_vars is None:
            global_vars = {}
        formatted_parameters = {}
        for k,v in self._params.items():
            if v is None:
                formatted_parameters[k] = None
                continue
            k_literals = re.findall(r"\${(\w+)}", k)
            if isinstance(v, list):
                v = '__SEPARATOR__'.join(v)
            v_literals = re.findall(r"\${(\w+)}", v)
            all_literals = set(k_literals).union(set(v_literals))
            for literal in all_literals:
                if literal not in global_vars:
                    raise RuntimeError(f"the substitute literal `{literal}` is undefined")
            for literal in k_literals:
                substitute = global_vars[literal]
                k = k.replace("${" + literal + "}", str(substitute))
            for literal in v_literals:
                substitute = global_vars[literal]
                v = v.replace("${" + literal + "}", str(substitute))
            if '__SEPARATOR__' in v:
                v = v.split("__SEPARATOR__")
            formatted_parameters[k] = v
        return formatted_parameters
    
    def makedirs(self, fname):
        dirname = os.path.dirname(fname)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)
    
    def execute(self, **params):
        raise NotImplementedError
    
    @classmethod
    def parse_as_kwargs(cls, text):
        kwargs = {}
        text = re.sub(r"\s*", "", text)
        list_attributes = re.findall(r"(\w+)=\[([^\[\]]+)\]", text)
        for attribute in list_attributes:
            kwargs[attribute[0]] = attribute[1].split(",")
            text = text.replace(f"{attribute[0]}=[{attribute[1]}]","")
        attributes = re.findall(r"(\w+)=([^,]+)", text)
        for attribute in attributes:
            kwargs[attribute[0]] = attribute[1]
        return kwargs
    
    @classmethod
    def parse(cls, text):
        raise NotImplementedError
        
class RooProcRDFAction(RooProcBaseAction):
    def _execute(self, rdf, **params):
        return rdf
    
    def execute(self, rdf, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        rdf_next = self._execute(rdf, **params)
        self.executed = True
        return rdf_next         
        
class RooProcHelperAction(RooProcBaseAction):
    def _execute(self, processor, **params):
        return processor
    
    def execute(self, processor, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        processor = self._execute(processor, **params)
        self.executed = True
        return processor

class RooProcHybridAction(RooProcBaseAction):
    
    def _execute(self, rdf, processor, **params):
        return rdf, processor
    
    def execute(self, rdf, processor, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        rdf_next, processor_next = self._execute(rdf, processor, **params)
        self.executed = True
        return rdf_next, processor_next
    
    
class RooProcTreeName(RooProcHelperAction):
    
    def __init__(self, treename:str):
        super().__init__(treename=treename)
        
    @classmethod
    def parse(cls, text):
        return cls(treename=text)
    
    def _execute(self, processor, **params):
        treename = params['treename']
        processor.treename = treename
        return processor
    
class RooProcExport(RooProcHelperAction):
    def __init__(self, filename:str):
        super().__init__(filename=filename)
        
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
    def _execute(self, processor, **params):
        filename = params['filename']
        data = {k:v.GetValue() for k,v in processor.external_variables.items()}
        dirname = os.path.dirname(filename)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        return processor
    
class RooProcGlobalVariables(RooProcHelperAction):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @classmethod
    def parse(cls, text):
        text = re.sub(r"\s*", "", text)
        tokens = text.split(",")
        globs = {}
        for token in tokens:
            result = re.match("^(\w+)=(.*)", token)
            if not result:
                raise RuntimeError(f"invalid expression {token}")
            globs[result[1]] = result[2]
        return cls(**globs)
    
    def _execute(self, processor, **params):
        processor.global_variables.update(params)
        return processor
    
class RooProcAlias(RooProcRDFAction):
    
    def __init__(self, alias:str, column_name:str):
        super().__init__(alias=alias, column_name=column_name)
        
    @classmethod
    def parse(cls, text):
        result = re.search(r"^\s*(\w+)\s*=\s*([\w\.]+)", text)
        if not result:
            raise RuntimeError(f"invalid expression {text}")
        alias = result.group(1)
        column_name = result.group(2)
        return cls(alias=alias, column_name=column_name)        
        
    def _execute(self, rdf, **params):
        alias = params['alias']
        column_name = params['column_name']
        rdf_next = rdf.Alias(alias, column_name)
        return rdf_next
    
class RooProcSafeAlias(RooProcHybridAction):
    
    def __init__(self, alias:str, column_name:str):
        super().__init__(alias=alias, column_name=column_name)
        
    @classmethod
    def parse(cls, text):
        result = re.search(r"^\s*(\w+)\s*=\s*([\w\.]+)", text)
        if not result:
            raise RuntimeError(f"invalid expression {text}")
        alias = result.group(1)
        column_name = result.group(2)
        return cls(alias=alias, column_name=column_name)    
    
    def _execute(self, rdf, processor, **params):
        alias = params['alias']
        column_name = params['column_name']
        all_column_names = [str(i) for i in rdf.GetColumnNames()]
        if column_name not in all_column_names:
            processor.stdout.warning(f"WARNING: Column name `{column_name}` does not exist. No alias made.")
            return rdf, processor
        rdf_next = rdf.Alias(alias, column_name)
        return rdf_next, processor
    
class RooProcDefine(RooProcRDFAction):
    
    def __init__(self, name:str, expression:str):
        super().__init__(name=name, expression=expression)
        
    @classmethod
    def parse(cls, text):
        result = re.search(r"^\s*(\w+)\s*=(.*)", text)
        if not result:
            raise RuntimeError(f"invalid expression {text}")
        name = result.group(1)
        expression = result.group(2)
        return cls(name=name, expression=expression)        
        
    def _execute(self, rdf, **params):
        name = params['name']
        expression = params['expression']
        rdf_next = rdf.Define(name, expression)
        return rdf_next
    
class RooProcFilter(RooProcRDFAction):
    def __init__(self, expression:str, name:Optional[str]=None):
        super().__init__(expression=expression,
                         name=name)
        
    @classmethod
    def parse(cls, text):
        name_literals = re.findall(r"@{([^{}]+)}", text)
        if len(name_literals) == 0:
            name = None
            expression = text.strip()
        elif len(name_literals) == 1:
            name = name_literals[0]
            expression = text.replace("@{" + name + "}", "").strip()
        else:
            raise RuntimeError(f"multiple filter names detected in the expression `{text}`")
        return cls(name=name, expression=expression)
        
    def _execute(self, rdf, **params):
        expression = params['expression']
        name = params.get("name", None)
        if name is not None:
            rdf_next = rdf.Filter(expression, name)
        else:
            rdf_next = rdf.Filter(expression)
        return rdf_next
    
class RooProcSave(RooProcHybridAction):
    
    def __init__(self, treename:str, filename:str, 
                 columns:Optional[List[str]]=None,
                 frame:Optional[str]=None):
        super().__init__(treename=treename,
                         filename=filename,
                         columns=columns,
                         frame=frame)
        
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
    def _execute(self, rdf, processor, **params):
        treename = params['treename']
        filename = params['filename']
        columns = params.get('columns', None)
        if columns is None:
            rdf_next = rdf.Snapshot(treename, filename)
        else:
            all_columns = [str(c) for c in rdf.GetColumnNames()]
            save_columns = []
            for column in columns:
                save_columns += [c for c in all_columns if fnmatch.fnmatch(c, column)]
            save_columns = list(set(save_columns))
            self.makedirs(filename)
            rdf_next = rdf.Snapshot(treename, filename, save_columns)
        processor.stdout.info(f"INFO: Writing output to `{filename}`.")
        return rdf_next, processor
    
class RooProcAsNumpy(RooProcRDFAction):
    
    def __init__(self, filename:str, 
                 columns:Optional[List[str]]=None):
        super().__init__(filename=filename,
                         columns=columns)
        
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
    def _execute(self, rdf, **kwargs):
        filename = kwargs['filename']
        columns = kwargs.get('columns', None)
        if columns is None:
            data = rdf.AsNumpy()
        else:
            data = rdf.AsNumpy(columns)
        np.save(filename, data)
        return rdf    
    
class RooProcReport(RooProcHybridAction):
    def __init__(self, display:bool=False, filename:Optional[str]=None):
        super().__init__(display=display,
                         filename=filename)
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
    def _execute(self, rdf, processor, **params):
        display = params['display']
        filename = params['filename']
        cut_report = rdf.Report()
        result = []
        cumulative_eff  = 1
        for report in cut_report:
            data = {}
            data['name'] = report.GetName()
            data['all']  = report.GetAll()
            data['pass'] = report.GetPass()
            data['efficiency'] = report.GetEff()
            cumulative_eff *= data['efficiency']/100
            data['cumulative_efficiency'] = cumulative_eff*100
            result.append(data)
        df = pd.DataFrame(result)
        if int(display):
            processor.stdout.info(df)
        if filename is not None:
            self.makedirs(filename)
            df.to_csv(filename)
        return rdf, processor
    
class RooProcStat(RooProcHybridAction):
    def __init__(self, ext_var_name:str, column_name:str):
        super().__init__(ext_var_name=ext_var_name,
                         column_name=column_name)
    @classmethod
    def parse(cls, text):
        name_literals = re.findall(r"@{([^{}]+)}", text)
        if len(name_literals) == 1:
            ext_var_name = name_literals[0]
            column_name = text.replace("@{" + ext_var_name + "}", "").strip()
        else:
            raise RuntimeError(f"unspecified external variable name (format:@{{ext_var_name}}): {text}")
        return cls(ext_var_name=ext_var_name, column_name=column_name)
    
    def _get_func(self, rdf):
        raise NotImplementedError
        
    def _execute(self, rdf, processor, **params):
        ext_var_name = params['ext_var_name']
        column_name = params['column_name']
        processor.external_variables[ext_var_name] = self._get_func(rdf)(column_name)
        return rdf, processor
    
class RooProcSum(RooProcStat):
    def _get_func(self, rdf):
        return rdf.Sum
    
class RooProcMax(RooProcStat):
    def _get_func(self, rdf):
        return rdf.Max
    
class RooProcMin(RooProcStat):
    def _get_func(self, rdf):
        return rdf.Min
    
class RooProcMean(RooProcStat):
    def _get_func(self, rdf):
        return rdf.Mean
        
class RooProcDeclare(RooProcHelperAction):
    
    def __init__(self, expression:str, name:Optional[str]=None):
        super().__init__(expression=expression,
                         name=name)
        
    @classmethod
    def parse(cls, text):
        return cls(expression=text)        
    
    def _execute(self, processor, **params):
        name = params.get("name", None)
        expression = params['expression']
        declare_expression(expression, name)
        return processor
    
class RooProcSaveFrame(RooProcHelperAction):
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, text):
        return cls(name=text)
    
    def _execute(self, processor, **params):
        frame_name = params['name']
        if frame_name in processor.rdf_frames:
            processor.stdout.warning(f"WARNING: Overriding existing rdf frame `{frame_name}`")
        processor.rdf_frames[frame_name] = processor.rdf
        return processor
    
class RooProcLoadFrame(RooProcHelperAction):
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, text):
        return cls(name=text)
    
    def _execute(self, processor, **params):
        frame_name = params['name']
        if frame_name not in processor.rdf_frames:
            raise RuntimeError(f"failed to load rdf frame `{frame_name}`: frame does not exist.")
        processor.rdf = processor.rdf_frames[frame_name]

ACTION_MAP = {
    'TREENAME': RooProcTreeName,
    'DECLARE': RooProcDeclare,
    'GLOBAL': RooProcGlobalVariables,
    'ALIAS': RooProcAlias,
    'SAFEALIAS': RooProcSafeAlias,
    'DEFINE': RooProcDefine,
    'FILTER': RooProcFilter,
    'SAVE': RooProcSave,
    'REPORT': RooProcReport,
    'GETSUM': RooProcSum,
    'GETMAX': RooProcMax,
    'GETMIN': RooProcMin,
    'GETMEAN': RooProcMean,
    'EXPORT': RooProcExport,
    'SAVE_FRAME': RooProcSaveFrame,
    'LOAD_FRAME': RooProcLoadFrame,
    'AS_NUMPY': RooProcAsNumpy
}