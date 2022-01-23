""" This module implements a factory for managing and creating Digital Twins according to Forest Modeling Language 4.0."""

from ml.app_logger import APP_LOGGER
from ml.tools import remove_namespace, check_var_conflict
from ml.ditto_feature import ditto_feature
import sys
import inspect
from ml.parameters import Parameters
from ml.entry import Entry
from ml.thing import Thing
from ml.ml40.roles.servives.service import Service
from ml.ml40.roles.hmis.app import App
from ml.ml40.roles.hmis.dashboard import Dashboard
from ml.ml40.roles.hmis.machine_ui import MachineUI
from ml.ml40.roles.hmis.hmd import HMD
from ml.ml40.roles.hmis.hmi import HMI
from ml.ml40.roles.dts.handheld_devices.handheld_device import HandheldDevice
from ml.ml40.roles.dts.machines.machine import Machine
from ml.ml40.roles.dts.parts.crane import Crane
from ml.ml40.roles.dts.parts.part import Part
from ml.ml40.roles.dts.parts.engine import Engine
from ml.ml40.roles.dts.parts.scale import Scale
from ml.ml40.roles.dts.parts.tank import Tank
from ml.ml40.roles.dts.persons.machine_operator import MachineOperator
from ml.ml40.roles.dts.persons.person import Person
from ml.ml40.roles.dts.sensors.sensor import Sensor
from ml.ml40.roles.dts.sensors.air_sensor import AirSensor
from ml.ml40.roles.dts.sensors.soil_sensor import SoilSensor
from ml.ml40.roles.dts.sites.site import Site
from ml.ml40.roles.dts.ways.way import Way

from ml.fml40.roles.dts.handheld_devices.brushcutter import Brushcutter
from ml.fml40.roles.dts.handheld_devices.chainsaw import Chainsaw
from ml.fml40.roles.dts.machines.forest_machine import ForestMachine
from ml.fml40.roles.dts.machines.forwarder import Forwarder
from ml.fml40.roles.dts.machines.harvester import Harvester
from ml.fml40.roles.dts.machines.log_truck import LogTruck
from ml.fml40.roles.dts.machines.mini_tractor import MiniTractor
from ml.fml40.roles.dts.machines.skidder import Skidder
from ml.fml40.roles.dts.machines.wheel_loader import WheelLoader
from ml.fml40.roles.dts.parts.grabber import Grabber
from ml.fml40.roles.dts.parts.harvesting_head import HarvestingHead
from ml.fml40.roles.dts.parts.log_loading_area import LogLoadingArea
from ml.fml40.roles.dts.parts.saw import Saw
from ml.fml40.roles.dts.parts.stacking_shield import StackingShield
from ml.fml40.roles.dts.parts.winch import Winch
from ml.fml40.roles.dts.persons.forest_owner import ForestOwner
from ml.fml40.roles.dts.persons.forest_worker import ForestWorker
from ml.fml40.roles.dts.persons.mini_tractor_operator import MiniTractorOperator
from ml.fml40.roles.dts.persons.skidder_operator import SkidderOperator
from ml.fml40.roles.dts.sensors.vitality_sensor import VitalitySensor
from ml.fml40.roles.dts.sensors.barkbeetle_sensor import BarkbeetleSensor
from ml.fml40.roles.dts.sites.forest_enterprise import ForestEnterprise
from ml.fml40.roles.dts.sites.hauler import Hauler
from ml.fml40.roles.dts.sites.mill.mill import Mill
from ml.fml40.roles.dts.sites.mill.papermill import Papermill
from ml.fml40.roles.dts.sites.mill.sawmill import Sawmill
from ml.fml40.roles.dts.woods.wood import Wood
from ml.fml40.roles.dts.woods.stem_segment import StemSegment
from ml.fml40.roles.dts.woods.wood_pile import WoodPile
from ml.fml40.roles.dts.forest.forest import Forest
from ml.fml40.roles.dts.forest.forest_segment import ForestSegment
from ml.fml40.roles.dts.forest.tree import Tree

from ml.mml40.roles.dts.parts.cantilever import Cantilever
from ml.mml40.roles.dts.sensors.strain_gauge import StrainGauge

from ml.ml40.features.properties.associations.association import Association
from ml.ml40.features.properties.associations.composite import Composite
from ml.ml40.features.properties.property import Property
from ml.ml40.features.properties.associations.shared import Shared
from ml.ml40.features.properties.values.address import Address
from ml.ml40.features.properties.values.count import Count
from ml.ml40.features.properties.values.dimensions import Dimensions
from ml.ml40.features.properties.values.distance import Distance
from ml.ml40.features.properties.values.expansion_length import ExpansionLength
from ml.ml40.features.properties.values.force import Force
from ml.ml40.features.properties.values.generic_property import GenericProperty
from ml.ml40.features.properties.values.last_service_check import LastServiceCheck
from ml.ml40.features.properties.values.lot import Lot
from ml.ml40.features.properties.values.lift import Lift
from ml.ml40.features.properties.values.liquid_filling_level import LiquidFillingLevel
from ml.ml40.features.properties.values.location import Location
from ml.ml40.features.properties.values.moisture import Moisture
from ml.ml40.features.properties.values.operating_hours import OperatingHours
from ml.ml40.features.properties.values.orientation_rpy import OrientationRPY
from ml.ml40.features.properties.values.personal_name import PersonalName
from ml.ml40.features.properties.values.rotational_speed import RotationalSpeed
from ml.ml40.features.properties.values.route import Route
from ml.ml40.features.properties.values.switching_stage import SwitchingStage
from ml.ml40.features.properties.values.temperature import Temperature
from ml.ml40.features.properties.values.time_slot import TimeSlot
from ml.ml40.features.properties.values.weight import Weight
from ml.ml40.features.properties.values.documents.jobs.generic_job import GenericJob
from ml.ml40.features.properties.values.documents.jobs.job import Job
from ml.ml40.features.properties.values.documents.jobs.job_list import JobList
from ml.ml40.features.properties.values.documents.jobs.job_status import JobStatus
from ml.ml40.features.properties.values.documents.reports.report import Report
from ml.ml40.features.properties.values.documents.reports.production_data import ProductionData

from ml.fml40.features.properties.values.abstract_inventory import AbstractInventory
from ml.fml40.features.properties.values.assortment import Assortment
from ml.fml40.features.properties.values.dbh import DBH
from ml.fml40.features.properties.values.fell_indicator import FellIndicator
from ml.fml40.features.properties.values.felling_period import FellingPeriod
from ml.fml40.features.properties.values.harvesting_parameter import HarvestingParameters
from ml.fml40.features.properties.values.harvested_volume import HarvestedVolume
from ml.fml40.features.properties.values.interfering_branches import InterferingBranches
from ml.fml40.features.properties.values.inventory_data import InventoryData
from ml.fml40.features.properties.values.overhang import Overhang
from ml.fml40.features.properties.values.stem_segment_properties import StemSegmentProperties
from ml.fml40.features.properties.values.thickness_class import ThicknessClass
from ml.fml40.features.properties.values.tilt import Tilt
from ml.fml40.features.properties.values.tree_data import TreeData
from ml.fml40.features.properties.values.tree_type import TreeType
from ml.fml40.features.properties.values.vitality_status import VitalityStatus
from ml.fml40.features.properties.values.wood_quality import WoodQuality

from ml.fml40.features.properties.values.documents.jobs.felling_job import FellingJob
from ml.fml40.features.properties.values.documents.jobs.fellung_support_job import FellingSupportJob
from ml.fml40.features.properties.values.documents.jobs.forwarding_job import ForwardingJob
from ml.fml40.features.properties.values.documents.jobs.log_transportation_job import LogTransportationJob

from ml.fml40.features.properties.values.documents.reports.afforestation_suggestion import AfforestationSuggestion
from ml.fml40.features.properties.values.documents.reports.felling_tool import FellingTool
from ml.fml40.features.properties.values.documents.reports.log_measurement import LogMeasurement
from ml.fml40.features.properties.values.documents.reports.log_transportation_report import LogTransportationReport
from ml.fml40.features.properties.values.documents.reports.map_data import MapData
from ml.fml40.features.properties.values.documents.reports.moisture_prediction_report import MoisturePredictionReport
from ml.fml40.features.properties.values.documents.reports.passability_report import PassabilityReport
from ml.fml40.features.properties.values.documents.reports.soil_moisture_measurement import SoilMoistureMeasurement

from ml.mml40.features.properties.values.Displacement import Displacement
from ml.mml40.features.properties.values.GeometryProperties import GeometryProperties
from ml.mml40.features.properties.values.LoadAlarm import LoadAlarm
from ml.mml40.features.properties.values.MaterialProperties import MaterialProperties
from ml.mml40.features.properties.values.Stretch import Stretch


from ml.ml40.features.functionalities.accepts_jobs import AcceptsJobs
from ml.ml40.features.functionalities.accepts_reports import AcceptsReports
from ml.ml40.features.functionalities.clears_jobs import ClearsJobs
from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.functionalities.manages_jobs import ManagesJobs
from ml.ml40.features.functionalities.plans_routes import PlansRoutes
from ml.ml40.features.functionalities.provides_map_data import ProvidesMapData
from ml.ml40.features.functionalities.provides_operational_data import ProvidesOperationalData
from ml.ml40.features.functionalities.renders import Renders

from ml.fml40.features.functionalities.accepts_felling_jobs import AcceptsFellingJobs
from ml.fml40.features.functionalities.accepts_felling_support_jobs import AcceptsFellingSupportJobs
from ml.fml40.features.functionalities.accepts_forwarding_jobs import AcceptsForwardingJobs
from ml.fml40.features.functionalities.accepts_log_measurements import AcceptsLogMeasurements
from ml.fml40.features.functionalities.accepts_log_transportaition_jobs import AcceptsLogTransportationJobs
from ml.fml40.features.functionalities.accepts_moisture_measurement import AcceptsMoistureMeasurement
from ml.fml40.features.functionalities.accepts_move_commands import AcceptsMoveCommands
from ml.fml40.features.functionalities.accepts_passability_report import AcceptsPassabilityReport
from ml.fml40.features.functionalities.accepts_proximity_alert import AcceptsProximityAlert
from ml.fml40.features.functionalities.accepts_shield_commands import AcceptsShieldCommands
from ml.fml40.features.functionalities.accepts_single_tree_felling_jobs import AcceptsSingleTreeFellingJobs
from ml.fml40.features.functionalities.accepts_winch_command import AcceptsWinchCommands
from ml.fml40.features.functionalities.classifies_tree_species import ClassifiesTreeSpecies
from ml.fml40.features.functionalities.cuts import Cuts
from ml.fml40.features.functionalities.determines_passability import DeterminesPassability
from ml.fml40.features.functionalities.displays_health_alarms import DisplaysHealthAlarms
from ml.fml40.features.functionalities.evaluates_stand_attributes import EvaluatesStandAttributes
from ml.fml40.features.functionalities.fells import Fells
from ml.fml40.features.functionalities.forest_planning_evaluation import ForestPlanningEvaluation
from ml.fml40.features.functionalities.forwards import Forwards
from ml.fml40.features.functionalities.generates_afforestation_suggestions import GeneratesAfforestationSuggestions
from ml.fml40.features.functionalities.generates_felling_suggestions import GeneratesFellingSuggestions
from ml.fml40.features.functionalities.grabs import Grabs
from ml.fml40.features.functionalities.harvests import Harvests
from ml.fml40.features.functionalities.measure_wood import MeasuresWood
from ml.fml40.features.functionalities.monitor_health_status import MonitorsHealthStatus
from ml.fml40.features.functionalities.provides_moisture_prediction import ProvidesMoisturePrediction
from ml.fml40.features.functionalities.provides_passability_information import ProvidesPassabilityInformation
from ml.fml40.features.functionalities.provides_production_data import ProvidesProductionData
from ml.fml40.features.functionalities.provides_tree_data import ProvidesTreeData
from ml.fml40.features.functionalities.provides_weather_data import ProvidesWeatherData
from ml.fml40.features.functionalities.simulates_tree_growth import SimulatesTreeGrowth
from ml.fml40.features.functionalities.supports_felling import SupportsFelling
from ml.fml40.features.functionalities.transports_logs import TransportsLogs

from ml.mml40.features.functionalities.CantileverConfigure import CantileverConfigure
from ml.mml40.features.functionalities.ProvidesDisplacementData import ProvidesDisplacementData
from ml.mml40.features.functionalities.ProvidesForceData import ProvidesForceData
from ml.mml40.features.functionalities.ProvidesStretchData import ProvidesStretchData
# TODO: Get rid of this global variable
# TODO: automatically get all classes in module
DT_FACTORY = {}

clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
for member in clsmembers:
    DT_FACTORY[member[0]] = member[1]


def build_sub_features(feature_ins, feature):
    """
    Instantiates and inserts ml40/fml40 sub features object into feature instance

    :param feature_ins: ml40/fml40 feature instance, which has a sub feature to be built
    :type feature_ins: object
    :param feature: ml40/fml40 feature containing subFeatures
    :type feature: dict

    """
    sub_features = feature.get("subFeatures", [])
    for sub_f in sub_features:
        sub_f_name = sub_f.get("name")
        if sub_f_name is None:
            sub_f_name = sub_f.get("identifier")
        if sub_f_name is None:
            sub_f_name = sub_f.get("class")
        _class_name = sub_f.get("class", "")
        sub_f_obj = DT_FACTORY.get(remove_namespace(_class_name), None)
        if sub_f_obj is None:
            APP_LOGGER.critical("Subfeature: %s is missing" % _class_name)
        else:
            APP_LOGGER.info("Adding subfeature: %s" % _class_name)
            sub_f_instance = sub_f_obj()
            for key in sub_f.keys():
                if key == "targets":
                    build_sub_thing(sub_f_instance, sub_f)
                elif key == "subFeatures":
                    build_sub_features(sub_f_instance, sub_f)
                else:
                    setattr(sub_f_instance, key, sub_f[key])
            sub_f_instance.parent = feature_ins
            feature_ins.subFeatures[sub_f_name] = sub_f_instance


def build_sub_thing(feature_ins, feature):
    """
    Instantiates and inserts sub thing object into a feature instance

    :param feature_ins: ml40/fml40 feature instance
    :type feature_ins: object
    :param feature: ml40/fml40 feature, which contains a sub thing
    :type feature: dict

    """
    json_sub_things = feature.get("targets", [])
    for json_sub_thing in json_sub_things:
        sub_thing_ref = create_thing(model_json={"attributes": json_sub_thing})
        sub_thing_name = json_sub_thing.get("name", None)
        feature_ins.targets[sub_thing_name] = sub_thing_ref
        sub_thing_ref.parent = feature_ins


def build(thing, model):
    """
    Builds a ml40 thing instance

    :param thing: ml40 thing instance
    :type thing: object
    :param model: model in ml40 thing JSON
    :type model: dict

    """
    attributes = model.get("attributes", None)
    ditto_features = model.get("features", None)

    if not isinstance(model, dict):
        # TODO JSON Schema
        APP_LOGGER.critical("model is no valid JSON")
        return
    roles = attributes.get("roles", [])
    for role in roles:
        role_instance = build_role(role)
        role_instance.parent = thing
        thing.roles[role.get("class")] = role_instance

    json_features = attributes.get("features", [])
    for feature in json_features:
        feature_ins = build_feature(feature=feature)
        feature_ins.parent = thing
        thing.features[feature.get("class")] = feature_ins

    if ditto_features is not None:
        build_ditto_features(thing, ditto_features)


def build_ditto_features(thing, ditto_features):
    for id in ditto_features.keys():
        for key in ditto_features[id]["properties"]:
            ditto_f = ditto_feature(id=id, key=key, value=ditto_features[id]["properties"][key])
        thing.ditto_features[ditto_f.id] = ditto_f


def build_role(role):
    """
     Instantiates and inserts a ml40/fml40 role object into a ml40 thing instance

    :param role: ml40/fml40 role
    :type role: dict

    """
    role_class_name = role.get("class", "")
    role_obj = DT_FACTORY.get(remove_namespace(role_class_name), None)
    if role_obj is None:
        APP_LOGGER.critical("Roles: %s is missing" % role_class_name)
        role_instance = None
    else:
        APP_LOGGER.info("Adding roles: %s" % role_class_name)
        role_instance = role_obj()
    return role_instance


def build_feature(feature):
    """
     Instantiates and inserts a ml40/fml40 feature object in a ml40 thing instance

    :param feature: ml40/fml40 feature
    :type feature: dict

    """
    feature_class_name = feature.get("class", "")
    feature_obj = DT_FACTORY.get(remove_namespace(feature_class_name), None)

    if feature_obj is None:
        APP_LOGGER.critical("Feature: %s is missing" % feature_class_name)
        feature_instance = None
    else:
        APP_LOGGER.info("Adding feature: %s" % feature_class_name)
        feature_instance = feature_obj()
        for key in feature.keys():
            if key == "class":
                continue
            if key == "targets":
                build_sub_thing(feature_instance, feature)
            elif key == "subFeatures":
                build_sub_features(feature_instance, feature)
            else:
                setattr(feature_instance, check_var_conflict(key), feature[key])
    return feature_instance


def add_function_impl_obj(thing, impl_obj, feature_name, **kwargs):
    """
    Adds user-specific implemented object to a thing instance

    :param thing: ml40 thing instance
    :type thing: object
    :param impl_obj: ml40/fml40 feature instance
    :type impl_obj: object
    :param feature_name: class name of a ml40/fml40 feature
    :type feature_name: str


    """
    feature = thing.features.get(feature_name, None)
    if feature is None:
        ### Check if it is a feature of a subthing
        if thing.features.get("ml40::Composite", None) is not None:
            subthings = thing.features["ml40::Composite"].targets
            for i in subthings.keys():
                feature = subthings[i].features.get(feature_name, None)
                if feature is not None:
                    break
    if feature is None:
        if thing.features.get("ml40::Shared", None) is not None:
            subthings = thing.features["ml40::Shared"].targets
            for i in subthings.keys():
                feature = subthings[i].features.get(feature_name, None)
                if feature is not None:
                    break
    if feature is None:
        APP_LOGGER.critical(
            "Functionality %s is not one of the build-in functionalities" % feature_name
        )
    else:
        APP_LOGGER.info("Implementation object is added into the functionality %s" % feature_name)
        impl_ins = impl_obj(**kwargs)
        impl_ins.class_name = feature_name
        thing.features[feature_name] = impl_ins


def create_thing(
        model_json,
        oauth2_secret="",
        grant_type="client_credentials",
        username=None,
        password=None,
        is_repository=False,
        is_broker=False,
        is_broker_rest=False,
        parameters=Parameters()
):
    attributes = model_json.get("attributes")
    if attributes is None:
        APP_LOGGER.error("Attributes are empty")

    identifier = model_json.get("thingId", "")
    name = attributes.get("name", "")
    APP_LOGGER.info("Build digital twin {} with id {}".format(name, identifier))
    entry_ref = Entry(identifier, name)
    build(entry_ref, model_json)
    return Thing(
        entry=entry_ref,
        oauth2_secret=oauth2_secret,
        grant_type=grant_type,
        username=username,
        password=password,
        is_repository=is_repository,
        is_broker=is_broker,
        is_broker_rest=is_broker_rest,
        parameters=parameters
    )


def _create_thing(model, grant_type="password",
                 secret="", username=None, password=None,
                 is_broker_rest=False, is_broker=False, is_repo=False, is_stanford2010=False,
                 is_stanford2010_sync=False,
                 stanford2010_sync_freq=None, stanford2010_path=None, is_database=False,
                 database_conf=None, database_file=None):
    """
    Creates and launches a thing which connects to the S3I

    :param model: edge-device or S³I Repository specified JSON entry
    :type model: dict
    :param grant_type: grant type of OAuth2.0, which can be password or client_credentials
    :type grant_type: str
    :param secret: secret of a thing
    :type secret: str
    :param username: username, if the grant_type is set as password, the username is required
    :type username: str
    :param password: password, if the grant_type is set as password, the password is required
    :type password: str
    :param is_broker: whether broker interface is enabled in the ml40::thing instance
    :type is_broker: bool
    :param is_broker_rest: whether the broker interface uses the HTTP REST
    :type is_broker_rest: bool
    :param is_repo: whether the repository interface is enabled in the ml40::thing instance
    :type is_repo: bool

    :returns: ml40::thing instance
    :rtype: object

    """
    attributes = model.get("attributes", None)
    if attributes is None:
        sys.exit("attributes are none")
    thing_type = attributes.get("class", "")
    thing_type = remove_namespace(thing_type)
    thing_name = attributes.get("name", "")
    APP_LOGGER.info("Build digital twin {} with id {}".format(thing_name, model.get("thingId", "")))

    _thing = DT_FACTORY.get(thing_type)

    thing_ref = _thing(
        model=model,
        grant_type=grant_type,
        client_secret=secret,
        username=username,
        password=password,
        is_broker_rest=is_broker_rest,
        is_broker=is_broker,
        is_repo=is_repo,
        is_stanford2010=is_stanford2010,
        stanford2010_sync_freq=stanford2010_sync_freq,
        is_stanford2010_sync=is_stanford2010_sync,
        stanford2010_path=stanford2010_path,
        is_database=is_database,
        database_file=database_file,
    )
    build(thing_ref, model)

    return thing_ref
