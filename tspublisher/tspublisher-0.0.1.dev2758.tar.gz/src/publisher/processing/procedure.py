import os.path
from shutil import copyfile

from publisher.processing.data_sources.asset import convert_files
from publisher.processing.data_sources.overview import get_overview_and_devices
from publisher.processing.data_sources.eula import copy_eula_to_procedure
from publisher.processing.data_sources.organisation import get_organisation_from_channel, get_data_from_channel
from publisher.processing.data_sources.author import get_author_from_overview
from publisher.processing.data_sources.ftrack import get_procedure_details, get_procedure_phase_list, get_phase_data
from publisher.processing.data_sources.step import get_step_data
from publisher.processing.data_sources.thumbnail import update_thumbnails, update_phase_thumbnails, \
    create_phase_thumbnail, create_procedure_thumbnails
from publisher.processing.data_sources.utils import YamlObject
from publisher.processing.models import Procedure, Phase, Channel
from publisher.processing.utils.file import ProcedureFileManager, PhaseFileManager, DeliveryFileManager
import publisher.settings as settings


def create_procedure(procedure_code):

    procedure = Procedure()
    procedure.code = procedure_code

    phase = Phase()
    phase.code = "{0}_010".format(procedure_code)
    procedure.phases.append(phase)

    procedure_files = ProcedureFileManager(procedure)

    create_yaml_file(procedure, procedure_files.procedure_file)
    create_yaml_file(phase, procedure_files.phase_files[0].phase_file)

    return procedure, procedure_files


def create_procedure_from_production(procedure_code):
    procedure, procedure_files = initialize_procedure(procedure_code)

    create_yaml_file(procedure, procedure_files.procedure_file)
    for phase in procedure.phases:
        phase_files = next(pf for pf in procedure_files.phase_files if pf.phase_code == phase.code)
        create_yaml_file(phase, phase_files.phase_file)

    setup_procedure_files(procedure, procedure_files)

    return procedure, procedure_files


def create_phase(procedure_code, phase_code):
    procedure, procedure_files = initialize_procedure(procedure_code)
    for phase in procedure.phases:
        if phase.code == phase_code:
            phase_files = next(pf for pf in procedure_files.phase_files if pf.phase_code == phase.code)
            create_yaml_file(phase, phase_files.phase_file)

    setup_phase_files(procedure, phase_code)

    return procedure, procedure_files


def initialize_procedure(procedure_code):
    procedure = build_procedure_object(procedure_code)
    procedure_files = ProcedureFileManager(procedure)
    load_existing_locales(procedure, procedure_files)

    return procedure, procedure_files


def load_existing_locales(procedure, procedure_files):
    yaml = YamlObject()
    if os.path.exists(procedure_files.procedure_file):
        with open(procedure_files.procedure_file, "r") as yaml_stream:
            existing_procedure = yaml.load(yaml_stream)
        procedure.locales = existing_procedure.get("locales", [])


def initialize_phase(phase_data):
    phase = build_phase_object(phase_data)
    phase_files = PhaseFileManager(phase, phase_data['procedure_code'])

    return phase, phase_files


def initialize_channel(channel_data):
    channel = build_channel_object(channel_data)
    channel_file = os.path.join(settings.CHANNELS_CHECKOUT_DIRECTORY, channel.code + ".yml")

    return channel, channel_file


def build_procedure_object(procedure_code):
    procedure = Procedure()
    procedure.code = procedure_code
    procedure.name, procedure.specialties, procedure.channel, vbs = get_procedure_details(procedure_code)
    procedure.vbs = vbs
    phases_data = get_procedure_phase_list(procedure_code)
    procedure.phases = [build_phase_object(p) for p in phases_data]

    return procedure


def build_phase_object(phase_data):

    phase = Phase()

    phase.procedureCode = phase_data['procedure_code']
    phase.code = phase_data['phase_code']
    phase.name = phase_data['phase_name']
    phase.countryRestriction = ",".join([country for country in phase_data['geo_restrictions']])
    # phase.released_as = phase_data['released_as']
    # phase.vbs = is_vbs(phase_data['vbs'])

    return phase


def build_channel_object(channel_data):
    channel = Channel()
    channel.code = channel_data["code"]
    channel.name = channel_data["name"]
    channel.type = channel_data["type"]
    channel.eula = channel_data["eula"]

    return channel


def build_procedure(procedure_code, build_phases=False, graphics=True,
                    pip_graphics=True, widget_graphics=True, thumbnails=True,
                    step_numbers=True, info_step=True):

    print("-- Updating procedure: %s --" % procedure_code)
    procedure, procedure_files = initialize_procedure(procedure_code)
    procedure.overview, procedure.devices = get_overview_and_devices(procedure_code, procedure_files.asset_directory)

    procedure.organisation = get_organisation_from_channel(procedure.channel)
    procedure.author = get_author_from_overview(procedure.overview)
    procedure.eulaFile = copy_eula_to_procedure(procedure_code, procedure_files.asset_directory)

    if thumbnails:
        update_thumbnails(procedure, procedure_files.asset_directory)

    create_yaml_file(procedure, procedure_files.procedure_file)

    if build_phases:
        for phase in procedure.phases:
            phase_files = next(pf for pf in procedure_files.phase_files if pf.phase_code == phase.code)
            build_phase(phase, phase_files, graphics, pip_graphics, widget_graphics, thumbnails,
                        step_numbers=step_numbers, info_step=info_step, vbs=procedure.vbs)


def build_single_phase(phase_code, graphics=True, pip_graphics=True,
                       widget_graphics=True, thumbnails=True, step_numbers=True,
                       info_step=True, csv_version=None):

    phase_data = get_phase_data(phase_code)
    _, _, _, vbs = get_procedure_details(phase_data['procedure_code'])

    phase, phase_files = initialize_phase(phase_data)

    build_phase(phase, phase_files, graphics, pip_graphics, widget_graphics, thumbnails,
                step_numbers=step_numbers, info_step=info_step, vbs=vbs,
                csv_version=csv_version)


def build_phase(phase, phase_files, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers=True,
                info_step=True, supported_app="touchsurgery", vbs=False, csv_version=None):

    print("-- Updating phase: %s --" % phase.code)
    phase.learnObjectives, phase.testObjectives = get_step_data(phase.code, csv_version)
    phase.phaseDir = phase_files.asset_directory

    phase.supported_app = supported_app
    phase.stepNumbers = step_numbers
    phase.infoStep = info_step
    phase.vbs = vbs

    create_yaml_file(phase, phase_files.phase_file)

    if thumbnails:
        update_phase_thumbnails(phase, phase_files.asset_directory)

    if graphics or widget_graphics or isinstance(pip_graphics, dict):
        convert_files(phase, phase_files.base_directory, graphics, pip_graphics, widget_graphics, vbs, csv_version)


def update_phase_name(phase_code, new_name):
    """Update the procedure's name
    """
    phase_data = get_phase_data(phase_code)

    phase, phase_files = initialize_phase(phase_data)
    phase.name = new_name

    create_yaml_file(phase, phase_files.phase_file)


def build_channel(channel_data):
    channel, channel_file = initialize_channel(channel_data)
    create_yaml_file(channel, channel_file)
    return channel, channel_file


def update_channel(code, updates):
    channel_data = get_data_from_channel(code)
    for key in updates:
        channel_data[key] = updates[key]
    build_channel(channel_data)


def setup_templates(procedure_files):
    source_overview = os.path.join(settings.TEMPLATE_DIRECTORY, "overview.yml")
    source_devices = os.path.join(settings.TEMPLATE_DIRECTORY, "devices.yml")
    dest_overview = os.path.join(procedure_files.overview_directory, "overview.yml")
    dest_devices = os.path.join(procedure_files.devices_directory, "devices.yml")
    copyfile(source_overview, dest_overview)
    copyfile(source_devices, dest_devices)


def setup_procedure_files(procedure, procedure_files):
    setup_templates(procedure_files)
    if os.path.isdir(settings.BASE_DATA_DIR):
        delivery_files = DeliveryFileManager(procedure.code, procedure.phases, procedure.vbs)
        create_procedure_thumbnails(delivery_files.proc_thumbnail_directory, None, None)
        for phase in delivery_files.phase_directories:
            create_phase_thumbnail(delivery_files.phase_directories[phase]["thumbnail_directory"], None)


def setup_phase_files(procedure, phase_code):
    if os.path.isdir(settings.BASE_DATA_DIR):
        delivery_files = DeliveryFileManager(procedure.code, procedure.phases, procedure.vbs)
        phase = delivery_files.phase_directories[phase_code]
        create_phase_thumbnail(phase["thumbnail_directory"], None)


def create_yaml_file(obj, output_file):

    yaml = YamlObject()

    with open(output_file, "wb") as yaml_stream:
        obj.dump(yaml, yaml_stream)

    # Check yaml validity by loading file
    with open(output_file, "r") as yaml_stream:
        yaml.load(yaml_stream)


def is_vbs(vbs_input):
    if vbs_input.lower() == "y":
        return True

    return False
