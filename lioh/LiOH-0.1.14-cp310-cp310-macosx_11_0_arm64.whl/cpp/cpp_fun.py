import LiOH_Cpp
import numpy as np
from typing import List
def floyd_warshall(matrix:np.ndarray)->np.ndarray:
    '''用floyd求邻接矩阵Matrix的全部节点间的最短距离.'''
    if type(matrix) != np.ndarray:
        raise TypeError('matrix is not np.ndarray')
    elif matrix.dtype != np.dtype('float64'):
        raise TypeError('matrix is not np.dtype[float64]')
    elif matrix.ndim != 2:
        raise TypeError('matrix is not 2 dimension')
    elif matrix.shape[0] != matrix.shape[1]:
        raise TypeError('Axis 0 and axis 1 of the matrix are not equal in length')
    else:
        matrix = matrix.tolist()
    return np.array(LiOH_Cpp.floyd_warshall(matrix))

def dijkstra(matrix:np.ndarray)->np.ndarray:
    '''用dijkstra求邻接矩阵Matrix的全部节点间的最短距离. '''
    if type(matrix) != np.ndarray:
        raise TypeError('matrix is not np.ndarray')
    elif matrix.dtype != np.dtype('float64'):
        raise TypeError('matrix is not np.dtype[float64]')
    elif matrix.ndim != 2:
        raise TypeError('matrix is not 2 dimension')
    elif matrix.shape[0] != matrix.shape[1]:
        raise TypeError('Axis 0 and axis 1 of the matrix are not equal in length')
    else:
        matrix = matrix.tolist()
    return np.array(LiOH_Cpp.dijkstra(matrix))

def brute_force(matrix:np.ndarray,N_neighbor:int)->np.ndarray:
    '''求Matrix中行向量间的距离,N_neighbor的距离为欧氏距离,其他为0.'''
    if type(matrix) != np.ndarray:
        raise TypeError('matrix is not np.ndarray')
    elif matrix.dtype != np.dtype('float64'):
        raise TypeError('matrix is not np.dtype[float64]')
    elif matrix.ndim != 2:
        raise TypeError('matrix is not 2 dimension')
    elif type(N_neighbor) != int:
        raise TypeError('the type of N_neighbor is not int')
    elif type(N_neighbor) <= matrix.shape[0]:
        raise TypeError('N_neighbor is greater than Number of samples ')
    else:
        matrix = matrix.tolist()
    return np.array(LiOH_Cpp.brute_force(matrix,N_neighbor))  
 
