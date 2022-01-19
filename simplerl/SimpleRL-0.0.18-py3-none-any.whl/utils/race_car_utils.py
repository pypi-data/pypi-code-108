#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 16:39:19 2021

@author: hemerson
"""

import numpy as np
import math
import pygame 
import random 
import scipy.spatial as spatial
import scipy.interpolate as interpolate
import warnings

# Testing 
import time

# Try using this to generate a race track:
# https://github.com/juangallostra/procedural-tracks

# Used to compute the convex hull
# https://startupnextdoor.com/computing-convex-hull-in-python/

# Used for B-Spline interpolation and evaluation:
# https://github.com/XuejiaoYuan/BSpline

# Used for car dynamics:
# https://github.com/mdeyo/simple-pycar

# TODO: comment all the bspline curve functions and change the variables to be more readable
# TODO: try to remove the scipy dependency

# Creating the Track ----------------------------------------------------------

"""
Function for generating the points of a track and several checkpoints mapped
evenly along it.
"""
def generate_track(track_width, width, height):
    
    # parameters for random points
    min_points = 20
    max_points = 30
    margin = 50
    min_distance = 20 
    
    # parameters for shape_track
    difficulty = 0.1
    max_displacement = 80
    max_angle = 70
    distance_between_points = 80
    
    # parameters for smooth_track
    spline_points = 1000
    
    # parameters for get checkpoints
    number_checkpoints = 20  

    # generate a set of random points
    points = random_points(min_p=min_points, max_p=max_points, margin=margin,
                           min_distance=min_distance, width=width, height=height)
    
    # calculate the convex hull of the random points
    hull = spatial.ConvexHull(points) # convex_hull(points)    
    hull_points = np.array([points[hull.vertices[i]] for i in range(len(hull.vertices))])

    # get the points of the track
    track_points = shape_track(hull_points, difficulty=difficulty, max_displacement=max_displacement, margin=margin, track_width=track_width,
                             max_angle=max_angle, distance_between_points=distance_between_points, width=width, height=height)
    
    # smooth the track points
    f_points = smooth_track(track_points, spline_points=spline_points)
    
    # get the checkpoint locations 
    checkpoints = get_checkpoints(f_points, n_checkpoints=number_checkpoints)
    
    return f_points, checkpoints


"""
Generate a random set of points subject to the outlined constraints
"""
def random_points(min_p, max_p, margin, min_distance, width, height):
    
    # get number of points
    point_count = random.randrange(min_p, max_p + 1, 1)
    
    points = []
    for i in range(point_count):
        
        # get x and y of points
        x = random.randrange(margin, width - margin + 1, 1)
        y = random.randrange(margin, height -margin + 1, 1)
        
        # remove any points which are less than the minimum distance
        distances = list(filter(lambda x: x < min_distance, [math.dist(p, [x, y]) for p in points]))
        
        # append x and y 
        if len(distances) == 0:
            points.append((x, y))
            
    return np.array(points)


"""
Generate a convex hull from a set of points
"""
def convex_hull(points):
    
    hull_points = []
    
    # set the starting point
    start = points[0, :]
    
    # set the minimum x
    min_x = start[0]
    
    # cycle through all the points
    for p in points[1:, :]:
        if p[0] < min_x:
            min_x = p[0]
            start = p
    
    # set the starting point
    point = start    
    hull_points.append(start)
    
    # cycle through points from start to finish
    far_point = None
    while not (far_point==start).all():        
        
        p1 = None
        for p in points:
            
            # if point is current point
            if (p==point).all():
                continue
            
            # if not set p1 as point
            else:
                p1 = p
                break
        
        # set the far point as p1
        far_point = p1
        
        # cycle through the points again
        for p2 in points:
            
            # p2 is current point or equal to p1
            if (p2==point).all() or (p2==p1).all():
                continue
            
            # get the direction between p1 and p2
            else:
                direction  = (((p2[0] - point[0]) * (far_point[1] - point[1])) 
                              - ((far_point[0] - point[0]) * (p2[1] - point[1])))
                if direction > 0:                    
                    far_point = p2
                    
        hull_points.append(far_point)
        point = far_point
    
    return np.array(hull_points)        

"""
Take a convex hull and ensure that all the points are sufficiently spaced, fit 
within the confines of the screen and do not incorporate any bends that are 
too sharp.
"""
def shape_track(track_points, difficulty, max_displacement, margin, track_width, max_angle, distance_between_points, width, height):
        
    # create a list of zero pairs twice as long as hull points
    track_set = [[0,0] for i in range(len(track_points) * 2)] 
            
    # create track vectors and displacements
    for i in range(len(track_points)):
        
        # get a random displacement
        displacement = math.pow(random.random(), difficulty) * max_displacement
        
        # multiply magnitude my random unit vector
        disp = [displacement * i for i in make_rand_vector(2)]
        
        # set first index to track point        
        track_set[i * 2] = list(track_points[i])
        
        # set second index to current track point + mean of current and next track point + magnitude of dispalcement
        track_set[i * 2 + 1][0] = int((track_points[i][0] + track_points[(i + 1) % len(track_points)][0]) / 2 + disp[0])
        track_set[i * 2 + 1][1] = int((track_points[i][1] + track_points[(i + 1) % len(track_points)][1]) / 2 + disp[1])
    
    # ensure angles are suitable and points are sufficiently far apart
    for i in range(3):
        track_set = fix_angles(track_set, max_angle=max_angle)
        track_set = push_points_apart(track_set, distance=distance_between_points)   
        
    # ensure all the points are within the screen limits
    final_set = []
    for point in track_set:
        
        # if outside x dimension including track width
        if point[0] < margin:
            point[0] = margin            
        elif point[0] > (width - margin):
            point[0] = (width - margin)
        
        # if outside y dimension including track width        
        if point[1] < margin:
            point[1] = margin
        elif point[1] > height - margin:
            point[1] = (height - margin)
            
        final_set.append(point)
     
    return final_set

"""
Generate a random unit vector of dims-dimensions
"""
def make_rand_vector(dims):
    
    # create a random dims-dimensional vector
    vec = [random.gauss(0, 1) for i in range(dims)]
    mag = sum(x**2 for x in vec) ** .5
    return [x/mag for x in vec]


"""
Take a set of angles and adjust them such that they do not exceed a maximum
angle
"""
def fix_angles(points, max_angle):
    
    for i in range(len(points)):
                
        # set the previous point
        if i > 0: prev_point = i - 1
        
        # set the previous point to the end of the list
        else: prev_point = len(points) - 1
        
        # set the next point
        next_point = (i + 1) % len(points)
        
        # get the difference between current point and previous point
        px = points[i][0] - points[prev_point][0]
        py = points[i][1] - points[prev_point][1]
                
        # get the distance
        pl = math.sqrt(px * px + py * py)
        
        # get norm of difference
        px /= (pl + 1e-5)
        py /= (pl + 1e-5)
        
        # compute the difference between the current point and the next point
        nx = -(points[i][0] - points[next_point][0])
        ny = -(points[i][1] - points[next_point][1])
        
        # get the distance
        nl = math.sqrt(nx * nx + ny * ny)
        
        # norm the distances
        nx /= (nl + 1e-5)
        ny /= (nl + 1e-5)
                                
        # calculate the angle of the corner
        a = math.atan2(px * ny - py * nx, px * nx + py * ny)
                        
        # if angle is suitable continue
        if (abs(math.degrees(a)) <= max_angle):
            continue
        
        # get the difference beyond the max angle
        diff = math.radians(max_angle * math.copysign(1, a)) - a
        
        # recalculate a new position which fits constraint
        c = math.cos(diff)
        s = math.sin(diff)
        
        new_x = (nx * c - ny * s) * nl
        new_y = (nx * s + ny * c) * nl
        
        # update the points
        points[next_point][0] = int(points[i][0] + new_x)
        points[next_point][1] = int(points[i][1] + new_y)
        
    return points

"""
Take a set of points and ensure that they are a minimum distance apart from 
one another
"""
def push_points_apart(points, distance):
    
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            
            # get distance between 2 points 
            p_distance =  math.dist(points[i], points[j])
            
            # if beyond the max distance
            if p_distance < distance:
                
                # get coord differences
                dx = points[j][0] - points[i][0]  
                dy = points[j][1] - points[i][1]  
                dl = math.sqrt(dx*dx + dy*dy)  
                
                # norm the distances
                dx /= (dl + 1e-5)
                dy /= (dl + 1e-5)
                
                # get the difference and update the coords
                dif = distance - dl
                dx *= dif  
                dy *= dif  
                
                # updated coords in array
                points[j][0] = int(points[j][0] + dx)
                points[j][1] = int(points[j][1] + dy)  
                points[i][0] = int(points[i][0] - dx)  
                points[i][1] = int(points[i][1] - dy) 
                    
    return points

"""
Take a set of point and smooth the boundaries by approximating the shape
using a B-spline function.
"""
def smooth_track(track_points, spline_points): 
        
    x, y = zip(*track_points)
    x, y = list(x), list(y)        
    
    # check that consecutive inputs are not the same as this causes an error
    x = [x[idx] + random.uniform(0, 1) for idx in range(len(x))] 
        
    # append the first value to the end
    x.append(x[0])
    y.append(y[0])
        
    # remove the runtime warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    
        # fit splines to x=f(u) and y=g(u), treating both as periodic. also note that s=0
        # is needed in order to force the spline fit to pass through all the input points.
        tck, _ = interpolate.splprep([x, y], s=0, per=True)   
    
    # evaluate the spline fits for # points evenly spaced distance values
    xi, yi = interpolate.splev(np.linspace(0, 1, spline_points), tck)
    return [(int(xi[i]), int(yi[i])) for i in range(len(xi))]    

    
"""
An alternative implementation of smooth track to avoid the scipy dependency. 
However, this function creates lines with discontinuities between the first and
last point.
"""
def smooth_track_alternative(track_points, spline_points):
    
    # TODO: this B-spline function is not working as intended 
    # -> the last point does not connect continuously
        
    # get x and y in the appropriate format
    x, y = zip(*track_points)
    x, y = list(x) + [x[0]], list(y) + [y[0]]   
    
    k, H = 3, len(x) - 1
        
    # combine the lists
    combined_list = [x, y]
    
    p_centripetal = centripetal(len(x), combined_list)
    knot = knot_vector(p_centripetal, k, len(x))
    P_control = curve_approximation(D=combined_list, N=len(x), H=H, k=k, param=p_centripetal, knot=knot)
    
    p_piece = np.linspace(0, 1, spline_points)    
    p_centripetal_new = centripetal(H, P_control)
    knot_new = knot_vector(p_centripetal_new, k, H)
    P_piece = curve(P_control, H, k, p_piece, knot_new)

    return [(int(P_piece[0][idx]), int(P_piece[1][idx])) for idx in range(len(P_piece[0]))]  
    

"""
Calculate a B-spline curve from a set of points
"""
def curve(control_points, n_points, degree, param, knot):
    
    Nik = np.zeros((len(param), n_points))

    for i in range(len(param)):
        for j in range(n_points):
            Nik[i][j] = base_function(j, degree + 1, param[i], knot)
            
    Nik[len(param) - 1][n_points - 1] = 1
    
    bspline_data = []
    for i in range(len(control_points)):
        bspline_data.append(np.dot(Nik, control_points[i]).tolist())
        
    return bspline_data

"""
Calculate a base_function using Cox-deBoor function
"""
def base_function(i, k, u, knot):
    '''
    Calculate base function using Cox-deBoor function.
    :param i: index of base function
    :param k: order (degree + 1)
    :param u: parameter
    :param knot: knot vector
    :return: base function
    '''
    Nik_u = 0
    if k == 1:
        if u >= knot[i] and u < knot[i + 1]:
            Nik_u = 1.0
        else:
            Nik_u = 0.0
    else:
        length1 = knot[i + k - 1] - knot[i]
        length2 = knot[i + k] - knot[i + 1]
        if not length1 and not length2:
            Nik_u = 0
        elif not length1:
            Nik_u = (knot[i + k] - u) / length2 * base_function(i + 1, k - 1, u, knot)
        elif not length2:
            Nik_u = (u - knot[i]) / length1 * base_function(i, k - 1, u, knot)
        else:
            Nik_u = (u - knot[i]) / length1 * base_function(i, k - 1, u, knot) + \
                    (knot[i + k] - u) / length2 * base_function(i + 1, k - 1, u, knot)
    return Nik_u

"""
Calculate the B-spline parameters using the centripetal method
"""
def centripetal(n, P):
    '''
    Calculate parameters using the centripetal method.
    :param n: the number of data points
    :param P: data points
    :return: parameters
    '''
    a = 0.5 
    parameters = np.zeros((1, n))
    
    # cycle throught the points
    for i in range(1, n):
        dis = 0

        # cycle through axes        
        for j in range(len(P)):
            
            # calculate the square difference between each consecutive value
            dis = dis + (P[j][i] - P[j][i - 1]) ** 2
            
        # square root the distance
        dis = np.sqrt(dis)
        
        # update the parameter value
        parameters[0][i] = parameters[0][i - 1] + np.power(dis, a)
    
    # divide each value my the max to normalise
    for i in range(1, n):
        parameters[0][i] = parameters[0][i] / parameters[0][n - 1]
        
    return parameters[0]

"""
Generate a knot vector for the B-spline function
"""
def knot_vector(param, k, N):
    '''
    Generate knot vector.
    :param param: parameters
    :param k: degree
    :param N: the number of data points
    :return: knot vector
    '''
    m = N + k
    knot = np.zeros((1, m + 1))
    
    for i in range(k + 1):
        knot[0][i] = 0
        
    for i in range(m - k, m + 1):
        knot[0][i] = 1
        
    for i in range(k + 1, m - k):
        for j in range(i - k, i):
            knot[0][i] = knot[0][i] + param[j]
        knot[0][i] = knot[0][i] / k
        
    return knot[0]

"""
For a set of data points find a B-spline curve of a specified degree that contains
the first and last data points and approximates data polygon in the sense of least
squares.
"""
def curve_approximation(D, N, H, k, param, knot):
    '''
    Given a set of N data points, D0, D1, ..., Dn, a degree k,
    and a number H, where N > H > k >= 1, find a B-spline curve
    of degree k defined by H control points that satisfies the
    following conditions:
        1. this curve contains the first and last data points;
        2. this curve approximates the data polygon in the sense
        of least square;
    :param D: data points (N x 2)
    :param H: the number of control points
    :param k: degree
    :param param: parameters
    :param knot: knot vector
    :return: control points (H x 2)
    '''
    
    P = []
    if H >= N or H <= k:
        print('Parameter H is out of range')
        return P
    
    for idx in range(len(D)):
        
        P_ = np.zeros((1, H))
        
        # set the final and initial points
        P_[0][0] = D[idx][0]
        P_[0][H - 1] = D[idx][N - 1]
        
        # initialise the arrays
        Qk = np.zeros((N - 2, 1))
        Nik = np.zeros((N, H))
        
        # calculate base function for each index
        for i in range(N):
            for j in range(H):
                Nik[i][j] = base_function(j, k + 1, param[i], knot)
                        
        for j in range(1, N - 1): 
            Qk[j - 1] = D[idx][j] - Nik[j][0] * P_[0][0] - Nik[j][H - 1] * P_[0][H - 1]
        
        # cut the input array
        N_part = Nik[1: N - 1, 1: H - 1]
        
        # perfrom dot product
        Q = np.dot(N_part.transpose(), Qk)
        
        # get squared value
        M = np.dot(np.transpose(N_part), N_part)
        
        # get the points which solve the equation
        P_[0][1 : H - 1] = np.dot(np.linalg.inv(M), Q).transpose()
        
        # add the values to the array
        P.append(P_.tolist()[0])
        
    return P

"""
Divide a track specified by a set of point into n checkpoints
"""
def get_checkpoints(track_points, n_checkpoints):
    
    # get step between checkpoints
    checkpoint_step = len(track_points) // n_checkpoints
    
    # get checkpoint track points
    checkpoints = []
    for i in range(n_checkpoints):
        index = i * checkpoint_step
        checkpoints.append(track_points[index])
    return checkpoints


# Drawing the track ---------------------------------------------------------

"""
Function for drawing the race track map using a set of track points and some 
checkpoint markers.
"""
def draw_map(f_points, checkpoints, screen, track_width, checkpoint_margin,
                checkpoint_angle_offset, track_colour, checkpoint_colour, start_colour, background_colour):
    
    # fill in the background    
    screen.fill(background_colour)
    
    # draw the road
    draw_track(screen, track_colour, f_points, track_width=track_width)
    
    # draw the checkpoints
    for checkpoint_idx, checkpoint in enumerate(checkpoints):
        draw_checkpoint(screen, f_points, checkpoint, checkpoint_idx, checkpoint_margin=checkpoint_margin,track_width=track_width, 
                        checkpoint_angle_offset=checkpoint_angle_offset, checkpoint_colour=checkpoint_colour, start_colour=start_colour)
    
    return screen
        
"""
Draw the road onto the map given a set of point specifying the location of the 
track. 
"""
def draw_track(surface, color, points, track_width):
    
    radius = track_width // 2
    
    # draw track
    chunk_dimensions = (radius * 2, radius * 2)
    for point in points:
        blit_pos = (point[0] - radius, point[1] - radius)
        track_chunk = pygame.Surface(chunk_dimensions, pygame.SRCALPHA)
        pygame.draw.circle(track_chunk, color, (radius, radius), radius)
        surface.blit(track_chunk, blit_pos)
        
"""
Draw the individual checkpoints including the starting point. 
"""
def draw_checkpoint(track_surface, points, checkpoint, checkpoint_idx, checkpoint_margin, track_width, checkpoint_angle_offset, start_colour, checkpoint_colour):
    
    # given the main point of a checkpoint, compute and draw the checkpoint box
    margin = checkpoint_margin
    radius = track_width // 2 + margin
    offset = checkpoint_angle_offset
    check_index = points.index(checkpoint)
    vec_p = [points[check_index + offset][1] - points[check_index][1], -(points[check_index+offset][0] - points[check_index][0])]
    n_vec_p = [vec_p[0] / math.hypot(vec_p[0], vec_p[1]), vec_p[1] / math.hypot(vec_p[0], vec_p[1])]
    
    # compute angle
    angle = math.degrees(math.atan2(n_vec_p[1], n_vec_p[0]))
    
    # set checkpoint colour for the start
    if checkpoint_idx == 0: colour = start_colour
    else: colour = checkpoint_colour
    
    # draw checkpoint    
    checkpoint = draw_rectangle((radius * 2, 5), colour, line_thickness=1, fill=False)    
    rot_checkpoint = pygame.transform.rotate(checkpoint, -angle)
    check_pos = (points[check_index][0] - math.copysign(1, n_vec_p[0]) * n_vec_p[0] * radius, points[check_index][1] - math.copysign(1, n_vec_p[1]) * n_vec_p[1] * radius)       
    track_surface.blit(rot_checkpoint, check_pos)

"""
Draw a rectangle of specified dimensions
"""
def draw_rectangle(dimensions, color, line_thickness=1, fill=False):
    filled = line_thickness
    if fill:
        filled = 0
    rect_surf = pygame.Surface(dimensions, pygame.SRCALPHA)
    pygame.draw.rect(rect_surf, color, (0, 0, dimensions[0], dimensions[1]), filled)
    
    return rect_surf 

# Updating the car ----------------------------------------------------------

class simulate_car:
    
    def __init__(self, fps=30, starting_position=(0, 0), starting_angle=0):
        
        self.fps = 30
        
        # intialise the car parameters
        self.dimensions = [20, 8]
        self.max_steering_angle = math.pi / 2
        self.acceleration_rate = 10
        self.velocity_dampening = 30
        self.max_speed = 200
        self.steering_elasticity = 5 / self.fps  
        self.max_laser_length = 200
        
        self.sensor_angles = [-90, -45, 0, +45, +90] 
        
        # reset the parameters
        self.reset(starting_position=starting_position, starting_angle=starting_angle)
        
    """
    Reset the car parameters
    """
    def reset(self, starting_position, starting_angle):
        
        # initialise the car parameters
        self.position = list(starting_position)
        self.speed = 0
        self.velocity = [0, 0]
        self.angle = starting_angle
        self.steering_angle = 0
       
    """
    Given an action update the cars position, angle and speed
    """
    def process_action(self, action):        
        
        # actions:
        # 0 = brake| 1 = left | 2 = right
        
        # always accelerate the car
        self.accelerate(+1)  
        
        # decelerate the car
        if action[0]:
            self.accelerate(-1)        
            
        # turn the car left
        if action[1]:
            self.turn(-1)
        
        # turn the car right
        if action[2]:
            self.turn(+1)   
        
        # update the car's current position
        self.update_position()
    
    """
    Update the speed of the car
    """            
    def accelerate(self, velocity_change):
        
        dv = velocity_change
        
        # move the car forward
        if dv > 0:  
            self.speed += self.acceleration_rate * dv
            self.speed = min(self.speed, self.max_speed)
            
        # reverse the car    
        elif dv < 0:
            self.speed += self.acceleration_rate * dv            
            self.speed = max(self.speed, -self.max_speed)
    
    """
    Update the turning angle of the car
    """            
    def turn(self, direction):        
        
        # update the steering angle
        new_steering_angle = self.steering_angle + direction * (math.pi / 10)
        
        # restrict the steering angle to a confined range
        if new_steering_angle > self.max_steering_angle:
            self.steering_angle = self.max_steering_angle            
            
        elif new_steering_angle < -self.max_steering_angle:
            self.steering_angle = -self.max_steering_angle
            
        # set the new angle    
        else: self.steering_angle = new_steering_angle
      
    """
    Update the position of the car and account for dampening
    """        
    def update_position(self):
        
        delta = 1 / self.fps
                
        # adjust the car's angle using the modified steering angle
        self.angle += self.steering_angle * delta * self.speed / 100
        self.angle = self.angle % (math.pi * 2)
        
        # calculate the velocity and hence its current position    
        self.velocity[0] = math.cos(self.angle) * self.speed
        self.velocity[1] = math.sin(self.angle) * self.speed
        self.position[0] += self.velocity[0] * delta
        self.position[1] += self.velocity[1] * delta
        
        # account for wheel dampening
        self.dampen_steering()
        self.dampen_speed()
        
    """
    Dampen the cars steering
    """    
    def dampen_steering(self):
    
        # steering is already at 0
        if self.steering_angle == 0:
            self.steering_angle = 0
        
        # reduce right steering
        elif self.steering_angle > 0:
            self.steering_angle = self.steering_angle - self.steering_elasticity
            
            if self.steering_angle <= 0:
                self.steering_angle = 0
        
        # reduce left steering
        elif self.steering_angle < 0:
            self.steering_angle = self.steering_angle + self.steering_elasticity
            
            if self.steering_angle >= 0:
                self.steering_angle= 0
                
    """
    Dampen the speed of the car
    """    
    def dampen_speed(self):
        
        delta = 1 / self.fps
        
        # if stopped keep speed constant
        if self.speed == 0:
            self.speed = 0
        
        # reduce forward speed
        elif self.speed > 0:
            self.speed = self.speed - self.velocity_dampening * delta * (self.speed / 10)
            
            if self.speed <= 0:
                self.speed = 0
                
        # reduce backward speed      
        elif self.speed < 0:
            self.speed = self.speed - self.velocity_dampening * delta * (self.speed / 10)
            
            if self.speed >= 0:
                self. speed = 0
                
    """
    Render the car's position, rotation and the laser's it uses for sensing the
    environment.
    """    
    def render_car(self, screen, car_colour, debugging=False):
        
        # create the car surface
        car_surface = draw_rectangle(self.dimensions, car_colour, line_thickness=1, fill=True)    
        
        # rotate the car and place the rotated rect at position
        rotated_car = pygame.transform.rotate(car_surface, (-self.angle * 360 / (2 * math.pi)))
        rotated_car_rect = rotated_car.get_rect(center=self.position)
                
        # render the car
        screen.blit(rotated_car, rotated_car_rect)
        
        if debugging:
            # draw the centre position 
            pygame.draw.circle(screen, (255, 0, 0), self.position, 3, 1)     
            
            # draw on the individual laser
            for idx, angle in enumerate(self.sensor_angles):
                screen = self.draw_laser(screen=screen, sensor_angle=angle, sensor_point=self.sensor_points[idx])                    
                 
            # draw the track outline
            for i in range(len(self.track_points)):
                pygame.draw.circle(screen, (255, 0, 0), list(self.track_points[i]), 3, 1)   
        
        return screen
    
    """
    Draw a laser given its angle and its position.
    """    
    def draw_laser(self, screen, sensor_angle, sensor_point):
        
        # calculate the distance to a collision
        laser_length = math.dist(sensor_point, self.position)
                
        # create the laser surface
        selected_laser_length = min(laser_length, self.max_laser_length)
        laser_surf = draw_rectangle([selected_laser_length, 2], (255, 0, 0), line_thickness=1, fill=True)
        
        input_angle = self.angle + math.radians(sensor_angle)
        laser_position = [self.position[0] + math.cos(input_angle) * (selected_laser_length / 2),
                         self.position[1] + math.sin(input_angle) * (selected_laser_length/ 2)]  
        
        # rotate the laser shape
        rotated_laser = pygame.transform.rotate(laser_surf, (-input_angle * 360 / (2 * math.pi)))
        rotated_laser_rect = rotated_laser.get_rect(center=laser_position)
        
        # draw on the shape
        screen.blit(rotated_laser, rotated_laser_rect)
        
        return screen
    
    """
    Get the collision points of the sensors used by the car.    
    """    
    def get_sensor_ranges(self, outside_track_points, inside_track_points, track_points, debugging=False):
        
        # combine inside and outside track points (selecting every 4 points)
        track_points = outside_track_points[::5] + inside_track_points[::5]
        transition_idx = len(outside_track_points[::5]) - 1      
        
        # get sensor lines is 10x slower   
        x_lines, track_x, common_y = self.get_sensor_lines(track_points=track_points, sensor_angles=self.sensor_angles)  
              
        # this function is still slow        
        sensor_points = []        
        for idx, angle in enumerate(self.sensor_angles):
            sensor_point = self.get_single_sensor_range(track_points=track_points, transition_idx=transition_idx, x_lines=x_lines,
                                                  track_x=track_x, common_y=common_y, sensor_angle=angle, idx=idx)
            sensor_points.append(sensor_point)
          
        # for debugging
        if debugging:
            self.track_points = track_points
            self.sensor_points = sensor_points  
        
        return sensor_points

    """
    Get the lines of the sensors 
    """                    
    def get_sensor_lines(self, track_points, sensor_angles):
        
        # get the range of sensor data        
        true_angles = [(self.angle + math.radians(angle)) % (2 * math.pi) for angle in sensor_angles]
        x_laser_lengths, y_laser_lengths = zip(*[(math.cos(angle) * self.max_laser_length, math.sin(angle) * self.max_laser_length) for angle in true_angles])
        
        # get the x and y track points
        x, y = zip(*track_points)
                        
        # extract the track values which fall in range
        common_y, track_x = y, x
        
        x_lines = []
        for i, y_val in enumerate(y):        
            
            # get the line x values (added small factor to stop division by zero error)
            x_pos, y_pos = self.position[0], self.position[1]
            intercept_x = [(y_val - y_pos) * (x_laser / (y_laser_lengths[idx] + 1e-5)) + x_pos for idx, x_laser in enumerate(x_laser_lengths)]
                          
            # update the total list
            x_lines.append(intercept_x)   
        
        # set the some variables for visualisation
        self.x_lines = x_lines
        self.common_y = common_y
        
        # convert to arrays
        x_lines = np.array(x_lines)
        track_x = np.array(track_x)
        
        return x_lines, track_x, common_y
                    
                    
    def get_single_sensor_range(self, track_points, transition_idx, x_lines, track_x, common_y, sensor_angle, idx=0):        
        
        # get the adjusted angle
        input_angle = (self.angle + math.radians(sensor_angle)) %  (2 * math.pi)
        x_line = x_lines[:, idx]
        
        # get the intercept indexes and their values
        x_idx = np.argwhere(np.diff(np.sign(x_line - track_x))).flatten()
        
        # added to stop not enough values to unpack with zip
        sensor_point = [100_000, 100_000]
        if len(x_idx) > 0:
        
            # get the adjusted differences
            x_pos, y_pos = self.position[0], self.position[1]        
            x_vals, y_vals = zip(*[(track_x[idx] - x_pos, common_y[idx] - y_pos) for idx in x_idx if idx != transition_idx])
            
            # ensure the collisions are only measured forward with a small factor for error
            error_margin = 12
            if input_angle > 0 and input_angle <= math.pi / 2:            
                correct_dir = [x for idx, x in enumerate(x_vals) if (x + error_margin >= 0 and y_vals[idx] + error_margin  >= 0)]            
            elif input_angle > math.pi / 2 and input_angle <= math.pi:
                correct_dir = [x for idx, x in enumerate(x_vals) if x - error_margin <= 0 and y_vals[idx] + error_margin >= 0]            
            elif input_angle > math.pi and input_angle <= 3/2 * math.pi:
                correct_dir = [x for idx, x in enumerate(x_vals) if x - error_margin <= 0 and y_vals[idx] - error_margin <= 0]        
            else:
                correct_dir = [x for idx, x in enumerate(x_vals)if x + error_margin >= 0 and y_vals[idx] - error_margin <= 0]   
                
            # get the smallest forward collision     
            correct_dist = [math.sqrt(x ** 2 + y_vals[x_vals.index(x)] ** 2)  for x in correct_dir] 
            
            # get the correct x index
            if len(correct_dist) > 0:
                
                # get the correct index
                min_dist = min(correct_dist)
                min_dist_index = correct_dist.index(min_dist)
                correct_x = correct_dir[min_dist_index]
                correct_x_index = x_vals.index(correct_x)         
                
                # get the x position
                chosen_x = x_vals[correct_x_index]
                 
                # set the point if it is less than the max distance
                if min_dist <= self.max_laser_length:                
                    sensor_point = [chosen_x + self.position[0], y_vals[correct_x_index] + self.position[1]]
        
        return sensor_point
        
                            
        
if __name__ == '__main__':
    
    # test params
    display = True
    seeds = 1
    
    # get screen params
    width = 800
    height = 600
    start_tile_height = 10
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    grass_green = (58, 156, 53)
    grey = (186, 182, 168)
    
    # function params
    track_width = 60
    checkpoint_margin = 5
    checkpoint_angle_offset = 3
    
    # initialise pygame
    if display:    
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        
    for seed in range(seeds):
        
        print('Seed {}'.format(seed))
        
        test = np.random.randint(0, 100000)        
        print(test)
        
        # set the seed
        random.seed(test)
        np.random.seed(test)
        
        # get the coords
        f_points, checkpoints = generate_track(track_width=track_width, width=width, height=height)
        
        # draw the screen 
        if display:
            draw_map(f_points, checkpoints, screen, track_width=track_width, checkpoint_margin=checkpoint_margin, 
                        checkpoint_angle_offset=checkpoint_angle_offset, track_colour=grey, start_colour=red, checkpoint_colour=blue, background_colour=grass_green)
            
            
            pygame.display.update()
    
    

