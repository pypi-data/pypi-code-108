from pydantic import BaseModel, Field, validator, PrivateAttr, validate_arguments
from typing import List, Dict, Union, Optional, Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.interpolate import interp1d
from enum import Enum
import folium
from folium.plugins import MarkerCluster, MeasureControl,MousePosition
import matplotlib.pyplot as plt
from plotly import graph_objects as go
#Local imports
from .mincurve import min_curve_method, vtk_survey
from .interpolate import interpolate_deviation, interpolate_position
from .projection import projection_1d

class InterpolatorsEnum(str,Enum):
    md_to_tvd = 'md_to_tvd'
    md_to_tvdss = 'md_to_tvdss'
    tvd_to_md = 'tvd_to_md'
    tvd_to_tvdss = 'tvd_to_tvdss'
    tvdss_to_md = 'tvdss_to_md'
    tvdss_to_tvd = 'tvdss_to_tvd'

class DepthRefsEnum(str,Enum):
    md = 'md'
    tvd = 'tvd'
    tvdss = 'tvdss'
    
    
class Survey(BaseModel):
    md: Optional[Union[List[float], np.ndarray]] = Field(None)
    inc: Optional[Union[List[float], np.ndarray]] = Field(None)
    azi: Optional[Union[List[float], np.ndarray]] = Field(None)
    tvd: Optional[Union[List[float], np.ndarray]] = Field(None)
    tvdss: Optional[Union[List[float], np.ndarray]] = Field(None)
    north_offset: Optional[Union[List[float], np.ndarray]] = Field(None)
    east_offset: Optional[Union[List[float], np.ndarray]] = Field(None)
    northing: Optional[Union[List[float], np.ndarray]] = Field(None)
    easting: Optional[Union[List[float], np.ndarray]] = Field(None)
    dleg: Optional[Union[List[float], np.ndarray]] = Field(None)
    fields: Dict[str,List[Union[float,str]]] = Field(None)
    crs: int = Field(..., gt=0) 
    _interpolators: Dict[InterpolatorsEnum,interp1d] = PrivateAttr({})
    
    @validator('md')
    def check_array_pressures_order(cls, v):
        v_array = np.array(v)
        diff = np.diff(v_array)
        if not np.all(diff>0):
            raise ValueError('Md must be increasing order')
        if not np.all(v_array>=0):
            raise ValueError('Md must be postive')
        return v
    
    class Config:
        extra = 'forbid'
        validate_assignment = True
        underscore_attrs_are_private = True
        arbitrary_types_allowed = True
        json_encoders = {np.ndarray: lambda x: x.tolist()}
        
    def df(
        self,
        projection:bool=False,
        azi: Optional[float]=90,
        center: Optional[Tuple[float,float]] = None,
        to_crs:int=None
    ):
        surv_dict = self.dict()
        fields = surv_dict.pop('fields',None)
        
        if fields is not None:
            surv_dict.update(fields)
            
        _gdf = gpd.GeoDataFrame(
            surv_dict, 
            geometry=gpd.points_from_xy(surv_dict['easting'],surv_dict['northing'])
        )
        _gdf.crs = self.crs
        
        if to_crs:
            _gdf = _gdf.to_crs(to_crs)

        if projection == True:
            _pr,c = projection_1d(_gdf[['easting','northing']].values, azi, center=center)
            _gdf['projection'] = _pr
            
        return _gdf
    
    def plot_projection(
        self,
        azi: Optional[float]=90,
        center: Optional[Tuple[float,float]] = None,
        to_crs:int=None,
        ax=None
    ):
        df = self.df(projection=True,azi=azi,center=center,to_crs=to_crs)
        sax = ax or plt.gca()
        sax.plot(df['projection'],df['tvdss'])
        return sax
        
    
    def make_vertical(
        self,
        td,
        surface_northing=0,
        surface_easting=0, 
        kbe = 0,
        n=2
    ):
        self.md = np.linspace(0,td,n)
        self.inc = np.zeros(n)
        self.azi = np.zeros(n)
        self.tvd = np.linspace(0,td,n)
        self.tvdss = (self.tvd - kbe)*-1
        self.north_offset = np.zeros(n)
        self.east_offset = np.zeros(n)
        self.northing = np.full(n,surface_northing)
        self.easting =  np.full(n,surface_easting)
        self.dleg = np.zeros(n)
        
        return self
        
        
    
    def from_deviation(
        self,
        df:pd.DataFrame=None, 
        md:Union[str,list,np.ndarray, pd.Series]='md',
        azi:Union[str,list,np.ndarray, pd.Series]='azi',
        inc:Union[str,list,np.ndarray, pd.Series]='inc',
        surface_northing=0,
        surface_easting=0, 
        kbe=0
    ):
        dev_dict = {}
        for i,name in zip([md,azi,inc],['md','azi','inc']):
            if isinstance(i,str):
                _var = df[i].values
            else:
                _var = np.atleast_1d(i)
            dev_dict[name] = _var
            
        gdf = min_curve_method(
            dev_dict['md'],
            dev_dict['inc'],
            dev_dict['azi'],
            surface_northing=surface_northing,
            surface_easting=surface_easting,
            kbe=kbe,
            crs = self.crs
        )
        
        for j in ['md','inc','azi','tvd','tvdss','north_offset','east_offset','northing','easting','dleg']:
            setattr(self,j,gdf[j].tolist())
        
        #? Is it good practice return self??
        return self
    
    @validate_arguments
    def sample_deviation(self,step:float=100)->pd.DataFrame:

        _survey = self.df()
        return interpolate_deviation(_survey['md'], 
                                        _survey['inc'], 
                                        _survey['azi'], md_step=step)

    @validate_arguments
    def sample_position(self,step:float=100):
        _survey = self.df()
        new_pos = interpolate_position(_survey['tvd'], 
                                        _survey['easting'], 
                                        _survey['northing'], 
                                        tvd_step=step
        )
        
        return gpd.GeoDataFrame(
            new_pos,
            geometry=gpd.points_from_xy(new_pos.new_easting,new_pos.new_northing),
            crs=self.crs
        )
    
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def depth_interpolate(
        self,
        values:Union[float,List[float],np.ndarray]=None,
        mode:InterpolatorsEnum=InterpolatorsEnum.md_to_tvd
    ):
        if self._interpolators is None or mode.value not in self._interpolators:
            str_split = mode.value.split('_')
            _survey=self.df()
            self._interpolators[mode.value] = interp1d(_survey[str_split[0]],_survey[str_split[2]],fill_value='extrapolate')

        if values is None:
            return self._interpolators[mode.value](self.df()['md'])
        else:
            return self._interpolators[mode.value](np.atleast_1d(values))     
    
    @validate_arguments
    def coord_interpolate(
        self,
        values:Union[float,List[float]]=None,
        depth_ref:DepthRefsEnum=DepthRefsEnum.md,
    ):

        if depth_ref != DepthRefsEnum.tvd:
            values_tvd = self.depth_interpolate(values = values, mode = f'{depth_ref.value}_to_tvd')
        else:
           
            values_tvd = np.atleast_1d(values)

        if any([self._interpolators is None,'tvd_easting' not in self._interpolators]):
            _survey=self.df()
            self._interpolators['tvd_easting'] = interp1d(_survey['tvd'],_survey['easting'],fill_value='extrapolate')
            self._interpolators['tvd_northing'] = interp1d(_survey['tvd'],_survey['northing'],fill_value='extrapolate')

        if values is None:
            easting = self._interpolators['tvd_easting'](self.df()['tvd'])
            northing = self._interpolators['tvd_northing'](self.df()['tvd'])
        else:

            easting = self._interpolators['tvd_easting'](values_tvd)
            northing = self._interpolators['tvd_northing'](values_tvd)
        
                
        return gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(easting,northing),
            crs = self.crs
        )
        
    def get_vtk(self, to_crs = None):
    
        _survey = self.df()
        
        if to_crs:
            _survey = _survey.to_crs(to_crs)
            
        _survey['x'] = _survey['geometry'].x
        _survey['y'] = _survey['geometry'].y
            
        surv_vtk = vtk_survey(_survey[['x','y','tvdss']].values)
        
        for col in _survey.iteritems():
            surv_vtk.point_data[col[0]] = col[1].values

        return surv_vtk
    
    def survey_map(
        self,
        zoom:int=10,
        map_style:str = 'OpenStreetMap',
        tooltip:bool=True,
        popup:bool=False,
        ax=None,
        radius=10
    ):

        _coord = self.df()
        _coord = _coord.to_crs('EPSG:4326')
        _coord['lon'] = _coord['geometry'].x
        _coord['lat'] = _coord['geometry'].y
        center = _coord[['lat','lon']].mean(axis=0)
        
        #make the map
        if ax is None:
            map_folium = folium.Map(
                location=(center['lat'],center['lon']),
                zoom_start=zoom,
                tiles = map_style)
        else:
            assert isinstance(ax,folium.folium.Map)
            map_folium = ax
            
        for i, r in _coord.iterrows():
            folium.Circle(
                [r['lat'],r['lon']],
                tooltip=f"md:{r['md']} <br>tvd:{r['tvd']} <br>tvdss:{r['tvdss']} <br>inc:{r['inc']} " if tooltip else None,
                popup = folium.Popup(html=f"<br>md:{r['md']} <br>tvd:{r['tvd']} <br>tvdss:{r['tvdss']} <br>inc:{r['inc']} ",show=True,max_width='50%') if popup else None,
                #icon=folium.Icon(icon='circle',prefix='fa', color='green'),
                radius=radius
                ).add_to(map_folium)

        folium.LayerControl().add_to(map_folium)
        #LocateControl().add_to(map_folium)
        MeasureControl().add_to(map_folium)
        MousePosition().add_to(map_folium)

        return map_folium
    
    def trace3d(
        self, 
        area_unit='m', 
        depth_unit='ft',
        name='survey',
        mode = 'lines',
        **kwargs
    ):
        
        df = self.df()
        
        coef_area = 1 if area_unit == 'm' else 3.28084
        coef_depth = 1 if depth_unit == 'ft' else 0.3048
        
        trace = go.Scatter3d(
            x = df['easting'] * coef_area,
            y = df['northing'] * coef_area,
            z = df['tvdss'] * coef_depth,
            hoverinfo = 'all',
            mode = mode,
            name = name,
            **kwargs
        )
        
        return trace
    
    def plot3d(
        self, 
        area_unit='m', 
        depth_unit='ft',
        name='survey',
        mode = 'lines',
        title = 'Survey',
        trace_kw = {},
        width = 800,
        height = 600,
        **kwargs
    ):
        
        traces = self.trace3d(
            area_unit=area_unit,
            depth_unit=depth_unit,
            name = name,
            mode = mode,
            **trace_kw
        )
        
        layout = go.Layout(
            title = title,
            scene = {
                'xaxis': {'title': 'Easting'},
                'yaxis': {'title': 'Northing'},
                'zaxis': {'title': 'TVDss'}
            },
            width = width,
            height = height,
            **kwargs
        )
        
        return go.Figure(data=[traces],layout=layout)
            

