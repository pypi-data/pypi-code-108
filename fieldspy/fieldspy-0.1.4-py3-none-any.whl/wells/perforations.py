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

# Perforations
class StatusEnum(str,Enum):
    unknown = 'unknown'
    open = 'open'
    isolated = 'isolated'
    squeezed = 'squeezed'
    abandoned = 'abandoned'
    
class PerforationStatus(BaseModel):
    start_date: date = Field(...)
    end_date: date = Field(None)
    status: StatusEnum = Field(...)
    description: str = Field(None)

    class Config:
        validate_assignment = True
        extra = 'ignore'
        
    def df(self, name = None):
        s = pd.Series(self.dict())
        s['status'] = s['status'].value
        
        if name:
            s.name = name
        return s
        

class Perforation(DepthModel):
    status: Dict[str,PerforationStatus] = Field(None)
    
    def status_df(self):
        if self.status:
            df = pd.concat([self.status[s].df(name=s) for s in self.status], axis=1).T
            df['name'] = self.name
            df['md_top'] = self.md_top
            df['md_bottom'] = self.md_bottom
            return df
        return pd.DataFrame()
                                  
class Perforations(BaseModel):
    perforations: Dict[str,Perforation] = Field(None)

    class Config:
        validate_assignment = True

    @validate_arguments
    def df(self, perforations: Union[str,List[str]] = None):
        gdf_list = []
        for f in self.perforations:
            gdf_list.append(self.perforations[f].df())
        
        gdf = gpd.GeoDataFrame(pd.concat(gdf_list, axis=0))
        gdf.crs = gdf_list[0].crs
            
        gdf.index.name='perforation'
        if perforations:
            if isinstance(perforations,str):
                perforations = [perforations]
            gdf = gdf.loc[perforations]
            
        return gdf
    
    @validate_arguments
    def estimate_average_midpoint(
        self, 
        perforations: Optional[Union[str,List[str]]] = None, 
        weights:Optional[str] = None, 
        depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md'],
        name:str = 'avg_mid_point'
    ):
        df = self.df(
            perforations=perforations
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
            
            new_perf = Perforation(**midpoint_dict)
            self.add_perforations(new_perf)
            
        #? It is good practice return self? 
        #return self
            
    def status_df(self):
        return pd.concat([self.perforations[f].status_df() for f in self.perforations], axis=0)
    
    
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
            
        self.perforations = parse_obj_as(Dict[str,Perforation],df.to_dict(orient='index'))
        
        return self
    
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def status_from_df(self,df:pd.DataFrame, name:str=None, **kwargs):
        df = df.copy()
        #Name must be the index to merge with the current perforations
        #To change columns name to match Object
        if bool(kwargs):
            kwargs = {v: k for k, v in kwargs.items()}
            df = df.rename(columns=kwargs)
            
        list_perforations = list(self.perforations.keys())
        df[name]=df[name].astype(str)
        for i in df[name].unique():
            if i not in list_perforations:
                print(f'{i} is not in current perforations  {list_perforations}')
                continue

            ps_dict = df.loc[df[name]==i].to_dict(orient='index')
            perf_status_obj = parse_obj_as(Dict[str,PerforationStatus],ps_dict)
            self.perforations[i].status = perf_status_obj
        
        return self
    
    @validate_arguments
    def add_perforations(self, perforations: Union[List[Perforation],Dict[str,Perforation],Perforation]):
        perf_dict = {}
        if isinstance(perforations,Perforation):
            perf_dict.update({perforations.name:perforations})
        elif isinstance(perforations,list):
            perf_dict.update({p.name:p for p in perforations})
        elif isinstance(perforations,dict):
            perf_dict = perforations
        
        if self.perforations:
            self.perforations.update(perf_dict)
        else:
            self.perforations = perf_dict
            
        return self
    
    @validate_arguments
    def estimate_ticks(self,perforations = None,depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md','tvd']):
        if perforations is None:
            perforations = self.perforations.keys()
            
        for f in perforations:
            self.perforations[f].estimate_ticks(depth_ref)
            
        return self
    
    @validate_arguments
    def estimate_midpoints(self,perforations = None,depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md','tvd','tvdss']):
        if perforations is None:
            perforations = self.perforations.keys()
            
        for f in perforations:
            self.perforations[f].estimate_midpoint(depth_ref)
            
        return self
    
    @validate_arguments
    def estimate_coordinate(self,survey: Survey,perforations=None, depth_ref:DepthRefsEnum='md'):
        if perforations is None:
            perforations = self.perforations.keys()
            
        for f in perforations:
            self.perforations[f].estimate_coordinate(survey,depth_ref=depth_ref)
            
        return self
    
    @validate_arguments
    def get_reference_depth(
        self,
        survey: Survey, 
        perforations=None,
        depth_ref:Union[InterpolatorsEnum,List[InterpolatorsEnum]] = [InterpolatorsEnum.md_to_tvd,InterpolatorsEnum.md_to_tvdss]
    ):
        
        if perforations is None:
            perforations = self.perforations.keys()
            
        for f in perforations:
            self.perforations[f].get_reference_depth(survey,depth_ref=depth_ref)  
            
        return self