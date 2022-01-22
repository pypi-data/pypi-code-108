#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 11:27:36 2022

@author: varunkapoor
"""
from tifffile import imread, imwrite
import napari
import glob
import os
import numpy as np
from pathlib import Path
from qtpy.QtWidgets import QComboBox, QPushButton, QApplication
import pandas as pd
from skimage.measure import label, regionprops
from scipy.interpolate import CubicSpline, interp1d


Boxname = 'Kymographs'
MTrack_label = '_MTrack_kymo'
MTrack_label_points = "_points"


class Image_opener(object):
    
    
     def __init__(self, viewer, imagename, Name):
     
          self.viewer = viewer
          print('reading image')      
          self.imagename = imagename  
          self.image = imread(imagename)
          self.Name = Name
          print('image read')
          for layer in list(self.viewer.layers):

                            self.viewer.layers.remove(layer)  
          self.viewer.add_image(self.image, name = self.Name)
          self.shapes_layer = self.viewer.add_shapes(shape_type='path', edge_width=2, edge_color=['red', 'blue'], name = self.Name + MTrack_label)
          
            
            
class Mtrack_exporter(object):

    
    def __init__(self, viewer, Name, savedir, save = False, fit = False):
     
          self.save = save
          self.viewer = viewer
          self.fit = fit 
          self.Name = Name
          self.image = self.viewer.layers[self.Name].data  
          self.shapes_layer = self.viewer.layers[self.Name + MTrack_label].data
          self.savedir = savedir
          
          
          self.kymo_create()
    def kymo_create(self):
                
                if self.save:
                        
                        self.save_kymo_csv()
                       
                if self.fit:
                    
                    self.fit_kymo()
                
                    
                

    def fit_kymo(self):
        
         coordinates_tl = self.viewer.layers[self.Name + MTrack_label].data

         coordinates_tl = sorted(coordinates_tl, key=lambda k: k[0], reverse = True)
         coordinates_tl = np.asarray(coordinates_tl)[0,:]   
         interpolate_length = CubicSpline(coordinates_tl[:,0], coordinates_tl[:,1])
         time_length = [(i,interpolate_length(i)) for i in range(self.image.shape[0]) ]

         df = pd.DataFrame(time_length, columns = ['Time', 'Length'])
         for layer in list(self.viewer.layers):
                     if MTrack_label_points in layer.name:
                            self.viewer.layers.remove(layer)
                           
                    
         self.viewer.add_points(time_length, face_color = 'red', edge_color = 'green', size = 1, name = MTrack_label_points)
            
            
         final_data = self.viewer.layers[MTrack_label_points].data 
         finaldf = pd.DataFrame(final_data, columns = ['Time', 'Length'])
         #Save the data as Mtrack readable text file
         finaldf.to_csv(self.savedir + '/' + self.Name + MTrack_label +  '.csv', index = None)       
            
            
    def save_kymo_csv(self):
            
                     try:
                         
                         coordinates_tl = self.viewer.layers[MTrack_label_points].data
                         coordinates_tl = sorted(coordinates_tl, key=lambda k: k[0], reverse = True)
                         coordinates_tl = np.asarray(coordinates_tl)
                            
                     except:       
            
                         coordinates_tl = self.viewer.layers[self.Name + MTrack_label].data

                         coordinates_tl = sorted(coordinates_tl, key=lambda k: k[0], reverse = True)
                         coordinates_tl = np.asarray(coordinates_tl)[0,:]   
                     finaldf = pd.DataFrame(coordinates_tl, columns = ['Time', 'Length'])
                     #Save the data as Mtrack readable text file
                     finaldf.to_csv(self.savedir + '/' + self.Name + MTrack_label +  '.csv', index = None)
                       
                     
      


def export(sourcedir, savedir):
    
    viewer = napari.Viewer()
    Imageids = []
    Path(savedir).mkdir(exist_ok = True)
    
    
    
    Raw_path = os.path.join(sourcedir, '*tif')
    X = glob.glob(Raw_path)
    for imagename in X:
             Imageids.append(imagename)
    
    imageidbox = QComboBox()   
      
    tracksavebutton = QPushButton('Save Kymo_csv')
    fitbutton = QPushButton('Fit Spline and save')
    imageidbox.addItem(Boxname) 
    for i in range(0, len(Imageids)):
    
    
         imageidbox.addItem(str(Imageids[i]))
            
       
            
    viewer.window.add_dock_widget(imageidbox, name="Image", area='bottom')    
    viewer.window.add_dock_widget(tracksavebutton, name="Save Clicks", area='top')
    viewer.window.add_dock_widget(fitbutton, name="Fit Splines", area='top') 
    imageidbox.currentIndexChanged.connect(
             lambda trackid = imageidbox: Image_opener(
                     viewer,
                      imageidbox.currentText(),
                           os.path.basename(os.path.splitext(imageidbox.currentText())[0]) ))     
    
    tracksavebutton.clicked.connect(
            lambda trackid= tracksavebutton:Mtrack_exporter(
                     viewer,
                      
                           os.path.basename(os.path.splitext(imageidbox.currentText())[0]), savedir, True, False ))
    
    fitbutton.clicked.connect(
            lambda trackid= fitbutton:Mtrack_exporter(
                     viewer,
                  
                           os.path.basename(os.path.splitext(imageidbox.currentText())[0]), savedir, False, True ))
     