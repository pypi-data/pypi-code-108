import os
import logging
from os.path import join, dirname, abspath
from vpv.common import get_stage_and_modality, error_dialog, load_yaml, Stage, Modality
from os.path import splitext, isfile, isdir

SCRIPT_DIR = dirname(abspath(__file__))
OPTIONS_DIR = join(SCRIPT_DIR, 'options')
OPTIONS_CONFIG_PATH = os.path.join(OPTIONS_DIR, 'annotation_conf.yaml')
PROCEDURE_METADATA = 'procedure_metadata.yaml'

ANNOTATION_DONE_METADATA_FILE = '.doneList.yaml'


class Annotation(object):
    """
    Records a single manual annotation

    Attributes
    ----------
    looked_at: bool
        Whether an annotator has looked at this term and checked the done box
    """
    def __init__(self, x, y, z, dims, stage):
        self.x = None
        self.y = None
        self.z = None
        self.x_percent = None
        self.y_percent = None
        self.z_percent = None
        self.dims = dims  # x,y,z
        self.set_xyz(x, y, z)
        # self.set_xyz(x, y, z)
        self.stage = stage
        self._looked_at = False

    @property
    def looked_at(self):
        return self._looked_at

    @looked_at.setter
    def looked_at(self, done):
        self._looked_at = done

    def __getitem__(self, index):
        if index == 0:  # First row of column (dimensions)
            return "{}, {}, {}".format(self.x, self.y, self.z)  # Convert enum member to string for table
        else: # The terms and stages columns
            return self.indexes[index - 1]

    def set_xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.set_percentages()

    def set_percentages(self):
        dims = self.dims
        if None in (self.x, self.y, self.z):  # Annotations at startup. No position when not annotated
            return None, None, None
        self.x_percent = 100.0 / dims[0] * self.x
        self.y_percent = 100.0 / dims[1] * self.y
        self.z_percent = 100.0 / dims[2] * self.z


class ImpcAnnotation(Annotation):
    def __init__(self, x, y, z, emapa_term, name, options, default_option, dims, stage: Stage, order, is_mandatory):
        super(ImpcAnnotation, self).__init__(x, y, z, dims, stage)
        self.term = str(emapa_term)
        self.name = name
        self.options = options
        self.selected_option = default_option
        self.dims = dims
        self.order = order
        self.is_mandatory = is_mandatory
        self.indexes = [self.term, self.selected_option, self.stage]
        self.type = 'emapa'
        # self.category = category


class SpecimenAnnotations(object):
    """
    Associated with a single Volume (specimen) contains multiple Annotation
    
    For testing we're just doing the E15.5 stage. We will have to have multiple stages later and there will need
    to be some way of only allowing one stage of annotation per volume

    """

    def __init__(self, dims: tuple, vol_path: str):
        """
        Parameters
        ----------
        dims: The dimensions of the image being annotated
        vol_path: The original path of the volume being annotated
            The vol_path is used in order to look for associated procedure metadata file
        """
        self.vol_path = vol_path
        self.annotation_dir = splitext(self.vol_path)[0]
        if not isdir(self.annotation_dir):
            self.annotation_dir = None
        self.annotations = []
        self.col_count = 4  # is this needed?
        self.dims = dims
        # self.load_annotation_options() # We don't load annotations until center + stage is selected
        self.index = len(self.annotations)

        # The center where the annotation is taking place
        self.center = None
        # The developmental stage of the embryo being annotated
        self._stage = None

        self.modality = None

        # self.date_of_annotation = None  # Will be set from the annotation gui_load_done_status
        self.saved_xml_fname = None  # Will be set when xml is loaded from file

        self.annotation_date = None

        self.proc_id = None  # The imaging procedure eg IMPC_EOL__002

        self._load_options_and_metadata()
        # self._load_done_status()

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, stage):
        # After setting stage we can then set the avaialble annotiton objects
        self._stage = stage

    def _load_done_status(self):
        """
        Load in the doneList.yaml which specifies which parameters have been loked at. This is used to populate the
        'done' checkboxes, which is just a guide for the user. Has no other effect
        """
        if self.annotation_dir:
            done_file = join(self.annotation_dir, ANNOTATION_DONE_METADATA_FILE)
            if not isfile(done_file):
                return

            done_status = load_yaml(done_file)
            if not done_status:
                return

            self.index = len(self.annotations)  # bodge. Need to reset the annotations iterator

            for ann in self:
                done = done_status.get(ann.term, 'notpresent')

                if done is 'notpresent':
                    logging.warning('Cannot find term in done metadata\n{}'.format(done_file))

                else:
                    ann.looked_at = done

    def _load_options_and_metadata(self):
        """
        The volume has been loaded. Now see if there is an associated annotation folder that will contain the IMPC
        metadata parameter file. Also load in any partially completed xml annotation files.

        """
        if not self.annotation_dir:
            return

        self.metadata_parameter_file = join(self.annotation_dir, PROCEDURE_METADATA)
        
        if not isfile(self.metadata_parameter_file):
            self.metadata_parameter_file = None
            return

        cso = centre_stage_options.opts

        metadata_params = load_yaml(self.metadata_parameter_file)
        if not metadata_params:
            return

        proc_id = metadata_params['procedure_id']

        # Temp fix 030320 to increment procedures to 002 so they vallidate correctly
        proc_id = proc_id.replace('_001', '_002')
        self.proc_id = proc_id

        center_id = metadata_params['centre_id']
        stage_id, modality = get_stage_and_modality(proc_id, center_id)

        self.stage = stage_id
        self.center = center_id
        self.modality = modality

        # Get the procedure parameters for the given center/stage
        try:
            cso['centers'][center_id]['procedures'][proc_id]
        except KeyError:
            logging.error(f'Procedure id {proc_id} not in the annotation_conf')
            return

        center_stage_default_params = cso['centers'][center_id]['procedures'][proc_id]['parameters']

        # opts['centers'][center]['procedures'][proc_id]['parameters'] = self.load_centre_stage_file(param_file_)

        for _, param_info in center_stage_default_params.items():

            try:
                options = centre_stage_options.opts['available_options'][param_info['options']]
            except TypeError as e:
                logging.error('Falied to load annotation parameter file {}'.format(e))
                return

            if param_info['default_option'] not in options:

                logging.error(
                    """Annotation parameter list load error
                    default option: {} not in available options:{}
                    Centre:, stage:{}""".format(param_info['default_option'], options, center_id, stage_id))

                error_dialog(None, 'Annotation options load error', "See log file - 'info/show log'")
                return


            default = param_info['default_option']

            self.add_impc_annotation(None,
                                     None,
                                     None,
                                     param_info['impc_id'],
                                     param_info['name'],
                                     options,
                                     default,
                                     self.stage,
                                     param_info['order'],
                                     param_info['mandatory'],
                                     self.dims
                                     )
        # Sort the list and set the interator index
        self.annotations.sort(key=lambda x: x.order, reverse=True)
        self.index = len(self.annotations)

    def update_annotation(self, term, x, y, z, selected_option: str):
        """
        Update an annotation
        Returns
        -------

        """
        ann = self.get_by_term(term)
        ann.set_xyz(x, y, z)
        # ann.x, ann.y, ann.z = x, y, z
        ann.selected_option = selected_option

    def add_impc_annotation(self, x: int, y:int, z:int, impc_param, name, options, default_option, stage: Stage, order,
                            is_mandatory, dims):
        """
        Add an emap type annotation from available terms on file
        """
        ann = ImpcAnnotation(x, y, z, impc_param, name, options, default_option, dims, stage, order, is_mandatory)
        self.annotations.append(ann)

    def remove(self, row):
        del self.annotations[row]

    def clear(self):
        self.annotations = []
        self.index = 0

    def __getitem__(self, index):
        return self.annotations[index]

    def __len__(self):
        return len(self.annotations)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == 0:
            self.index = len(self.annotations)
            raise StopIteration
        self.index -= 1
        return self.annotations[self.index]

    def get_by_term(self, term: str) -> Annotation:
        for annotation in self:
            if annotation.term == term:
                self.index = len(self.annotations)  # Bodge. How am I supposed to reset index
                return annotation
        self.index = len(self.annotations)
        return False


class CenterStageOptions(object):
    def __init__(self):
        # Add assert for default in options
        try:
            opts = load_yaml(OPTIONS_CONFIG_PATH)
        except OSError:
            logging.warning('could not open the annotations yaml file {}'.format(OPTIONS_CONFIG_PATH))
            raise
        self.opts = opts
        self.available_options = self.opts['available_options']

        # Get the centre/stage-specific parameters

        for centre_id, centre_data in opts['centers'].items():
            for proc_id, proc_data in centre_data['procedures'].items():
                param_file_ = proc_data['file_']

                # now add the parameters from each individual centre/stage file to the main options config
                try:
                    opts['centers'][centre_id]['procedures'][proc_id]['parameters'] = self.load_centre_stage_file(param_file_)
                except KeyError as e:
                    raise

    def load_centre_stage_file(self, yaml_name):
        """
        Load in centrer-specific annotation parameter list
        Parameters
        ----------
        yaml_name: str
            basename of annotation parameter file

        Returns
        -------
        dict


        """
        path = join(OPTIONS_DIR, yaml_name)
        opts = load_yaml(path)

        # Rename the param_1, param_2 keys with IMPC parameter key
        renamed = {}

        for k in list(opts['parameters']):

            new_key = opts['parameters'][k]['impc_id']
            renamed[new_key] = opts['parameters'][k]

        opts['parameters'] = renamed
        return opts['parameters']

    def all_stages(self, center):
        return [x for x in self.opts['centers'][center]['stages'].keys()]

    def all_centers(self):
        return [x for x in self.opts['centers']]

centre_stage_options = CenterStageOptions()
