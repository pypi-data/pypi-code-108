"""
Build an object to represent a Clarisse Conductor submission.

In this case the submission may contain xrefs nested to any level and we do a
pretty good job of resolving them. However, if the render errors due to xref
the localize method is the fallback.
"""

import errno
import json
import os

import shutil
import sys

from ciotemplate.expander import Expander
import cioclarisse.clarisse_config as ccfg
import cioclarisse.dependencies as deps
import ix

from ciocore import conductor_submit
from cioclarisse.utils import ConductorError
from cioclarisse import utils
from ciocore import data as coredata
from cioseq.sequence import Sequence
from cioclarisse import frames_ui
from cioclarisse.task import Task
from ciocore.package_environment import PackageEnvironment

from ciopath.gpath import Path
from ciopath.gpath_list import PathList


class Submission(object):
    """
    Submission holds all data needed for a submission.

    It has potentially many Jobs, and those Jobs each have many Tasks. A
    Submission can provide the correct args to send to Conductor, or it can be
    used to create a dry run to show the user what will happen.

    A Submission also sets a list of tokens that the user can access as <angle
    bracket> tokens in order to build strings in the UI such as commands, job
    title, and (soon to be added) metadata.
    """

    def __init__(self, node):
        """
        Collect data from the Clarisse UI.

        Collect attribute values that are common to all jobs, then call
        get_context(). After get_context has been called, the Submission level
        token variables are valid and calls to evaluate expressions will
        correctly resolve where those tokens have been used.
        """
        self.node = node
        self.project_filename = ix.application.get_current_project_filename()
        self.tmpdir = Path(utils.conductor_temp_dir())

        self.render_package_path = self._get_render_package_path()
        self.local_upload = self.node.get_attribute("local_upload").get_bool()

        self.should_delete_render_package = (
            self.node.get_attribute("clean_up_render_package").get_bool()
            and self.local_upload
        )

        self.upload_only = self.node.get_attribute("upload_only").get_bool()
        self.project = self._get_project()
        self.notifications = self._get_notifications()

        self.sequence = self._get_sequence()
        self.sources = self._get_sources()
        self.instance = self._get_instance()

        out = self._get_output_directory()
        self.common_output_path = out["common_path"]
        self.output_paths = out["output_paths"]


        tile_width = int(self.node.get_attribute("tiles").get_long())
        self.tiles = tile_width * tile_width

        sw = self._get_software()
        self.environment = sw["env"]
        self.package_ids = sw["ids"]


        self.dependencies = deps.collect(self.node)
        self.dependencies.add(self.render_package_path)
 

        self.tokens = self.get_context()
        expander = Expander(**self.tokens)
        self.title = expander.evaluate(self.node.get_attribute("title").get_string())

 
        self.tasks = []

        task_att = self.node.get_attribute("task_template")
        for chunk in self.sequence["main"].chunks():
            for tile_number in range(1, self.tiles + 1):
                tile_spec = (self.tiles, tile_number)
                self.tasks.append(
                    Task(chunk, task_att, self.sources, tile_spec, self.tokens)
                )



    def _get_sources(self):
        """
        Get the images/layers, along with associated Sequence objects.

        If we are not rendering a custom range, then the sequence for
        each image may be different.

        Returns:
            list of dict: elements contain an image along with the Sequence that
            represents the image range.
        """

        images = ix.api.OfObjectArray()
        self.node.get_attribute("images_and_layers").get_values(images)

        use_custom = self.node.get_attribute("use_custom_frames").get_bool()

        # cast to list because OfObjectArray is true even when empty.
        if not list(images):
            msg = "No render outputs added. Please add images and/or layers in the Submitter"
            raise ConductorError(msg)
        seq = self.sequence["main"]
        result = []
        for image in images:
            if not use_custom:
                seq = Sequence.create(*frames_ui.image_range(image))
            result.append({"image": image, "sequence": seq})
        return result


    def _get_sequence(self):

        """
        Get sequence objects from the frames section of the UI.

        Returns:
            dict: main sequence and scout sequence.
        """
        return {
            "main": frames_ui.main_frame_sequence(self.node),
            "scout": frames_ui.resolved_scout_sequence(self.node),
        }



    def _get_instance(self):
        """
        Get everything related to the instance.

        Get the machine type, preemptible flag, and number of retries if
        preemptible. We use the key from the instance_type menu and look
        up the machine spec in the shared data where the full list of
        instance_types is stored. When exhaustion API is in effect, the
        list of available types may be dynamic, so wetell the user to
        refresh.

        Returns:
            dict: Fields to specify the render node behaviour.
        """
        instance_types = coredata.data().get("instance_types")

        label = self.node.get_attribute("instance_type").get_applied_preset_label()

        result = {
            "preemptible": self.node.get_attribute("preemptible").get_bool(),
            "retries": self.node.get_attribute("retries").get_long(),
        }

        try:
            found = next(it for it in instance_types if str(it["description"]) == label)
        except StopIteration:
            msg = 'Invalid instance type "{}". Try a refresh (Press the Connect button).'.format(label)
            raise ConductorError(msg)

        result.update(found)
        return result



    def _get_project(self):
        """Get the project from the attr.

        Get its ID in case the current project is no longer in the list
        of projects at conductor, throw an error.
        """


        projects = coredata.data().get("projects")
        project_att = self.node.get_attribute("conductor_project_name")
        label = project_att.get_applied_preset_label()

        found = next((p for p in projects if p== label), None)
        if not found:
            msg = 'Cannot find project "{}" at Conductor. Please ensure the PROJECT dropdown contains a valid project.'.format(label)
            raise ConductorError(msg)

        return found

    def _get_notifications(self):
        """Get notification prefs."""
        if not self.node.get_attribute("notify").get_bool():
            return None

        emails = self.node.get_attribute("email_addresses").get_string()
        return [email.strip() for email in emails.split(",") if email.strip()]

    def get_context(self):
        """Env tokens are variables to help the user build expressions.

        The user interface has fields for strings such as job title,
        task command. The user can use these tokens with <angle brackets> to build those strings. Tokens at the Submission
        level are also available in Job level fields, and likewise
        tokens at the Job level are available in Task level fields.
        """
        tokens = {}

        pdir_val = ix.application.get_factory().get_vars().get("PDIR").get_string()

        tokens["pdir"] = '"{}"'.format(Path(pdir_val).fslash(with_drive=False))

        tokens["temp_dir"] = "{}".format(self.tmpdir.fslash(with_drive=False))
        tokens["tempdir"] =tokens["temp_dir"]

        tokens["submitter"] = self.node.get_name()

        tokens["render_package"] = '"{}"'.format(
            self.render_package_path.fslash(with_drive=False)
        )
        tokens["renderpackage"] = tokens["render_package"] 

        tokens["project"] = self.project 

        main_seq = self.sequence["main"]
        scout_seq = self.sequence["scout"]

        tokens["scout"] = str(scout_seq)
        tokens["chunksize"] = str(main_seq.chunk_size)
        tokens["chunkcount"] = str(main_seq.chunk_count())
        tokens["scoutcount"] = str(len(scout_seq or []))
        tokens["sequencelength"] = str(len(main_seq))
        tokens["sequence"] = str(main_seq)
        tokens["sequencemin"] = str(main_seq.start)
        tokens["sequencemax"] = str(main_seq.end)
        tokens["instance_type"] = self.instance["name"]
        tokens["instance"] = self.instance["description"]
        tokens["tiles"] = str(self.tiles)
        pidx = int(self.instance["preemptible"])
        tokens["preemptible"] = "preemptible" if pidx else "non-preemptible"
        tokens["retries"] = str(self.instance["retries"])
        tokens["job"] = self.node_name

        # Space delimited list of output paths are needed for a mkdir cmd. As
        # mentioned above, no longer needed now that directories are created in
        # the prerender script. Just don't want to remove right now as no time
        # to test.
        tokens["directories"] = " ".join(
            '"{}"'.format(p.fslash(with_drive=False)) for p in self.output_paths
        )

        return tokens

    def _get_render_package_path(self):
        """
        Calc the path to the render package.

        The name is not always known until
        preview/submission time because it is based on the filename. 

        It will however always show up in the preview window.

        We replace spaces in the filename because of a bug in Clarisse
        https://www.isotropix.com/user/bugtracker/376

        Returns:
            string: path
        """

        msg= 'Cannot create a submission from this file. Has it ever been saved?'
        current_filename = ix.application.get_current_project_filename()
        if not current_filename:
            raise ConductorError(msg)

        node_name =self.node.get_attribute("title").get_string()

        node_name = "".join(x for x in node_name if x.isalpha() or x.isdigit()  )


        path = os.path.splitext(current_filename)[0]

        path = os.path.join(
            os.path.dirname(path), os.path.basename(path).replace(" ", "_")
        )
        result = "{}.{}.cio.project".format(path,node_name)
        try:
            result =  Path(result)
        except ValueError as ex:
            msg = "{} - while resolving {}".format(str(ex), result)
            raise ConductorError(msg)
        
        return result




    def _get_output_directory(self):
        """
        Get the common path for all image output paths.

        NOTE: We don't really need the subpaths any longer because directory
        creation is handled in the prerender script. Don't want to mess with
        things right now though.

        Returns:
            dict: common path and list of paths below it
        """
        out_paths = PathList()

        images = ix.api.OfObjectArray()
        self.node.get_attribute("images_and_layers").get_values(images)

        for image in images:
            directory = os.path.dirname(image.get_attribute("save_as").get_string())
            try:
                out_paths.add(directory)
            except ValueError as ex:
                msg = "{} - while resolving {}".format(str(ex), directory)
                raise ConductorError(msg)
        return {"common_path": out_paths.common_path(), "output_paths": out_paths}


 


    def _get_software(self):

        result = {
            "ids": [],
            "env": PackageEnvironment()
        }

        clarisse_version_att = self.node.get_attribute("clarisse_version")
        name = clarisse_version_att.get_applied_preset_label()

        tree_data = coredata.data().get("software")
        host_package = tree_data.find_by_path(name)

        result["ids"].append(host_package["package_id"])
        result["env"].extend(host_package)
        result["env"].extend(self._get_extra_env_vars())

        return result


    def _get_extra_env_vars(self):
        """
        Collect any environment specified by the user.

        Returns:
            list of dict: name, value and merge policy of user specified env vars.
        """

        result = []
        json_entries = ix.api.CoreStringArray()
        self.node.get_attribute("extra_environment").get_values(json_entries)

        for entry in [json.loads(j) for j in json_entries]:
            result.append(
                {
                    "name": entry["key"],
                    "value": os.path.expandvars(entry["value"]),
                    "merge_policy": ["append", "exclusive"][int(entry["excl"])],
                }
            )

        return result

    def get_args(self):
        """
        Prepare the args for submission to conductor.

        Returns:
            list: list of dicts containing submission args per job.
        """
        result = {}

        result["local_upload"] = self.local_upload
        result["upload_only"] = self.upload_only
        
        result["project"] = self.project
        result["notify"] = self.notifications

        result["upload_paths"] = sorted([d.fslash() for d in self.dependencies])
        result["autoretry_policy"] = (
            {"preempted": {"max_retries": self.instance["retries"]}}
            if self.instance["preemptible"]
            else {}
        )
        result["software_package_ids"] = self.package_ids 

        result["preemptible"] = self.instance["preemptible"]
        result["environment"] = dict(self.environment)
        result["scout_frames"] = ", ".join(
            [str(s) for s in self.sequence["scout"] or []]
        )
        result["output_path"] = self.common_output_path.fslash()
        result["chunk_size"] = self.sequence["main"].chunk_size
        result["instance_type"] = self.instance["name"]
        if not result["upload_only"]:
            result["tasks_data"] = [task.data() for task in self.tasks]

        result["job_title"] = self.title
  
        return result

    def submit(self):
        """
        Submit all jobs.

        Returns:
            list: list of response dictionaries, containing response codes
            and descriptions.
        """

        submission_args = self.get_args()
        self._before_submit()

        self.remove_missing_upload_paths(submission_args)

        try:
            remote_job = conductor_submit.Submit(submission_args)
            response, response_code = remote_job.main()
            ix.log_info({"code": response_code, "response": response})
        except BaseException:
            raise
        finally:
            self._after_submit()
        return response

    def _before_submit(self):
        """
        Prepare the project files that will be shipped.

        We first write out the current project file. 
        
        Then (on Windows) we find additional referenced project 
        files and adjust paths in all of them so they may be 
        rendered on linux render nodes.
        """
        self.write_render_package()


    def write_render_package(self):
        """
        Write a package suitable for rendering.

        A render package is a project file with a special name.
        """

        self._before_write_package()

        context = ix.get_item("project:/")
        ix.log_info("Writing render package: context is '{}'".format(context))
            
        package_file = self.render_package_path.fslash()

        has_refs = self._contains_project_refs()


        with utils.disabled_app():
            # If the project has references, then try to use:
            # export_context_as_project_with_dependencies() as it makes all the refs local, meaning we
            # dont need to linuxify recursively.
            # However, it can fail in some situations due to the resulting file not being compatible
            # with cnode (possible bug). So if there are no refs, we just save project in the
            # regular way.
            if has_refs:
                success = ix.export_context_as_project_with_dependencies(context, package_file)
            else:
                success = ix.application.save_project(package_file, True)
        
        if success:
            ix.log_info("Wrote render package '{}'".format(package_file))
        else:
            msg = "Failed to write render package file '{}'".format(package_file)
            raise ConductorError(msg)

        self._after_write_package()

        if utils.is_windows():
            ix.log_info("Windows path adjustments")
            utils.linuxify(self.render_package_path.fslash())
            ix.log_info("Linuxified render project file")
        else:
            ix.log_info("Not using Windows")

        return package_file

    def _contains_project_refs(self):
        """
        True if the project contains references to other projects.
        """
        contexts = ix.api.OfContextSet()
        ix.application.get_factory().get_root().resolve_all_contexts(contexts)
        for ctx in contexts:
            if ctx.is_reference() and ctx.get_attribute("filename").get_string().endswith(".project"):
                return True
        return False



    def remove_missing_upload_paths(self, submission_args):
        """
        Alert the user of missing files. If the user doesn't want to continue
        with missing files, the result will be False. Otherwise it will be True
        and the potentially adjusted args are returned.

        Args:
            submission_args (obj): 

        Returns:
           tuple (bool, adjusted args):
        """
        missing_files = []

  
        existing_files = []
        for path in submission_args["upload_paths"]:
            if os.path.exists(path):
                existing_files.append(path)
            else:
                missing_files.append(path)

        submission_args["upload_paths"] = existing_files

        missing_files = sorted(list( missing_files))
        if missing_files:
            ix.log_warning("Skipping missing files:")
            for f in missing_files:
                ix.log_warning(f)


    def _before_write_package(self):
        """
        Prepare to write render package.
        """
        self._prepare_temp_directory()
        self._copy_system_dependencies_to_temp()

    def _prepare_temp_directory(self):
        """
        Make sure the temp directory has a conductor subdirectory.
        """
        tmpdir = self.tmpdir.fslash()
        try:
            os.makedirs(tmpdir)
        except OSError as ex:
            if not (ex.errno == errno.EEXIST and os.path.isdir(tmpdir)):
                raise
        ix.log_info("Prepared tmpdir '{}'".format(tmpdir))

    def _copy_system_dependencies_to_temp(self):
        """
        Copy over all system dependencies to a tmp folder.

        Wrapper scripts, config files etc. The clarisse.cfg file is special. See
        ../clarisse_config.py
        """
        for entry in deps.system_dependencies():
            if os.path.isfile(entry["src"]):
                if entry["src"].endswith(".cfg"):
                    safe_config = ccfg.legalize(entry["src"])
                    with open(entry["dest"], "w") as dest:
                        dest.write(safe_config)
                    ix.log_info(
                        "Copy with mods {} to {}".format(entry["src"], entry["dest"])
                    )
                else:
                    ix.log_info("Copy {} to {}".format(entry["src"], entry["dest"]))
                    shutil.copy(entry["src"], entry["dest"])


    def _after_submit(self):
        """Clean up, and potentially other post submission actions."""
        self._delete_render_package()

    def _after_write_package(self):
        """
        Runs operations after saving the render package.

        If we did something destructive, like localize contexts, then
        a backup will have been saved and we now reload it. This strategy
        is used because Clarisse's undo is broken when it comes to
        undoing context localization.
        """
        pass
 
    def _delete_render_package(self):
        """
        Delete the render package from disk if the user wants to.
        """
        if self.should_delete_render_package:
            render_package_file = self.render_package_path.fslash()
            if os.path.exists(render_package_file):
                os.remove(render_package_file)
 

    @property
    def node_name(self):
        """node_name."""
        return self.node.get_name()

    @property
    def filename(self):
        """filename."""
        return ix.application.get_current_project_filename()

    def has_notifications(self):
        """has_notifications."""
        return bool(self.notifications)

    @property
    def email_addresses(self):
        """email_addresses."""
        if not self.has_notifications():
            return []
        return self.notifications["email"]["addresses"]
