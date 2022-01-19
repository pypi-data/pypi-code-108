#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 22:23:28 2021

@author: hemerson
"""

""" 
hopsital_env - a simple grid environment for managing a hospital

The player has limited resources and is tasked with treating as many patients
as possible during a set time window. Patients enter the hospital with one of
either a: mild, moderate or severe disease. 

The player must assign staff to the patients to reduce the time they spend 
waiting for treatment and also reduce the likelihood of the patient dying. 
The more staff assigned to a patient the faster the treatment. 

Patients must be first diagnosed and then assigned to the relevant treatment.

"""

import numpy as np
import pygame
import os
import math

from SimpleRL.utils import generate_patient, generate_staff, generate_rooms
from SimpleRL.utils import init_video, save_frames, create_video

class hospital_env:
    def __init__(self, render=False, seed=None, max_timestep=180, render_mode="default"):
        
        # TODO: perform general optimisation
        # TODO: optimise the image display code to remove long conditional statements
        # TODO: ensure that all the inputs are correct
        # TODO: may need to test the difficulty of this environment
        
        # Ensure the render_mode for the environment is valid
        valid_render = ["default", "video"]
        render_error = "render_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_render)
        assert render_mode in valid_render, render_error
        
        # Display the input settings 
        print('\nHospital Settings')
        print('--------------------')
        print('Render: {}'.format(render))        
        print('Seed: {}'.format(seed))
        print('Max Timestep: {} days'.format(max_timestep))
        print('Render Mode: {}'.format(render_mode)) 
        print('--------------------')
        
        self.render = render
        self.seed = seed
        self.max_timestep = max_timestep # in days
        self.render_mode = render_mode
        
        # define the environmental parameters
        np.random.seed(self.seed)  
        self.environment_name = 'Hopsital'
        
        # define the illness parameters (for mild, moderate & severe)
        self.disease_classification = ["mild", "moderate", "severe"]
        self.illness_likelihood = [0.5, 0.3, 0.2] # liklihood of a patient class
        self.death_probs = {"mild": 0.05, "moderate": 0.15, "severe": 0.25} # mean likelihood of death per class
        self.recovery_time = {"mild": 2, "moderate": 4, "severe": 6} # mean recovery time for each class
        
        # define the patient paramaters
        self.patient_spawn_prob = 1.0 # probability of patient per timestep 
        self.patient_spawn_mean = 1.0
        self.patient_spawn_std = 1.0
        
        # define the staff parameters (for doctors and nurses)
        self.staff_number = 10 # number of staff at the hospital
        self.staff_split = [0.5, 0.5] # ratio of doctors to nurses
        self.staff_efficiency = {"doctor": 2, "nurse": 1} # healing bonus for non-specific tasks 
        self.staff_roles = {"doctor": ["diagnosis", "treatment"], "nurse": ["treatment"]}
        
        # define the reward
        self.death_penalty = -100
        self.waiting_penalty = -1
        
        # define the hospital parameters    
        self.number_rooms = 10
        
        # Reset the environment parameters
        self.reset()
        
        # Intialise the display
        if self.render: 
            
            # Check if there is an available display
            try: os.environ["DISPLAY"]
            
            # Configure a dummy display
            except: os.environ["SDL_VIDEODRIVER"] = "dummy"
            
            if self.render_mode == 'video':
                self.frame_count, self.image_folder, self.video_folder = init_video(environment_name=self.environment_name)
            
            # set the screen dimensions
            self.window_width = 414
            self.window_height = 414
            
            # get the screen
            self._init_display() 
            
            # set the fps
            self.fps = 1
            
            # get the font 
            self.font = pygame.font.Font(None, 24)
            
            # create the colours
            self.green = (0, 153, 0)
            self.grass_green = (104, 184, 69)            
            self.light_grey = (199,199,199)
            self.blue = (102, 178, 255)
            self.red = (255, 51, 51)
            self.black = (0, 0, 0)  
            self.brown = (112, 85, 49)
            self.pale_blue = (193, 223, 234)
            self.glass_blue = (86, 184, 212)            
            self.orange = (255, 128, 0)
            self.light_orange = (199, 155, 123)
            self.sand_yellow = (188, 177, 140)
        
    def reset(self):
        
        # reset the staff roster
        self.hospital_staff, self.doctor_ids = generate_staff(
            staff_split=self.staff_split, 
            staff_efficiency=self.staff_efficiency, 
            staff_roles=self.staff_roles
            )
        
        # reset the current patients in the hospital
        self.hospital_patients = []
        self.current_patient_id = 0
        self.day_counter = 0
        
        # get the score tallys
        self.total_deaths = 0
        self.total_days_waited = 0
        self.total_recoveries = 0
        
        # set up the room arrangement
        self.room_arrangement = generate_rooms(number_rooms=self.number_rooms)
        
        state = np.zeros((self.number_rooms, 3))
        
        return state.flatten()
        
        
    def step(self, action=None):
        
        """
        state:
        ------
            
        1D array: (3 x no. of rooms)
        
        Each room has:
            - patient_severity (0=None, 1=Mild, 2=Moderate, 3=Severe) 
            - days waiting (0, 1, 2, 3, ...)
            - diagnosis or treatment (0=None, 1=diagnosis, 2=treatment)
        
        action:
        -------
        
        1d array: (1 x no. of staff)
        
        Each staff member is assigned the room in which they are needed (0, 1, 2 ..)
        
        """
        
        # initialise the reward tallys
        waiting_today = 0
        deaths_today = 0    
        recovered_today = 0
        
        # update the rooms with the staff choices -------------------
        
        # clear the current staff arrangements
        for idx, _ in enumerate(self.room_arrangement):
            self.room_arrangement[idx]['staff_ids'] = []            
        
        # cycle through the staff assignments
        for staff_idx, room_num in enumerate(action):
            
            # add the ids of the staff to the relevant rooms
            self.room_arrangement[room_num]["staff_ids"].append(staff_idx)                  
            
        # add the changes as a result of staff presence -------------       
        
        for room_idx, room in enumerate(self.room_arrangement):
            
            # if there is a patient in the room
            if room["patient_id"] != None:
                
                current_patient = None
                current_patient_idx = None
                                
                # find the patient's medical record
                for idx, patient in enumerate(self.hospital_patients):                     
                    if patient["id"] == room["patient_id"]:
                        current_patient = patient
                        current_patient_idx = idx
                        break
                
                # cycle through staff and allow doctors actions first
                for stf in room['staff_ids']:
                    
                    # if this staff member is a doctor
                    if stf in self.doctor_ids:
                        
                        # diagnose the patient
                        if not current_patient['diagnosed']:
                            current_patient['diagnosed'] = True
                            continue
                    
                        # allow treatment if patient has been diagnosed                    
                        if current_patient['diagnosed']:                        
                            # treat the patient
                            current_patient['recovery_time'] -= self.staff_efficiency['doctor']
                
                # now allow nurses' actions
                for stf in room['staff_ids']:
                    
                    # if this staff member is a doctor
                    if stf not in self.doctor_ids and current_patient['diagnosed']:
                 
                        # treat the patient
                        current_patient['recovery_time'] -= self.staff_efficiency['nurse']
                
                # remove the patient if they have recovered
                recovered = False                
                if current_patient['recovery_time'] <= 0 and current_patient['diagnosed']:
                    
                    # remove from hospital patients
                    self.hospital_patients.pop(current_patient_idx)
                    
                    # update the room
                    self.room_arrangement[room_idx]["patient_id"] = None       
                    
                    # update recovered
                    recovered_today += 1
                    recovered = True
                
                # update the days deaths
                dead = False
                if np.random.uniform(0, 1, 1) < current_patient['death_prob'] and not recovered:
                    
                    # update deaths
                    deaths_today += 1
                    dead = True
                    
                    # remove from hospital patients
                    self.hospital_patients.pop(current_patient_idx)
                    
                    # update the room
                    self.room_arrangement[room_idx]["patient_id"] = None 
                    
                # update the illness of the patient    
                if not dead and not recovered:
                    self.hospital_patients[current_patient_idx]['waiting_time'] += 1
                    waiting_today += 1
                    
                            
        # generate a patient ----------------------------------------
        
        # determine how many patient spawn this turn
        num_patient_spawn = max(math.ceil(np.random.normal(self.patient_spawn_mean, self.patient_spawn_std, 1)[0]), 0)          
        if len(self.hospital_patients) + (num_patient_spawn - 1) < self.number_rooms:
            
            for patient_spawn in range(num_patient_spawn):
            
                # create new patient
                new_patient = generate_patient(
                    disease_classification=self.disease_classification,
                    illness_likelihood=self.illness_likelihood, 
                    death_probs=self.death_probs, 
                    recovery_time=self.recovery_time, 
                    id_number = self.current_patient_id
                    )
                
                # check if hospital is at max capacity
                if len(self.hospital_patients) <= self.number_rooms:
            
                    # add patients to the rooms
                    for room in self.room_arrangement:
                        
                        # add patient ID to room and update current_id
                        if room['patient_id'] == None:
                            
                            # add patient id to room
                            room['patient_id'] = self.current_patient_id
                            
                            # add room number to patient
                            new_patient['room_number'] = room['room_number']
                            
                            # add patient to the hospital list
                            self.hospital_patients.append(new_patient)
                            
                            # update patient_id
                            self.current_patient_id += 1
                            
                            break
                
        # display the hospital ------------------------------------
        
        if self.render:
            self._display()            
                
        # visualise the next state --------------------------------
        
        state = np.zeros((self.number_rooms, 3))        
        for idx, room in enumerate(self.room_arrangement):
            
            # if there is a patient in the room
            if room["patient_id"]:
                
                current_patient = None
                
                # find the patient's medical record
                for idx, patient in enumerate(self.hospital_patients):                    
                    if patient["id"] == room["patient_id"]:
                        current_patient = patient
                
                # get the disease class, days waiting and treatment/diagnosis stage
                state[idx, 0] = self.disease_classification.index(current_patient["disease_class"]) + 1
                state[idx, 1] = current_patient["waiting_time"]
                state[idx, 2] = int(current_patient["diagnosed"]) + 1
        
        # calculate the reward -----------------------------------
        
        self.total_days_waited += waiting_today
        self.total_deaths += deaths_today
        self.total_recoveries += recovered_today
        
        reward = self.death_penalty * deaths_today + self.waiting_penalty * waiting_today
        
        # get done -----------------------------------------------
        
        done = False
        self.day_counter += 1
        
        # terminate when max timesteps reached
        if self.day_counter == self.max_timestep:
            done = True
            
            # close the pygame window
            if self.render:
                self._close_display()
        
        # get additional info ------------------------------------
        
        info = {}
            
        return state, reward, done, info     
    
    def _init_display(self):
        
        # quit any previous games
        pygame.display.quit()
        
        # initialise pygame
        pygame.init()  
        
        pygame.display.set_caption("Hospital Environment")
        
        # initialise the clock
        self.clock = pygame.time.Clock()
        
        # create the screen
        self.screen = pygame.display.set_mode([self.window_width, self.window_height])
        
        
    def _display(self):   
        
        # quit the game
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.display.quit()
                        
        # set the background colour to green
        self.screen.fill(self.black)

        grid_size = 18
        
        # set the size of the block
        block_size = int(self.window_height / grid_size) 
        
        # loop through the grid
        for x in range(0, self.window_width, block_size):
            for y in range(0, self.window_height, block_size):
                
                # set the floor colour
                colour = self.light_grey  
                text = ""
                    
                # fill in the hopsital border
                if (x == block_size * 2) or (x == self.window_width - block_size * 3) or (y == block_size) or (y == self.window_height - block_size * 2):
                    colour = self.light_orange
                    
                # fill in the vertical hospital walls
                if (x == block_size * 7) or (x == block_size * 10):
                    colour = self.light_orange
                
                # add in additional room features
                if (y % (block_size * 3) == block_size * 2):
                    
                    # add some windows
                    if ((x == block_size * 2) or (x == self.window_width - block_size * 3)):
                        colour = self.glass_blue
                        
                    # add the patient room doors
                    if ((x == block_size * 7) or (x == block_size * 10)):
                         colour = self.brown
                         
                # calculate the room number
                
                # get the patient corridor
                column = 0    
                if x > block_size * 8:
                    column = 1
                
                # get the row
                row = int(y / (block_size * 3)) - 1
                
                # calculate the room_num
                room_num = row + column * 5            
                
                if y > block_size and y < (self.window_width - block_size):
                    
                    # add in patients                
                    if (y % (block_size * 3) == 0) and (x == block_size * 3 or x == block_size * 4 or x == block_size * 13 or x == block_size * 14):   
                            
                            # find the patient record
                            current_patient = None
                            for patient in self.hospital_patients:                        
                                if patient['room_number'] == room_num:
                                    current_patient = patient
                                    break
                            
                            if current_patient:   
                                
                                # get the bed colouring
                                if current_patient['disease_class'] == 'mild':
                                    colour = self.green
                                elif current_patient['disease_class'] == 'moderate':
                                    colour = self.orange
                                elif current_patient['disease_class'] == 'severe':
                                    colour = self.red
                                    
                                # add their recovery time remaining
                                if (x == block_size * 3) or (x == block_size * 13):
                                    text = str(current_patient["recovery_time"])   
                                    
                                # add whether they have been diagnosed or not
                                if (x == block_size * 4) or (x == block_size * 14):
                                    text = "T" if current_patient["diagnosed"] else "D"   
                    
                    # add in doctors                
                    doctor_count = 0
                    if (y % (block_size * 3) == 0) and (x == block_size * 6 or x == block_size * 11):  
                        
                        staff_ids = self.room_arrangement[room_num]["staff_ids"]
                        if len(staff_ids) > 0:
                            
                            # count in the doctors
                            for stf in staff_ids:
                                if stf in self.doctor_ids:
                                    doctor_count += 1
                            
                            # display the number
                            if doctor_count:
                                text = str(doctor_count)
                                colour = self.blue                                                    
                    
                    # add in nurses
                    nurse_count = 0
                    if (y % (block_size * 3) == block_size * 2) and (x == block_size * 5 or x == block_size * 12):
                        
                        # + 1 needed with room_num for nurses to be added in the correct space
                        staff_ids = self.room_arrangement[room_num + 1]["staff_ids"]
                        if len(staff_ids) > 0:
                            
                            # count in the doctors
                            for stf in staff_ids:
                                if stf not in self.doctor_ids:
                                    nurse_count += 1
                            
                            if nurse_count:
                                text = str(nurse_count)
                                colour = self.pale_blue                 
                     
                # add the main doors
                if ((x == block_size * 8) or (x == block_size * 9)) and (y == block_size * 16):
                     colour = self.brown 
                    
                # fill in the horizontal hospital walls
                if (y % (block_size * 3) == block_size) and (x < block_size * 7 or x > block_size * 10):
                    colour = self.light_orange   
                
                # fill in grass outside the hopsital
                if (x < block_size * 2) or (x >= self.window_width - block_size * 2) or (y == 0) or (y == self.window_height - block_size):
                    colour = self.grass_green      
                
                # add a path
                if (y == self.window_height - block_size) and (x == block_size * 8 or x == block_size * 9):
                    colour = self.sand_yellow                
                
                # create the rect for the grid
                rect = pygame.Rect(x, y, block_size, block_size)
                
                # get the centred text                    
                text_surface = self.font.render(text, True, self.black)
                text_rect = text_surface.get_rect(center=(rect.x + block_size/2, rect.y + block_size/2))  
                
                # draw the square
                pygame.draw.rect(self.screen, colour, rect)   
                self.screen.blit(text_surface, text_rect)
                
        # save frames to the folder
        if self.render_mode == "video":            
            self.frame_count = save_frames(screen=self.screen, image_folder=self.image_folder, frame_count=self.frame_count)
          
        # update the display
        pygame.display.update()
        
        # update the frame rate
        self.clock.tick(self.fps)
        
        
    def _close_display(self):
        
        # shut the display window
        pygame.display.quit()
        
        # create a video
        if self.render_mode == 'video':    
            create_video(image_folder=self.image_folder, video_folder=self.video_folder, fps=self.fps)
            
        
if __name__ == "__main__": 
    
    # test parameters
    test_days = 10
    staff_number = 10
    seeds = 1
    render = True
    
    # print logging
    display = False
    
    for seed in range(seeds):
    
        # initialise the environment
        env = hospital_env(render=render,
                           seed=seed,
                           max_timestep=test_days)
        
        for days in range(test_days):
        
            # test action with each element representing a person 
            # and the idx representing their room assignment        
            action = np.random.randint(10, size=10)  
            
            # take a step
            env.step(action=action)
            
            if display:
                print('Chosen_action: {}'.format(action))            
                print('\nDay {} ----------'.format(days))
                
                print('\nRoom Arrangement:')
                print(env.room_arrangement)
                
                print('\nCurrent Patients:')
                print(env.hospital_patients)
                print('---------------------------')
        
        if display:
            print('\nSUMMARY ----------------------------------')
            print('Total patients seen: {}'.format(env.current_patient_id + 1))
            print('Total deaths: {}'.format(env.total_deaths))
            print('Total recoveries: {}'.format(env.total_recoveries))
            print('Total days waiting: {}'.format(env.total_days_waited))
            print('-------------------------------------------')        
    