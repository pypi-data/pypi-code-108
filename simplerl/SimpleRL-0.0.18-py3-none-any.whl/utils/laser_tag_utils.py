#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 22:12:23 2021

@author: hemerson
"""

import numpy as np

def generate_scenario(grid_size=8, player_param=1, enemy_param=2, terrain_param=3, empty_param=0): 
    
    """
    creates a random grid with players, enemies and terrain for the laser_tag game.
    
    Parameters:
    ----------
    grid_size - int (how large a grid should the game be set in)
        
    Return:
    ------
     map_grid - np.int32 (A 2d numpy array with values corresponding to player, enemy
                          and terrain obstacles)         
    """
    
    percent_terrain = 0.3 # what is the percentage coverage of the grid with terrain
   
    # generate a numbered grid and get an array of the edge elements
    array_grid = np.arange(grid_size * grid_size).reshape(grid_size, grid_size)
    array_edges = np.concatenate([array_grid[0,:-1], array_grid[:-1,-1], array_grid[-1,::-1], array_grid[-2:0:-1,0]])
    
    # randomly select an edge element and assign position to player and opposite position to enemys
    start_num = array_edges[np.random.choice(len(array_edges), size=1, replace=False)]
    player_pos = np.array([start_num[0] / grid_size, start_num[0] % grid_size], dtype=np.int32)
    enemy_pos = np.absolute(player_pos - np.array([grid_size - 1, grid_size - 1]))
    
    # get the positions which are not at the edge and make PERCENT_TERRAIN of tiles terrain
    array_centre = np.setdiff1d(array_grid.flatten(), array_edges)
    num_terrain_squares = int(len(array_centre) * percent_terrain)
    terrain_squares = array_centre[np.random.choice(len(array_centre), size=num_terrain_squares, replace=False)]
    
    get_pos = lambda x: np.array([x/grid_size, x % grid_size], dtype=np.int32)
    terrain_pos = get_pos(terrain_squares)
    
    # create a grid and assign numbers representing player, enemy and terrain
    # 0, 1, 2, 3 = vacant, player, enemy, terrain
    map_grid = np.ones((grid_size, grid_size), dtype=np.int32) * empty_param
    map_grid[player_pos[0], player_pos[1]] = player_param
    map_grid[enemy_pos[0], enemy_pos[1]] = enemy_param
    map_grid[terrain_pos[0, :], terrain_pos[1, :]] = terrain_param
    
    return map_grid        


def shortest_path(grid, start, goal):
    
    """
    Calculates the shortest path between a start point and a goal in a given 
    grid for the laser_tag game.
    
    Parameters:
    ----------
    grid - np.int32 (the current board configuration)
    start - np.int32 (the position of the starting point in the grid)
    goal - np.int32 (the position of the goal point in the grid)
        
    Return:
    ------
    path - list (a list of coordinates for the shortest path in the given grid         
    """
    
    # Implementation largely inspired by the following article:
    # https://levelup.gitconnected.com/dijkstras-shortest-path-algorithm-in-a-grid-eb505eb3a290
    
    # get the dimensions of the grid
    max_val = grid.shape[0]    
    
    # convert the grid to the correct format
    processed_grid = np.copy(grid)
    processed_grid[processed_grid == 3] = 999 # assign boulders = 999
    processed_grid[processed_grid == 0] = 4 # assign empty spaces to be 4
    processed_grid[processed_grid == 1] = 0 # assign player to be 0
    processed_grid[processed_grid == 2] = 0 # assign computer to be 0
    processed_grid[processed_grid == 4] = 1 # assign empty spaces to be 1  
        
    # Create arrays to store the distance, _ and visited
    distmap = np.ones((max_val, max_val), dtype=int) * np.Infinity
    originmap = np.ones((max_val, max_val), dtype=int) * np.nan
    visited = np.zeros((max_val, max_val), dtype=bool)    
    
    # set starting and end position 
    start_row, start_col = start
    end_row, end_col = goal    
    
    # get the initialisation coords
    row, col = start_row, start_col
    
    # Initialise the distance map to starting location
    distmap[row, col] = 0
    finished = False
    count = 0
    
    # STEP 1: Loop Dijkstra until reaching the target cell
    while not finished:
        
      # move to row + 1, col
      if row < max_val - 1:
          
        # update the distance map to show the number of steps from the source
        if (distmap[row + 1, col] > processed_grid[row + 1, col] + distmap[row, col]) and not (visited[row + 1, col]) and (grid[row + 1, col] != 3):
          distmap[row + 1, col] = processed_grid[row + 1, col] + distmap[row, col]
          
          # if the array were a flat list what index would (row, col) correspond to for a shape (max_val, max_val)
          originmap[row + 1, col] = np.ravel_multi_index([row, col], (max_val, max_val))
          
      # move to row - 1, col
      if row > 0:
          
        # update the distance map to show the number of steps from the source
        if (distmap[row - 1, col] > processed_grid[row - 1, col] + distmap[row, col]) and not (visited[row - 1, col]) and (grid[row - 1, col] != 3):
          distmap[row - 1, col] = processed_grid[row - 1, col] + distmap[row, col]
          
          # if the array were a flat list what index would (row, col) correspond to for a shape (max_val, max_val)
          originmap[row - 1, col] = np.ravel_multi_index([row, col], (max_val, max_val))
          
      # move to row, col + 1
      if col < max_val - 1:
          
        # update the distance map to show the number of steps from the source
        if (distmap[row, col + 1] > processed_grid[row, col + 1] + distmap[row, col]) and not (visited[row, col + 1]) and (grid[row, col + 1] != 3):
          distmap[row, col + 1] = processed_grid[row, col + 1] + distmap[row, col]
          
          # if the array were a flat list what index would (row, col) correspond to for a shape (max_val, max_val)
          originmap[row, col + 1] = np.ravel_multi_index([row, col], (max_val, max_val))
          
      # move to row, col - 1
      if col > 0:
          
        # update the distance map to show the number of steps from the source
        if (distmap[row, col - 1] > processed_grid[row, col - 1] + distmap[row, col]) and not (visited[row, col - 1]) and (grid[row, col - 1] != 3):
          distmap[row, col - 1] = processed_grid[row, col - 1] + distmap[row, col]
          
          # if the array were a flat list what index would (row, col) correspond to for a shape (max_val, max_val)
          originmap[row, col - 1] = np.ravel_multi_index([row, col], (max_val, max_val))
          
      # set this index to visited
      visited[row, col] = True
      
      # set the visited locations to infinity in the distance map
      dismaptemp = distmap
      dismaptemp[np.where(visited)] =  np.Infinity
      
      # now we find the shortest path so far      
      
      # if the array were a flat array what index would np.argmin(dismaptemp) correspond to for a shape np.shape(dismaptemp)
      # as argmin returns the position in a flat array
      minpost = np.unravel_index(np.argmin(dismaptemp), np.shape(dismaptemp))
      
      # set the coordinates as the current point with the shortest distance
      row, col = minpost[0], minpost[1]
      
      # Terminate if algorithm has reached the goal
      if row == end_row and col == end_col:
        finished = True
                
      count = count + 1    
                
    # STEP 2: Start backtracking to plot the path
    
    # initialise the temporary array
    mattemp = processed_grid.astype(float)
    row, col = end_row, end_col
    path = []
    
    # set the end point to NaN
    mattemp[int(row), int(col)] = np.nan
    
    # run until back to the original position
    while row != start_row or col != start_col :
    
      # add coords to the path
      path.append([int(row), int(col)])      
      
      # follow the originmap to the previous position
      rowrowcolcol = np.unravel_index(int(originmap[int(row), int(col)]), (max_val, max_val))
      
      # set row, col to prev_row, prev_col      
      row, col = rowrowcolcol[0], rowrowcolcol[1]
      
      # Nan current position
      mattemp[int(row), int(col)] = np.nan
      
    path.append([int(row), int(col)])
    
    return path

if __name__ == "__main__":
    
    # seed the environment
    np.random.seed(0)
    
    # generate the grid
    grid = generate_scenario()
    
    # create an additional obstacle
    grid[0, 1] = 3    
    
    print(grid)
    
    # get the start and end
    start = np.asarray(np.where(grid == 1)).flatten() 
    goal = np.asarray(np.where(grid == 2)).flatten()  
    
    # calculate shortest path
    path = shortest_path(grid, start, goal)

    print(path)
