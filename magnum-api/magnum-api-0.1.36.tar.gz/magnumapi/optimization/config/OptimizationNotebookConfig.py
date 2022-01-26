from dataclasses import dataclass


@dataclass
class OptimizationNotebookConfig:
    """Class for optimization notebook config used for parametrizing notebooks used for optimization.

    Attributes:
       notebook_folder (str): The name of the root folder with the notebook
       notebook_name (str): The name of the notebook
       input_parameters (dict): The dictionary of input notebook parameters. The key is the variable name inside the
       notebook, while the value is the name of the exposed variable from another notebook
       output_parameters (list): The list of output notebook parameters
       input_artefacts (int): A dictionary of input artefacts for a notebook. The key is the path of an artefact for
       the notebook that takes this artefact as an input. The value is the output path from a notebook generating the
       artefact (w.r.t. the root directory).
       output_artefacts (list): The list of output artefacts produced by a given notebook.
    """
    notebook_folder: str
    notebook_name: str
    input_parameters: dict
    output_parameters: list
    input_artefacts: dict
    output_artefacts: list

    def __str__(self):
        return "notebook_folder: %s\n" \
               "notebook_name: %s\n" \
               "input_parameters: %s\n" \
               "output_parameters: %s\n" \
               "input_artefacts: %s\n" \
               "output_artefacts: %s" % (self.notebook_folder,
                                         self.notebook_name,
                                         self.input_parameters,
                                         self.output_parameters,
                                         self.input_artefacts,
                                         self.output_artefacts)
