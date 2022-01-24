import matplotlib.patches as mpatches
import numpy as np
import sympy as sp
import traits.api as tr
from bmcs_cross_section.mkappa import MKappa
from bmcs_beam.beam_config.boundary_conditions import BoundaryConditions
from bmcs_utils.api import InteractiveModel, \
    Item, View, Float, Int, FloatEditor, FloatRangeEditor, mpl_align_yaxis
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from sympy.physics.continuum_mechanics.beam import Beam

class UltimateLimitState(InteractiveModel):

    F_max = Float(1, desc='maximum load value', BC=True)
    theta_F = Float(1.0, desc='load factor', BC=True)

    F = tr.Property(depends_on='+BC')

    ipw_view = View(
        Item('theta_F', latex=r'\theta [-]',
             editor=FloatRangeEditor(low=0, high=1)),
        Item('F_max', latex='F_\mathrm{max} [\mathrm{N}]',
             readonly=True),
        Item('G_adj', param=True, latex='G_{adj} [\mathrm{-}]', minmax=(1e-3, 1e-1)),
        Item('n_x', param=True, latex='n_x [\mathrm{-}]'),
    )

    x = tr.Property(depends_on='_GEO')

    @tr.cached_property
    def _get_x(self):
        pass

    def get_M_x(self):
        pass

    def plot_geo(self, ax1):
        pass

    def subplots(self, fig):
        pass

    def update_plot(self, axes):
        ax1, ax2, ax3 = axes
        self.plot_geo(ax1)
        self.plot_MQ(ax2, ax3)
        ax1.axis('equal')
        ax1.autoscale(tight=True)

class ServiceabilityLimitState(InteractiveModel):

    F_max = Float(1, desc='maximum load value', BC=True)
    theta_F = Float(1.0, desc='load factor', BC=True)

    F = tr.Property(depends_on='+BC')

    ipw_view = View(
        Item('theta_F', latex=r'\theta [-]',
             editor=FloatRangeEditor(low=0, high=1)),
        Item('F_max', latex='F_\mathrm{max} [\mathrm{N}]',
             readonly=True),
        Item('G_adj', param=True, latex='G_{adj} [\mathrm{-}]', minmax=(1e-3, 1e-1)),
        Item('n_x', param=True, latex='n_x [\mathrm{-}]'),
    )

    x = tr.Property(depends_on='_GEO')

    @tr.cached_property
    def _get_x(self):
        pass

    def get_M_x(self):
        pass

    def plot_geo(self, ax1):
        pass

    def subplots(self, fig):
        ax1, ax2 = fig.subplots(2, 1)
        ax3 = ax2.twinx()
        return ax1, ax2, ax3

    def update_plot(self, axes):
        ax1, ax2, ax3 = axes
        self.plot_geo(ax1)
        self.plot_MQ(ax2, ax3)
        ax1.axis('equal')
        ax1.autoscale(tight=True)





#From MATLAB code


# % ANALYSIS AND DESIGN OF RECTANGULAR AND FLANGED BEAMS PER EUROCODE 2
# % THIS PROGRAM WILL CALCULATE THE AREA OF REINFORCEMENT REQUIRED, AND ALSO DO THE DEFLECTION VERIFICATION USING THE DEEMED TO SATISFY RULES OF EC2
#
#
# % INPUT MATERIAL PROPERTIES
Fck = 1 #(‘Enter the grade of concrete (N/mm^2)Fck  = ‘);
Fyk = 1 #(‘Enter the yield strength of steel (N/mm^2)Fyk = ‘);
#
# % INPUT DESIGN MOMENT
MEd = 1 #(‘Enter the ultimate design moment (KNm) MEd = ‘);

# % INPUT SECTION AND DESIGN PROPERTIES
h = 1 #(‘Enter the depth of beam (mm)h = ‘);
b = 1 #(‘Enter the effective flange width of the beam (mm)b = ‘);
bw = 1 #(‘Enter the beam width (mm)bw = ‘);
Cc = 1 #(‘Enter concrete cover (mm) = ‘);
dr = 1 #(‘Enter the diameter of reinforcement (mm) = ‘);
dl = 1 #(‘Enter the diameter of links = ‘);

# % CALCULATION OF EFFECTIVE DEPTH

d = h-Cc-(dr/2)-dl # ‘Effective depth d (mm)’

do = Cc+dl+(dr/2) # ‘Depth of reinforcement from the face of concrete’

# % ANALYSIS FOR INTERNAL STRESSES
ko = 0.167
k = (MEd*10^6)/(Fck*b*d**2)
if k>ko:

    # disp(‘Since k > ko, Compression reinforcement is required’)
    Mcd = (Fck*b*d**2*(k-ko))*10**(-6)
    As2 = (Mcd*10**6)/(0.87*Fyk*(d-do))
    z = 0.5*d*(1+(1-3.53*ko) ** 0.5)
    As1 = ((ko*Fck*b*d^2)/(0.87*Fyk*z))+ As2
else:
    # disp(‘Since k < ko, No Compression reinforcement is required’)
    # disp(‘Lever arm (la)’)
    la = 0.5+ (0.25-0.882*k) ** 0.5
    if la>0.95:
        # disp(‘Since la > 0.95,’)
        la = 0.95
    else:
        la = 0.5+ (0.25-0.882*k)**0.5
        As1 =(MEd*10^6)/(0.87*Fyk*la*d)


# % MINIMUM AREA OF STEEL REQUIRED
fctm = 0.3*(Fck **(2/3)) #%MEAN TENSILE STRENGTH OF CONCRETE (TABLE 3.1 EC2)
ASmin = 0.26*(fctm/Fyk)*bw*d
if ASmin < 0.0013*bw*d:
    ASmin = 0.0013*bw*d
elif As1<ASmin:
    As1 = ASmin
else:
    print('Since As1 > Asmin, provide As1 which is the area of steel required')



Asprov1 = 1 #(‘Enter area of tension steel provided (mm^2) = ‘);
Asprov2 = 1 #(‘Enter area of compression steel provided if any (mm^2) = ‘);



# % CHECK FOR DEFLECTION
#
# disp(‘DO YOU WANT TO CHECK FOR DEFLECTION?’)
# G = input(‘ENTER (1) FOR YES OR (0) FOR NO = ‘);
# if G == 1;
#     disp(‘CHECK FOR DEFLECTION’)
# disp(‘BASIC SPAN/EFFECTIVE DEPTH RATIO (K)’)
# disp(‘CANTILEVER = 0.4’)
# disp(‘SIMPLY SUPPORTED = 1.0’)
# disp(‘SIMPLY SUPPORTED AND FIXED AT ONE END = 1.3’)
# disp(‘FIXED AT BOTH ENDS = 1.5’)
# K = input(‘Enter the selected value of k = ‘);
# L = input(‘Enter the deflection critical length of the member (mm) = ‘);
#
# disp(‘Fs is the stress in tensile reinforcement under service loading’)
# Fs = (310*Fyk*As1)/(500*Asprov1)
# disp(‘Bs = 310/Fs’)
# Bs = 310/Fs
# disp(‘P is the reinforcement ratio in the section (Asprov1)/(b*d)’)
# P = (Asprov1)/(b*d)
# disp(‘Po = sqrt(Fck)/1000’)
# Po = sqrt(Fck)/1000
# P1 = (Asprov2)/(b*d)
# if
#   P <= Po
#   I_deflection = K*(11+(1.5*sqrt(Fck)*(Po/P)) + 3.2*sqrt(Fck)*((Po/P)-1)^1.5)
# else
#     I_deflection = K*(11+(1.5*sqrt(Fck)*(Po/(P-P1))) + 3.2*sqrt(Fck)*((Po/P)-1)^1.5)
# end
# CV = input(‘Is the beam is flanged? (1) for YES and (0) for NO = ‘)
# if CV == 1
# disp(‘S is the ratio of beff/bw’)
# S = b/bw
#   bn = (11-(b/bw))/10
#
#   if S >= 3.0;
#    K_deflection = Bs*0.8* I_deflection
# else
#    K_deflection = Bs*bn* I_deflection
#   end
#    if L>7000
#     Limiting_deflection = (7000/L)*K_deflection
# else
#     Limiting_deflection =  K_deflection
# end
#   end
# else
#   Limiting_deflection =   Bs*I_deflection
# end
# Actual_deflection = L/d
# if
# Limiting_deflection > Actual_deflection
#     disp(‘Deflection is satisfactory’)
# else
#     disp(‘DEFLECTION IS NOT SATISFACTORY !!!!! Increase depth of beam, or increase area of steel, or both. Then rerun proforma’)
#
#
# end
#
# 2.0 MATLAB CODE FOR SHEAR DESIGN ACCORDING TO EC2
#
# % SHEAR DESIGN IN EUROCODE 2
# clc
# disp(‘SHEAR DESIGN ACCORDING TO EC2′)
# disp(‘THIS PROFORMA WAS WRITTEN BY O.U.R. UBANI’)
#
#
# % MATERIALS PROPERTIES
# Fck = input(‘Enter the grade of concrete (N/mm^2) = ‘);
# Fyk = input(‘Enter the yield strength of steel (N/mm^2) = ‘);
#
# VEd = input(‘Enter the value of shear force at ULS (KN) = ‘);
#
# % SECTION PROPERTIES
# h = input(‘Enter the depth of beam (mm) = ‘);
# bw = input(‘Enter the beam width (mm) = ‘);
# Cc = input(‘Enter concrete cover (mm) = ‘);
# dr = input(‘Enter the diameter of reinforcement (mm) = ‘);
# dl = input(‘Enter the diameter of links = ‘)
# d = h-Cc-(dr/2)-dl % Effective depth
# do = Cc+dl+(dr/2)
#
# % CALCULATION OF THE SHEAR CAPACITY OF THE SECTION WITH NO SHEAR REINFORCEMENT
#
# Asprov1= input(‘Enter the area of steel provided in the shear zone (mm^2) = ‘) % The reinforcement must exceed the design anchorage length by at least the effective depth
# Crd = 0.12
# k1= 1+sqrt(200/d)
# if k1>2
# k1=2
# end
# disp(‘Reinforcement ratio’)
# P1 = (Asprov1/(bw*d))
# if P1>0.02
# P1 = 0.02
# end
#
# % THIS SECTION IS TO BE CONSIDERED IF THERE IS AXIAL FORCE IN THE SECTION
# disp(‘Axial force in the section’)
# N = input(‘Enter the value of AXIAL FORCE IF ANY(+VE FOR COMP, AND -VE FOR TENSION)(kN) = ‘)
# disp(‘Axial stress in the section (Ds)’)
# Ds = (N*1000)/(bw*h)
# if Ds > (0.2*0.85*Fck)/1.5
# Ds = (0.2*0.85*Fck)/1.5
# end
# k2 = 0.15;
# disp(‘Minimum shear stress in the section (N/mm^2)’)
# Vmin = 0.035*k1^(1.5)*sqrt(Fck)
# disp(‘Concrete resistance shear stress (VRd) (N/mm^2)’)
# VRdQ = ((Crd*k1)*(100*P1*Fck)^(1/3)*(bw*d))/1000 % SHEAR FORCE CONTRIBUTION
# VRdN = ((k2*Ds)*(bw*d))/1000 % AXIAL FORCE CONTRIBUTION
# VRd = VRdQ + VRdN % TOTAL SHEAR RESISTANCE
# if VRd < ((Vmin+(k2*Ds))*(b*d))/1000
# VRd = ((Vmin+(k2*Ds))*(b*d))/1000
# end
# if VRd>VEd
# disp(‘Since VRd > VEd’)
# disp(‘NO SHEAR REINFORCEMENT REQUIRED, PROVIDE NOMINAL LINKS’)
# else
# if VRd<VEd
# disp(‘Since  VRd < VEd’)
# disp(‘SHEAR REINFORCEMENT REQUIRED, CALCULATE COMPRESSION STRUT CAPACITY’)
# disp(‘Assume strut angle (thetha) = 21.8 deg, cot(thetha)= 2.5’)
# thetha = 21.8
# V1 = 0.6*(1-(Fck/250))
# disp(‘Design compressive strength of concrete (fcd) (N/mm^2)’)
# fcd = 0.567*Fck
# z = 0.9*d
# disp(‘Maximum capacity of compression strut (KN)’)
# VRDmax = ((b*z*V1*fcd)/(2.9))/1000
# if VRDmax > VEd
# disp(‘Since VRDmax > VEd’)
# disp(‘OK! Calculate diameter and spacing of links’)
# ASMINlinks_to_spacing = ((0.08*sqrt(Fck))/Fyk)*b
# ASlinks_to_spacing = (VEd*1000)/(z*0.87*Fyk*2.5)
# else
# disp(‘Since VRDmax > VEd, it means we need a higher strut angle (beta)’)
# disp(‘By calculating the strut angle’)
# disp(‘Shear stress at the section (N/mm^2)’)
# v = (VEd*1000)/(b*d)
# beta = (0.5)*asind((v)/(0.153*Fck*(1-(Fck/250))))
# if beta>45
# disp(‘Since beta < 45 deg, SECTION INADEQUATE FOR SHEAR, INCREASE DEPTH !!!!!’)
#    else
# disp(‘The ratio of Area of steel/spacing of links’)
# ASlinks_to_spacing = (VEd*1000)/(z*0.87*Fyk*cotd(beta))
# end
# end
# end
# Area_of_legs = input(‘Enter the area of number of legs selected = ‘)
# Spacing = input(‘Enter the spacing = ‘)
# disp(‘CHECK’)
# T = Area_of_legs/Spacing
# if T > ASlinks_to_spacing
# disp(‘Shear reinforcement is ok’)
# else
# disp(‘Increase area of steel, or reduce spacing’)
# end
# end