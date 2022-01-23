from ase.formula import Formula
from ase.io import read, write
from ase.build import molecule
from ase import Atoms


# Adsorbate elements must be different from catalyst elements
adsorbate_elements = ['H', 'C', 'N', 'O', 'F', 'S', 'Cl']

# Adsorbate height on different sites
site_heights = {'ontop': 1.8, 
                'bridge': 1.5, 
                'shortbridge': 1.5,
                'longbridge': 1.5,
                'fcc': 1.3, 
                'hcp': 1.3,
                '3fold': 1.3, 
                '4fold': 1.3,
                '5fold': 1.5,
                '6fold': 0.,}

# The default adsorbate list already contains most common adsorbate 
# species. If you want to add any species, make sure you always sort 
# the indices of the atoms in the same order as the symbolm, by adding 
# entries in the adsorbate_molecule function. 

# Adsorbate nomenclature: first element always starts from bonded index 
# or the bonded element with smaller atomic number if multi-dentate.
# Hydrogen is not considered as a bonding element except for H and H2.
# The hydrogens should always follow the atom that they bond to.
# This is different from ASE's nomenclature, e.g. water should be 'OH2',
# hydrogen peroxide should be 'OHOH'

# Monodentate (vertical)                            
monodentate_adsorbate_list = ['H','C','N','O','S',
                              'CH','NH','OH','SH','CO','NO','CN','CS','NS',
                              'CH2','NH2','OH2','SH2','COH','NOH',
                              'CH3','NH3','OCH',
                              'OCH2',
                              'OCH3',]

                              # You may want to put some monodentate species here
# Multidentate (lateral)      # as potential multidentate species on rugged surfaces
multidentate_adsorbate_list = ['H2','C2','N2','O2','S2','OS',
                               'CO2','NO2','N2O','O2S','CS2','NS2','CHN','CHO','NHO','COS','C3','O3',
                               'CHOH','CH2O','COOH','CHOO','OHOH',
                               'CH3O','CH2OH','CH3S','CH2CO',
                               'CH3OH','CHOOH','CH3CO',
                               'CH3COOH',
                               'CHCHCHCHCHCH',]

adsorbate_list = monodentate_adsorbate_list + multidentate_adsorbate_list
adsorbate_formulas = {k: ''.join(list(Formula(k))) for k in adsorbate_list}

# Add entries and make your own adsorbate molecules
def adsorbate_molecule(adsorbate):
    # The ase.build.molecule module has many issues.       
    # Adjust positions, angles and indexing for your needs.
    if adsorbate == 'CO':
        ads = molecule(adsorbate)[::-1]
    elif adsorbate == 'C2':
        ads = molecule('C2H2')
        del ads[-2:]
        ads.rotate(90, 'x')
    elif adsorbate in ['H2','N2','O2','S2']:
        ads = molecule(adsorbate)
        ads.rotate(90, 'x')
    elif adsorbate == 'NS':
        ads = molecule('CS')
        ads[0].symbol = 'N'
    elif adsorbate == 'OS':
        ads = molecule('SO')
        ads.rotate(90, 'x')
    elif adsorbate == 'OH2':
        ads = molecule('H2O')
        ads.rotate(180, 'y')
    elif adsorbate == 'CH2':
        ads = molecule('NH2')
        ads[0].symbol = 'C'
        ads.rotate(180, 'y')
    elif adsorbate in ['NH2','SH2']:
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate == 'COH':
        ads = molecule('H2COH')
        del ads[-2:]
        ads.rotate(90, 'y')
    elif adsorbate == 'NOH':
        ads = molecule('H2COH')
        ads[0].symbol = 'N'
        del ads[-2:]
        ads.rotate(90, 'y')
    elif adsorbate == 'CO2':     
        ads = molecule(adsorbate)
        ads.rotate(90, 'x')
    elif adsorbate in ['CS2','N2O']:
        ads = molecule(adsorbate)[[1,0,2]]
        ads.rotate(90, 'x')
    elif adsorbate == 'NS2':
        ads = molecule('CS2')[[1,0,2]]
        ads[0].symbol = 'N'
        ads.rotate(90, 'x')
    elif adsorbate == 'NO2':
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate == 'O2S':
        ads = molecule('SO2')[::-1]
        ads.rotate(180, 'y')
    elif adsorbate == 'CHN':
        ads = molecule('HCN')[[0,2,1]]
        ads.rotate(90, 'x')
    elif adsorbate == 'CHO':
        ads = molecule('HCO')[[0,2,1]] 
    elif adsorbate == 'NHO':
        ads = molecule('HCO')[[0,2,1]]
        ads[0].symbol = 'N'
    elif adsorbate == 'COS':
        ads = molecule('OCS')[[1,0,2]]
        ads.rotate(90, 'x')
    elif adsorbate == 'C3':
        ads = molecule('C3H4_D2d')
        del ads[-4:]
        ads.rotate(90, 'x')
    elif adsorbate == 'O3':
        ads = molecule(adsorbate)[[1,0,2]]
        ads.rotate(180, 'y')
    elif adsorbate == 'CH3':
        ads = molecule('CH3O')[[0,2,3,4]]
        ads.rotate(90, '-x')
    elif adsorbate == 'NH3':
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate == 'OCH2':
        ads = molecule('H2CO')
        ads.rotate(180, 'y')
    elif adsorbate == 'OCH3':
        ads = molecule('CH3O')[[1,0,2,3,4]]
        ads.rotate(90, '-x')
    elif adsorbate == 'CH2O':
        ads = molecule('H2CO')[[1,2,3,0]]
        ads.rotate(90, 'y')
    elif adsorbate in ['CH3O','CH3S']:
        ads = molecule(adsorbate)[[0,2,3,4,1]]
        ads.rotate(30, 'y')
    elif adsorbate == 'CH2CO':
        ads = molecule('H2CCO')[[0,2,3,1,4]]
        ads.rotate(90, 'y')
    elif adsorbate == 'CHOH':
        ads = molecule('H2COH')
        del ads[-1]
        ads = ads[[0,3,1,2]]
    elif adsorbate == 'OHOH':
        ads = molecule('H2O2')[[0,2,1,3]]
    elif adsorbate == 'CH2OH':
        ads = molecule('H2COH')[[0,3,4,1,2]]
    elif adsorbate == 'CH3OH':
        ads = molecule(adsorbate)[[0,2,4,5,1,3]]
        ads.rotate(-30, 'y')
    elif adsorbate == 'CHOOH':
        ads = molecule('HCOOH')[[1,4,2,0,3]]
    elif adsorbate == 'CH3CO':
        ads = molecule(adsorbate)[[0,2,3,4,1,5]]
    elif adsorbate == 'COOH':
        ads = molecule('HCOOH')
        del ads[-1]
        ads = ads[[1,2,0,3]]
        ads.rotate(90, '-x')
        ads.rotate(15, '-y')
    elif adsorbate == 'CHOO':
        ads = molecule('HCOOH')
        del ads[-2]
        ads = ads[[1,3,2,0]]
        ads.rotate(90, 'x')
        ads.rotate(7.5, 'y')
    elif adsorbate == 'CH3COOH':
        ads = molecule('CH3COOH')[[4,5,6,7,0,1,2,3]]
        ads.rotate(180, 'x')
    elif adsorbate == 'CHCHCHCHCHCH':
        ads = molecule('C6H6')[[0,6,1,7,2,8,3,9,4,10,5,11]] 
    elif adsorbate == 'X':
        ads = Atoms('X', positions=[[0, 0, 0]])
    else:
        try:
            ads = molecule(adsorbate)
        except:
            print('Molecule {} is not supported in the database.'.format(adsorbate))
            return 
    return ads

