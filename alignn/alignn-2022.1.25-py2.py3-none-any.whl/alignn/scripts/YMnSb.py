"""Module to predict using a trained model."""
import torch
from jarvis.core.atoms import Atoms
from jarvis.core.graphs import Graph
from alignn.models.alignn import ALIGNN
from jarvis.analysis.structure.spacegroup import Spacegroup3D

device = "cpu"
if torch.cuda.is_available():
    device = torch.device("cuda")
gap_model_path = "/home/knc6/Software/version/alignn/alignn/tests/ALL_DATASETS/MP15_133k/mp133k_formation_energy_per_atom_alignnn/checkpoint_200.pt"

gap_model_path = "/home/knc6/Software/version/alignn/alignn/tests/ALL_DATASETS/JV15_55k/jv_formation_energy_peratom_alignn/checkpoint_300.pt"
model = ALIGNN()
model.load_state_dict(torch.load(gap_model_path, map_location=device)["model"])
model.to(device)
model.eval()


atoms = Atoms.from_poscar("POSCAR")
cvn = Spacegroup3D(atoms).conventional_standard_structure

g, lg = Graph.atom_dgl_multigraph(atoms)
out_data = (
    model([g.to(device), lg.to(device)])
    .detach()
    .cpu()
    .numpy()
    .flatten()
    .tolist()[0]
)
print("original", out_data)

"""
g, lg = Graph.atom_dgl_multigraph(cvn)
out_data = (
    model([g.to(device), lg.to(device)])
    .detach()
    .cpu()
    .numpy()
    .flatten()
    .tolist()[0]
)
print("cvn", out_data)


atoms = atoms.make_supercell([3, 3, 3])
g, lg = Graph.atom_dgl_multigraph(atoms)
out_data = (
    model([g.to(device), lg.to(device)])
    .detach()
    .cpu()
    .numpy()
    .flatten()
    .tolist()[0]
)
print("supercell", out_data)
"""
