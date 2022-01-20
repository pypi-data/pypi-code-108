from __future__ import absolute_import, division, print_function, unicode_literals

from publisher.procedure_content import build_procedure_list, build_phase_list, has_unstaged_changes, reset_repo, \
    change_procedure, save_working_changes, get_commits_for_procedure, publish, create_procedure_branch, \
    save_channel_changes, build_channel_list
from publisher.utils import get_procedure_code
from publisher.processing.procedure import build_single_phase, build_procedure, create_procedure_from_production,\
    update_phase_name, build_channel, update_channel, create_phase
from publisher.processing.data_sources.organisation import get_data_from_channel
from publisher.processing.data_sources.csv_steps_file import get_csv_steps_file
import publisher.settings as settings


class Publisher(object):
    def __init__(self):
        self.procedure_code = None

    def get_channel_list(self):
        return build_channel_list()

    def get_channel_data(self, channel):
        return get_data_from_channel(channel)

    def get_procedure_list(self):
        return build_procedure_list()

    def get_phase_list(self):
        phase_list = build_phase_list()
        phase_list.sort()
        return phase_list

    def get_current_procedure(self):
        self.procedure_code = get_procedure_code()
        return self.procedure_code

    def set_current_procedure(self, proc_code):
        self.procedure_code = proc_code

    def get_delivery_directory(self, vbs):
        if vbs:
            return settings.VBS_ROOT
        else:
            return settings.CG_APP5_ROOT

    def workon_procedure(self, proc_code):
        self.check_unstaged_changes()
        change_procedure(proc_code)
        self.set_current_procedure(proc_code)

    def check_unstaged_changes(self):
        if has_unstaged_changes():
            raise UnsavedChangesError("Unsaved changes found, please contact pipeline.")

    def reset_repo(self):
        reset_repo()

    def save_working_changes(self, message):
        save_working_changes(message)

    def publish(self, message, distribution_group):
        print("-- Saving changes --")
        save_working_changes(message)
        print("-- Saved changes --")
        selected_commit = get_commits_for_procedure()[0]
        print("-- Publishing to TS-Testing --")
        publish(selected_commit.copy_with_new_note(distribution_group))
        print("-- Publish Successful --")

    def update_phase(self, phase_code, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers, info_step,
                     country_restrict, csv_version):
        build_single_phase(phase_code, graphics=graphics,
                           pip_graphics=pip_graphics,
                           widget_graphics=widget_graphics,
                           thumbnails=thumbnails, step_numbers=step_numbers,
                           info_step=info_step, csv_version=csv_version)

    def update_phase_name(self, phase_code, new_name):
        update_phase_name(phase_code, new_name)

    def update_procedure(self, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers, info_step,
                         country_restrict):
        build_procedure(self.procedure_code, build_phases=True,
                        graphics=graphics, pip_graphics=pip_graphics,
                        widget_graphics=widget_graphics, thumbnails=thumbnails,
                        step_numbers=step_numbers, info_step=info_step)

    def update_procedure_info(self, thumbnails):
        build_procedure(self.procedure_code, build_phases=False, graphics=False,
                        pip_graphics=False, widget_graphics=False,
                        thumbnails=thumbnails, step_numbers=False,
                        info_step=False)

    def create_procedure(self, proc_code):
        if proc_code not in build_procedure_list():
            self.check_unstaged_changes()
            create_procedure_branch(proc_code)
        else:
            raise ProcedureExistsError("The procedure {0} already exists and thus cannot be created".format(proc_code))

        create_procedure_from_production(proc_code)
        save_working_changes("Initial commit", initial=True, procedure_code=proc_code)

        self.set_current_procedure(proc_code)

    def create_phase(self, proc_code, phase_code):
        if proc_code in build_procedure_list():
            self.workon_procedure(proc_code)
        else:
            raise MissingProcedureError("The procedure {0} doesn't exist, please create it".format(proc_code))

        create_phase(proc_code, phase_code)
        save_working_changes("Added new phase {0}".format(phase_code))

        self.update_procedure_info(None)

    def create_channel(self, channel_data):
        build_channel(channel_data)
        message = "Adding channel - {}".format(channel_data['code'])
        save_channel_changes(message)

    def update_channel(self, code, updates):
        update_channel(code, updates)
        message = "Updating channel - {}".format(code)
        save_channel_changes(message)

    def get_csv_file(self, phase_code, csv_version):
        return get_csv_steps_file(phase_code, csv_version)


class UnsavedChangesError(IOError):
    pass


class ProcedureExistsError(IOError):
    pass


class MissingProcedureError(IOError):
    pass
