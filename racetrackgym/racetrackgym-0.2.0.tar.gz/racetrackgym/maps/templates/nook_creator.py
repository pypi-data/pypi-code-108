import sys
import os
import copy
import subprocess


x_zero = 35
y_zero = 13

def create_map(dim):
    if dim == 1:
        pass
    map = copy.deepcopy(start)

    for j in range(len(map)):
        for _ in range(dim - 2):
            row = map[j]
            row = row + between[j]
            map[j] = row

    for j in range(len(map)):
        row = map[j]
        row = row + end[j]
        map[j] = row

    x_dim = x_zero * dim
    y_dim = y_zero

    with open('../nook_' + str(dim) + '.track', 'w') as f:
        f.write('dim: ' + str(y_dim) + ' ' + str(x_dim) + '\n')

        for line in map:
            f.write(line)


with open('nook_start.track', 'r') as f:
    start = f.readlines()
    for i,line in enumerate(start):
        line = line.replace('\n', '')
        start[i] = line

with open('nook_end.track', 'r') as f:
    end = f.readlines()

with open('nook_empty.track', 'r') as f:
    between = f.readlines()
    for i,line in enumerate(between):
        line = line.replace('\n', '')
        between[i] = line



num = int(sys.argv[1])

for i in range(2, num+1):
    create_map(i)