# import abc
# import importlib
# import inspect
import os
import ix

from ciopath.gpath import Path
from ciopath.gpath_list import GLOBBABLE_REGEX, PathList
from ciocore.validator import Validator, ValidationError
from cioclarisse import const as k
from ciocore import data as coredata
from cioclarisse import frames_ui 
from cioclarisse import dependencies as deps
from cioclarisse import validation_ui
from cioclarisse import utils

from cioseq.sequence import Sequence
 
class ValidateImagesAndLayers(Validator):
    def run(self, _):
 
        images = ix.api.OfObjectArray()
        self._submitter.get_attribute("images_and_layers").get_values(images)
        out_paths = PathList()

        num_images = images.get_count()

        if not num_images:
            msg = "No render outputs added. Please add images and/or layers in the Submitter"
            self.add_error(msg)
            return

        for image in images:
            if not image.get_attribute("render_to_disk").get_bool():
                msg = "Image or Layer does not have render_to_disk attribute set: {}".format(image.get_full_name())
                self.add_error(msg)
                continue
            

            save_path = image.get_attribute("save_as").get_string()
            if not save_path:
                msg = "Image save_as path is not set: {}".format(image.get_full_name())
                self.add_error(msg)
                continue
    
            if save_path.endswith("/"):
                msg =  "Image save_as path must be a filename, not a directory: {}".format( image.get_full_name() )
                self.add_error(msg)
                continue
    

            directory = os.path.dirname(save_path)
            out_paths.add(directory)

        if not out_paths:
            msg = "There are no images or layers with Save to Disk turned on."
            self.add_error(msg)
            return
    
        common_path = out_paths.common_path()

        paths = "\n".join(p.fslash() for p in out_paths)

        if common_path.depth == 0:
            msg = "Your output files should be rendered to a common folder. {}\n{}".format(common_path.fslash(), paths )
            self.add_error(msg)
            return

        if self._submitter.get_attribute("use_custom_frames").get_bool():
            frame_seq = frames_ui.custom_frame_sequence(self._submitter)
            if not frame_seq:
                self.add_error("Error validating custom frames sequence.")
            for image in images:
                image_rng = frames_ui.image_range(image)
                image_seq = Sequence.create(*image_rng)
                isect = image_seq.intersection(frame_seq)
                if list(isect) != list(frame_seq):
                    self.add_warning("Image has less frames than custom sequence. {}".format( image.get_full_name()))


class ValidateTaskCount(Validator):
    def run(self, _): 
        seq = frames_ui.main_frame_sequence(self._submitter)
        if not seq:
            self.add_error("No valid frame seqence. Either ensure connected images have a valid sequence, or overide the fame range in the subitter.")
            return
        count = seq.chunk_count()
        if  count > 1000:
            self.add_notice(
                "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(count))

class ValidatePackages(Validator):
    def run(self, _):
 
        if not (
            self._submitter.get_attribute("clarisse_version")
            .get_applied_preset_label()
            .startswith("clarisse")
        ):
            self.add_error("No Clarisse package selected.")

class ValidateProject(Validator):
    def run(self, _): 
        projects = coredata.data().get("projects")

        project_att = self._submitter.get_attribute("conductor_project_name")
        label = project_att.get_applied_preset_label()
        if not label or label == k.NOT_CONNECTED :
            msg = 'Project is not set for "{}".'.format(self._submitter.get_name())
            self.add_error(msg)
        try:
            next(p for p in projects if str(p) == label)
        except StopIteration:
            msg = 'Cannot find project "{}" at Conductor. Please ensure the PROJECT dropdown contains a valid project.'.format(label)
            self.add_error(msg)
 
class ValidateUploadDaemon(Validator):


    def run(self, _): 
        if  self._submitter.get_attribute("local_upload").get_bool():
            msg ="Local Upload is turned on, which means your Clarisse session will be\n"
            msg+="unusable until all assets have uploaded. If you have a large number of\n"
            msg+="assets that don't already exist on Conductor, you are advised to use a\n"
            msg+="background process to handle the upload. Its easy to set up. Just cancel\n"
            msg+="this window, turn Local Upload OFF in the submitter and resubmit. You'll\n"
            msg+="then see instructions to start the upload daemon."

            self.add_notice(msg)
            return
        # daemon
        msg  = "Local Upload is turned off. Therefore this submission expects an uploader\n"
        msg += "daemon to be running. If you haven't started an uploader daemon, follow\n"
        msg += "the instructions below.\n"
        if utils.is_windows():
            msg += "Open a new command prompt or Powershell and type:\npython.exe Conductor\\bin\\conductor uploader\nthen press enter."
        else:
            msg += "Open a new terminal window and type:\nConductor/bin/conductor uploader\nthen press enter."
        msg += "For more information, search 'upload daemon' at docs.conductortech.com"
        self.add_notice(msg)

class ValidateMissingAssets(Validator):

    def run(self, _):
 
        basenames =  deps.CONDUCTOR_SCRIPTS + [deps.CLARISSE_CFG_FILENAME]

        path_list = PathList()

        for gpath in deps.collect(self._submitter, do_glob=False):

            # we can assunme that all globbable paths, (those containing glob
            # characters) cannot possibly represent missing files because they are
            # literally resolved  by checking what matches on disk. Therfore, we ignore them.
            if not GLOBBABLE_REGEX.search(gpath.fslash()):
                path_list.add(gpath)

        # path_list has taken care of deduplication by now - yay
        missing = []
        for gpath in path_list:
            pp = gpath.fslash()
            if any(pp.endswith(x) for x in basenames):
                continue
            if not os.path.exists(pp):
                missing.append(pp)

        if missing:
            for asset in missing:
                self.add_warning("Missing: {}".format(asset))

def run(node):
 
    errors, warnings, notices = _run_validators(node)

    if errors:
        for error in errors:
            ix.log_error(error)
        msg = "There are some critical issues. You can't submit until you fix them."
        raise ValidationError(msg)

    if notices or warnings:
        dialog_result = validation_ui.proceed(warnings,notices)
        
        if not dialog_result:
            msg = "Submission cancelled by user."
            raise ValidationError(msg)
    else:
        ix.log_info("There are no Notices or Warnings")

 
def _run_validators(node):
    validators =  [plugin(node) for plugin in Validator.plugins()]
    for validator in validators:
        validator.run("main")

    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(
        set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices
