# -*- coding: utf-8 -*-

"""
Created on Fri Oct 29 09:32:34 2021

@author: Marc Boucsein
"""
import numpy as np
from napari_plugin_engine import napari_hook_implementation
import napari.types
import napari
from napari.layers import Layer

from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel, QFileDialog, QCheckBox, QGridLayout

from magicgui.widgets import ComboBox, Container, SpinBox





from superqt.qtcompat import QtCore
Horizontal = QtCore.Qt.Orientation.Horizontal




from functools import partial



class elementary_numpy(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        

        self.setLayout(QVBoxLayout())
        
        
        #Select a layer
        possible_layers= [x.name  for x in self.viewer.layers if (isinstance(x, napari.layers.image.image.Image) or isinstance(x, napari.layers.labels.labels.Labels))]
        self.select_layer=Container(widgets=[ComboBox(choices=possible_layers, label="Select a layer:", visible=True)])
        self.layout().addWidget(self.select_layer.native)
        select_layer_name=self.select_layer[0].current_choice
        try:
         self.layer_sel_layer=self.viewer.layers[select_layer_name]
         self.viewer.layers.selection.active=self.viewer.layers[select_layer_name] 
        except:
         pass  
     
        
        #Spin Box for axes
        self.axis_1=Container(widgets=[SpinBox(value=0, label='Axis 1:', min=0, max=self.layer_sel_layer.ndim-1)])
        self.axis_2=Container(widgets=[SpinBox(value=0, label='Axis 2:', min=0, max=self.layer_sel_layer.ndim-1)])
        self.w_slider_container_total = QWidget() 
        self.w_slider_container_total.setLayout(QHBoxLayout())
        self.w_slider_container_total.layout().addWidget(self.axis_1.native)
        self.w_slider_container_total.layout().addWidget(self.axis_2.native)
        self.layout().addWidget(self.w_slider_container_total)
        
        
        #Buttons
        w_buttons = QWidget()  
        grid=QGridLayout()
        w_buttons.setLayout(grid)
        
        names = ['Squeeze', 'Flip', 'Rot 90°', 'Swap']
        squeeze=  partial(self.squeeze,  self.layer_sel_layer.data, self.axis_1[0].value, self.axis_2[0].value )
        flip=  partial(self.flip,  self.layer_sel_layer.data, self.axis_1[0].value)
        rot_90=   partial(self.rot_90,  self.layer_sel_layer.data, self.axis_1[0].value, self.axis_2[0].value )
        swap=   partial(self.swap_axes,  self.layer_sel_layer.data, self.axis_1[0].value, self.axis_2[0].value )
       
        self.operations=[squeeze, flip, rot_90, swap]
        
        positions = [(i, j) for i in range(2) for j in range(2)]

        for position, name, operation in zip(positions, names, self.operations):         
         button = QPushButton(name)
         w_buttons.layout().addWidget(button, *position)
         button.clicked.connect(operation)
        
         
        self.layout().addWidget(w_buttons) 
         
         
           
        
        
        
        
        
        #Connections
        self.select_layer.changed.connect(self.selected_layer)
        
        self.select_layer.changed.connect(self.change_SpinBox)
        self.select_layer.changed.connect(self.remove_SpinBox)
        
        self.viewer.layers.events.inserted.connect(self.change_SpinBox)
        self.viewer.layers.events.inserted.connect(self.remove_SpinBox)

        self.viewer.layers.events.removed.connect(self.change_SpinBox)
        self.viewer.layers.events.removed.connect(self.remove_SpinBox)


        self.viewer.layers.events.inserted.connect(self.change_combo)
        self.viewer.layers.events.inserted.connect(self.remove_combo)
     
        self.viewer.layers.events.removed.connect(self.change_combo)
        self.viewer.layers.events.removed.connect(self.remove_combo)
        
        self.viewer.layers.events.inserted.connect(self.selected_layer)
        self.viewer.layers.events.removed.connect(self.selected_layer)
        
        self.axis_1.changed.connect(self.update_buttons)
        self.axis_2.changed.connect(self.update_buttons)
        self.select_layer.changed.connect(self.update_buttons)
        
    def update_buttons(self):
        w_buttons = QWidget()  
        grid=QGridLayout()
        w_buttons.setLayout(grid)
        
        names = ['Squeeze', 'Flip', 'Rot 90°', 'Swap']
        squeeze=  partial(self.squeeze,  self.layer_sel_layer.data, self.axis_1[0].value, self.axis_2[0].value )
        flip=  partial(self.flip,  self.layer_sel_layer.data, self.axis_1[0].value)
        rot_90=   partial(self.rot_90,  self.layer_sel_layer.data, self.axis_1[0].value, self.axis_2[0].value )
        swap=   partial(self.swap_axes,  self.layer_sel_layer.data, self.axis_1[0].value, self.axis_2[0].value )
       
        self.operations=[squeeze, flip, rot_90, swap]
        
        positions = [(i, j) for i in range(2) for j in range(2)]

        for position, name, operation in zip(positions, names, self.operations):         
         button = QPushButton(name)
         w_buttons.layout().addWidget(button, *position)
         button.clicked.connect(operation)
        
         
        self.layout().insertWidget(2, w_buttons)
        self.layout().itemAt(3).widget().deleteLater()
        self.layout().itemAt(4).widget().deleteLater()
        
        
    def selected_layer(self):
            select_layer_name=self.select_layer[0].current_choice
           
            try:
             self.layer_sel_layer=self.viewer.layers[select_layer_name] 
             self.viewer.layers.selection.active=self.viewer.layers[select_layer_name] 
          
            except:
             pass   
           
    def remove_combo(self, event):
            self.layout().itemAt(0).widget().deleteLater()


             
    def change_combo(self, event):

             possible_layers= [x.name  for x in self.viewer.layers if (isinstance(x, napari.layers.image.image.Image) and x or isinstance(x, napari.layers.labels.labels.Labels))]

             Image_select_old=self.select_layer
             try:
              self.select_layer=Container(widgets=[ComboBox(choices=possible_layers, label="Select a layer:", value=Image_select_old[0].current_choice)])

              self.layout().insertWidget(0,self.select_layer.native )
             except:
              self.select_layer=Container(widgets=[ComboBox(choices=possible_layers, label="Select a layer:")])
              self.layout().insertWidget(0,self.select_layer.native ) 
             
             self.select_layer.changed.connect(self.selected_layer)
             
             self.select_layer.changed.connect(self.change_SpinBox)
             self.select_layer.changed.connect(self.remove_SpinBox)

             self.select_layer.changed.connect(self.update_buttons) 
             
             
             self.selected_layer()
             
           #  self.change_SpinBox()
             
             
    def remove_SpinBox(self, event):
            self.layout().itemAt(2).widget().deleteLater()
         


             
    def change_SpinBox(self, event):
        max_value=self.layer_sel_layer.ndim-1
        self.axis_1=Container(widgets=[SpinBox(value=0, label='Axis 1:', min=0, max=max_value)])
        self.axis_2=Container(widgets=[SpinBox(value=0, label='Axis 2:', min=0, max=max_value)])
        self.w_slider_container_total = QWidget() 
        self.w_slider_container_total.setLayout(QHBoxLayout())
        self.w_slider_container_total.layout().addWidget(self.axis_1.native)
        self.w_slider_container_total.layout().addWidget(self.axis_2.native)
        self.layout().insertWidget(1, self.w_slider_container_total)
        
        self.axis_1.changed.connect(self.update_buttons)
        self.axis_2.changed.connect(self.update_buttons)
   
    def swap_axes(self, array, axis_1, axis_2):
        if axis_1==axis_2:
           return array 
        try:
          array=array.compute()   
        except:
          pass
        swap_arr=np.swapaxes(array,axis_1, axis_2)
        new_layer_data_tup=list(self.layer_sel_layer.as_layer_data_tuple())
        new_layer_data_tup[0]=swap_arr
        new_layer_data_tup[1]['name']=self.layer_sel_layer.name+'_Swap'     
        new_layer_data_tup=tuple(new_layer_data_tup)
        new_layer=Layer.create(*new_layer_data_tup)
        self.viewer.add_layer(new_layer)
      
        
    def rot_90(self, array, axis_1, axis_2):
        if axis_1==axis_2:
           return array 
        try:
          array=array.compute()   
        except:
          pass
        axes=(axis_1, axis_2)
        rot_arr=np.rot90(array,k=1, axes=axes)
        new_layer_data_tup=list(self.layer_sel_layer.as_layer_data_tuple())
        new_layer_data_tup[0]=rot_arr
        new_layer_data_tup[1]['name']=self.layer_sel_layer.name+'_Rot_90'     
        new_layer_data_tup=tuple(new_layer_data_tup)
        new_layer=Layer.create(*new_layer_data_tup)
        self.viewer.add_layer(new_layer)
        
    def squeeze(self, array, axis_1, axis_2):
        try:
          array=array.compute()   
        except:
          pass
        if axis_1==0 and axis_2==0:
          try:  
           squeeze_arr= np.squeeze(array)
           #new_layer_data_tup=list(self.layer_sel_layer.as_layer_data_tuple())
           #new_layer_data_tup[0]=squezze_arr
           #new_layer_data_tup[1]['name']=self.layer_sel_layer.name+'_Squeeze'     
           #new_layer_data_tup=tuple(new_layer_data_tup)
           #new_layer=Layer.create(*new_layer_data_tup)
           #self.viewer.add_layer(new_layer)
           self.viewer.add_image(squeeze_arr, name=self.layer_sel_layer.name+'_Squeeze')
          except: 
           return array   
        else:
          try:  
           squeeze_arr= np.squeeze(array, axis=axis_1)
           #new_layer_data_tup=list(self.layer_sel_layer.as_layer_data_tuple())
           #new_layer_data_tup[0]=squezze_arr
           #new_layer_data_tup[1]['name']=self.layer_sel_layer.name+'_Squeeze'     
           #new_layer_data_tup=tuple(new_layer_data_tup)
           #new_layer=Layer.create(*new_layer_data_tup)
           #self.viewer.add_layer(new_layer)
           self.viewer.add_image(squeeze_arr, name=self.layer_sel_layer.name+'_Squeeze')
          except:
           return array   

       
    def flip(self, array, axis_1):
        try:
          array=array.compute()   
        except:
          pass
        flip_arr= np.flip(array, axis=axis_1)
        new_layer_data_tup=list(self.layer_sel_layer.as_layer_data_tuple())
        new_layer_data_tup[0]=flip_arr
        new_layer_data_tup[1]['name']=self.layer_sel_layer.name+'_Flip'     
        new_layer_data_tup=tuple(new_layer_data_tup)
        new_layer=Layer.create(*new_layer_data_tup)
        self.viewer.add_layer(new_layer)
 
            
@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [elementary_numpy]

