# -*- encoding: utf-8 -*-

'''
Description: Raser parameter settings      
@Date       : 2021/09/02 09:57:00
@Author     : tanyuhang
@version    : 1.0
'''
import json

# Define all input parameters used in raser main process
class Setting:
    def __init__(self,parameters):
        """
        Description:
            1.Different functions detector(), fenics(), pygeant4() define 
            different class parameters.
            2.Parameter defined according input parameters.
        Parameters:
        ---------
        det_model : str
            Define the sensor models for simulation.eg. planar-3D plugin-3D
        _pardic : dictionaries
            Storage the input parameters
        steplength : float
            The length of  each step for e-h pairs drift
        laser_model : str
            Define the Laser Absorption Pattern 
        
        @Modify:
        ---------
            2021/09/02
        """
        self._pardic = {}
        self.input2dic(parameters)
        self.det_model = self._pardic['det_model']
        self.read_par(self._pardic['parfile'])
        if "laser_model" in self._pardic:
            self.laser_model=self._pardic['laser_model']
            self.append_par(self._pardic['laser_file'])
        if "plugin3D" in self.det_model or "planar3D" in self.det_model or "lgad3D" in self.det_model:
            self.scan_variation()

    def input2dic(self,parameters):
        " Transfer input list to dictinary"
        for par in parameters:
            name,_,value=par.rpartition('=')
            self._pardic[name]=value

    def read_par(self,jsonfile):
        "Read the setting.json file and save the input parametersin paras"
        with open(jsonfile) as f:
            dic_pars = json.load(f)
        for dic_par in dic_pars:
            if dic_par['name'] in self.det_model:
                self.steplength = float(dic_par['steplength'])
                paras =  dic_par
        for x in paras: 
            if self.is_number(paras[x]):          
                paras[x] = float(paras[x])
            else:
                paras[x] = paras[x]
        self.paras = paras

    def append_par(self,jsonfile):
        "Read the laser.json file and save the input parameters in paras"
        with open(jsonfile) as f:
            dic_pars = json.load(f)
        for dic_par in dic_pars:
            for x in dic_par: 
                if self.is_number(dic_par[x]):          
                    dic_par[x] = float(dic_par[x])
                else:
                    dic_par[x] = dic_par[x]
            self.paras.update(dic_par) 

    @property
    def detector(self):
        """
        Description:
            Define differnet types detectors parameters. Like:
            planar3D, plugin3D
        Parameters:
        ---------
        lx,ly,lz : float
            Detector length, width and height
        doping : float
            Doping concentation should times 1e12 /um^3  
            -- N-type is positive (negetive volatge applied) 
            -- P-type is negetive (positive volatge applied)
        temp : float
            Tempareture
        e_ir : float
            Radius of electrode in 3D
        e_gap : float
            Spacing between the electrodes in 3D
        @Returns:
        ---------
            A dictionary containing all parameters used in detector  
        @Modify:
        ---------
            2021/09/02
        """
        p = self.paras
        if "planar3D" in self.det_model:
            detector = {'name':'planar3D', 'lx':p['lx'], 'ly':p['ly'], 
                        'lz':p['lz'], 'doping':p['doping'], 
                        'voltage':p['voltage'], 'temp':p['temp'], 'custom_electron': p['custom_electron']
                        }
            
        if "plugin3D" in self.det_model:
            detector = {'name':'plugin3D', 'lx':p['lx'], 'ly':p['ly'], 
                        'lz':p['lz'], 'doping':p['doping'], 
                        'voltage':p['voltage'], 'temp':p['temp'], 
                        'e_ir':p['e_ir'], 'e_gap':p['e_gap'], 'custom_electron': p['custom_electron']
                        }
        if "lgad3D" in self.det_model:
            detector = {'name':'lgad3D', 'lx':p['lx'], 'ly':p['ly'], 'lz':p['lz'],
                        'bond1':p['bond1'], 'bond2':p['bond2'], 'doping1':p['doping1'],
                        'doping2':p['doping2'], 'doping3':p['doping3'], 'part':p['part'], 
                        'voltage':p['voltage'], 'temp':p['temp'], 'custom_electron':p['custom_electron'],
                        'Avalanche':p['Avalanche']
                        }
        return detector

    def electron_custom(self,electrodes):
        self.electrodes = electrodes

    @property
    def electron_customs(self):
        return self.electrodes
        
    @property
    def fenics(self):
        """
        Description:
            Define differnet fenics parameters
        Parameters:
        ---------
        mesh : int
            Mesh precision value, the bigger the higher the accuracy
        xyscale : int
            In plane detector, scale_xy is scaling sensor 50 times at x and 
            y axis, so the precision can improve 50 times in echo distance 

        @Returns:
        ---------
            A dictionary containing all parameters used in fenics  
        @Modify:
        ---------
            2021/09/02
        """
        p = self.paras
        if "planar3D" in self.det_model:
            fenics = {'name':'planar3D', 
                      'mesh':p['mesh'], "xyscale":p['xyscale']}
        if "plugin3D" in self.det_model:
            fenics = {'name':'plugin3D', 
                      'mesh':p['mesh'], "xyscale":p['xyscale']}
        return fenics

    @property
    def pygeant4(self):
        """
        Description:
            Define differnet geant4 parameters
        Parameters:
        ---------
        maxstep : float
            Simulate the step size of each step in Geant4
        par_in : list
            Incident particle position
        par_out : list
            Theoretical position of outgoing particles
        g4_vis : bool
            False: Graphical interface of geant4 particles Disabled
            True: Graphical interface of geant4 particles Enabled
        @Returns:
        ---------
            A dictionary containing all parameters used in geant4  
        @Modify:
        ---------
            2021/09/02
        """
        p = self.paras
        if "planar3D" in self.det_model:
            pygeant4 = {'name':'planar3D',
                        'maxstep':p['maxstep'], 'g4_vis':p['g4_vis'],
                        'par_in':[p['par_inx'], p['par_iny'], p['par_inz']], 
                        "par_out":[p['par_outx'], p['par_outy'], p['par_outz']],
                        }
        if "plugin3D" in self.det_model:
            pygeant4 = {'name':'plugin3D', 
                        'maxstep':p['maxstep'], 'g4_vis':p['g4_vis'],
                        'par_in':[p['par_inx'], p['par_iny'], p['par_inz']], 
                        "par_out":[p['par_outx'], p['par_outy'], p['par_outz']],
                        }
        return pygeant4

    # @property
    # def mips(self):
    #     """
    #     Description:
    #         Define mips parameters
    #     Parameters:
    #     ---------
    #     track_entry : list
    #         Incident particle position
    #     track_exit : list
    #         Exit position
    #     n_div: int
    #         Divide the track line to n_div points
    #     @Returns:
    #     ---------
    #         A dictionary containing all parameters
    #     @Modify:
    #     ---------
    #         2021/09/07
    #     """
    #     p = self.paras
    #     track_par = {'name':'mips',
    #                  'track_entry':[25,0],
    #                  'track_exit':[25,50],
    #                  'n_div':100}      
    #     return track_par

    @property
    def laser(self):
        """
        Description:
            Define laser parameters
        Parameters:
        ---------
        tech : str
            Interaction Pattern Between Laser and Detector
        direction : str
            Direction of Laser Incidence, Could be "top" "edge" or "bottom"

        alpha : float
            the Linear Absorption Coefficient of the Bulk of the Device
        beta_2 : float
            the Quadratic Absorption Coefficient of the Bulk of the Device
        refractionIndex :float
            the Refraction Index of the Bulk of the Device

        wavelength : float
            the Wavelength of Laser in nm
        tau : float
            the Full-width at Half-maximum (FWHM) of the Beam Temporal Profile
        power : float
            the Energy per Laser Pulse
        widthBeamWaist : float
            the Width of the Beam Waist of the Laser in um
        l_Rayleigh : float
            the Rayleigh Width of the Laser Beam

        r_step, h_step : float
            the Step Length of Block in um,
            Carriers Generated in the Same Block Have the Same Drift Locus
        @Returns:
        ---------
            A dictionary containing all parameters used in TCTTracks 
        @Modify:
        ---------
            2021/09/08
        """
        p = self.paras
        if hasattr(self,"laser_model"):
            laser = {'tech':p['laser_model'],'direction':p['direction'],
                    'refractionIndex':p['refractionIndex'],
                    "wavelength":p["wavelength"],"tau":p["tau"],"power":p["power"],"widthBeamWaist":p["widthBeamWaist"],
                    'r_step':p['r_step'],'h_step':p['h_step']
                    }
            if self.laser_model == "SPA":
                laser.update({'alpha':p['alpha']})
            if self.laser_model == "TPA":
                laser.update({'beta_2':p['beta_2']})
            if 'l_Rayleigh' in p:
                laser.update({'l_Rayleigh':p['l_Rayleigh']})
        return laser

    @property
    def amplifer(self):
        """
        Description:
            Define differnet amplifers parameters
        Parameters:
        ---------
        maxstep : float
            Simulate the step size of each step in Geant4
        par_in : list
            Incident particle position
        par_out : list
            Theoretical position of outgoing particles
        g4_vis : bool
            False: Do not display graphical interface of geant4 partivles
            True: Do not display graphical interface of geant4 partivles
        @Returns:
        ---------
            A dictionary containing all parameters used in geant4  
        @Modify:
        ---------
            2021/09/02
        """
        p = self.paras
        CSA_par = {'name':'CSA_ampl', 't_rise':p['t_rise'], 
                   't_fall':p['t_fall'], 'trans_imp':p['trans_imp'], 
                   'CDet':p['CDet']
                  }
        BB_par = {'name':'BB_ampl', 'BBW':p['BBW'], 
                  'BBGain':p['BBGain'], 'BB_imp':p['BB_imp'],'OscBW':p['OscBW']
                 }
        return [CSA_par,BB_par]

    def scan_variation(self):
        " Define parameters of batch mode"
        if "3Dscan" in self.det_model:
            self.total_events = int(self._pardic['total_e'])
            self.intance_number = int(self._pardic['instan'])
            self.g4seed = self.intance_number * self.total_events
            self.output = self._pardic["output"]
        else:
            p = self.paras
            self.total_events = int(p['total_events'])
            self.g4seed = 0 

    def is_number(self,s):
        "Define whethre the s is a number or not"
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False 