'''
Created on 29 Jan. 2017

@author: HAssan
'''

import math
import numpy as np
from scipy.special import comb



class Laplacenoise(object):
    
    DEL_LIM = 2**(-30)
   
    k = 0
    perc = 0.95 # with probability perc the answers are within
    pure = True # whether each application of the mechanism is (eps, 0) (pure) or (eps, del) (not pure)
    publicn = False # whether or not the population count is public or not
    

    def __init__(self, nb_marginal, eps_lim):
        '''
        Constructor
        '''
        self.k = comb(nb_marginal, 2) + nb_marginal
        self.EPS_LIM =eps_lim 


    
    
    #Calculate the noise if we work with 3-way marginals
    def getSpecial3noise(self, nb_marginal, eps_lim): 
        self.k = comb(nb_marginal, 3)
        self.EPS_LIM =eps_lim 
        return self.getEpsilon()
        
        
    #Generate noise    
    def getNoisefromEpsilon(self, loc, epsilon):
        scale = float(2/epsilon)
        lap= np.random.laplace(loc, scale,1)
        return lap[0]
    
    #calculate epsilon   
    def getEpsilon(self):
        ebar1, dbar1 = self.paramsadvcomp( self.pure)
        ebar2, dbar2 = self.paramsbasiccomp( self.pure)

        return max(ebar1,ebar2)
    
    
    #calculate basic epsilon   
    def getBasicEpsilon(self):
        ebar1, dbar1 = self.paramsadvcomp( self.pure)
        return ebar1
    
    
    def getMaxBound(self):
        eps = self.getEpsilon()
        max = 2/eps*math.log(100)
        return max

    def getMaxBound_formEps(self, epsilon):
        max = 2/epsilon*math.log(100)
        return max
        
    def getdeltalim(self):
        print ()
        return self.DEL_LIM

    #calculate epsilon limit   
    def getepslim(self):
        return self.EPS_LIM
    
    def advcompformula(self,ebar, dbar, k):
        a = np.sqrt(2*k*np.log(1/dbar))*ebar + k*ebar*(np.exp(ebar) - 1) # In DP-book, page 49
        return a
    
    def basiccompformula(self,ebar, k):
        a = k*ebar 
        return a
    
    def paramsadvcomp(self, pure):
        delta = self.getdeltalim()
        eps = self.getepslim() # overall epsilon
        if pure:
            dbar = delta # this means the k mechanisms are (eps, 0)-diff private
        else:
            dbar = delta/(self.k + 1) # we set dbar and delta to be the same

        #print ('k', self.k, 'delta', delta,'dbar', dbar )
        ebar = 1
        s = 0.000001 #precision level
        found = False
        while not found:
            cebar = self.advcompformula(ebar, dbar, self.k)
            #print(cebar)
            if cebar < eps:
                found = True
            else:
                ebar = ebar - s
        return ebar, dbar # this is the setting of each mechanism

    def paramsbasiccomp(self, pure):
        delta = self.getdeltalim()
        eps = self.getepslim() # overall epsilon
        if pure:
            dbar = 0 # this means the k mechanisms are (eps, 0)-diff private
        else:
            dbar = delta/self.k # we set dbar and delta to be the same
        ebar = 1
        s = 0.000001 #precision level
        found = False
        while not found:
            cebar = self.basiccompformula(ebar, self.k)
            #print(cebar)
            if cebar < eps:
                found = True
            else:
                ebar = ebar - s
        return ebar, dbar # this is the setting of each mechanism
    
    def checkthresholdsh(self,eps, delta):
        thr = 2*np.log(2/delta)/(eps) + 1
        alp = 1
        thr = thr*alp
        #print("thr:", thr)
        noise = np.random.laplace(loc = 0, scale = 2/(eps))
        #print("noise:", noise)
        return thr, noise
    
    def sanitycheck(self,ebar, dbar, k):
        b = np.sqrt(2*k*np.log(1/dbar))*ebar + k*ebar*(np.exp(ebar) - 1)
        return b
    
    def getlapnoisebound(self,eps, perc, publicn):
        t = -np.log(1 - perc)
        if publicn:
            return 2*t/eps
        else:
            return t/eps
        
    
    
    def getNoisycontingency( self, binary_contingency):
        laplace = {}
        loc =0
        epsilon, dbar = self.paramsbasiccomp( self.pure)
        for i in binary_contingency.keys():
            laplace[i] = self.getNoisefromEpsilon(loc, epsilon) + binary_contingency[i]
        return laplace
        