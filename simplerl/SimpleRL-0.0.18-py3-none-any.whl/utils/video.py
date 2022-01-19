#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 18:02:25 2021

@author: hemerson
"""

import imageio
import os
import pygame
import datetime


def init_video(environment_name):
    
    frame_count = 0     
    
    # make the image directory if it doesn't exist
    image_folder = '{}_images'.format(environment_name)
    if not os.path.isdir(image_folder):
        os.makedirs(image_folder)
    
    # delete the pre-existing image files to avoid adding wrong images
    for file in os.listdir(image_folder):
        os.remove(os.path.join(image_folder, file))
    
    # make the video directory
    video_folder = "{}_videos".format(environment_name)
    if not os.path.isdir(video_folder):
        os.makedirs(video_folder)
        
        
    return frame_count, image_folder, video_folder

def save_frames(screen, image_folder, frame_count):
    
    frame_count += 1
    filename = "{}/screen_{:04}.png".format(image_folder, frame_count)
    pygame.image.save(screen, filename)
    
    return frame_count


def create_video(image_folder, video_folder, fps):
    
    # define the image directory
    images = []

    # create the full image paths
    for file_name in sorted(os.listdir(image_folder)):
        if file_name.endswith('.png'):
            file_path = os.path.join(image_folder, file_name)
            images.append(imageio.imread(file_path))

    # convert to gif format
    final_timestamp = str(datetime.datetime.now())
    imageio.mimsave('{}/{}.gif'.format(video_folder, final_timestamp), images, fps=fps) 

    # delete the image files
    for file in os.listdir(image_folder):
        os.remove(os.path.join(image_folder, file))

    # remove the empty directory
    os.rmdir(image_folder)