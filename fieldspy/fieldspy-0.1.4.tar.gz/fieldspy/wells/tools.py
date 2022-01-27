from pydantic import BaseModel, Field, validate_arguments, validator, parse_obj_as
import pandas as pd
import numpy as np
import geopandas as gpd
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import date
#local imports
from .survey import Survey, InterpolatorsEnum, DepthRefsEnum
from .depthmodel import DepthModel


# tools

class Tool(DepthModel):
    pass
        
class Tools(BaseModel):
    tools: Dict[str,Tool] = Field(None)

    class Config:
        validate_assignment = True
    
    @validate_arguments
    def df(self, tools:Union[str,List[str]]=None):
        gdf_list = []
        for f in self.tools:
            gdf_list.append(self.tools[f].df())
        
        gdf = gpd.GeoDataFrame(pd.concat(gdf_list, axis=0))
        gdf.crs = gdf_list[0].crs
        gdf.index.name='tool'
        if tools:
            if isinstance(tools,str):
                tools = [tools]
            gdf = gdf.loc[tools]
        return gdf
    
    @validate_arguments
    def estimate_average_midpoint(
        self, 
        tools: Optional[Union[str,List[str]]] = None, 
        weights:Optional[str] = None, 
        depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md'],
        name:str = 'avg_mid_point'
    ):
        df = self.df(
            tools=tools
        )
        
        midpoint_dict = {'name':name}
        for d in depth_ref:
            top_column = f'{d}_top'
            bottom_column = f'{d}_bottom'
            if weights is not None:
                if weights not in df.columns:
                    raise ValueError(f'{weights} is not a column in the dataframe')
            value_top = df[top_column].dropna()
            value_bottom = df[bottom_column].dropna()
            
            if value_top.shape[0] > 0:
                top = np.average(value_top, weights=df[weights] if weights is not None else None)
                midpoint_dict[f'{d}_top'] = top
            if value_bottom.shape[0] > 0:
                bottom = np.average(value_bottom, weights=df[weights] if weights is not None else None)
                midpoint_dict[f'{d}_bottom'] = bottom
            
        if len(midpoint_dict) > 0:
            
            new_tool = Tool(**midpoint_dict)
            self.add_tools(new_tool)
            
        #? It is good practice return self? 
        #return self
    
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def from_df(self,df:pd.DataFrame,name:str=None,**kwargs):
        df = df.copy()
        if name:
            df['name'] = df[name].copy()
            df = df.set_index(name)
        else:
            df['name'] = df.index
            
        #To change columns name to match Object
        if bool(kwargs):
            kwargs = {v: k for k, v in kwargs.items()}
            df = df.rename(columns=kwargs)
        self.tools = parse_obj_as(Dict[str,Tool],df.to_dict(orient='index'))

        return self
    
    @validate_arguments
    def add_tools(self, tools: Union[List[Tool],Dict[str,Tool],Tool]):
        form_dict = {}
        if isinstance(tools,Tool):
            form_dict.update({tools.name:tools})
        elif isinstance(tools,list):
            form_dict.update({p.name:p for p in tools})
        elif isinstance(tools,dict):
            form_dict = tools
        
        if self.tools:
            self.tools.update(form_dict)
        else:
            #print(form_dict)
            self.tools = form_dict
        return self
    
    @validate_arguments
    def estimate_ticks(self,tools = None,depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md','tvd']):
        if tools is None:
            tools = self.tools.keys()
            
        for f in tools:
            self.tools[f].estimate_ticks(depth_ref)
            
        return self
    
    @validate_arguments
    def estimate_coordinate(self,survey: Survey,tools=None, depth_ref:DepthRefsEnum='md'):
        if tools is None:
            tools = self.tools.keys()
            
        for f in tools:
            self.tools[f].estimate_coordinate(survey,depth_ref=depth_ref)
            
        return self
    
    @validate_arguments
    def get_reference_depth(
        self,
        survey: Survey, 
        tools=None,
        depth_ref:Union[InterpolatorsEnum,List[InterpolatorsEnum]] = [InterpolatorsEnum.md_to_tvd,InterpolatorsEnum.md_to_tvdss]
    ):
        
        if tools is None:
            tools = self.tools.keys()
            
        for f in tools:
            self.tools[f].get_reference_depth(survey,depth_ref=depth_ref)    
        
        return self
            
    @validate_arguments
    def bottom_from_next_top(self, depth_ref:DepthRefsEnum='md',end_depth:float=None,plus_depth:float=100):
        df = self.df().sort_values(by=[f'{depth_ref}_top'])
        
        for i,(idx,row) in enumerate(df.iterrows()):
            if i+1 == len(df):
                if end_depth is not None:
                    setattr(self.tools[idx],f'{depth_ref}_bottom',end_depth)
                if plus_depth is not None:
                    setattr(self.tools[idx],f'{depth_ref}_bottom',row[f'{depth_ref}_top']+plus_depth)
            else:
                setattr(self.tools[idx],f'{depth_ref}_bottom',df[f'{depth_ref}_top'].iloc[i+1])
        
        return self
        
