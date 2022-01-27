import math
import ROOT
import numpy as np
from raser.geometry import R3dDetector

class TCTTracks():
    """
    Description:
        Transfer Carrier Distribution from Laser Coordinate System 
        to 2d Detector Coordinate System
    Parameters:
    ---------
    my_d : R2dDetector or R3dDetector
        the Detector
    laser : dict
        the Parameter List of Your Laser
    x_rel,y_rel,z_rel:
        the Normalized Coordinate for Laser Focus 
        in Detector Coordinate System
    @Modify:
    ---------
        2021/09/13
    """
    def __init__(self,my_d,laser,x_rel,y_rel,z_rel,min_carrier=0):
        self.tech=laser["tech"]
        self.direction=laser["direction"]

        self.refractionIndex=laser["refractionIndex"]

        self.wavelength=laser["wavelength"]*1e-3 #um
        self.tau=laser["tau"]
        self.power=laser["power"]
        self.widthBeamWaist=laser["widthBeamWaist"]#um
        
        self.r_step=laser["r_step"]#um
        self.h_step=laser["h_step"]#um

        if "l_Reyleigh" not in laser:
            self.l_Rayleigh = np.pi*self.widthBeamWaist**2*self.refractionIndex/self.wavelength
        else:
            self.l_Rayleigh = laser["l_Rayleigh"]#um

        if self.direction in ("top","bottom"):
            self.y_step=self.h_step
            self.z_step=self.x_step=self.r_step
            if self.direction == "top":
                def _getCarrierDensity(x,y,z):
                    return self.getCarrierDensity(y,x**2+z**2)
            if self.direction == "bottom":
                def _getCarrierDensity(x,y,z):
                    return self.getCarrierDensity(self.ly-y,x**2+z**2)

        elif self.direction == "edge":
            self.x_step=self.h_step
            self.z_step=self.y_step=self.r_step
            def _getCarrierDensity(x,y,z):
                return self.getCarrierDensity(x,y**2+z**2)
        else:
            raise NameError(self.direction)

        if isinstance(my_d,R2dDetector):
            self.lx=my_d.det_width#um
            self.ly=my_d.det_thin
            self.lz=my_d.det_width
        elif isinstance(my_d,R3dDetector):
            self.lx=my_d.l_x#um
            self.ly=my_d.l_y
            self.lz=my_d.l_z
        else:
            raise TypeError(my_d)

        if self.tech == "SPA":
            self.alpha=laser["alpha"]
            
        elif self.tech == "TPA":
            self.beta_2=laser["beta_2"]

        xArray = np.linspace(0.5*self.x_step,self.lx-0.5*self.x_step,int(self.lx/self.x_step))-self.lx*x_rel
        yArray = np.linspace(0.5*self.y_step,self.ly-0.5*self.y_step,int(self.ly/self.y_step))-self.ly*y_rel
        zArray = np.linspace(0.5*self.z_step,self.lz-0.5*self.z_step,int(self.lz/self.z_step))-self.lz*z_rel

        Y,X,Z=np.meshgrid(yArray,xArray,zArray) #Feature of numpy.meshgrid
        self.projGrid=_getCarrierDensity(X,Y,Z)\
            *self.x_step*self.y_step*self.z_step*1e-18

        if isinstance(my_d,R2dDetector):
            Y2d,X2d=np.meshgrid(yArray+self.ly*y_rel,xArray+self.lx*x_rel)
            self.projGrid=np.sum(self.projGrid,axis=2)
            self.track_position = list(np.transpose(np.array([list(np.ravel(X2d)),list(np.ravel(Y2d))])))
            self.ionized_pairs = list(np.ravel(self.projGrid))
            self.ionized_total_pairs = 0
            self.x_min,self.y_min = self.lx,self.ly
            self.x_max,self.y_max = 0,0
            for i in range(len(self.ionized_pairs)-1,-1,-1):
                if self.ionized_pairs[i]<=min_carrier:
                    del self.ionized_pairs[i]
                    del self.track_position[i]
                else:
                    self.ionized_total_pairs+=self.ionized_pairs[i]
                    self.x_min=min(self.x_min,self.track_position[i][0])
                    self.y_min=min(self.y_min,self.track_position[i][1])
                    self.x_max=max(self.x_max,self.track_position[i][0])
                    self.y_max=max(self.y_max,self.track_position[i][1])

        elif isinstance(my_d,R3dDetector):
            pass

        self.draw_nocarrier2D(x_rel,y_rel,z_rel,min_carrier)

    def getCarrierDensity(self,h,r2):
        widthSquared=(self.widthBeamWaist**2)*(1+(h/self.l_Rayleigh)**2)

        if self.tech=="SPA":
            intensity = ((2*self.power)/(np.pi*widthSquared*1e-12))*np.exp((-2*r2/(widthSquared)))*np.exp(-self.alpha*h*1e-6)
            e0 = 1.60217733e-19
            return self.alpha*intensity/(3.6*e0)
            
        elif self.tech=="TPA":
            k=(self.power**2)*8*np.log(2)/(self.tau*(np.pi**2.5)*(np.log(4))**0.5)
            intensity_squared = k*np.exp(-4*r2/widthSquared)/((widthSquared**2)*1e-24)
            h_Planck = 6.626*1e-34
            speedofLight = 2.998*1e8
            return self.beta_2*self.wavelength*1e-6*intensity_squared/(2*h_Planck*speedofLight)

    def draw_nocarrier2D(self,x_rel,y_rel,z_rel,min_carrier):
        c1 = ROOT.TCanvas("c1","canvas2",200,10,1000,1000)
        h = ROOT.TH2D("h","pairs of carrier generation",\
            int((self.x_max-self.x_min)/self.x_step)+1,self.x_min-0.5*self.x_step,self.x_max+0.5*self.x_step,\
            int((self.y_max-self.y_min)/self.y_step)+1,self.y_min-0.5*self.y_step,self.y_max+0.5*self.y_step)
        for i in range(len(self.track_position)):
            h.Fill(self.track_position[i][0], self.track_position[i][1],self.ionized_pairs[i])
        h.Draw()
        h.GetXaxis().SetTitle("Width [μm]")
        h.GetYaxis().SetTitle("Depth [μm]")
        c1.SaveAs("./fig/nocarrier_"\
            +str(round(x_rel,5))+"_"\
            +str(round(y_rel,5))+"_"\
            +str(round(z_rel,5))+"_"\
            +str(min_carrier)+".pdf")  
