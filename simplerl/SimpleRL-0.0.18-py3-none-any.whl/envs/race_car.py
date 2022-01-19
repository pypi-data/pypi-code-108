#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 16:15:32 2021

@author: hemerson
"""

""" 
race_car_env - a race car track where the agent is timed for 1 lap.

"""

import numpy as np
import random
import pygame
import os
import math

from SimpleRL.envs import environment_base 
from SimpleRL.utils import generate_track, draw_map, simulate_car
from SimpleRL.utils import init_video, save_frames, create_video

# Testing
import time

class race_car_env(environment_base):
    
    # TODO: remove inefficiency in the code (i.e. repeated expressions, improve speed)
    # TODO: trying doing some greater optimising -> move code which doesn't change outside of loops
    # TODO: may need to tweak the balance between reducing no of track points and increasing error margin
    # TODO: may need to increase crash penalty to avoid agent terminating
    #       to reduce existence penalty  
    
    def __init__(self, render=False, seed=None, render_mode="default", driver_mode="human", use_selected_tracks=True):
        
        # Get assertion errors
        
        # Ensure the render_mode for the environment is valid
        valid_render = ["default", "video"]
        render_error = "render_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_render)
        assert render_mode in valid_render, render_error
        
        # Ensure the driver_mode for the environment is valid
        valid_driver= ["default", "human"]
        driver_error = "driver_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_driver)
        assert driver_mode in valid_driver, driver_error
        
        # Display the input settings 
        print('\nRace Car Settings')
        print('--------------------')
        print('Render: {}'.format(render))        
        print('Seed: {}'.format(seed))
        print('Render Mode: {}'.format(render_mode))   
        print('Driver Mode: {}'.format(driver_mode)) 
        print('Use Selected Tracks: {}'.format(use_selected_tracks))
        print('--------------------')
        
        self.render = render 
        self.render_mode = render_mode
        self.seed = seed 
        self.driver_mode = driver_mode
        
        # Debugging
        self.debugging = False
        
        # set render to true if human driver
        if self.driver_mode == "human":
            self.render = True
            
        # run only tracks which are definitely well generated
        if use_selected_tracks:
            safe_seeds = np.array([25027, 57447, 12855, 97307, 32899,
                                   1944, 22906, 29030, 90129, 93030], dtype=np.int32)
            self.seed = np.random.choice(safe_seeds, 1)[0]
            
            print(self.seed)
        
        # Set environmetal parameters
        np.random.seed(self.seed)  
        random.seed(self.seed)
        self.environment_name = 'Race_car'
        self.action_dim = 1
        self.action_num = np.array([3], dtype=np.int32)
        self.state_dim = 6
        
        self.height, self.width = 600, 800
        self.track_width = 60 
        self.checkpoint_threshold = 1.1
        self.fps = 30        
        
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
            self.window_width = self.width
            self.window_height = self.height
            
            # set map render parameters
            self.checkpoint_margin = 5
            self.checkpoint_angle_offset = 3
            
            # get the screen
            self._init_display() 
            
            # get the font 
            self.font = pygame.font.Font(None, 32)
            
            # create the colours
            self.white = (255, 255, 255)
            self.black = (0, 0, 0)    
            self.blue = (102, 178, 255)
            self.red = (255, 51, 51)
            self.grass_green = (58, 156, 53)            
            self.grey = (186, 182, 168)
            self.yellow = (255, 233, 0)
            
    
    def reset(self):
        
        # generate the new track points and checkpoints
        self.track_points, self.checkpoints = generate_track(height=self.height, width=self.width, track_width=self.track_width) 
        
        # get the player start position, track edges and checkpoint edges
        (self.start_point, self.start_angle, self.inside_track_points,
         self.outside_track_points, self.checkpoint_edges) = self._set_track_edges(track_points=self.track_points, checkpoints=self.checkpoints)
                
        # initialise the car
        self.car = simulate_car(fps=self.fps, starting_position=self.start_point, starting_angle=self.start_angle)
        
        # get the state
        if self.driver_mode == "default":
            return self._process_state()            
        
        
    def step(self, player_action=None):
        
        # actions:
        # 0 = brake | 1 = left | 2 = right
                
        # change the form of the action
        if self.driver_mode == "default":            
            index = player_action[0]
            empty_array = np.zeros((self.action_num), dtype=bool)
            empty_array[index] = True
            player_action = empty_array
        
        # update the state of the according to the action
        self.car.process_action(action=player_action)
        
        if self.debugging:
            tic = time.perf_counter()
        
        # get the updated sensor positions
        self.sensor_points = self.car.get_sensor_ranges(outside_track_points=self.outside_track_points, 
                                                        inside_track_points=self.inside_track_points,
                                                        track_points=self.track_points)
        
        if self.debugging:
            toc = time.perf_counter()        
            print('{}s'.format(toc - tic))
        
        # check whether the car has completed a lap or crashed
        done, info = self._check_collisions(sensor_points=self.sensor_points)
        
        # determine the reward
        reward = self._process_reward(information=info)        
        
        # display the map
        if self.render: 
            self._display() 
            
            # shut the display
            if done:  self._close_display()
        
        # if there is an AI driver
        if self.driver_mode == "default": 
            
            # get the state and output
            state = self._process_state()            
            return state, reward, done, info
        
        elif self.driver_mode == "human":   
            return done
        
    """
    Given the points of the track and the selected checkpoints get the starting
    position of the car, the edges of the track and the edges of the checkpoints
    """        
    def _set_track_edges(self, track_points, checkpoints):
        
        # initialise the arrays and get the track radius
        inside_track_points, outside_track_points = [], []
        radius = self.track_width // 2
        
        # cycle through the points and calculate their edges based on the angle
        final_index = len(track_points) - 1 
        for idx, point in enumerate(track_points):
            
            # get the next and current point
            current_point = point
            next_point = track_points[(idx + 30) % final_index]
            prev_point = track_points[(idx - 30) % final_index]
            
            # calculate an angle between the two points (in radians)
            angle = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
                        
            # add the outside track coordinates
            outside_track_x = current_point[0] + radius * math.sin(angle)
            outside_track_y = current_point[1] - radius * math.cos(angle)   
            outside_track_points.append((outside_track_x, outside_track_y))  
            
            # add the inside track coordinates
            inside_track_x = current_point[0] - radius * math.sin(angle)
            inside_track_y = current_point[1] + radius * math.cos(angle)
            inside_track_points.append((inside_track_x, inside_track_y))   
            
            # record the angle between the final point and the first 
            if idx == final_index:
                final_angle = angle
                
        # removes error of appending inside and outside
        inside_track_points += inside_track_points[:5]
        outside_track_points += outside_track_points[:5]
                
        # get the start point of the car
        start_point = checkpoints[0]
        start_angle = final_angle
        
        # cycle through the checkpoints and get their edge coordinates        
        checkpoint_edges = []        
        for idx, checkpoint in enumerate(self.checkpoints):
            
            # get the next and current point
            current_point = checkpoint
            next_point = self.checkpoints[(idx + 1) % len(self.checkpoints)]
            prev_point = self.checkpoints[(idx - 1) % len(self.checkpoints)]
            
            # calculate an angle between the two points (in radians)
            angle = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
                        
            # add the outside track coordinates
            out_checkpoint_x = current_point[0] + radius * math.sin(angle)
            out_checkpoint_y = current_point[1] - radius * math.cos(angle) 
            
            # add the inside track coordinates
            in_checkpoint_x = current_point[0] - radius * math.sin(angle)
            in_checkpoint_y = current_point[1] + radius * math.cos(angle) 
            
            checkpoint_edges.append([[out_checkpoint_x, out_checkpoint_y], [in_checkpoint_x, in_checkpoint_y]]) 
            
        # add the start point as the final checkpoint
        starting_checkpoint = checkpoint_edges.pop(0) 
        checkpoint_edges.append(starting_checkpoint)   
        
        return start_point, start_angle, inside_track_points, outside_track_points, checkpoint_edges
    
    """
    Return a numpy array containing the current sensor distances for the car
    and its current speed
    """
    def _process_state(self):
        
        # get the car's speed
        current_speed = self.car.speed             
        
        # get the sensor collision points
        sensor_points = self.car.get_sensor_ranges(outside_track_points=self.outside_track_points, 
                                                  inside_track_points=self.inside_track_points,
                                                  track_points=self.track_points,
                                                  debugging=self.debugging
                                                  )  
        # get the distances from car position
        distances = [math.dist(self.car.position, sensor_point) for sensor_point in sensor_points]
                  
        # return the state of the environment                                          
        return np.array(distances + [current_speed], dtype=np.float32) 
    
    """
    Given the current sensor distances for the car, check if the car has crashed
    and update the number of checkpoints its passed.
    """    
    def _check_collisions(self, sensor_points):
        
        # check for collisions with the edge of track
        crashed_front = math.dist(sensor_points[2], self.car.position) < (self.car.dimensions[0] / 2)
        crashed_side = math.dist(sensor_points[0], self.car.position) < (self.car.dimensions[1] / 2)
        
        # if a crash has occurred end the race
        if crashed_side or crashed_front:
            return True, {"outcome": "crash"}    
            
        # get the current position and the next checkpoint position 
        current_position = self.car.position
        next_checkpoint = self.checkpoint_edges[0]
        
        # calculate the combined distance of the player form the edges
        outside_edge = math.dist(current_position, next_checkpoint[0])
        inside_edge = math.dist(current_position, next_checkpoint[1])
        combined_dist = outside_edge + inside_edge
        
        # if a checkpoint has been passed update the remaining checkpoints
        if combined_dist < (self.checkpoint_threshold * self.track_width):
            self.checkpoint_edges.pop(0)
            
            # update the user
            if self.render:
                print('{} checkpoints remaining'.format(len(self.checkpoint_edges)))
            
            # if this was the last checkpoint end the game
            if len(self.checkpoint_edges) == 0:
                if self.render: print('Lap completed')
                return True, {"outcome": "lap"}
            
            # return state for checkpoint passed
            return False, {"outcome": "checkpoint"}
            
        return False, {"outcome": None}
            
    """
    Calculate the agent reward using the outcome of the player action/
    """
    def _process_reward(self, information):
        
        # get the outcome
        outcome = information["outcome"]
        
        # deduct reward for existing this turn
        reward_total = -1
        
        # add reward based on outcome
        if outcome:
            if outcome == "lap":
                reward_total += 1000            
            elif outcome == "checkpoint":
                reward_total += 100                
            elif outcome == "crash":
                reward_total -= 1000
                
        return reward_total
    
    def _init_display(self):
        
        # quit any previous games
        pygame.display.quit()
        
        # initialise pygame
        pygame.init()    
        
        # set the environment name
        pygame.display.set_caption("Race Car Environment")
        
        # initialise the clock
        self.clock = pygame.time.Clock()
        
        # create the screen
        self.screen = pygame.display.set_mode([self.window_width, self.window_height])
        
    
    def _display(self):   
        
        # quit the game
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.display.quit()
                
        # draw the map
        self.screen = draw_map(f_points=self.track_points, checkpoints=self.checkpoints, screen=self.screen,
                               track_width=self.track_width, checkpoint_margin=self.checkpoint_margin, 
                               checkpoint_angle_offset=self.checkpoint_angle_offset, track_colour=self.grey, 
                               checkpoint_colour=self.blue, start_colour=self.red, background_colour=self.grass_green)  

        
        # this is for debugging
        """
        for checkpoints in self.checkpoint_edges:            
            pygame.draw.circle(self.screen, (0, 0, 255), checkpoints[0], 3, 1)
            pygame.draw.circle(self.screen, (0, 0, 255), checkpoints[1], 3, 1)
        """            
        
        # render the car
        self.screen = self.car.render_car(screen=self.screen, car_colour=self.yellow, debugging=self.debugging)        
                
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
        
    seed_range = 1
    driver_mode = "human" # "default"
    render = True
    
    # track the player wins out of max
    total_reward = 0        
    
    for seed in range(seed_range):
    
        # intialise the environment
        env = race_car_env(render=render, driver_mode=driver_mode, use_selected_tracks=True)

        # reset the state
        done, counter = False, 0
        if driver_mode == "default":
            state = env.reset() 
            
        elif driver_mode == "human":
            started = False
            done = env.step(player_action=[False] * 3)
        
        # run the training loop
        while not done:
            
            if driver_mode == "human":
                
                # get the human action
                action = [False] * 3
                keys = pygame.key.get_pressed()  
                
                # have brake on until player presses up key
                if not started:
                    action[0] = True
                    
                if keys[pygame.K_UP]:                    
                    started = True                
                if keys[pygame.K_DOWN]:                    
                    action[0] = True
                if keys[pygame.K_LEFT]:
                    action[1] = True
                if keys[pygame.K_RIGHT]:                    
                    action[2] = True
                    
                done = env.step(player_action=action)
                counter += 1
                
            elif driver_mode == "default":
                
                action = np.random.randint(0, 3, size=(1,))                
                next_state, reward, done, info = env.step(player_action=action)
                
                if info['outcome'] == "crash":
                    print('Crash')
            
                total_reward += reward
                    
                state = next_state
                
                counter += 1            
                if counter >= 1000:
                    done = True
                
        print('Ep {} - Lap completed in {} timesteps'.format(seed, counter))
        print('reward {}'.format(total_reward))
        
    