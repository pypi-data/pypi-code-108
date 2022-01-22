""" Testing the generation of random structures.

Test by Bartosz Gren
Version from 17.02.2020
"""

#!/usr/bin/env python
from topoly import generate_lasso, generate_loop, generate_walk, generate_handcuff
import numpy as np                                                               
import os
import pytest

def calc_dist(block):
    block = np.array(block) 
    vec  = block[1:,:]-block[:-1,:]
    dist = np.square(vec).sum(axis=1)
    return list(dist)

def check_dist(filename, folder, eps = 0.00001):                                                         
    # takes .xyz file and calculates distances between residues                      
    # returns 1 if they are close to 1, otherwise returns 0        
    block = []
    dists = []
    with open(folder + '/' + filename, 'r') as f:
        for line in f.readlines():
            if line == 'X\n':
                dists = dists + calc_dist(block)
                block = []
            else: 
                block.append(list(map(float, line.split()[1:4])))
    dists = np.array(dists + calc_dist(block))
    res   = np.logical_and(np.all(1-eps < dists), np.all(dists < 1+eps))
    return int(res)                                                              

#@pytest.mark.skip
def test_polygongen():
    print('Testing polygongen')
    res = 0

    # basic use: generate 3 lassos with looplength = 10 and taillength = 5
    generate_lasso(10, 5, 3)
    # output is in folder 'l010_t005', files 'lasso00000.xyz' to 'lasso00002.xyz'
    folder = 'l010_t005'
    file_prefix = 'lasso'
    for filename in os.listdir(folder):
        if filename.startswith(file_prefix):
            res = res + check_dist(filename, folder)

    generate_loop(10, 3)
    # output is in folder 'l010', files 'loop00000.xyz' to 'loop00002.xyz'
    folder = 'l010'
    file_prefix = 'loop'
    for filename in os.listdir(folder):
        if filename.startswith(file_prefix):
            res = res + check_dist(filename, folder)

    generate_walk(5, 3)
    # output is in folder 'w005', files 'walk00000.xyz' to 'walk00002.xyz'
    folder = 'w005'
    file_prefix = 'walk'
    for filename in os.listdir(folder):
        if filename.startswith(file_prefix):
            res = res + check_dist(filename, folder)

    generate_handcuff((10, 7), 5, 3)
    # output is in folder 'l010_007_t005', files 'hdcf00000.xyz' to 'hdcf00002.xyz'
    folder      = 'l010_007_t005'
    file_prefix = 'hdcf'
    for filename in os.listdir(folder):
        if filename.startswith(file_prefix):
            res = res + check_dist(filename, folder)

    # formats can be changed
    generate_lasso(10, 5, 3, folder_prefix='test_', file_prefix='a_', file_fmt=(2, 1, 1))
    # output is in folder 'l10_t5', files 'a_0.xyz' to 'a_2.xyz'
    folder = 'test_l10_t5'
    file_prefix = 'a'
    for filename in os.listdir(folder):
        if filename.startswith(file_prefix):
            res = res + check_dist(filename, folder)
    assert res == 15
    # try:
    #     assert res == 15
    #     print('Polygongen test passed :)')
    # except:
    #     print('Polygongen test failed :(')
    


if __name__ == '__main__':
    test_polygongen()

