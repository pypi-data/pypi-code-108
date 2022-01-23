from acat.adsorption_sites import SlabAdsorptionSites
from ase.io import read, write
import pickle

slab = read('Ni3Pt_111_slab.traj')

sas = SlabAdsorptionSites(slab, surface='fcc111', 
                          allow_6fold=True,
                          composition_effect=True)

for s in sas.site_list:
    print(s)

with open('Ni3Pt_111_sites.pkl', 'wb') as output:
    pickle.dump(sas, output, pickle.HIGHEST_PROTOCOL)       
