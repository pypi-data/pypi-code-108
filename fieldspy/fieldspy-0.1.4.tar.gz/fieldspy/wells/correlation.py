from pydantic import BaseModel, Field, validate_arguments, validator, parse_obj_as
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Union
#local imports
from .survey import Survey, InterpolatorsEnum, DepthRefsEnum
from .depthmodel import DepthModel


# Correlations


class Correlation(DepthModel):
    pass
        
class Correlations(BaseModel):
    correlations: Dict[str,Correlation] = Field(None)

    class Config:
        validate_assignment = True
    
    @validate_arguments
    def df(self, correlations:Union[str,List[str]]=None):
        gdf = gpd.GeoDataFrame()
        for f in self.correlations:
            gdf = gdf.append(self.correlations[f].df())
        gdf.index.name='correlation'
        if correlations:
            if isinstance(correlations,str):
                correlations = [correlations]
            gdf = gdf.loc[correlations]
        return gdf
    
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
        self.correlations = parse_obj_as(Dict[str,Correlation],df.to_dict(orient='index'))
        
        return self

    
    @validate_arguments
    def add_correlations(self, correlations: Union[Correlation,List[Correlation],Dict[str,Correlation]]):
        form_dict = {}
        if isinstance(correlations,Correlation):
            form_dict.update({correlations.name:correlations})
        elif isinstance(correlations,list):
            form_dict.update({p.name:p for p in correlations})
        elif isinstance(correlations,dict):
            form_dict = correlations
        
        if self.correlations:
            self.correlations.update(form_dict)
        else:
            self.correlations = form_dict
        
        return self
    
    @validate_arguments
    def estimate_ticks(self,correlations = None,depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md','tvd']):
        if correlations is None:
            correlations = self.correlations.keys()
            
        for f in correlations:
            self.correlations[f].estimate_ticks(depth_ref)
            
        return self
    
    @validate_arguments
    def estimate_coordinate(self,survey: Survey,correlations=None, depth_ref:DepthRefsEnum='md'):
        if correlations is None:
            correlations = self.correlations.keys()
            
        for f in correlations:
            self.correlations[f].estimate_coordinate(survey,depth_ref=depth_ref)
            
        return self
    
    @validate_arguments
    def get_reference_depth(
        self,
        survey: Survey, 
        correlations=None,
        depth_ref:Union[InterpolatorsEnum,List[InterpolatorsEnum]] = [InterpolatorsEnum.md_to_tvd,InterpolatorsEnum.md_to_tvdss]
    ):
        
        if correlations is None:
            correlations = self.correlations.keys()
            
        for f in correlations:
            self.correlations[f].get_reference_depth(survey,depth_ref=depth_ref)   
            
        return self 
            
