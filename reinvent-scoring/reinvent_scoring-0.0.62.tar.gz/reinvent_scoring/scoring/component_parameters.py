from dataclasses import dataclass


@dataclass
class ComponentParameters:
    component_type: str
    name: str
    weight: float
    #TODO: remove smiles and model_path
    model_path: str = None
    smiles: str = None
    specific_parameters: dict = None
