import sys
import time

import colorlog
import atexit
from uuid import uuid4
from functools import lru_cache
from weakref import WeakSet

from .SIMULTAN.Project.Services import IAuthenticationService
from .ParameterStructure import Projects
from .SIMULTAN.Project.Project import ExtendedProjectData
from .SIMULTAN.Project.ProjectLoaders import ZipProjectIO
from .SIMULTAN.UI.Services import ServicesProvider

# from .SIMULTAN.DataExchange import ComponentGeometryExchange
# from .ParameterStructure.Component import ComponentManagerType
from .ParameterStructure.Users import *
from .GeometryViewer import TemporaryGeometryViewerInstance
from .GeometryViewer.Service import GeometryViewerService
from .GeometryViewer.Model import *
from .GeometryViewer.IO import SimGeoIO
from .GeometryViewer import IGeometryViewerService
from System.Security import SecureString
from System.IO import FileInfo
from System import ArgumentOutOfRangeException
from .ParameterStructure.Components import SimComponent
from .ParameterStructure.Components import SimSlot, SimSlotBase, SimChildComponentEntry, ComponentUtils
from .ParameterStructure.Algorithms.Components import ComponentManagement
# from .ParameterStructure.Algorithms.Components import ComponentMapping
# from .ParameterStructure.Parameters import SimParameter
from .ParameterStructure.Values import SimMultiValueBigTable
# from .ParameterStructure.Assets import ContainedResourceFileEntry


ProjectData = Projects.ProjectData

# from .utils import *
# from .geo_default_types import *

# from .geometry import GeometryModel


logger = colorlog.getLogger('PySimultan')


class IAuthenticationServiceNew(IAuthenticationService):
    __namespace__ = "authenticate_namespace"

    user_name = None
    password = None

    def Authenticate(self, user_manager, project_file):
        # user_name = 'admin'
        # password = 'admin'

        sec_str = SecureString()
        for char in self.password:
            sec_str.AppendChar(char)

        user = user_manager.Authenticate(self.user_name, sec_str)

        user_manager.CurrentUser = user.Item1
        user_manager.EncryptionKey = user.Item2

        return user.Item1


data_models = WeakSet()


class DataModel:

    def __new__(cls, *args, **kwargs):

        instance = super().__new__(cls)

        try:
            data_models.add(instance)
        except Exception as e:
            logger.error(f'Error adding instance {instance} to data_models: {e}')
        return instance

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self.user_name = kwargs.get('user_name', 'admin')
        self.password = kwargs.get('password', 'admin')

        atexit.register(self.cleanup)

        self.id = uuid4()
        self.data = None
        self._project_data_manager = None
        self._user = None
        self._project = None
        self._zip_loader = None

        self.project_path = kwargs.get('project_path', None)

        self.service_provider = ServicesProvider()

        self.i_aut_service = IAuthenticationServiceNew
        self.i_aut_service.user_name = self.user_name
        self.i_aut_service.password = self.password

        # self.i_aut_service = create_IAuthenticationService(self.user_name, self.password)
        self.service_provider.AddService[IAuthenticationService](self.i_aut_service())

        self.serv = GeometryViewerService([], self.service_provider)

        self.service_provider.AddService[IGeometryViewerService](self.serv)

        self.exch = self.project.AllProjectDataManagers.GeometryCommunicator
        self.exch.ModelStore = self.serv
        self.inst = TemporaryGeometryViewerInstance(self.exch)
        self.resources = {}
        self.models_dict = {}

        if self.project_data_manager.AssetManager.Resources.__len__() > 0:
            for resource in self.project_data_manager.AssetManager.Resources:
                if resource is None:
                    continue
                self.resources[resource.Key] = resource
                self.models_dict[resource.Key] = None
                current_full_path = resource.CurrentFullPath
                if current_full_path == '?':
                    continue

                file_info = FileInfo(resource.CurrentFullPath)

                if file_info.Extension == '.simgeo':
                    model = SimGeoIO.Load(file_info, self.inst, self.serv)
                    self.models_dict[resource.Key] = model
                    try:
                        self.serv.AddGeometryModel(model)
                    except ArgumentOutOfRangeException as e:
                        logger.warning(f'Error while loading Model: {model} from {model.File}: {e}. Trying reload...')
                        model = SimGeoIO.Load(file_info, self.inst, self.serv)
                        self.models_dict[resource.Key] = model
                        self.serv.AddGeometryModel(model)

        self.ValueFields = self.project_data_manager.ValueManager.Items
        self.import_data_model()

    @property
    def models(self):
        return self.models_dict.values()

    @property
    def project_data_manager(self):
        if (self._project_data_manager) is None and (self.user is not None):
            self._project_data_manager = ExtendedProjectData()
        return self._project_data_manager

    @project_data_manager.setter
    def project_data_manager(self, value):
        self._project_data_manager = value

    @property
    def user(self):
        if self._user is None:
            self._user = SimUserRole.ADMINISTRATOR
        return self._user

    @user.setter
    def user(self, value):
        if value != self._user:
            self.project_data_manager = None
            self._project = None
        self._user = value

    @property
    def project(self):
        if (self._project is None) and (self.project_path is not None) and (self.project_data_manager is not None):
            logger.debug('loading project')
            self.project = ZipProjectIO.Load(FileInfo(self.project_path), self.project_data_manager, self.service_provider)
            exit_code = ZipProjectIO.AuthenticateUserAfterLoading(self.project, self.project_data_manager, bytearray('ThWmZq4t6w9z$C&F', 'ascii'))
            if not exit_code:
                logger.error('Could not open project. Wrong user or password! Exiting program...')
            ZipProjectIO.OpenAfterAuthentication(self.project, self.project_data_manager)
            logger.debug('project loaded successfull')
        return self._project

    @project.setter
    def project(self, value):
        self._project = value

    def get_typed_data(self, template_parser, create_all=False):

        template_parser._create_all = create_all
        template_parser.current_data_model = self

        for cls in template_parser.template_classes.values():
            if create_all:
                cls._create_all = True
            else:
                cls._create_all = False

        data = []

        for item in self.data.Items:
            logger.info(f'Creating python object for: {item.Name}')
            new_comp = template_parser.create_python_object(item)

            try:
                if create_all:
                    try:
                        _ = new_comp.contained_components
                    except AttributeError:
                        pass

                    try:
                        _ = new_comp.contained_parameters
                    except AttributeError:
                        pass

                    try:
                        _ = new_comp.referenced_components
                    except AttributeError:
                        pass

            except Exception as e:
                logger.error(f'Could create all sub-components for {new_comp.name}:\n{e}')
            data.append(new_comp)

        logger.info('\n\nType info: \n----------------------------------')
        logger.info(f'created {data.__len__()} top level instances')
        for cls in set(template_parser.template_classes.values()):
            if hasattr(cls, 'cls_instances'):
                logger.info(f'created {cls.cls_instances.__len__()} instances of type {cls.__name__}')
        return data

    def import_data_model(self):
        self.data = self.project_data_manager.Components
        self.data.set_EnableAsyncUpdates(False)

        return self.data

    @lru_cache(maxsize=None)
    def get_geo_instance(self, file_id, type, id):
        geo_model = self.models[file_id]
        objects = getattr(geo_model.Geometry, type)

        return next((x for x in objects.Items if x.Id == id), None)

    def add_component(self, component: SimComponent):
        self.data.Add(component)

    def save(self):
        ZipProjectIO.Save(self.project, False)

    def cleanup(self):
        """
        Close and cleanup project
        """
        logger.info('closing project...')
        try:
            if self._project is not None:
                if self._project.IsOpened:
                    ZipProjectIO.Close(self._project, False, True)
                if self._project.IsLoaded:
                    ZipProjectIO.Unload(self._project)
        except Exception as e:
            pass

    # def create_new_component(self):
    #
    #     ref_comp = self.data.Items[0]
    #
    #     new_comp = SimComponent()
    #     new_comp.Name = 'Test'
    #
    #     new_param = SimParameter('test_param', 'Unicorn', 15.268)
    #     new_comp.Parameters.Add(new_param)
    #
    #     sub_new_comp = SimComponent()
    #     sub_new_comp.CurrentSlot = SimSlotBase(ComponentUtils.COMP_SLOT_AREAS)
    #     sub_new_comp.Name = 'SubTest'
    #
    #     entry = SimChildComponentEntry(SimSlot(SimSlotBase(ComponentUtils.COMP_SLOT_AREAS), '15'),
    #                                    sub_new_comp)
    #     new_comp.Components.Add(entry)
    #
    #     slot = SimSlot(ref_comp.CurrentSlot, '11')
    #     ComponentManagement.AddReferencedComponentSlot(new_comp, slot, self.user)
    #     ComponentManagement.AddReferencedComponent(new_comp, slot, ref_comp, self.user)
    #
    #     self.add_component(new_comp)
    #     self.save()
    #
    #     return new_comp

    def add_component_reference(self, comp: SimComponent, ref_comp: SimComponent, slot_extension: str, slot_name: str):

        slot = SimSlot(slot_name, str(slot_extension))
        ComponentManagement.AddReferencedComponentSlot(comp, slot, self.user)
        ComponentManagement.AddReferencedComponent(comp, slot, ref_comp, self.user)

    def add_new_geometry_model(self, file_name: str, model_name: str = None, return_resource=False):
        """
        Create and add a new geometry model
        :param file_name: name of the created .simgeo file
        :param model_name: name of the geometry model
        :param return_resource: return the resource
        :return: GeometryViewer.Model.GeometryModel, geo_resource
        """
        geo_resource = self.add_geometry_resource(file_name)
        file_info = FileInfo(geo_resource.CurrentFullPath)
        try:
            model = SimGeoIO.Load(file_info, self.inst, self.serv)
            self.models_dict[geo_resource.Key] = model
            self.serv.AddGeometryModel(model)
        except ArgumentOutOfRangeException as e:
            logger.warning(f'Error while loading Model: {model} from {model.File}: {e}. Trying reload...')
            model = SimGeoIO.Load(file_info, self.inst, self.serv)
            self.models_dict[geo_resource.Key] = model
            self.serv.AddGeometryModel(model)

        if model_name is not None:
            model.Name = model_name

        if return_resource:
            return model, geo_resource
        else:
            return model

    def add_geometry_resource(self, model_name: str):
        """
        Add / create new geometry resource (.simgeo file)
        :param model_name: name of the new .simgeo file without file extension; Example: 'new_model'
        """
        self.service_provider.GetService[IGeometryViewerService]()
        new_resource = self.project.AddEmptyGeometryResource(self.project.ProjectUnpackFolder, model_name, self.service_provider)

        return new_resource

    def add_resource(self, filename: str):
        return self.project.CopyResourceAsContainedFileEntry(FileInfo(filename), self.project.ProjectUnpackFolder)

    def add_table(self, table: SimMultiValueBigTable):
        self.project_data_manager.ValueManager.Add(table)

    def __del__(self):
        self.cleanup()


# if __name__ == '__main__':
#
#     # create example templates
#     templates = create_example_template_bim_bestand_network()
#
#     # write the example templates to a file:
#     with open('example_templates.yml', mode='w') as f_obj:
#         yaml.dump(templates, f_obj)
#
#     # load the example templates:
#     templates = load_templates('example_templates.yml')
#
#     # create classes from the templates:
#     template_classes = create_template_classes(templates)
#
#     simultan_components = create_example_simultan_components(templates, n=5)
#
#     simultan_components = class_type_simultan_components(simultan_components, template_classes)
#
#     # the simultan components are now of the type which is defined in the templates
#     print(simultan_components)
#
#     # the class typed components still keep all methods and attributes from simultan:
#     print(simultan_components[0].simultan_method())
#
#     # and the class typed components have the new defined method python_spec_func:
#     simultan_components[10].python_spec_func()
