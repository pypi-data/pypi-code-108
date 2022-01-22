import os
import numpy as np
from topoly.polvalues import polvalues
import re
from abc import ABC, abstractmethod
from numpy.polynomial.polynomial import Polynomial

class Poly(ABC):
    """
    Main mother-class from which other classes inherit:
    Poly -> {Poly2D, Jones, BLMHo, Yamada, Conway, Alexander, Kauffman_bracket}.
    Each 1D object has a: 
        name -- i.e. '3_1', '3_1 # 4_1', '3_1 U 3_1'
        value -- tuple of polynomial coefficients and value of the smallest power
        invariant -- name of invariant
    Connecting objects is easy: 
        for disjoint union (U) use „+", for creating composite knotting use „*",
        for Yamada polynomial use „*" for compositing via 2-grade vertices (#2)
        and „**" for composiring via 3-grade vertices (#3)
    """
    @abstractmethod
    def __init__(self, name, value, invariant = None):
        self.name  = name
        self.val   = value[0]
        self.inv   = invariant
        if value[1] == None: self.power = None
        else: self.power = float(value[1])
    def __add__(self, other):
        self.check_compatibility(other)
        new_name = self.name + ' U ' + other.name
        return new_name
    def __mul__(self, other):
        self.check_compatibility(other)
        new_name = self.name + ' # ' + other.name
        return new_name
    def __repr__(self):
        return '{}: {}'.format(self.name, self.pol2str())
    def check_compatibility(self,other):
        if self.inv != other.inv:
            print("Don't mix invariants!!")
            return None
    def pol2str(self):
        arr = [str(int(s)) for s in self.val]
        return ' '.join(arr)
    @staticmethod
    def str2pol(poly):
        if '{' in poly:
            power, poly = poly.split(' | ')
            power = power.lstrip('{ ').rstrip(' }')
        else:
            power = None
        converted = [int(s) for s in poly.split(' ')] 
        return Polynomial(converted), power


class Poly2D(Poly):
    """
    Child of Poly. Second mother-class from which 2D polynomials inherit
    Poly2D -> {HOMFLYPY, Kauffman_polynomial}
    Each 2D object has a: 
        name -- i.e. '3_1', '3_1 # 4_1', '3_1 U 3_1'
        value -- tuple of polynomial coefficients and indexes of row/column
                 where one of variables has 0 power
        invariant -- name of invariant
    Connecting objects is easy: 
        for disjoint union (U) use „+", for creating composite knotting use „*",
        for Yamada polynomial use „*" for compositing via 2-grade vertices (#2)
        and „**" for composiring via 3-grade vertices (#3)
    """
    @abstractmethod
    def __init__(self, name, value, invariant = None):
        self.name = name
        self.val  = value
        self.inv  = invariant
    def pol2str(self):
        val, col0, row0 = self.val
        y = val.shape[0]
        arr = val.tolist()
        string = ''
        for j in range(y):
            arr[j][col0] = '[{}]'.format(str(arr[j][col0]))
            arr[j] = '{}'.format(str(arr[j])).replace("'",'')[1:-1]
            arr[j] = arr[j].replace(',','').strip(' 0')
        arr[row0] = '[{}]'.format(arr[row0])
        arr = '|'.join(arr)
        return arr
    @staticmethod
    def mul_val(val1, val2):
        arr1, col01, row01 = val1
        arr2, col02, row02 = val2
        x1,y1 = arr1.shape
        x2,y2 = arr2.shape
        new_arr = np.zeros([x1+x2-1,y1+y2-1], dtype=np.int)
        col0 = col01 + col02
        row0 = row01 + row02
        for j in range(y1):
            for i in range(x1):
                new_arr[i:i+x2,j:j+y2] += arr2*arr1[i,j]
        return new_arr, col0, row0
    @staticmethod
    def str2pol(poly):
        poly   = poly.split('|')
        col0   = []
        rowlen = []
        # identify where second variable vanishes
        for j in range(len(poly)):
            poly[j] = poly[j].split(' ')
            for i in range(len(poly[j])):
                m = re.search('\[-?[0-9]+\]', poly[j][i])
                if m:
                    poly[j][i] = poly[j][i][1:-1]
                    col0.append(i)
                    rowlen.append(len(poly[j]))
                    break
        # identify where first variable vanishes
        for j in range(len(poly)):
            m = re.search('\[.*',poly[j][0])
            if m:
                poly[j][0] = poly[j][0][1:]
                poly[j][-1] = poly[j][-1][:-1]
                row0 = j
        # create matrix
        left = max(col0)
        right = max([rowlen[i] - col0[i] - 1 for i in range(len(col0))])
        arr = np.zeros([len(rowlen),left+right+1], dtype=np.int)
        for j in range(len(poly)):
            for i in range(len(poly[j])):
                arr[j,i+left-col0[j]] = poly[j][i]
        col0 = left
        return arr, col0, row0

class HOMFLYPT(Poly2D):
    def __init__(self, name, value):
        super().__init__(name, value, 'HOMFLYPT')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val = self.mul_val(self.val, other.val)
        new_val = self.mul_val(new_val, invs[self.inv].str2pol('[[0]]|-1 [0] 1'))
        return invs[self.inv](new_name, new_val)
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = Poly2D.mul_val(self.val, other.val)
        return invs[self.inv](new_name, new_val)

class Kauffman_polynomial(Poly2D):
    def __init__(self, name, value):
        super().__init__(name, value, 'Kauffman polynomial')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val = self.mul_val(self.val, other.val)
        new_val = self.mul_val(new_val, invs[self.inv].str2pol('[[-1]]|1 [0] 1'))
        return invs[self.inv](new_name, new_val)
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = Poly2D.mul_val(self.val, other.val)
        return invs[self.inv](new_name, new_val)

class Jones(Poly):
    def __init__(self, name, value):
        super().__init__(name, value, 'Jones')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val = self.val * other.val * Polynomial((-1, -1))
        new_power = self.power + other.power - 0.5
        return invs[self.inv](new_name, (new_val, new_power))
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = self.val * other.val
        new_power = self.power + other.power
        return invs[self.inv](new_name, (new_val, new_power))
    def pol2str(self):
        if self.power == int(self.power):
            power = int(self.power)
        else:
            power = self.power
        arr = [str(int(s)) for s in self.val]
        string = "{{ {} }} | {}".format(power, ' '.join(arr))
        return string

class BLMHo(Poly):
    def __init__(self, name, value):
        super().__init__(name, value, 'BLM/Ho')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val = self.val * other.val * Polynomial((2, -1))
        new_power = self.power + other.power - 1
        return invs[self.inv](new_name, (new_val, new_power))
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = self.val * other.val
        new_power = self.power + other.power
        return invs[self.inv](new_name, (new_val, new_power))
    def pol2str(self):
        if self.power == int(self.power):
            power = int(self.power)
        else:
            power = self.power
        arr = [str(int(s)) for s in self.val]
        string = "{{ {} }} | {}".format(power, ' '.join(arr))
        return string

class Yamada(Poly):
    def __init__(self, name, value):
        super().__init__(name, value, 'Yamada')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val = self.val * other.val
        return invs[self.inv](new_name, (new_val, None))
    def __mul__(self, other):
        self.check_compatibility(other)
        new_name = self.name + ' #2 ' + other.name
        new_val = self.val * other.val // Polynomial((1,1,1))
        return invs[self.inv](new_name, (new_val, None))
    def __pow__(self, other):
        self.check_compatibility(other)
        new_name = self.name + ' #3 ' + other.name
        new_val = self.val * other.val // Polynomial((-1,-1,-2,-1,-1))
        return invs[self.inv](new_name, (new_val, None))

class Alexander(Poly):
    def __init__(self, name, value):
        super().__init__(name, value, 'Alexander')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val  = Polynomial((0))
        return invs[self.inv](new_name, (new_val, None))
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = self.val * other.val
        return invs[self.inv](new_name, (new_val, None))

class Conway(Poly):
    def __init__(self, name, value):
        super().__init__(name, value, 'Conway')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val  = Polynomial((0))
        return invs[self.inv](new_name, (new_val, None))
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = self.val * other.val
        return invs[self.inv](new_name, (new_val, None))

class Kauffman_bracket(Poly):
    def __init__(self, name, value):
        super().__init__(name, value, 'Kauffman bracket')
    def __add__(self, other):
        new_name = super().__add__(other)
        new_val = self.val * other.val * Polynomial((-1, 0, 0, 0, -1))
        return invs[self.inv](new_name, (new_val, None))
    def __mul__(self, other):
        new_name = super().__mul__(other)
        new_val = self.val * other.val
        return invs[self.inv](new_name, (new_val, None))

invs={'Alexander': Alexander,
      'Conway': Conway,
      'Jones': Jones,
      'HOMFLY': HOMFLYPT,
      'HOMFLYPT': HOMFLYPT,
      'HOMFLY-PT': HOMFLYPT,
      'Yamada': Yamada,
      'Kauffman bracket': Kauffman_bracket,                               
      'Kauffman polynomial': Kauffman_polynomial,                         
      'BLM/Ho': BLMHo,     
      'BLMHo': BLMHo,
      'a': Alexander,
      'c': Conway,
      'j': Jones,
      'h': HOMFLYPT,
      'y': Yamada,
      'kb': Kauffman_bracket,
      'kp': Kauffman_polynomial,
      'b': BLMHo}
    
invs_small={'Alexander': Alexander,
            'Conway': Conway,
            'Jones': Jones,
            'HOMFLYPT': HOMFLYPT,
            'Yamada': Yamada,
            'Kauffman bracket': Kauffman_bracket,                               
            'Kauffman polynomial': Kauffman_polynomial,                         
            'BLM/Ho': BLMHo} 

polval_invs={'Alexander': polvalues['Alexander'],
             'Conway': polvalues['Conway'],
             'Jones': polvalues['Jones'],
             'HOMFLY': polvalues['HOMFLYPT'],
             'HOMFLYPT': polvalues['HOMFLYPT'],
             'HOMFLY-PT': polvalues['HOMFLYPT'],
             'Yamada': polvalues['Yamada'],
             'APS': polvalues['APS'],
             'Kauffman bracket': polvalues['Kauffman bracket'],
             'Kauffman polynomial': polvalues['Kauffman polynomial'],
             'BLM/Ho': polvalues['BLM/Ho'],
             'BLMHo': polvalues['BLM/Ho'],
             'a': polvalues['Alexander'],
             'c': polvalues['Conway'],
             'j': polvalues['Jones'],
             'h': polvalues['HOMFLYPT'],
             'y': polvalues['Yamada'],
             'aps': polvalues['APS'],
             'kb': polvalues['Kauffman bracket'],
             'kp': polvalues['Kauffman polynomial'],
             'b': polvalues['BLM/Ho']}

def create(inv, name, val = None):
    """
    Create list of objects for invariant „inv" with name „name" and „value" val.
    If value is not specified, then basing on invariant nad knot name value(s)
    are searched in polvalues.py. Created objects class are ones that are childs
    of Poly or Poly2D.
    To create disjoint union of knots sum their objects using plus sign „+". 
    To create composite knot multiply their objects using asterisk sign „*".
    For Yamada you can create two types of composite knots -- connecting them
    by 2-grade vertices (#2) or 3-grade vertices (#3). Use „*" to connect by
    2-grade vertices and „**" to connect by 3-grade vertices.
    """
    if val != None:
        return [invs[inv](name, invs[inv].str2pol(val))]
    if '#' in name or 'U' in name:
        print('Function accepts only prime structures.')
        raise NameError
    topols_list = np.array(list(polval_invs[inv].values()))
    polys_list = np.array(list(polval_invs[inv].keys()))
    polys = []
    for name in [name, '+'+name, '-'+name, name+'.1', name+'.2']:
        indexes = np.where(name == topols_list)[0]
        for index in indexes:
            val  = str(polys_list[index]).replace("'",'')
            val  = invs[inv].str2pol(val)
            poly = invs[inv](name, val)
            polys.append(poly)
    return polys

def export(polys, export_file = 'new_polvalues.py'):
    """
    Export list of polynomial objects (polys) to file „export_file".
    """
    print('export_file: ', export_file)
    try: os.mknod(export_file)
    except: print('{} exists. Deleting'.format(export_file))
    with open(export_file, 'w') as f:
        for poly in polys:
            f.write("{}['{}'] = '{}'\n".format(poly.inv, str(poly), poly.name))
        dic = """\npolvalues = {'Alexander': Alexander,
             'Conway': Conway,
             'Jones': Jones,
             'HOMFLY': HOMFLYPT,
             'HOMFLYPT': HOMFLYPT,
             'HOMFLY-PT': HOMFLYPT,
             'Yamada': Yamada,
             'APS': APS,
             'Kauffman bracket': Kauffman_bracket,
             'Kauffman polynomial': Kauffman_polynomial,
             'BLM/Ho': BLMHo,
             'BLMHo': BLMHo}"""
        f.write(dic)

if __name__ == '__main__':
    """ Example """
    polys = []
    for inv in invs_small.keys():
        print('====={}====='.format(inv))
        aa = create(inv, '3_1')
        bb = create(inv, '4_1')
        print('Lists of knots')
        print(aa)
        print(bb)
        for a in aa:
            for b in bb:
                print('\nKnots:')
                print(a)
                print(b)
                # Disjoint union of knots:
                c = a+b
                print(c)
                # Composite knots:
                d = a*b
                print(d)
                polys.append(c)
                polys.append(d)
                if inv == 'Yamada':
                    e = a**b
                    print(e)
                    polys.append(e)
        print('\n')
    export(polys) 
