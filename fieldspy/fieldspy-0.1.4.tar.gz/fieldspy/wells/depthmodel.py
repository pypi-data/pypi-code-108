from pydantic import BaseModel, Field, validate_arguments, validator, parse_obj_as
import pandas as pd
import numpy as np
import geopandas as gpd
from typing import Dict, List, Union
from enum import Enum
from datetime import date
#local imports
from .survey import Survey, InterpolatorsEnum, DepthRefsEnum

class DepthModel(BaseModel):
    name: str = Field(None)
    md_top: float = Field(None)
    md_bottom: float = Field(None)
    tvd_top: float = Field(None)
    tvd_bottom: float = Field(None)
    tvdss_top: float = Field(None)
    tvdss_bottom: float = Field(None)
    md_tick: float = Field(None)
    tvd_tick: float = Field(None)
    md_midpoint: float = Field(None)
    tvd_midpoint: float = Field(None)
    tvdss_midpoint: float = Field(None)
    fields: Dict[str, float] = Field(None)
    northing: float = Field(None)
    easting: float = Field(None)
    crs: int = Field(None)
    
    @validator('md_tick',always=True)
    def get_md_tick(cls, v, values):
        if values['md_top'] is None or values['md_bottom'] is None:
            return None
        else:
            return np.abs(values['md_top'] - values['md_bottom'])
        
    @validator('tvd_tick', always=True)
    def get_tvd_tick(cls, v, values):
        if values['tvd_top'] is None or values['tvd_bottom'] is None:
            return None
        else:
            return np.abs(values['tvd_top'] - values['tvd_bottom'])
        
    def df(self):
        d = self.dict(exclude={'fields','name'})
        if self.fields:
            d.update(self.fields)
        
        if self.northing and self.easting:
            geometry = gpd.points_from_xy(x=[self.easting], y=[self.northing], crs=self.crs)
        else:
            geometry = None
            
        return gpd.GeoDataFrame(d,index=[self.name], geometry=geometry, crs=self.crs)   
    
    @validate_arguments
    def estimate_ticks(self,depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md','tvd']):
        ref_list = []
        
        if isinstance(depth_ref,list):
            ref_list.extend(depth_ref)
        else:
            ref_list.append(depth_ref)
            
        for r in ref_list:
            try:
                tick = np.abs(getattr(self,f'{r}_top') - getattr(self,f'{r}_bottom'))
                setattr(self,f'{r}_tick',tick)
            except:
                #print(f'{self.name} Error with reference {r}-> Top:{getattr(self,f"{r}_top")}/ Bottom:{getattr(self,f"{r}_bottom")}')
                pass
            
        return self
    
    @validate_arguments
    def estimate_midpoint(self,depth_ref:Union[DepthRefsEnum,List[DepthRefsEnum]]=['md','tvd','tvdss']):
        ref_list = []
        
        if isinstance(depth_ref,list):
            ref_list.extend(depth_ref)
        else:
            ref_list.append(depth_ref)
            
        for r in ref_list:
            try:
                midpoint = (getattr(self,f'{r}_top') + getattr(self,f'{r}_bottom'))*0.5
                setattr(self,f'{r}_midpoint',midpoint)
            except:
                #print(f'{self.name} Error with reference {r}-> Top:{getattr(self,f"{r}_top")}/ Bottom:{getattr(self,f"{r}_bottom")}')
                pass
            
        return self
    
    @validate_arguments
    def estimate_coordinate(self,survey: Survey, depth_ref:DepthRefsEnum='md'):
        top = getattr(self,f'{depth_ref}_top')
        gdf = survey.coord_interpolate(top,depth_ref=depth_ref)
        
        self.easting = gdf['geometry'].iloc[0].x
        self.northing = gdf['geometry'].iloc[0].y
        self.crs = survey.crs

        return self
    
    @validate_arguments
    def get_reference_depth(
        self,
        survey: Survey, 
        depth_ref:Union[InterpolatorsEnum,List[InterpolatorsEnum]] = [InterpolatorsEnum.md_to_tvd,InterpolatorsEnum.md_to_tvdss]
    ):
        ref_list = []
        
        if isinstance(depth_ref,list):
            ref_list.extend(depth_ref)
        else:
            ref_list.append(depth_ref)
            
        for ref in ref_list:
            str_split = ref.value.split('_')
            
            if getattr(self,f'{str_split[0]}_top') is not None:
                to_top = survey.depth_interpolate(
                    getattr(self,f'{str_split[0]}_top'),
                    mode = ref
                )
                setattr(self,f'{str_split[2]}_top',np.squeeze(to_top))
            
            if getattr(self,f'{str_split[0]}_bottom') is not None:
                to_bottom = survey.depth_interpolate(
                    getattr(self,f'{str_split[0]}_bottom'),
                    mode = ref
                )
                setattr(self,f'{str_split[2]}_bottom',np.squeeze(to_bottom))

        return self
        
    class Config:
        extra = 'ignore'
        validate_assignment = True