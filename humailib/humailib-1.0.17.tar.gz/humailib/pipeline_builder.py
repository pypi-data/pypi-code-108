import pandas as pd
import numpy as np
import datetime

from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
import joblib

from humailib.cloud_tools import GoogleCloudStorage
from humailib.transformers import DataframeFeatureUnion

class PipelineBuilder:
    """
    This class allows you to build a pipeline, by executing and adding one ore more steps 
    at a time, in a way that lends itself well to how data transformation is implemented in Notebooks.
    """
    
    def __init__(self):
        
        self.steps = {}
        self.step_names = {}
        
        self.new_pipeline('default')
        
        return
    
    def new_pipeline(self, name):
        
        self.steps[name] = []
        self.step_names[name] = {}
        self.current_pipeline = name
    
    def transform_and_add(self, steps, df):
        
        pipeline = Pipeline(steps)
        df_out = pipeline.transform(df)
        
        self.add(steps)
        
        return df_out
    
    def fit_transform_and_add(self, steps, df):
        
        pipeline = Pipeline(steps)
        df_out = pipeline.fit_transform(df)
        
        self.add(steps)
        
        return df_out
    
    def add(self, steps):
        
        for step in steps:
            if step[0] not in self.step_names[self.current_pipeline]:
                self.steps[self.current_pipeline].append(step)
                self.step_names[self.current_pipeline][step[0]] = len(self.steps[self.current_pipeline])-1
                
        return
    
    def add_pipeline(self, pipeline):
        
        for name, sub in pipeline.steps:
            self.steps[ name ] = sub.steps
            self.step_names[ name ] = {sub_step_name:i for i,(sub_step_name,_) in enumerate(sub.steps)}
            
        return
    
    
    def get_all_pipelines(self):
        
        return [pipeline_name for pipeline_name in self.steps.keys() if len(self.steps[pipeline_name]) > 0]
            
    
    def build(self, pipelines=None, catch_all_params=None, overwrite_params=False, verbose=False):
        
        assert pipelines is not None and len(pipelines)>0
        
        if isinstance(pipelines, str):
            pipelines = [pipelines]
        
        sub_names = []
        sub_pipes = []
        for current_pipeline in pipelines:
            if current_pipeline in self.steps and len(self.steps[current_pipeline]) > 0:
                sub_names.append(current_pipeline)
                sub_pipes.append(self.steps[current_pipeline])
                
        pipe_out = Pipeline([
            (name, Pipeline(sub)) for name,sub in zip(sub_names,sub_pipes)
        ])
        
        if verbose:
            print("[PipelineBuilder::build] Built:")
            print(pipe_out.steps)
            
        params_changed = False        
        if catch_all_params is not None:
            for catch_all_name, catch_all_value in catch_all_params.items():
                for current_pipeline in pipelines:
                    # Get the parameters for all components in this pipeline.
                    components_params = pipe_out.named_steps[current_pipeline].get_params()
                    if verbose:
                        print("[PipelineBuilder::build] ==== All component params for '{}':".format(current_pipeline))
                        for p,v in components_params.items():
                            print('  {} -> {}'.format(p,v))
                            
                    # See if any parameters have names that contain the catch-all name
                    params = {name:catch_all_value for name,_ in components_params.items() if catch_all_name in name}
                    if not overwrite_params:
                        for name,val in components_params.items():
                            if catch_all_name in name:
                                if isinstance(val, list):
                                    params[name] = list(set(val+catch_all_value))
                                elif isinstance(val, dict):
                                    for k,v in catch_all_value.items():
                                        val[k] = v
                                    params[name] = val
                    if verbose:
                        print("[PipelineBuilder::build] ==== Found matching component params:")
                        for p,v in params.items():
                            print('  {} -> {}'.format(p,v))
                            
                    # Set these to have the catch-all value
                    if len(params) > 0:
                        print("[PipelineBuilder::build] ==== Setting params...".format(params))
                        for p,v in params.items():
                            if isinstance(v, str):
                                print("...setting '{}' -> '{}'".format(p,v))
                            else:
                                print("...setting '{}' -> {}".format(p,v))
                        params_changed = True
                        pipe_out.named_steps[current_pipeline].set_params(**params)
                    
        if not params_changed:
            print("[PipelineBuilder::build] No params changed.")
        
        return pipe_out
    
    def load(self, filename, gcs=None, cache_dir='./cache'):
        
        if 'gs://' in filename:
            cache_file = Path(cache_dir + '/' + filename.split('/')[-1])
            gcs.download_file(filename, cache_file)
            pipeline = joblib.load(cache_file)
        else:
            pipeline = joblib.load(filename)
            
        self.__init__()
        self.add_pipeline(pipeline)
            
        return
    
    def save(self, filename, gcs=None, cache_dir='./cache'):
        
        if len(self.steps) == 0:
            return
        
        pipeline = self.build(pipelines=[name for name in self.step_names])
        
        if 'gs://' in filename:
            if gcs is None:
                gcs = GoogleCloudStorage()
            cache_file = cache_dir + '/' + filename.split('/')[-1]
            #print(cache_file)
            joblib.dump(pipeline, cache_file)
            gcs.upload_file(cache_file, filename)
        else:
            joblib.dump(pipeline, filename)
        
        return
    