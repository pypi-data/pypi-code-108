# -*- encoding: utf-8 -*-
'''
Description: 
    Simulate induced current through BB or CSA amplifier 
@Date       : 2021/09/02 14:11:57
@Author     : tanyuhang
@version    : 1.0
'''

import math
import ROOT

# CSA and BB amplifier simulation
class Amplifier:
    def __init__(self,my_d,ampl_par,mintstep="50e-12"):
        """
        Description:
            Get current after CSA and BB amplifer
        Parameters:
        ---------
        CSA_par : dic
            All input paramters of CSA in CSA_par
        BB_par : dic
            All input paramters of BB in CSA_par
        mintsteo : float
            The readout time step (bin width)        
        @Modify:
        ---------
            2021/09/09
        """
        CSA_par = ampl_par[0]
        BB_par = ampl_par[1]
        self.ampli_define(CSA_par,BB_par)
        self.sampling_charge(my_d,mintstep)
        self.ampl_sim() 

    def ampli_define(self,CSA_par,BB_par):
        """
        Description:
            The parameters of CSA and BB amplifier.
            Details introduction can be got in setting module.
        @Modify:
        ---------
            2021/09/09
        """
        self.t_rise    = CSA_par['t_rise']
        self.t_fall    = CSA_par['t_fall']
        self.trans_imp = CSA_par['trans_imp']
        self.CDet      = CSA_par['CDet']
        self.BBW       = BB_par['BBW']
        self.BBGain    = BB_par['BBGain']
        self.BB_imp    = BB_par['BB_imp']
        self.OscBW     = BB_par['OscBW'] 
        ##BB simualtion parameter
        tau_C50 = 1.0e-12*50.*self.CDet          #Oscil. RC
        tau_BW = 0.35/(1.0e9*self.OscBW)/2.2      #Oscil. RC
        tau_BB_RC = 1.0e-12*self.BB_imp*self.CDet     #BB RC
        tau_BB_BW = 0.35/(1.0e9*self.BBW)/2.2    #BB Tau
        self.tau_scope = math.sqrt(pow(tau_C50,2)+pow(tau_BW,2))
        self.tau_BBA =  math.sqrt(pow(tau_BB_RC,2)+pow(tau_BB_BW,2))    #BB_out

    def sampling_charge(self,my_d,mintstep):
        """ Transform current to charge 
        with changing bin width to oscilloscope bin width
        """
        self.max_num = my_d.sum_cu.GetNbinsX()
        self.max_hist_num = my_d.n_bin
        self.undersampling = int(float(mintstep)/my_d.t_bin)
        self.time_unit = my_d.t_bin*self.undersampling
        self.CDet_j = 0     # CSA readout mode
        self.itot = [0.0]*self.max_num
        self.qtot = 0.0
        # get total charge
        i=0
        for j in range(0,self.max_hist_num,self.undersampling):
            self.itot[i] = my_d.sum_cu.GetBinContent(j)
            self.qtot = self.qtot + self.itot[i]*self.time_unit
            i+=1
        max_hist_num = int(self.max_hist_num/self.undersampling)
        IintTime = max(2.0*(self.t_rise+self.t_fall)*1e-9/self.time_unit,
                       3.0*self.tau_BBA/self.time_unit)
        self.IMaxSh = int(max_hist_num + IintTime)

    def ampl_sim(self):
        """
        Description:
            CSA and BB amplifier Simulation         
        Parameters:
        ---------
        arg1 : int
            
        @Modify:
        ---------
            2021/09/09
        """
        IMaxSh = self.IMaxSh
        preamp_Q = [0.0]*IMaxSh
        self.CSA_p_init()
        self.BB_p_init()
        step=1
        for i in range(IMaxSh-step):
            if(i>0 and i <self.max_hist_num-step):
                preamp_Q[i] = 0.0
                for il in range(i,i+step):
                    preamp_Q[i] += self.itot[il]*self.time_unit
            elif (i != 0):
                preamp_Q[i]=0.0

        for i in range(IMaxSh-step):
            if i >= step:
                dif_shaper_Q = preamp_Q[i]
            else:
                dif_shaper_Q = 0
            for j in range(IMaxSh-i):
                self.fill_CSA_out(i,j,dif_shaper_Q)
                self.fill_BB_out(i,j,dif_shaper_Q)
            self.max_CSA(i)
        self.fill_CSA_th1f()
        self.fill_BB_th1f()

    def CSA_p_init(self):
        """ CSA parameter initialization"""
        t_rise = self.t_rise
        t_fall = self.t_fall
        self.tau_rise = t_rise/2.2*1e-9
        self.tau_fall = t_fall/2.2*1e-9
        if (self.tau_rise == self.tau_fall):
            self.tau_rise *= 0.9
        self.sh_max = 0.0  
        self.shaper_out_Q = [0.0]*self.IMaxSh
        self.shaper_out_V = [0.0]*self.IMaxSh

    def BB_p_init(self):
        """ BB parameter initialization"""
        self.Vout_scope = [0.0]*self.IMaxSh
        self.Iout_BB_RC = [0.0]*self.IMaxSh
        self.Iout_C50 = [0.0]*self.IMaxSh   
        self.BBGraph = [0.0]*self.IMaxSh

    def fill_CSA_out(self,i,j,dif_shaper_Q):
        """ Fill CSA out variable"""     
        self.shaper_out_Q[i+j] += self.tau_fall/(self.tau_fall+self.tau_rise) \
                                  * dif_shaper_Q*(math.exp(-j*self.time_unit
                                  / self.tau_fall)-math.exp(
                                  - j*self.time_unit/self.tau_rise))

    def fill_BB_out(self,i,j,dif_shaper_Q):
        """ Fill BB out variable"""   
        self.Iout_C50[i+j] += (dif_shaper_Q)/self.tau_scope \
                                * math.exp(-j*self.time_unit/self.tau_scope)
        self.Iout_BB_RC[i+j] += (dif_shaper_Q)/self.tau_BBA \
                                * math.exp(-j*self.time_unit/self.tau_BBA)
        self.BBGraph[i+j] = 1e+3 * self.BBGain * self.Iout_BB_RC[i+j]
        self.Vout_scope[i+j] = 50 * self.Iout_C50[i+j]
        if (abs(self.BBGraph[i+j]) > 800):
            self.BBGraph[i+j] = 800*self.BBGraph[i+j]/abs(self.BBGraph[i+j])

    def max_CSA(self,i):
        """ Get max out value of CSA"""               
        if (abs(self.shaper_out_Q[i]) > abs(self.sh_max)):
            self.sh_max = self.shaper_out_Q[i]

    def fill_CSA_th1f(self):
        """ Change charge to amplitude [mV]
            and save in the th1f
        """
        Ci = 3.5e-11  #fF
        Qfrac = 1.0/(1.0+self.CDet*1e-12/Ci)
        self.CSA_ele = ROOT.TH1F("electronics", "electronics",
                                 self.IMaxSh, 0, self.IMaxSh*self.time_unit)
        for i in range(self.IMaxSh):
            if self.sh_max == 0.0:
                self.shaper_out_V[i] = 0.0
            elif self.CDet_j == 0:
                self.shaper_out_V[i] = self.shaper_out_Q[i]*self.trans_imp\
                                       * 1e15*self.qtot*Qfrac/self.sh_max            
            elif self.CDet_j ==1:
                self.shaper_out_V[i] = self.shaper_out_Q[i]*self.trans_imp\
                                       * 1e15*self.qtot/self.sh_max
            self.CSA_ele.SetBinContent(i,self.shaper_out_V[i])
        #Print the max current time of CSA
        max_CSA_height = min(self.shaper_out_V)
        time_t = self.shaper_out_V.index(max_CSA_height)
        print("CSA_time=%s" %(time_t*self.time_unit))

    def fill_BB_th1f(self):
        """ Change charge to amplitude [mV]
            and save in the th1f
        """
        self.BB_ele = ROOT.TH1F("electronics BB","electronics BB",
                                self.IMaxSh,0,self.IMaxSh*self.time_unit)
        for i in range(len(self.BBGraph)+1):
            if i == 0:
                self.BB_ele.SetBinContent(i,0)
            else:
                self.BB_ele.SetBinContent(i,self.BBGraph[i-1])
        # Print the max current time of BB
        max_BB_height = min(self.BBGraph)
        time_t = self.BBGraph.index(max_BB_height)
        print("BB_time=%s"%(time_t*self.time_unit))
          
    def __del__(self):
        pass