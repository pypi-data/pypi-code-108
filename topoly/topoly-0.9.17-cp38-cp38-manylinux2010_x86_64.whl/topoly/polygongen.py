#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 12:49:58 2018

@author: bartosz
"""
import numpy as np
import os

class Polygon(object):
    def __init__(self, no_of_structures, bond_length = 1, print_with_index = True,
                 file_prefix = 'polygon', folder_prefix = '', file_fmt = (3,3,5)):
        """
        Mother class for Polyg_lasso, Polyg_loop, Polyg_walk
        """
        self.nop = no_of_structures
        self.scale = bond_length
        self.file_prefix = file_prefix
        self.fold_prefix = folder_prefix
        self.print_with_index = print_with_index
        self.polyg_coors = None

        
    def random_xyz(self):
        init_angle = np.random.uniform(0,2*np.pi,[2,self.nop])
        xyz = np.vstack([np.cos(init_angle[0,:])*np.sin(init_angle[1,:]),
                        np.sin(init_angle[0,:])*np.sin(init_angle[1,:]),
                        np.cos(init_angle[1,:])])
        return xyz 

    
    def gen_diagonals(self):
        for p in range(self.nop):
            while 1:
                while 1:
                    s               = np.zeros(self.nos-1)
                    # s[0] = 0 for numeration consistency with Canterella_2016
                    s[1:self.nos-2] = np.random.uniform(-1,1,self.nos-3)
                    s[self.nos-2]   = -np.sum(s)
                    if np.greater(np.abs(s[self.nos-2]), 1):
                        pass
                    else:
                        break
                d = np.ones(self.nos-1)      
                # d[0] = 1 for numeration consistency with Canterella_2016
                # (also d[n-2] = 1)
                for i in range(1,self.nos-2): 
                    d[i] = d[i-1] + s[i]
                if np.any(np.less(d[:-1] + d[1:], 1)):
                    pass
                else:
                    break
            theta = np.random.uniform(0,2*np.pi,self.nos-3)
            self.vec_d[:,p] = d
            self.vec_theta[1:,p] = theta
            # theta[0] = 0 for numeration consistency with Canterella_2016

    def calc_loop_vertices(self): # d1 = [x1, x2, x3]
        self.loop_coors[:,0,:] = np.zeros([3,self.nop])
        self.loop_coors[:,1,:] = self.random_xyz()
        for i in range(2, self.nos):
            d2_len = self.vec_d[i-1,:]
            d1_len = self.vec_d[i-2,:]
            d1     = self.loop_coors[:,i-1,:]
            theta  = self.vec_theta[i-2,:]
            
            alpha, betha = self.rotate(d1)
            x   = (np.square(d1_len) - 1 + np.square(d2_len)) / (2 * d1_len)
            rho = np.sqrt(np.square(d2_len) - np.square(x))
            y   = rho * np.cos(theta)
            z   = rho * np.sin(theta)
            self.loop_coors[:,i,:] = self.unrotate([x,y,z],alpha,betha)

    def rotate(self,v): 
        # rotate vector v = [x,y,z] -> w = [d,0,0] (d = length of v)
        x,y,z = v
        #       | 1     0           0      |      | cos(betha) -sin(betha) 0 |
        #   A = | 0 cos(alpha) -sin(alpha) |  B = | sin(betha)  cos(betha) 0 |
        #       | 0 sin(alpha)  cos(alpha) |      |     0           0      1 |
        alpha = np.arctan2(-z,y)
        #       |            x                |
        #  Av = | y cos(alpha) - z sin(alpha) |
        #       | y sin(alpha) + z cos(alpha) |
        # third component equal to zero gives condition on angle alpha that 
        #  rotates v to the XY plane
        betha = np.arctan2( +z*np.sin(alpha) - y*np.cos(alpha), x )
        #       | x cos(betha) - sin(betha)[y cos(alpha) - z sin(alpha)] |
        # BAv = | z sin(betha) + cos(betha)[y cos(alpha) - z sin(alpha)] |
        #       |                         0                              |
        # second component equal to zero gives condition on angle betha that 
        # rotates Av to the x-axis
        return alpha, betha

    def unrotate(self,w,alpha,betha): 
        # unrotates vector rotated by B(betha)A(alpha)
        w = np.array(w)
        alpha = np.array(alpha)
        betha = np.array(betha)
        # A(-alpha)B(-betha)
        try: zero = np.zeros(len(alpha))#; one = np.ones(len(alpha))
        except: zero = 0#; one = 1
        # TRANSPOSED, BUT DOESN'T LOOK LIKE (bracket order)
        # transposition handled by np.einsum
        AB = np.array([[         np.cos(betha),               np.sin(betha),             zero      ],
                       [ -np.cos(alpha)*np.sin(betha),  np.cos(alpha)*np.cos(betha), np.sin(alpha) ],
                       [  np.sin(alpha)*np.sin(betha), -np.sin(alpha)*np.cos(betha), np.cos(alpha) ]])
        return np.einsum('ijk,jk->ik',AB,w)

    def gen_tail(self):
        fi    = np.random.uniform(0,2*np.pi,[self.lot, self.nop])
        theta = np.random.uniform(0,np.pi,[self.lot, self.nop])
        x = np.cos(fi) * np.sin(theta)
        y = np.sin(fi) * np.sin(theta)
        z = np.cos(theta)
        i = 0
        self.tail_coors[0,i,:] = x[i,:]
        self.tail_coors[1,i,:] = y[i,:]
        self.tail_coors[2,i,:] = z[i,:]
        for i in range(1,self.lot):
            self.tail_coors[0,i,:] = x[i,:] + self.tail_coors[0,i-1,:]
            self.tail_coors[1,i,:] = y[i,:] + self.tail_coors[1,i-1,:]
            self.tail_coors[2,i,:] = z[i,:] + self.tail_coors[2,i-1,:]

    def out2string(self, node, polyg):
        string = '{:10f} {:10f} {:10f}\n'.format( 
                                          self.polyg_coors[0, node, polyg],
                                          self.polyg_coors[1, node, polyg],
                                          self.polyg_coors[2, node, polyg])
        if self.print_with_index:
            string = '{:3d} '.format(node+1) + string
        return string

    def out2list(self, node, polyg):
        x = self.polyg_coors[0, node, polyg]
        y = self.polyg_coors[1, node, polyg]
        z = self.polyg_coors[2, node, polyg]
        if self.print_with_index:
            return [node,x,y,z]
        else:
            return [x,y,z]

class Polygon_walk(Polygon):
    def __init__(self, walk_length, no_of_structures, bond_length = 1, 
                 print_with_index = True, file_prefix = 'walk', 
                 folder_prefix = '', file_fmt = (3,5)):
        """
        Program creates random equilateral random walk open polygon chain.                  
        
        Parameters:
        int walk_length    -- number of edges of your random_walk. 
        int no_of_structures -- number of desired polygons, take into account your
                              free RAM cause program creates polygons
                              in parallel (for speed-up).
        float bond_length  -- length of edge.
        str output         -- output type: 'file' or 'list'
        bool print_with_index -- output .xyz file will have format (index x y z)
                                 instead of (x y z)
        str file_prefix     -- prefix for created .xyz files
        str folder_prefix   -- prefix for created folder with .xyz files
        int,int file_fmt -- change space for numbers in names of created 
                           folder/files
                           first number is equal to number of digits of 
                           <walk-length>
                           second is equal to number of digits of <file_num>

        program creates folder with format: 
        <folder_prefix><walk-length>
        and saves files inside with format:
        <file_prefix><file_num>.xyz        
        """
        super().__init__(no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)
        self.lot = walk_length
        self.tail_fmt, self.polyg_fmt = file_fmt
        
        self.tail_coors = np.zeros([3, self.lot, self.nop], order='F')
        self.gen_tail()
        zero = np.zeros([3, 1, self.nop], order='F')
        self.polyg_coors = np.hstack([zero, self.tail_coors]) * self.scale

        self.folder = '{}w{:0{:d}d}/'.format(self.fold_prefix,self.lot,self.tail_fmt)

    def export_polyg_xyz(self):
        try: os.mkdir(self.folder)
        except: pass
        for polyg in range(self.nop):
            with open(self.folder + '/{}{:0{:d}d}.xyz'.format(self.file_prefix, 
                                         polyg, self.polyg_fmt),'w') as f:        
                for node in range(np.shape(self.polyg_coors)[1]):
                    f.write(self.out2string(node, polyg))
        return 'Results saved in {} folder'.format(self.folder)

    def export_polyg_list(self):
        polygs = []
        for polyg in range(self.nop):
            nodes = []
            for node in range(np.shape(self.polyg_coors)[1]):
                nodes.append(self.out2list(node, polyg))
            polygs.append(nodes)
        return polygs

class Polygon_loop(Polygon):
    def __init__(self, loop_length, no_of_structures, bond_length=1,
                 print_with_index=True, file_prefix='loop', folder_prefix='', 
                 file_fmt=(3, 5)):
        """
        Program creates random equilateral closed polygons (loops).
                                                                  
        Algorithm for generating random equilateral polygons based on 
        J. Cantarella \"A fast direct sampling algorithm for equilateral closed 
        polygons\". If you use this program, please, cite his article.  

        Parameters:
        int loop_length    -- number of sides of your loop
        int no_of_structures -- number of desired polygons, take into account your
                              free RAM cause program creates polygons in
                              parallel (for speed-up).
        float bond_length  -- length of edge.
        str output         -- output type: 'file' or 'list'
        bool print_with_index -- output .xyz file will have format (index x y z)
                                 instead of (x y z)
        str file_prefix     -- prefix for created .xyz files
        str folder_prefix   -- prefix for created folder with .xyz files
        int,int file_fmt -- change space for numbers in names of created 
                           folder/files
                           first number is equal to number of digits of 
                           <loop-length>
                           second is equal to number of digits of <file_num>

        program creates folder with format: 
        <folder_prefix><loop-length>
        and saves files inside with format:
        <file_prefix><file_num>.xyz        
        """
        super().__init__(no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)
        self.nos = loop_length
        self.loop_fmt, self.polyg_fmt = file_fmt

        # diagonal lengths
        self.vec_d     = np.zeros([self.nos-1, self.nop], order='F')
        # dihedral angles
        self.vec_theta = np.zeros([self.nos-2, self.nop], order='F')
        self.loop_coors = np.zeros([3, self.nos, self.nop], order='F')

        self.gen_diagonals()
        self.calc_loop_vertices()

        self.polyg_coors = self.loop_coors * self.scale
        self.folder = '{}l{:0{:d}d}/'.format(self.fold_prefix,self.nos,self.loop_fmt)


    def export_polyg_xyz(self):
        try: os.mkdir(self.folder)
        except: pass
        for polyg in range(self.nop):
            with open(self.folder + '/{}{:0{:d}d}.xyz'.format(self.file_prefix, 
                                             polyg, self.polyg_fmt),'w') as f:        
                for node in range(self.nos):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(0, polyg))
        return 'Results saved in {} folder'.format(self.folder)

    def export_polyg_list(self):
        polygs = []
        for polyg in range(self.nop):
            nodes = []
            for node in range(np.shape(self.polyg_coors)[1]):
                nodes.append(self.out2list(node, polyg))
            nodes.append(self.out2list(0, polyg))
            polygs.append(nodes)
        return polygs


class Polygon_lasso(Polygon):
    def __init__(self, loop_length, tail_length, no_of_structures, bond_length = 1, 
                 print_with_index = True, file_prefix = 'lasso', 
                 folder_prefix = '', file_fmt = (3,3,5)):
        """
        Program creates random equilateral closed polygons (loops) with 
        random walk tails (lassos).                  
                                                                  
        Algorithm for generating random equilateral polygons based on 
        J. Cantarella \"A fast direct sampling algorithm for equilateral closed 
        polygons\". If you use this program, please, cite his article.  

        Parameters:
        int loop_length    -- number of sides of your loop
        int tail_length    -- number of vertices of your lasso tail 
        int no_of_structures -- number of desired polygons, take into account your
                              free RAM cause program creates polygons in
                              parallel (for speed-up).
        float bond_length  -- length of edge.
        str output         -- output type: 'file' or 'list'
        bool print_with_index -- output .xyz file will have format (index x y z)
                                 instead of (x y z)
        str file_prefix     -- prefix for created .xyz files
        str folder_prefix   -- prefix for created folder with .xyz files
        int,int,int file_fmt -- change space for numbers in names of created 
                               folder/files
                               first number is equal to number of digits 
                               of <loop-length>
                               second is equal to number of digits of 
                               <tail-length>
                               third is equal to number of digits of 
                               <file_num>

        program creates folder with format: 
        <folder_prefix>l<loop-length>_t<tail-length>
        and saves files inside with format:
        <file_prefix><file_num>.xyz        
        """
        super().__init__(no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)
        self.nos = loop_length
        self.lot = tail_length
        self.loop_fmt, self.tail_fmt, self.polyg_fmt = file_fmt

        # diagonal lengths
        self.vec_d     = np.zeros([self.nos-1, self.nop], order='F')
        # dihedral angles
        self.vec_theta = np.zeros([self.nos-2, self.nop], order='F')
        self.loop_coors = np.zeros([3, self.nos, self.nop], order='F')
        self.tail_coors = np.zeros([3, self.lot, self.nop], order='F')

        self.gen_diagonals()
        self.calc_loop_vertices()
        self.gen_tail()
        self.polyg_coors = np.hstack([self.loop_coors, self.tail_coors]) * self.scale

        self.folder = '{}l{:0{:d}d}_t{:0{:d}d}/'.format(self.fold_prefix, 
                                  self.nos, self.loop_fmt, self.lot, self.tail_fmt)

    def export_polyg_xyz(self):
        try: os.mkdir(self.folder)
        except: pass
        for polyg in range(self.nop):
            with open(self.folder + '/{}{:0{:d}d}.xyz'.format(self.file_prefix, 
                                             polyg, self.polyg_fmt),'w') as f:        
                for node in range(self.nos):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(0, polyg))
                f.write('X\n')
                f.write(self.out2string(0, polyg))
                for node in range(self.nos, self.nos + self.lot):
                    f.write(self.out2string(node, polyg))
        return 'Results saved in {} folder'.format(self.folder)
            
    def export_polyg_list(self):
        polygs = []
        for polyg in range(self.nop):
            nodes = []
            for node in range(self.nos):
                nodes.append(self.out2list(node, polyg))
            nodes.append(self.out2list(0, polyg))
            nodes.append(self.out2list(0, polyg))
            for node in range(self.nos, self.nos + self.lot):
                nodes.append(self.out2list(node, polyg))
            polygs.append(nodes)
        return polygs


class Polygon_handcuff(Polygon):
    def __init__(self, loop_lengths, linker_length, no_of_structures, 
                 bond_length=1, print_with_index=True, file_prefix='hdcf',
                 folder_prefix='', file_fmt=(3, 3, 3, 5)):
        """
        Program creates two random equilateral closed polygons (loops)
        connected by random walk linker (handcuffs).
                                                                  
        Algorithm for generating random equilateral polygons based on 
        J. Cantarella \"A fast direct sampling algorithm for equilateral closed 
        polygons\". If you use this program, please, cite his article.  

        Parameters:
        (int, int) loop_lengths -- number of sides of your loops
        int linker_length       -- number of edges of your linker; 
        int no_of_structures      -- number of desired polygons, take into account
                                   your free RAM cause program creates
                                   polygons in parallel (for speed-up).
        float bond_length  -- length of edge.
        str output         -- output type: 'file' or 'list'
        bool print_with_index -- output .xyz file will have format (index x y z)
                                 instead of (x y z)
        str file_prefix     -- prefix for created .xyz files
        str folder_prefix   -- prefix for created folder with .xyz files
        (int,int,int,int) file_fmt -- change space for numbers in names of created 
                                   folder/files
                                   first number is equal to number of digits 
                                   of <loop1-length>
                                   first number is equal to number of digits 
                                   of <loop2-length>
                                   second is equal to number of digits of 
                                   <linker-length>
                                   third is equal to number of digits of 
                                   <file_num>

        program creates folder with format: 
        <folder_prefix>l<loop1-length>_<loop2-length>_t<linker_length>
        and saves files inside with format:
        <file_prefix><file_num>.xyz        
        """
        super().__init__(no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)

        if type(loop_lengths)==int: loop_lengths = [loop_lengths,loop_lengths]
        self.nos_list = loop_lengths
        self.lot = linker_length
        self.loop1_fmt, self.loop2_fmt, self.tail_fmt, self.polyg_fmt = file_fmt
        
        loops = []
        for i in range(2):
            self.nos = self.nos_list[i]
            # diagonal lengths
            self.vec_d      = np.zeros([self.nos-1, self.nop], order='F')
            # dihedral angles
            self.vec_theta  = np.zeros([self.nos-2, self.nop], order='F')
            self.loop_coors = np.zeros([3, self.nos, self.nop], order='F')
            self.tail_coors = np.zeros([3, self.lot, self.nop], order='F')

            self.gen_diagonals()
            self.calc_loop_vertices()
            loops.append(self.loop_coors)
        self.gen_tail()

        for i in range(self.nos):
            loops[1][:,i,:] += self.tail_coors[:,-1,:]
        self.polyg_coors = np.hstack([loops[0], self.tail_coors[:,:-1,:], loops[1]]) * self.scale

        self.folder = '{}l{:0{:d}d}_{:0{:d}d}_t{:0{:d}d}/'.format(self.fold_prefix, 
                                   loop_lengths[0], self.loop1_fmt, loop_lengths[1],
                                   self.loop2_fmt, self.lot, self.tail_fmt)

    def export_polyg_xyz(self):
        try: os.mkdir(self.folder)
        except: pass
        for polyg in range(self.nop):
            with open(self.folder + '/{}{:0{:d}d}.xyz'.format(self.file_prefix, 
                                             polyg, self.polyg_fmt),'w') as f:        
                for node in range(self.nos_list[0]):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(0, polyg))
                f.write('X\n')
                f.write(self.out2string(0, polyg))
                for node in range(self.nos_list[0], self.nos_list[0]+self.lot-1):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(node+1, polyg))
                f.write('X\n')
                for node in range(self.nos_list[0]+self.lot-1, self.nos_list[0]+self.lot+self.nos_list[1]-1):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(self.nos_list[0]+self.lot-1, polyg))
        return 'Results saved in {} folder'.format(self.folder)

    def export_polyg_list(self):
        polygs = []
        for polyg in range(self.nop):
            nodes = []
            for node in range(self.nos_list[0]):
                nodes.append(self.out2list(node, polyg))
            nodes.append(self.out2list(0, polyg))
            nodes.append(self.out2list(0, polyg))
            for node in range(self.nos_list[0], self.nos_list[0]+self.lot-1):
                nodes.append(self.out2list(node, polyg))
                nodes.append(self.out2list(node+1, polyg))
            for node in range(self.nos_list[0]+self.lot-1, self.nos_list[0]+self.lot+self.nos_list[1]-1):
                nodes.append(self.out2list(node, polyg))
            nodes.append(self.out2list(self.nos_list[0]+self.lot-1, polyg))
            polygs.append(nodes)
        return polygs


class Polygon_link(Polygon):
    def __init__(self, loop_lengths, loop_dist, no_of_structures, 
                 bond_length=1, print_with_index=True, file_prefix='link', 
                 folder_prefix='', file_fmt=(3, 3, 3, 5)):
        """
        Program creates two random equilateral closed polygons (loops)
        connected by random walk linker (handcuffs).
                                                                  
        Algorithm for generating random equilateral polygons based on 
        J. Cantarella \"A fast direct sampling algorithm for equilateral closed 
        polygons\". If you use this program, please, cite his article.  

        Parameters:
        (int, int) loop_lengths -- number of sides of your loops
        ifloat loops_dist       -- distance between geometric enters of loops; 
        int no_of_structures      -- number of desired pairs of polygons, take 
                                   into account your free RAM cause program 
                                   creates polygons in parallel (for speed-up).
        float bond_length  -- length of edge.
        str output         -- output type: 'file' or 'list'
        bool print_with_index -- output .xyz file will have format (index x y z)
                                 instead of (x y z)
        str file_prefix     -- prefix for created .xyz files
        str folder_prefix   -- prefix for created folder with .xyz files
        (int,int,int,int) file_fmt -- change space for numbers in names of created 
                                   folder/files
                                   first number is equal to number of digits 
                                   of <loop1-length>
                                   second number is equal to number of digits 
                                   of <loop2-length>
                                   third is equal to the distance between 
                                   geometrical centers of loops
                                   <linker-length>
                                   fourth is equal to number of digits of 
                                   <file_num>

        program creates folder with format: 
        <folder_prefix>l<loop1-length>_<loop2-length>_d<loops-distance>
        and saves files inside with format:
        <file_prefix><file_num>.xyz        
        """
        super().__init__(no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)
        self.nos_list = loop_lengths
        self.dist = loop_dist
        self.loop1_fmt, self.loop2_fmt, self.dist_fmt, self.polyg_fmt = file_fmt
        
        loops = []
        for i in range(2):
            self.nos = self.nos_list[i]
            # diagonal lengths
            self.vec_d      = np.zeros([self.nos-1, self.nop], order='F')
            # dihedral angles
            self.vec_theta  = np.zeros([self.nos-2, self.nop], order='F')
            self.loop_coors = np.zeros([3, self.nos, self.nop], order='F')

            self.gen_diagonals()
            self.calc_loop_vertices()
            center = np.mean(self.loop_coors, axis=1)
            for i in range(self.nos):
                self.loop_coors[:,i,:] -= center[:,:]
            loops.append(self.loop_coors)

        loops[1][0,:,:] += self.dist
        self.polyg_coors = np.hstack([loops[0], loops[1]]) * self.scale

        self.folder = '{}l{:0{:d}d}_{:0{:d}d}_d{:0{:d}.0f}/'.format(self.fold_prefix, 
                                   loop_lengths[0], self.loop1_fmt, loop_lengths[1],
                                   self.loop2_fmt, self.dist*10, self.dist_fmt)


    def export_polyg_xyz(self):
        try: os.mkdir(self.folder)
        except: pass
        for polyg in range(self.nop):
            with open(self.folder + '/{}{:0{:d}d}.xyz'.format(self.file_prefix, 
                                             polyg, self.polyg_fmt),'w') as f:        
                for node in range(self.nos_list[0]):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(0, polyg))
                f.write('X\n')
                for node in range(self.nos_list[0], self.nos_list[0]+self.nos_list[1]):
                    f.write(self.out2string(node, polyg))
                f.write(self.out2string(self.nos_list[0], polyg))
        return 'Results saved in {} folder'.format(self.folder)


    def export_polyg_list(self):
        polygs = []
        for polyg in range(self.nop):
            nodes = []
            for node in range(self.nos_list[0]):
                nodes.append(self.out2list(node, polyg))
            nodes.append(self.out2list(0, polyg))
            for node in range(self.nos_list[0], self.nos_list[0]+self.nos_list[1]):
                nodes.append(self.out2list(node, polyg))
            nodes.append(self.out2list(self.nos_list[0], polyg))
            polygs.append(nodes)
        return polygs

def generate_polygon(struct, n, *args, **kwargs):
    dic={'walk': Polygon_walk, 'loop': Polygon_loop, 'lasso': Polygon_lasso,
         'handcuff': Polygon_handcuff, 'link': Polygon_link}
    for i in range(n):
        P = dic[struct](*args, **kwargs)
        yield P.export_polyg_list()[0]
