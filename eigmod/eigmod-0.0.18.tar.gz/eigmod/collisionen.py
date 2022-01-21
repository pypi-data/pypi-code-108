import math

def square_square(cord1, dim1, cord2, dim2, speed1 = (0,0), speed2 = (0,0)):
    """checks for collision between two squares

    Args:
        cord1 (tuple): (x1, y1)
        dim1 (tuple): (width1, height1)
        cord2 (tuple): (x2, y2)
        dim2 (tuple): (width2, heigh2)
        speed1 (tuple, optional): check for col in advance. Defaults to (0,0).
        speed2 (tuple, optional): check for col in advance. Defaults to (0,0).

    Returns:
        [type]: [description]
    """
    if cord1[0] + dim1[0] + speed1[0] > cord2[0] + speed2[0]  and cord1[0] + speed1[0] < cord2[0]  + dim2[0] + speed2[0]: # x-achse Überlappung
        if cord1[1] + dim1[1] + speed1[1] > cord2[1] + speed2[1] and cord1[1] + speed1[1] < cord2[1]  + dim2[1]+ speed2[1]: # y achenn Überlappung
            return True
    return False

# print(square_square((-23, 389), (40, 40), (-1600, 0), (0, 1200)))
# print(square_square((1, 1), (1, 1), (1, 1), (2, 2)))

### UNUSED #########################
def square_wall(cord1, dim1, cord2, dim2, speed1 = (0,0)):
    return square_square(cord1, dim1, cord2, dim2, speed1)
####################################

def point_square(cord1, cord2, dim2):
    if cord1[0] > cord2[0] and cord1[0] < cord2[0]  + dim2[0]: # x-achse Überlappung
        if cord1[1] > cord2[1]  and cord1[1] < cord2[1]  + dim2[1] : # y achenn Überlappung
            return True
    return False

    
def point_line(cord1, cord2, dim2, mode):
    
    if dim2[0] == 0: # vertikale Linie 
        if cord1[1] > cord2[1] and cord1[1] < cord2[1] + dim2[1]:
            if mode == "g": # größer modus
                if cord1[0] > cord2[0]:
                    return True
            elif mode == "k": 
                if cord1[0] < cord2[0]:
                    return True
            
        return False

    elif dim2[1] == 0: # hoizontale Linie 
        if cord1[0] > cord2[0] and cord1[0] < cord2[0] + dim2[0]:
            if mode == "g": # größer modus
                if cord1[1] > cord2[1]:
                    return True
            elif mode == "k": 
                if cord1[1] < cord2[1]:
                    return True
            
        return False
            
    else: 
        raise ValueError

def circle_circle(x1,y1, r1, x2,y2,r2, uberscheindungs_fact =1):
    """checks for two colliding circles

    Args:
        x1 (numb): 
        y1 (numb): 
        r1 (numb): 
        x2 (numb): 
        y2 (numb): 
        r2 (numb): 
        uberscheiungs_fakt: das mal radius bestimmt über col, wenn 1 dann bei geringerster beruhrung true

    Returns: True/False 
    """
    
    center_dis = math.sqrt((x1- x2) ** 2 + (y1-y2)**2)
    if center_dis < (r1 + r2) * uberscheindungs_fact:
        return True
    else:
        return False

# print(circle_circle(1,1,1,2,2,1, 0.8))




