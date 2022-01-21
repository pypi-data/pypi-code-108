# -*- coding: utf-8 -*-

"""
Created on Fri Oct 29 09:32:34 2021

@author: Marc Boucsein
"""
import numpy as np
import dask.array as da
from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation
import napari.types
from napari.types import  LayerDataTuple
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari
    

from concurrent.futures import Future






@magic_factory(call_button='Create Label layer')
def Creator(viewer: 'napari.viewer.Viewer') -> Future[LayerDataTuple]:
           
           from napari.qt import thread_worker
           future: Future[LayerDataTuple] = Future()
    
           def _on_done(result, self=Creator):
             future.set_result(result)  
           
               
               
             
           @thread_worker
           def create():
               selection_list=[s for s in viewer.layers.selection]
               if len(selection_list) == 0:
                  print('No available layers')
                  return 
               label_layer_list=[]
               for layer in selection_list:
                   if isinstance(layer.data, da.core.Array):
                       layer_data= layer.data.compute()
                   else:
                       layer_data= layer.data
                   label=np.zeros_like(layer_data, dtype=np.uint8)
                   LayerdataTuple=list(viewer.layers[layer.name].as_layer_data_tuple())                  
                   LayerdataTuple[0]=label
                   LayerdataTuple[1]['name']=layer.name+'_Label'
                   LayerdataTuple[1]['translate']=layer.translate
                   LayerdataTuple[1]['scale']=layer.scale
                   LayerdataTuple[1].pop('rgb')
                   LayerdataTuple[1].pop('colormap')
                   LayerdataTuple[1].pop('contrast_limits')
                   LayerdataTuple[1].pop('interpolation')
                   LayerdataTuple[1].pop('iso_threshold')
                   LayerdataTuple[1].pop('attenuation')
                   LayerdataTuple[1].pop('rendering')
                   LayerdataTuple[1].pop('gamma')
                   LayerdataTuple[2]='labels'
                   LayerdataTuple_new=tuple(LayerdataTuple)
                   #Layer_tuple= (label, {'name': layer.name+'_Label', 'translate': layer.translate,'scale': layer.scale}, 'labels')
                   label_layer_list.append(LayerdataTuple_new)
               return label_layer_list 
           worker = create()
           worker.returned.connect(_on_done)
           worker.start()
           
           return future
       
    

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return Creator


