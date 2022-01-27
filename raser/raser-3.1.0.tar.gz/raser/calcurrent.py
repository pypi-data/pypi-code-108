# -*- encoding: utf-8 -*-
'''
Description:  Simulate the e-h pairs drift and calculate induced current     
@Date       : 2021/09/02 14:01:46
@Author     : tanyuhang
@version    : 1.0
'''

import random
import numpy as np
import ROOT
import math
import sys
from array import array
from raser.model import Mobility
from raser.model import Avalanche

#The drift of generated particles
class CalCurrent:
    def __init__(self, my_d, my_f, my_g4p, dset, batch=0):
        #mobility related with the magnetic field (now silicon useless)
        self.muhh=1650.0   
        self.muhe=310.0
        self.BB=np.array([0,0,0])
        self.sstep=dset.steplength #drift step
        print(self.sstep)
        self.det_dic = dset.detector
        self.kboltz=8.617385e-5 #eV/K
        self.max_drift_len=1e9 #maximum diftlenght [um]
        self.parameters(my_g4p, my_d, batch)
        self.ionized_drift(my_g4p,my_f,my_d)
        if (self.det_dic['name'] == "lgad3D"):
            self.ionized_drift_gain(my_f,my_d)
        else:
            pass
            
    def parameters(self,my_g4p, my_d, batch): 
        """" Define the output dictionary """   
        self.d_dic_n = {}
        self.d_dic_p = {}
        self.gain_dic_p = [ [] for n in range(5) ]
        self.gain_cu_p = {}
        self.gain_cu_n = {}
        self.events_position(my_g4p, batch) 
        for n in range(len(self.tracks_p)-1):
            self.d_dic_n["tk_"+str(n+1)] = [ [] for n in range(5) ]
            self.d_dic_p["tk_"+str(n+1)] = [ [] for n in range(5) ]
           
    def events_position(self,my_g4p, batch):
        """
        Description:
            Events position and energy depositon
        Parameters:
        ---------
        batch : int
            batch = 0: Single event, choose hit electron
            batch != 0: Multi event, batch is the number of electron     
        @Modify:
        ---------
            2021/09/13
        """     
        if batch == 0:
            for j in range(len(my_g4p.p_steps)):
                if len(my_g4p.p_steps[j])>10 and batch == 0:
                    self.beam_number = j
                    self.tracks_p = my_g4p.p_steps[j]
                    self.tracks_step_edep = my_g4p.energy_steps[j]
                    self.tracks_t_edep = my_g4p.edep_devices[j]
                    batch+=1
                    break
            if batch == 0:
                print("the sensor did have the hit particles")
                sys.exit()
        else:
            self.beam_number = batch
            self.tracks_p = my_g4p.p_steps[batch]
            self.tracks_step_edep = my_g4p.energy_steps[batch]
            self.tracks_t_edep = my_g4p.edep_devices[batch]

    def ionized_drift(self,my_g4p,my_f,my_d):
        """
        Description:
            The drift simulation of all tracks
            One track is corresponding to one electron-hole pair 
        """
        for i in range(len(self.tracks_p)-1):
            self.n_track=i+1
            self.ionized_pairs=self.energy_deposition(my_d,i)
            for j in range(2):
                if (j==0):
                    self.charg=1 #hole
                if (j==1):
                    self.charg=-1 #electron 
                self.loop_electon_hole(my_g4p,my_f,my_d,i)
        self.get_current(my_d)

    def ionized_drift_gain(self,my_f,my_d):
        """
        Description:
            The drift simulation of gain tracks
        """
        for i in range(len(self.gain_dic_p[0])-1):
            self.gain_cu_p["tk_"+str(i+1)] = [ [] for n in range(5) ]
            self.gain_cu_n["tk_"+str(i+1)] = [ [] for n in range(5) ]
            self.n_track = i+1
            for j in range(2):
                self.initial_parameter()
                if (j==0):
                    self.charg = self.gain_dic_p[1][i] #hole
                if (j==1):
                    self.charg = -self.gain_dic_p[1][i] #electron 
                self.d_time = self.gain_dic_p[0][i]
                self.d_x = self.gain_dic_p[2][i]
                self.d_y = self.gain_dic_p[3][i]
                self.d_z = self.gain_dic_p[4][i]
                while (self.end_cond == 0):
                    if self.judge_whether_insensor(my_d,my_f):               
                        pass
                    else:                                                                     
                        self.delta_p() #delta_poisiton               
                        self.drift_v(my_d,my_f) #drift_position                   
                        self.drift_s_step(my_d) #drift_next_posiiton
                        self.charge_collection(my_f)             
                        self.save_gain_track() 
                        self.drift_end_condition()
                    self.n_step+=1 
        self.get_current_gain(my_d)

    def energy_deposition(self,my_d,j):
        """" Deposition energy and generate e-h pair """
        sic_loss_e=self.meter_choose(my_d)
        n_pairs=self.tracks_step_edep[j]*1e6/sic_loss_e
        return n_pairs 

    def loop_electon_hole(self,my_g4p,my_f,my_d,i):
        """
        Description:
            Loop and record the induced cuurent of each eletron or holes         
        Parameters:
        ---------
        arg1 : int
            
        @Modify:
        ---------
            2021/09/13
        """
        self.initial_parameter()
        self.d_x=self.tracks_p[i+1][0]
        self.d_y=self.tracks_p[i+1][1]
        self.d_z=self.tracks_p[i+1][2] - my_g4p.init_tz_device 
        while (self.end_cond == 0):
            if self.judge_whether_insensor(my_d,my_f):               
                pass
            else:                                                                     
                self.delta_p() #delta_poisiton               
                self.drift_v(my_d,my_f) #drift_position                   
                self.drift_s_step(my_d) #drift_next_posiiton
                self.charge_collection(my_f)
                self.update_gain_track()
                self.save_inf_track(my_d) 
                self.drift_end_condition()
            self.n_step+=1 
        
        
    def initial_parameter(self):
        """ initial the parameter in the drift """
        self.end_cond=0
        self.d_time=1.0e-9
        self.path_len=0
        self.n_step=0
        self.charge=0
        self.gain_charge=0
        self.gain_time=0
        self.s_gain=0

    def judge_whether_insensor(self,my_d,my_f):
        """
        Judge the whether the point(x,y,z) is in the sensor
        and whether the electric field is zero
        """
        # electic field of the position
        self.e_field = my_f.get_e_field(self.d_x,
                                        self.d_y,
                                        self.d_z)
        # modify this part										
        if (self.d_y>=(my_d.l_y-1.0) or self.d_x>=(my_d.l_x-1.0) or self.d_z>=(my_d.l_z-1.0)):
            self.end_cond=3  
        elif (self.d_y<=(1.0) or self.d_x<=(1.0) or self.d_z<=(1.0)):
            self.end_cond=8                    
        elif (self.e_field[0]==0 and self.e_field[1]==0 and self.e_field[1]==0):
            self.end_cond=9
        return self.end_cond

    def delta_p(self):
        """ sstep(1um) split to three position """
        if(self.charg)>0:
            eorh = 1
            FF=self.list_add(self.e_field,
                             self.cross(self.e_field,self.BB,self.muhh))
        else:
            eorh =-1
            FF=self.list_sub(self.e_field,
                             self.cross(self.e_field,self.BB,self.muhe))   
        total_ef = self.root_mean_square(FF)
        if(total_ef!=0):
            self.delta_x=-self.sstep*eorh*FF[0]/total_ef
            self.delta_y=-self.sstep*eorh*FF[1]/total_ef
            self.delta_z=-self.sstep*eorh*FF[2]/total_ef
        else:
            self.delta_x=0.0
            self.delta_y=0.0
            self.delta_z=0.0

    def cross(self,p1,p2,scale):
        """ Get vector cross product of p1, p2 """
        o1 = p1[1]*p2[2]-p1[2]*p2[1]
        o2 = p1[2]*p2[0]-p1[0]*p2[2]
        o3 = p1[0]*p2[1]-p1[1]*p2[0]
        return [scale*o1,scale*o2,scale*o3]

    def root_mean_square(self,p1):
        " Return root_mean_square of p1"
        return math.sqrt(p1[0]*p1[0]+p1[1]*p1[1]+p1[2]*p1[2])

    def list_add(self,p1,p2):
        " Return the added two lists. eg:[1,2,3]+[1,2,3] = [2,4,6]"
        return [ a+b for a,b in zip(p1,p2) ]

    def list_sub(self,p1,p2):
        " Return the added two lists. eg:[1,2,3]-[1,2,3] = [0,0,0]"
        return [ a-b for a,b in zip(p1,p2) ]

    def drift_v(self,my_d,my_f):
        """ The drift of e-h pairs at electric field """
        e_delta_f = my_f.get_e_field(self.d_x+self.delta_x,
                                     self.d_y+self.delta_y,
                                     self.d_z+self.delta_z)
        te_delta_f = self.root_mean_square(e_delta_f)
        aver_e = (self.root_mean_square(self.e_field) 
                  + te_delta_f)/2.0*1e4            # V/cm

        if self.det_dic['name'] == "lgad3D":
            self.choose_avalanche(my_d,aver_e)

        mobility = sic_mobility(self.charg,aver_e,my_d,self.det_dic,self.d_z+self.delta_z)  # mobility cm2/(V s) v : cm/s
        self.v_drift = mobility*aver_e 
        #drift part
        if(self.v_drift==0):
            self.delta_x=0.0
            self.delta_y=0.0
            self.delta_z=0.0
            self.dif_x=0.0
            self.dif_y=0.0
            self.dif_z=0.0
            self.end_cond=9
        else:
            #off when the field gets large enough
            DiffOffField=100.0  # if the electric field  
                                # > 100V/um, the holes will multiplicat             
            if(te_delta_f < DiffOffField) or (self.det_dic['name'] == "lgad3D"):
                self.s_time = self.sstep*1e-4/self.v_drift
                s_sigma = math.sqrt(2.0*self.kboltz*mobility
                                    *my_d.temperature*self.s_time)
                self.dif_x=random.gauss(0.0,s_sigma)*1e4
                self.dif_y=random.gauss(0.0,s_sigma)*1e4
                self.dif_z=random.gauss(0.0,s_sigma)*1e4
            else:
                print("the eletric field is too big, \
                       the multiplication appear. The system shold end. ")
                sys.exit(0)

    def drift_s_step(self,my_d):
        """" Drift distance
        d_x: raw position
        delta_x: eletric field
        dif_x thermal diffusion
        """
        # x axis   
        if((self.d_x+self.delta_x+self.dif_x)>=my_d.l_x): 
            self.d_cx = my_d.l_x
        elif((self.d_x+self.delta_x+self.dif_x)<0):
            self.d_cx = 0
        else:
            self.d_cx = self.d_x+self.delta_x+self.dif_x
        # y axis
        if((self.d_y+self.delta_y+self.dif_y)>=my_d.l_y): 
            self.d_cy = my_d.l_y
        elif((self.d_y+self.delta_y+self.dif_y)<0):
            self.d_cy = 0
        else:
            self.d_cy = self.d_y+self.delta_y+self.dif_y
        # z axis
        if((self.d_z+self.delta_z+self.dif_z)>=my_d.l_z): 
            self.d_cz = my_d.l_z
        elif((self.d_z+self.delta_z+self.dif_z)<0):
            self.d_cz = 0
        else:
            self.d_cz = self.d_z+self.delta_z+self.dif_z

    def charge_collection(self,my_f):
        """ Calculate charge collection """ 
        self.wpot = my_f.get_w_p(self.d_cx,self.d_cy,self.d_cz)
        delta_Uw = (self.wpot 
                    - my_f.get_w_p(self.d_x,self.d_y,self.d_z))
        self.charge=self.charg*delta_Uw
        if(self.v_drift!=0):
            self.d_time=self.d_time+self.sstep*1e-4/self.v_drift
            self.path_len+=self.sstep
        self.d_x=self.d_cx
        self.d_y=self.d_cy
        self.d_z=self.d_cz

    def update_gain_track(self):
        """ update the gain track"""
        if self.det_dic['name']=="lgad3D":
            if (self.charg>0) and (self.s_gain>1):
                self.gain_charge = self.ionized_pairs*self.charg*self.s_gain
                self.gain_time=self.d_time
                self.gain_dic_p[0].append(self.gain_time)
                self.gain_dic_p[1].append(self.gain_charge)
                self.gain_dic_p[2].append(self.d_x)
                self.gain_dic_p[3].append(self.d_y)
                self.gain_dic_p[4].append(self.d_z)
            else:
                pass
        else:
            pass


    def drift_end_condition(self): 
        """ Judge whether the drift loop should end """
        if(self.wpot>(1-1e-5)):
            self.end_cond=1
        if(self.d_x<=1.0):
            self.end_cond=2
        if(self.d_y<=1.0):
            self.end_cond=4
        if(self.d_z<=1.0):
            self.end_cond=5
        if(self.path_len>self.max_drift_len):
            self.end_cond=6
        if(self.n_step>10000):
            self.end_cond=7

    def save_inf_track(self,my_d):
        """ Save the information in the dictionary """
        if(((self.charge<0 and my_d.v_voltage<0)  
             or (self.charge>0 and my_d.v_voltage>0))): 
            if(self.charg>0):
                self.d_dic_p["tk_"+str(self.n_track)][0].append(self.d_x)
                self.d_dic_p["tk_"+str(self.n_track)][1].append(self.d_y)
                self.d_dic_p["tk_"+str(self.n_track)][2].append(self.d_z)
                self.d_dic_p["tk_"+str(self.n_track)][3].append(self.charge)
                self.d_dic_p["tk_"+str(self.n_track)][4].append(self.d_time)
            else:
                self.d_dic_n["tk_"+str(self.n_track)][0].append(self.d_x)
                self.d_dic_n["tk_"+str(self.n_track)][1].append(self.d_y)
                self.d_dic_n["tk_"+str(self.n_track)][2].append(self.d_z)
                self.d_dic_n["tk_"+str(self.n_track)][3].append(self.charge)
                self.d_dic_n["tk_"+str(self.n_track)][4].append(self.d_time)

    def save_gain_track(self):
        """ Save the gain carrier information in the dictionary """
        if (self.charg>0):
            self.gain_cu_p["tk_"+str(self.n_track)][0].append(self.d_x)
            self.gain_cu_p["tk_"+str(self.n_track)][1].append(self.d_y)
            self.gain_cu_p["tk_"+str(self.n_track)][2].append(self.d_z)
            self.gain_cu_p["tk_"+str(self.n_track)][3].append(self.charge)
            self.gain_cu_p["tk_"+str(self.n_track)][4].append(self.d_time)
        else:
            self.gain_cu_n["tk_"+str(self.n_track)][0].append(self.d_x)
            self.gain_cu_n["tk_"+str(self.n_track)][1].append(self.d_y)
            self.gain_cu_n["tk_"+str(self.n_track)][2].append(self.d_z)
            self.gain_cu_n["tk_"+str(self.n_track)][3].append(self.charge)
            self.gain_cu_n["tk_"+str(self.n_track)][4].append(self.d_time)

    def get_current(self,my_d):
        """ Charge distribution to initial current"""
        self.reset_start(my_d)
        test_p = ROOT.TH1F("test+","test+",my_d.n_bin,my_d.t_start,my_d.t_end)
        test_n = ROOT.TH1F("test-","test-",my_d.n_bin,my_d.t_start,my_d.t_end)
        total_pairs=0
        sic_loss_e=self.meter_choose(my_d)
        for j in range(len(self.tracks_p)-2):
            test_p,test_n = self.get_trackspn(my_d, test_p, test_n, j)   
            n_pairs=self.tracks_step_edep[j]*1e6/sic_loss_e
            total_pairs+=n_pairs
            test_p.Scale(n_pairs)
            test_n.Scale(n_pairs)            
            my_d.positive_cu.Add(test_p)
            my_d.negative_cu.Add(test_n)
            test_p.Reset()
            test_n.Reset()

        # self.landau_t_pairs = self.tracks_t_edep*1e6/sic_loss_e
        # print("landau_t_pairs=%s"%self.landau_t_pairs)

        # if total_pairs != 0:
        #     n_scale = self.landau_t_pairs/total_pairs
        # else:
        #     n_scale=0
        if self.det_dic['name']=="lgad3D":
            pass
        else:
            my_d.sum_cu.Add(my_d.positive_cu)
            my_d.sum_cu.Add(my_d.negative_cu)
        # my_d.sum_cu.Scale(n_scale)

    def get_current_gain(self,my_d):
        """ Charge distribution to gain current"""
        my_d.gain_positive_cu.Reset()
        my_d.gain_negative_cu.Reset()
        test_p_gain = ROOT.TH1F("testgain+","testgain+",my_d.n_bin,my_d.t_start,my_d.t_end)
        test_n_gain = ROOT.TH1F("testgain-","testgain-",my_d.n_bin,my_d.t_start,my_d.t_end)
        e0 = 1.60217733e-19
        for j in range(len(self.gain_dic_p[0])-2):
            for i in range(len(self.gain_cu_p["tk_"+str(j+1)][2])):
                test_p_gain.Fill(self.gain_cu_p["tk_"+str(j+1)][4][i],
                        self.gain_cu_p["tk_"+str(j+1)][3][i]/my_d.t_bin*e0)
            for i in range(len(self.gain_cu_n["tk_"+str(j+1)][2])):
                test_n_gain.Fill(self.gain_cu_n["tk_"+str(j+1)][4][i],
                        self.gain_cu_n["tk_"+str(j+1)][3][i]/my_d.t_bin*e0)
            my_d.gain_positive_cu.Add(test_p_gain)
            my_d.gain_negative_cu.Add(test_n_gain)
            test_p_gain.Reset()
            test_n_gain.Reset()
        my_d.sum_cu.Add(my_d.gain_positive_cu)
        my_d.sum_cu.Add(my_d.gain_negative_cu)

    def reset_start(self,my_d):
        """ Reset th1f """
        my_d.positive_cu.Reset()
        my_d.negative_cu.Reset()
        my_d.sum_cu.Reset()

    def meter_choose(self,my_d):
        """ Judge the material of sensor """
        if (my_d.mater == 1): # silicon carbide
            sic_loss_e = 8.4 #ev
        elif (my_d.mater == 0):   # silicon
            sic_loss_e = 3.6 #ev
        return sic_loss_e

    def choose_avalanche(self,my_d,aver_e):
        """Choose the avalanche model"""
        my_avalanche = Avalanche(self.det_dic['Avalanche'])
        tmp_coefficient = my_avalanche.cal_coefficient(aver_e,self.charg,my_d.temperature)
        self.s_gain = math.exp(self.sstep*1e-4*tmp_coefficient)

    def get_trackspn(self, my_d, test_p, test_n, j):
        """ Total current of each e-h pair"""
        e0 = 1.60217733e-19
        for i in range(len(self.d_dic_p["tk_"+str(j+1)][2])):
            test_p.Fill(self.d_dic_p["tk_"+str(j+1)][4][i],
                        self.d_dic_p["tk_"+str(j+1)][3][i]/my_d.t_bin*e0)   
        for i in range(len(self.d_dic_n["tk_"+str(j+1)][2])):
            test_n.Fill(self.d_dic_n["tk_"+str(j+1)][4][i],
                        self.d_dic_n["tk_"+str(j+1)][3][i]/my_d.t_bin*e0)
        return test_p, test_n
        
# # # mobility model
def sic_mobility(charge,aver_e,my_d,det_dic,z):
    """ SiC mobility model 
    SiC reference: TCAD SIMULATION FOR ALPHA-PARTICLE SPECTROSCOPY USING SIC SCHOTTKY DIODE
    Si  reference: Signal development in irradiated silicon detectors
    """
    T=my_d.temperature
    E=aver_e
    if det_dic['name'] == "lgad3D":
        if det_dic['part'] == 2:
            bond = det_dic['bond1']
            if (z < bond):
                Neff = det_dic['doping1']
            else:
                Neff = det_dic['doping2']
        elif det_dic['part'] == 3:
            bond1 = det_dic['bond1']
            bond2 = det_dic['bond2']
            if (z < bond1):
                Neff = det_dic['doping1']
            elif (z > bond2):
                Neff = det_dic['doping3']
            else:
                Neff = det_dic['doping2']
    else:
        Neff=abs(my_d.d_neff)
    #silicon
    if my_d.mater == 0:
        alpha = 0.72*math.pow(T/300.0,0.065)
        if(charge>0):
            ulp = 460.0 * math.pow(T / 300.0, -2.18)
            uminp = 45.0*math.pow(T / 300.0, -0.45)
            Crefp = 2.23e17*math.pow(T / 300.0, 3.2)
            betap = 1.0
            vsatp = 9.05e6 * math.sqrt(math.tanh(312.0/T))
            lfm = uminp + (ulp-uminp)/(1.0 + math.pow(Neff*1e12 / Crefp, alpha))
            hfm = 2*lfm / (1.0+math.pow(1.0 + math.pow(2*lfm * E / vsatp, betap), 1.0 / betap))                        
        else:
            uln = 1430.0 * math.pow(T / 300.0, -2.0)
            uminn = 80.0*math.pow(T / 300.0, -0.45)
            Crefn = 1.12e17*math.pow(T/300.0,3.2)
            betan = 2
            vsatn = 1.45e7 * math.sqrt(math.tanh(155.0/T))
            lfm = uminn + (uln-uminn)/ (1.0 + math.pow(Neff*1e12 / Crefn, alpha))
            hfm = 2*lfm / (1.0+math.pow(1.0 + math.pow(2*lfm * E / vsatn, betan), 1.0/betan))
    #silicon carbide
    elif my_d.mater == 1:
        if(charge>0):
            alpha = 0.34
            ulp = 124.0 * math.pow(T / 300.0, -2.0)
            uminp = 15.9
            Crefp = 1.76e19
            betap = 1.213 * math.pow(T / 300.0, 0.17)
            vsatp = 2e7 * math.pow(T / 300.0, 0.52)
            lfm = uminp + ulp/(1.0 + math.pow(Neff*1e12 / Crefp, alpha))
            hfm = lfm / (math.pow(1.0 + math.pow(lfm * E / vsatp, betap), 1.0 / betap))                        
        else:
            alpha = 0.61
            ulp = 947.0 * math.pow(T / 300.0, -2)
            Crefp = 1.94e19
            betap = 1.0 * math.pow(T / 300.0, 0.66)
            vsatp = 2e7 * math.pow(T / 300.0, 0.87)
            lfm = ulp/ (1.0 + math.pow(Neff*1e12 / Crefp, alpha))
            hfm = lfm / (math.pow(1.0 + math.pow(lfm * E / vsatp, betap), 1.0/betap))                      
    return hfm
