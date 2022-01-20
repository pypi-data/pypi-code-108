"""
Dataset with format:
variable original name
processor (just as a note)
interface (just as a note)
variable transformed name
value or expression
list of variables in the expression
scenario
time


For an scenario and time
* dictionary of changed name <-> original name
* Look for directly known variables
  - Add to dictionary (transform name to that in the expression)
* Parse expressions, look for variable names
* Transform expressions
* Prepare set of expressions
* Look for variables with known value
* Substitute
"""
from nexinfosys.model_services import State, get_case_study_registry_objects


def preprocess_expressions(state: State):
    """

    :param state:
    :return:
    """

    glb_idx, p_sets, hh, datasets, mappings = get_case_study_registry_objects(state)
    #