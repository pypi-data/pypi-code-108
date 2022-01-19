#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 21:57:14 2021

@author: hemerson
"""

""" 
laser_tag_env - a simple grid environment for 1 vs 1 laser tag 

Players can perform an shot and a movement each turn which are limited to either:
up, down, left or right. A player loses a life if they are shot by their opponent,
when either player has no lives left the game is over.

"""

import numpy as np
import pygame
import os

from SimpleRL.envs import environment_base 
from SimpleRL.utils import generate_scenario, shortest_path
from SimpleRL.utils import init_video, save_frames, create_video

class laser_tag_env(environment_base):
    
    # TODO: is it really necessary to have multi and single action space -> I don't think so
    # TODO: remove inefficiency in the code (i.e. repeated expressions, improve speed)
    
    def __init__(self, render=False, seed=None, action_mode="default", enemy_mode="default", difficulty="hard", lives=1, render_mode="default"):
        
        # Get assertion errors
        
        # Ensure the enemy mode for the environment is valid
        valid_action_mode = ["default", "single"]
        action_mode_error = "action_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_action_mode)
        assert action_mode in valid_action_mode, action_mode_error
        
        # Ensure the enemy mode for the environment is valid
        valid_enemy_mode = ["default", "adversarial"]
        enemy_mode_error = "enemy_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_enemy_mode)
        assert enemy_mode in valid_enemy_mode, enemy_mode_error
        
        # Ensure the difficulty for the environment is valid
        valid_difficulty = ["easy", "medium", "hard"]
        difficulty_error = "enemy_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_difficulty)
        assert difficulty in valid_difficulty, difficulty_error
        
        # Ensure the render_mode for the environment is valid
        valid_render = ["default", "video"]
        render_error = "render_mode is not valid for this environment, " \
            + "please select one of the following {} ".format(valid_render)
        assert render_mode in valid_render, render_error
        
        # Display the input settings 
        print('\nLaser Tag Settings')
        print('--------------------')
        print('Render: {}'.format(render))        
        print('Seed: {}'.format(seed))
        print('Action Mode: {}'.format(action_mode))
        print('Enemy Mode: {}'.format(enemy_mode))
        print('Difficulty: {}'.format(difficulty))
        print('Lives: {}'.format(lives))
        print('Render Mode: {}'.format(render_mode))   
        print('--------------------')
        
        self.render = render 
        self.render_mode = render_mode
        self.seed = seed 
        self.enemy_mode = enemy_mode
        self.action_mode = action_mode
        self.lives = lives
        
        # create a 1D action space
        if self.action_mode == "single":
            self.action_dim = 1 # how many actions are made each turn?
            self.action_num = np.array([25], dtype=np.int32) # how many values are there per action?  
         
        # create the default multi-dimensional action space
        elif self.action_mode == "default":
            self.action_dim = 2
            self.action_num = np.array([5, 5], dtype=np.int32)             
            
        # initialise the difficulty
        self.difficulty = difficulty
        self.computer_error = 0.0      
        
        # set medium difficulty
        if self.difficulty == "medium":
            self.computer_error = 0.25
            
        # set easy difficulty
        elif self.difficulty == "easy":
            self.computer_error = 0.5
        
        # Set environmetal parameters
        np.random.seed(self.seed)  
        self.environment_name = 'Laser_tag'
        self.shot_range = 5 # how many squares will a bullet travel?
        self.grid_size = 8
        self.positive_reward = +1
        self.negative_reward = -1
        self.player_param = 1
        self.enemy_param = 2
        self.terrain_param = 3
        self.empty_param = 0
        
        # Initialise the environment
        self.bullet_path = None # for displaying the bullets path
        self.bullet_hits = None # for displaying successful shots
        
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
            self.window_width = 400
            self.window_height = 400
            
            # get the screen
            self._init_display() 
            
            # set the fps
            self.fps = 5
            
            # get the font 
            self.font = pygame.font.Font(None, 32)
            
            # create the colours
            self.green = (0, 153, 0)
            self.grey = (160, 160, 160)
            self.blue = (102, 178, 255)
            self.red = (255, 51, 51)
            self.black = (0, 0, 0)          
    
    def reset(self):
        
        # reset the map parameters
        self.current_player = self.player_param
        self.player_lives = self.lives
        self.opposing_player = self.enemy_param
        self.enemy_lives = self.lives
        
        self.game_outcome = None
        self.grid_map = generate_scenario(
                grid_size = self.grid_size
                )
        
        return self.grid_map.flatten()
        
    def step(self, player_action=None):
        
        # check the action input is valid (i.e. np.int32 of valid range)        
        self.check_discrete_input(player_action)  
        
        # update the grid according to the player move
        reward, done, info = self._update_grid(action=player_action)
        
        # display the map
        if self.render:
            self._display()
          
        # check if the episode has terminated
        if not done:
            
            # get the computer action
            if self.enemy_mode == "default":
                computer_action = self._get_computer_action()                  
                reward, done, info = self._update_grid(action=computer_action)  
                
                # display the map
                if self.render:
                    self._display()                
            
            # get the action of another network
            elif self.enemy_mode == "adversarial":       
                pass
               
        if done and self.render: 
            self._close_display()         
                 
        return self.grid_map.flatten(), reward, done, info
    
    def sample_discrete_action(self):
        return np.random.randint(self.action_num - 1, size=self.action_dim)
    
    def _update_grid(self, action):
        
        # 25 actions --------        
        #      NO|LM|UM|RM|DM
        #   NO|00|01|02|03|04
        #   LS|05|06|07|08|09
        #   US|10|11|12|13|14
        #   RS|15|15|16|17|18
        #   DS|20|21|22|23|24
        # -------------------
        
        # 0, 1, 2, 3, 4 = no_move, move_left, move_up, move_right, move_down
        # 0, 1, 2, 3, 4 = no_shot, shoot_left, shoot_up, shoot_right, shoot_down
              
        if self.action_mode == "single":
            move_action = action % 5        
            shot_action = np.floor_divide(action, 5)
        
        elif self.action_mode == "default":
            move_action = action[0].reshape(1,)
            shot_action = action[1].reshape(1,)
        
        move_direction = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]])
        reward, done, info = 0, False, {"outcome" : None}    
        
        # reset the bullet path and the hit arrays
        self.bullet_path = np.empty((0, 2), dtype=np.int32)
        self.bullet_hits = np.empty((0, 2), dtype=np.int32)
        
        # get the player's location
        player_pos = np.asarray(np.where(self.grid_map == self.current_player)).flatten() 
        
        # if the action is a move
        if move_action > 0:
            
            # get the player move direction
            chosen_move = move_direction[move_action[0] - 1, :]
            
            # get the grid value of the move           
            final_player_pos = player_pos + chosen_move   
                        
            valid_move = self._is_move_valid(final_player_pos, self.grid_map)
            
            # Update the grid if the move is valid
            if valid_move:
                
                # assign players to correct square
                self.grid_map[final_player_pos[0], final_player_pos[1]] = self.current_player
                self.grid_map[player_pos[0], player_pos[1]] = 0
                
                # update the player position for the shot
                player_pos = final_player_pos            
                
        # if the action is a shot
        if shot_action > 0:
                        
            # get the player shot direction
            chosen_move = move_direction[shot_action[0] - 1, :]
            
            # get the outcome of the shot
            reward, done, info = self._get_shot_trajectory(chosen_move, player_pos, self.grid_map, self.current_player)
            
            # if the player has been shot remove them
            if done:
                
                done = False
                
                # update the lives
                if self.current_player == self.player_param:
                    self.enemy_lives -= 1            
                else:
                    self.player_lives -= 1
                
                # end the game when lives have run out
                if self.player_lives == 0 or self.enemy_lives == 0:                
                
                    # get the enemy position
                    enemy_pos = np.asarray(np.where(self.grid_map == self.opposing_player)).flatten() 
                    
                    # remove the enemy and update the display
                    self.grid_map[enemy_pos[0], enemy_pos[1]] = 0
                    self.bullet_hits = np.append(self.bullet_hits, enemy_pos.reshape(1, -1), axis=0)
                    
                    done = True
                                                
        # switch the current player to the opposite player 
        temp_opposing_player = self.opposing_player 
        self.opposing_player = self.current_player
        self.current_player = temp_opposing_player
                
        return reward, done, info    
    
    def _get_shot_trajectory(self, chosen_move, current_player_pos, grid_map, current_player):
                
        # get the player value
        if current_player == self.player_param:
            opposing_player = self.enemy_param
        else:
            opposing_player = self.player_param
        
        # the default outcomes
        reward, done, info = 0, False, {"outcome" : None}  
        
        for i in range(self.shot_range):
            
            # get the current bullet position
            bullet_vec = chosen_move * (i + 1)
            bullet_pos = current_player_pos + bullet_vec                
            row, col = bullet_pos
            
            # is the bullet out of bounds?
            if (row < 0 or row >= self.grid_size) or (col < 0 or col >= self.grid_size):
                break
            
            # has the bullet hit terrain?
            if grid_map[row, col] == self.terrain_param:
                break
            
            # has the bullet hit the enemy?
            if grid_map[row, col] == opposing_player: 
                
                # set the parameters to end the game
                
                # get the correct reward
                if self.current_player == self.player_param:
                    reward = self.positive_reward
                elif self.current_player == self.enemy_param:
                    reward = self.negative_reward
                
                done = True
                info["outcome"] = current_player
                break
            
            # add the bullet path to the array for displaying
            self.bullet_path = np.append(self.bullet_path, bullet_pos.reshape(1, -1), axis=0)
            
        return reward, done, info
    
    def _is_move_valid(self, final_player_pos, grid_map):   
        
        # assign the new player position
        row, col = final_player_pos          
        
        # check the square is within the grid
        if (row >= 0 and row < self.grid_size) and (col >= 0 and col < self.grid_size):
        
            # check the square is empty
            if grid_map[row, col] == 0:
                return True
                
        return False     
    
    def _get_computer_action(self):
        
        # select a random action in the case the agent difficulty is set
        random_num = np.random.uniform(0, 1, 1)        
        if random_num < self.computer_error:
            
            if self.action_mode == "single":                
                return np.random.randint(25, size=1)
            
            elif self.action_mode == "default":
                return np.random.randint(5, size=2)

        # get the computer's and the player's location
        computer_pos = np.asarray(np.where(self.grid_map == self.current_player)).flatten() 
        player_pos =  np.asarray(np.where(self.grid_map == self.opposing_player)).flatten()    
        
        # get the possible shot direction
        # left, up, right, down
        directions = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]])
        
        # STEP 1: Check if a shot is possible
        
        # cycle through possible shots
        for shot_direction in range(directions.shape[0]):
            
            #  check if the game could conclude with a shot            
            _, done, _ = self._get_shot_trajectory(directions[shot_direction, :], computer_pos, self.grid_map, self.current_player)
            
            # select the concluding action
            if done: 
                
                move_action = 0 
                shot_action = shot_direction + 1
                
                if self.action_mode == "single":
                    return np.array([move_action + shot_action * 5], dtype=np.int32)
                
                elif self.action_mode == "default":
                    return np.array([move_action, shot_action], dtype=np.int32)
        
        # STEP 2: Check if a step shot is possible
        
        valid_computer_moves = []
        
        # cycle through possible moves
        for move_direction in range(directions.shape[0]):
            
            # get the possible moves
            chosen_move = directions[move_direction, :]        
            final_computer_pos =  computer_pos + chosen_move
            
            # Check if the move is valid
            valid_move = self._is_move_valid(final_computer_pos, self.grid_map)
            
            #  check if the game could conclude with a move-shot  
            if valid_move:
                
                valid_computer_moves.append(chosen_move)
                
                # update a temporary grid
                temp_grid_map = np.copy(self.grid_map)
                temp_grid_map[final_computer_pos[0], final_computer_pos[1]] = self.current_player
                temp_grid_map[computer_pos[0], computer_pos[1]] = 0   
                
                for shot_direction in range(directions.shape[0]):
                    _, done, _ = self._get_shot_trajectory(directions[shot_direction, :], final_computer_pos, temp_grid_map, self.current_player)
                    
                    # select the concluding action
                    if done: 
                        move_action = move_direction + 1 
                        shot_action = shot_direction + 1
                        
                        if self.action_mode == "single":
                            return np.array([move_action + shot_action * 5], dtype=np.int32)
                        
                        elif self.action_mode == "default":
                            return np.array([move_action, shot_action], dtype=np.int32)
       
        # STEP 3: Check if any moves would result in the possibility of an enemy step shot
        
        # only cycle through valid moves
        valid_computer_moves = np.array(valid_computer_moves, dtype=np.int32)
        
        # initialise the safe computer moves
        unsafe_computer_moves = []
        safe_computer_moves = []
        
        # cycle through current player moves
        for computer_move_direction in range(valid_computer_moves.shape[0]):
            
            computer_move_safe = True
            
            # get the possible moves
            comp_chosen_move = valid_computer_moves[computer_move_direction, :]                
            final_computer_pos = computer_pos + comp_chosen_move
            
            # update a temporary grid
            temp_grid_map = np.copy(self.grid_map)
            temp_grid_map[final_computer_pos[0], final_computer_pos[1]] = self.current_player
            temp_grid_map[computer_pos[0], computer_pos[1]] = 0   
            
            # update temp player
            temp_player = self.opposing_player
            
            # cycle through the player moves                            
            for player_move_direction in range(directions.shape[0]):
                
                # get the possible moves
                play_chosen_move = directions[player_move_direction, :]        
                final_player_pos =  player_pos + play_chosen_move
                
                # Check if the move is valid
                valid_player_move = self._is_move_valid(final_player_pos, temp_grid_map)
                
                if valid_player_move:
                    
                    # update the temporary grid again
                    player_temp_grid_map = np.copy(temp_grid_map)
                    player_temp_grid_map[final_player_pos[0], final_player_pos[1]] = temp_player
                    player_temp_grid_map[player_pos[0], player_pos[1]] = 0   
                    
                    # cycle through player shots
                    for player_shot_direction in range(directions.shape[0]):
                        
                        #  check if the game could conclude with a shot            
                        _, done, _ = self._get_shot_trajectory(directions[player_shot_direction, :], final_player_pos, player_temp_grid_map, temp_player)
                        
                        # mark this computer move as unsafes
                        if done:              
                            computer_move_safe = False
                            unsafe_computer_moves.append(comp_chosen_move)
                            break
                
                # break the loop if an unsafe move is found
                if not computer_move_safe:                    
                    break
            
            # make a list of safe moves
            if computer_move_safe:
                safe_computer_moves.append(comp_chosen_move)
       
        # STEP 4: Take the shortest path to the player excluding those that would result in a step shot from opponent
        
        unsafe_computer_moves = np.array(unsafe_computer_moves, np.int32)
        safe_computer_moves = np.array(safe_computer_moves, np.int32)
        
        # if there is only one safe move take it
        if safe_computer_moves.shape[0] == 1:            
            move_action = np.where(np.all(directions == safe_computer_moves, axis=1))[0][0] + 1 
            
            if self.action_mode == "single":
                return np.array([move_action], dtype=np.int32)
            
            elif self.action_mode == "default":
                return np.array([move_action, 0], dtype=np.int32)   
        
        # if there are no safe moves, do not move
        if safe_computer_moves.shape[0] == 0:     
            
            if self.action_mode == "single":
                return np.array([0], dtype=np.int32)
            
            elif self.action_mode == "default":
                return np.array([0, 0], dtype=np.int32)   
                    
        # Remove the dangerous moves from the scope of the search algorithm
        temp_grid_map = np.copy(self.grid_map)
        for moves in range(unsafe_computer_moves.shape[0]):
            
            # get the possible moves
            chosen_move = unsafe_computer_moves[moves, :]        
            final_computer_pos = computer_pos  + chosen_move
            
            # Block out the dangerous move from the search
            temp_grid_map[final_computer_pos[0], final_computer_pos[1]] = 3
        
        # get the shortest path
        path = shortest_path(temp_grid_map, start=computer_pos, goal=player_pos)
        
        # get the selected move
        selected_move = np.array(path[-2], dtype=np.int32) - computer_pos        
        move_action = np.where(np.all(directions == selected_move, axis=1))[0][0] + 1   
        
        if self.action_mode == "single":
            return np.array([move_action], dtype=np.int32)
        
        elif self.action_mode == "default":
            return np.array([move_action, 0], dtype=np.int32)

            
    def _init_display(self):
        
        # quit any previous games
        pygame.display.quit()
        
        # initialise pygame
        pygame.init()    
        
        pygame.display.set_caption("Laser Tag Environment")
        
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
        self.screen.fill(self.green)        
        
        # set the size of the block
        block_size = int(400 / self.grid_size) 
        
        # loop through the grid
        for x in range(0, self.window_width, block_size):
            for y in range(0, self.window_height, block_size):
                
                row = int(x / block_size)
                col = int(y / block_size)
                
                colour = self.green
                text = ""
                
                # create the rect for the grid
                rect = pygame.Rect(x, y, block_size, block_size)
                
                # mark the player
                if self.grid_map[row, col] == 1:
                    colour = self.blue     
                    text = str(self.player_lives)
                    
                # mark the enemy
                elif self.grid_map[row, col] == 2:
                    colour = self.red    
                    text = str(self.enemy_lives)
                
                # mark obstacles
                elif self.grid_map[row, col] == 3:
                    colour = self.grey 
                
                # mark hits
                if self.bullet_hits.shape[0] > 0:                    
                    if row == self.bullet_hits[0, 0] and col == self.bullet_hits[0, 1]:
                        text = 'X'
                        
                # mark the bullet path
                if self.bullet_path.shape[0] > 0:  
                    for blt in range(self.bullet_path.shape[0]):
                        if row == self.bullet_path[blt, 0] and col == self.bullet_path[blt, 1]:
                            text = "*"
                            break                        
                
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
        
    seed_range = 10
    enemy_mode = "default"
    difficulty = "hard"
    action_mode = "default"
    
    # track the player wins out of max
    total_reward = 0
    
    for seed in range(seed_range):
    
        # intialise the environment
        env = laser_tag_env(seed=seed, 
                            render=True,
                            action_mode=action_mode,
                            enemy_mode=enemy_mode,
                            difficulty=difficulty,
                            lives=3)
        
        # reset the state
        state, done = env.reset(), False
        counter = 0
        
        # run the training loop
        while not done and counter < 100:
            
            action = env.sample_discrete_action()            
            next_state, reward, done, info = env.step(player_action=action)
            
            if reward > 0:
                total_reward += reward
            
            # print the winner
            if done: 
                print('Seed {} - Player {} wins'.format(seed, info["outcome"]))
                
            state = next_state
            counter += 1
            
            # get an action from the opposing network in adversarial mode
            if enemy_mode == "adversarial" and not done:
                
                action = env.sample_discrete_action()            
                next_state, reward, done, info = env.step(player_action=action)
                
                # print the winner
                if done: 
                    print('Seed {} - Player {} wins'.format(seed, info["outcome"]))
                    
                state = next_state
                counter += 1
        
    print('Player won {}/{}'.format(total_reward, seed_range))
    
            