import pandas as pd
import os
import numpy as np
from typing import List
from pydantic import PrivateAttr, BaseModel, Field, PrivateAttr, validator, validate_arguments, FilePath, parse_obj_as
import lasio
from typing import Union

##Local imports
from .survey import Survey, InterpolatorsEnum
from .formations import Formations
from .perforations import Perforations
from ..petrophysics.workflows import Estimator 

class LasItem(BaseModel):
    original_mnemonic: str = Field(None, description="Original MNEMONIC")
    mnemonic: str = Field(None, description="mnemonic")
    unit: str = Field(None, description="unit")
    value: str = Field(None, description="value")
    descr: str = Field(None, description="description")
    data: np.ndarray = Field(None, description="data")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {np.ndarray: lambda x: x.tolist()}
        validate_assignment = True
        extra = 'ignore'
        
class HeaderItem(LasItem):
    pass
        
class CurveItem(LasItem):
    pass

    
class Las(BaseModel):
    version: List[HeaderItem] = Field(None, description="version") 
    well: List[HeaderItem] = Field(None, description="well")
    curves: List[CurveItem] = Field(None, description="curves")
    parameters: List[HeaderItem] = Field(None, description="parameters")
    other: str = Field('', description="other")
    _lasio: lasio.LASFile = PrivateAttr()
        
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {np.ndarray: lambda x: x.tolist()}
        validate_assignment = True
        extra = 'ignore'
    
    @validate_arguments
    def from_las(self, las_file: FilePath):
        las = lasio.LASFile(las_file)
        
        ## version
        list_version_header = []
        for v in las.version:
            list_version_header.append(v.__dict__)
            
        version_obj = parse_obj_as(List[HeaderItem], list_version_header)
              
        ## well
        list_well_header = []
        for v in las.well:
            list_well_header.append(v.__dict__)
            
        well_obj = parse_obj_as(List[HeaderItem], list_well_header)
            
        ## params
        list_params_header = []
        for v in las.params:
            list_params_header.append(v.__dict__)
            
        params_obj = parse_obj_as(List[HeaderItem], list_params_header)

        ## curves
        list_curves_header = []
        for v in las.curves:
            list_curves_header.append(v.__dict__)
            
        curves_obj = parse_obj_as(List[CurveItem], list_curves_header)

        self.version = version_obj
        self.well = well_obj
        self.curves = curves_obj
        self.parameters = params_obj
        self._lasio = las
        
        return self
    
    
    # TODO: Make dataframe building starting from any size curves and make the merge properly by the index
    # ? Would the attribute curve be a Pandas Series in order to have the index?
    def df(self):
        list_data = []
        list_columns = []
        for i,curve in enumerate(self.curves):
            #First curve is the depth.
            if i == 0:
                index = curve.data
                continue
            list_data.append(curve.data)
            list_columns.append(curve.mnemonic)
            
        data = np.stack(list_data,axis=1)
        return pd.DataFrame(data, columns=list_columns, index=index)
    
    def columns(self):
        list_columns = []
        for i,curve in enumerate(self.curves):
            list_columns.append(curve.mnemonic)
        return list_columns
    
    def data_shape(self):
        return self.df().shape
    
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
            
            _depth = survey.depth_interpolate(
                self.curves[0].data,
                mode = ref
            )
            curve = CurveItem(
                mnemonic = str_split[2],
                data = _depth,
                descr = f'{str_split[2]} depth'
            )
            self.curves.append(curve)
        
        return self
            
    @validate_arguments
    def formations_to_log(
        self,
        formations: Formations
    ):
        depth = self.curves[0].data
        for fm in formations.formations:
            arr = np.zeros(depth.shape)
            arr[(depth >= formations.formations[fm].md_top) & (depth <= formations.formations[fm].md_bottom)] = 1
            curve = CurveItem(
                mnemonic = f'{formations.formations[fm].name}',
                data = arr,
                descr = f'OneHot Encoding for {formations.formations[fm].name}'
            )
            self.curves.append(curve)
            
        return self
            
    @validate_arguments
    def perforations_to_log(
        self,
        perforations: Perforations
    ):
        depth = self.curves[0].data
        for fm in perforations.perforations:
            arr = np.zeros(depth.shape)
            arr[(depth >= perforations.perforations[fm].md_top) & (depth <= perforations.perforations[fm].md_bottom)] = 1
            curve = CurveItem(
                mnemonic = f'fm_{perforations.perforations[fm].name}',
                data = arr,
                descr = f'OneHot Encoding for {perforations.perforations[fm].name}'
            )
            self.curves.append(curve)
            
        return self
                     
            
    def to_lasio(self):
        las_ex = lasio.LASFile()
        for v in self.version:
            las_ex.version[v.mnemonic] = lasio.HeaderItem(**v.dict(exclude={'original_mnemonic'}))

        for p in self.parameters:
            las_ex.params[p.mnemonic] = lasio.HeaderItem(**p.dict(exclude={'original_mnemonic'}))

        for c in self.curves:
            curve_dict = c.dict(exclude={'original_mnemonic'})
            curve_name = curve_dict.pop('mnemonic')
            curve_data = curve_dict.pop('data')
            las_ex.add_curve(curve_name, curve_data, **curve_dict)
        
        las_ex.other = self.other
        
        return las_ex
    
    @validate_arguments
    def apply_estimator(self, estimator:Estimator):
        df = self.df()
        
        # If the estimator is applied to a formation interval, the las file must contain
        # a curve OneHot encoded for the formation.
        if isinstance(estimator.interval,str):
            if estimator.interval not in self.columns():
                raise ValueError(f'{estimator.interval} is not a column in the las file')
            df_interval = df.loc[df[estimator.interval] == 1, :]
        else:
            if estimator.depth_ref is None:
                bool_array = (df.index >= estimator.interval[0]) & (df.index <= estimator.interval[1])
            else:
                bool_array = (df[estimator.depth_ref] >= estimator.interval[0]) & (df[estimator.depth_ref] <= estimator.interval[1])
            df_interval = df.loc[bool_array, :]
            
        # Estimator loop
        columns_added = []
        for est in estimator.estimators:
            prop_df = est.forward_log(df_interval)
            df_interval = df_interval.join(prop_df, how='left')
            columns_added.append(est.col_name)
        
        #Join the estimators columns to the big dataframe
        df = df.join(df_interval[columns_added], how='left')
        
        for i,col in enumerate(columns_added):
            curve = CurveItem(
                mnemonic = col,
                data = df[col].values,
                descr = estimator.estimators[i].description
            )
            self.curves.append(curve)
            
        return self