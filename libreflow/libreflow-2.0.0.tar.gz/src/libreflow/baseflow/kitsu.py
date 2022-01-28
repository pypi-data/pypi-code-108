import gazu
import os
import fnmatch

from kabaret import flow
from kabaret.subprocess_manager.flow import RunAction

from .maputils import ClearMapAction
from .users import PresetChoiceValue


class KitsuAPIWrapper(flow.Object):

    _server_url = flow.Param("")
    _config = flow.Parent()

    def set_host(self, url):
        gazu.client.set_host(url)

    def get_host(self):
        return gazu.client.get_host()

    def set_server_url(self, url):
        self._server_url.set(url)

    def get_server_url(self):
        return self._server_url.get()

    def log_in(self, username, password):
        try:
            user_data = gazu.log_in(username, password)
        except (
            gazu.exception.AuthFailedException,
            gazu.exception.ServerErrorException,
        ):
            user_data = None

        return user_data
    
    def log_out(self):
        gazu.log_out()

    def get_tokens(self):
        return gazu.client.default_client.tokens

    def set_tokens(self, tokens):
        gazu.client.set_tokens(tokens)

    def host_is_valid(self):
        if not gazu.client.host_is_up(gazu.client.default_client):
            return False
        try:
            gazu.client.post("auth/login", {"email": "", "password": ""})
        except Exception as exc:
            return (
                type(exc) == gazu.exception.ParameterException
                or type(exc) == gazu.exception.ServerErrorException
            )

    def current_user_logged_in(self):
        """
        Checks if the current user is logged in.

        This method assumes Kitsu client's host is valid.
        """
        try:
            gazu.client.get_current_user()
        except gazu.exception.NotAuthenticatedException:
            return False

        return True
    
    def get_project_id(self):
        import requests
        try:
            data = gazu.project.get_project_by_name(
                self._config.project_name.get()
            )
        except requests.exceptions.ConnectionError:
            return None
        else:
            return data['id']
    
    def get_shot_data(self, name, sequence):
        if isinstance(sequence, str):
            sequence = self.get_sequence_data(sequence)

        if not sequence:
            return None
        
        return gazu.shot.get_shot_by_name(
            sequence,
            name
        )
    
    def get_shot_casting(self, shot, sequence=None):
        if isinstance(shot, str):
            shot = self.get_shot_data(shot, sequence)

        if not shot:
            return None

        return gazu.casting.get_shot_casting(shot)
    
    def get_sequence_data(self, name):
        return gazu.shot.get_sequence_by_name(
            self._config.project_id.get(),
            name
        )
    
    def get_sequence_casting(self, sequence):
        if isinstance(sequence, str):
            sequence = self.get_sequence_data(sequence)

        if not sequence:
            return None

        return gazu.casting.get_sequence_casting(sequence)
    
    def get_asset_data(self, name):
        return gazu.asset.get_asset_by_name(
            self._config.project_id.get(),
            name
        )
    
    def get_asset_type(self, asset):
        if isinstance(asset, str):
            asset = self.get_asset_data(asset)

        if not asset:
            return None

        return gazu.asset.get_asset_type(asset["entity_type_id"])
    
    def get_task(self, entity, task_type_name):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        
        # Check if task type is valid
        if task_type is None:
            task_types = gazu.task.all_task_statuses()
            names = [tt['name'] for tt in task_types]
            self.root().session().log_error((
                f"Invalid task type '{task_type_name}'. "
                "Should be one of " + str(names) + "."
            ))
            return None
        
        task = gazu.task.get_task_by_entity(entity, task_type)
        
        if task is None:
            self.root().session().log_error("Invalid Kitsu entity")
            return None
        
        task = gazu.task.get_task(task['id'])
        
        return task
    
    def get_task_statutes(self):
        task_statuses = gazu.task.all_task_statuses()
        return [ts['name'] for ts in task_statuses]
    
    def get_task_current_status(self, entity, task_type_name):
        task = self.get_task(entity, task_type_name)
        
        if task is None:
            return None
        
        return task['task_status']['name']
    
    def get_shot_task_types(self):
        types = gazu.task.all_task_types()
        return [t['name'] for t in types if t['for_shots']]
    
    def get_user(self, project_user_name=None):
        if project_user_name is None:
            project_user_name = self.root().project().get_user_name()
        
        user = self.root().project().get_user(project_user_name)
        
        if user is None:
            self.root().session().log_error((
                f"No user '{project_user_name}' registered in this project"
            ))
            return None
        
        user_kitsu_id = user.kitsu_id.get()
        kitsu_user = gazu.person.get_person_by_desktop_login(user_kitsu_id)
        
        if kitsu_user is None:
            kitsu_user = gazu.person.get_person_by_email(user_kitsu_id)
        
        return kitsu_user
    
    def user_is_assigned(self, kitsu_user, kitsu_task):
        kitsu_id = kitsu_user.get('id', None)
        
        if kitsu_id is None:
            self.root().session().log_error("Invalid Kitsu user")
            return None
        
        assignees = kitsu_task.get('assignees', None)
        
        if assignees is None:
            self.root().session().log_error("Invalid Kitsu task")
            return None
        
        return kitsu_id in assignees
    
    def upload_preview(self, kitsu_entity, task_type_name, task_status_name, file_path, comment="", user_name=None):
        # Get user
        user = self.get_user(user_name)
        
        # Get task
        task = self.get_task(kitsu_entity, task_type_name)
        
        if task is None or user is None:
            return False
        
        # Add comment with preview
        
        # Check if preview file exists
        if not os.path.exists(file_path):
            self.root().session().log_error(
                f"Preview file '{file_path}' does not exists."
            )
            return False
        
        task_status = gazu.task.get_task_status_by_name(task_status_name)
        
        # Check if status is valid
        if task_status is None:
            task_statuses = gazu.task.all_task_statuses()
            names = [ts['name'] for ts in task_statuses]
            self.root().session().log_error((
                f"Invalid task status '{task_status_name}'."
                "Should be one of " + str(names) + "."
            ))
            return False
        
        comment = gazu.task.add_comment(task, task_status, comment=comment)
        gazu.task.add_preview(task, comment, file_path)
        
        return True


class KitsuBindings(flow.Object):

    asset_types = flow.HashParam()
    asset_families = flow.HashParam()
    task_type_files = flow.DictParam({})

    def _kitsu_api(self):
        return self.root().project().kitsu_api()

    def get_asset_oid(self, kitsu_asset_name):
        kitsu_api = self.root().project().kitsu_api()
        kitsu_asset = kitsu_api.get_asset_data(kitsu_asset_name)

        asset_type = kitsu_api.get_asset_type(kitsu_asset['name'])['name']
        asset_type = self.get_asset_type(asset_type)
        asset_family = self.get_asset_family(kitsu_asset['data']['family'])

        return '%s/asset_lib/asset_types/%s/asset_families/%s/assets/%s' % (
            self.root().project().oid(),
            asset_type,
            asset_family,
            kitsu_asset['name']
        )

    def get_asset_data(self, name):
        kitsu_api = self._kitsu_api()
        kitsu_asset = kitsu_api.get_asset_data(name)

        return dict(
            type=kitsu_api.get_asset_type(name)['name'],
            family=kitsu_asset['data']['family']
        )

    def get_shot_casting(self, shot_name, sequence_name):
        kitsu_api = self._kitsu_api()
        kitsu_casting = kitsu_api.get_shot_casting(shot_name, sequence_name)
        
        if kitsu_casting is None:
            return {}
        
        casting = dict()

        for asset in kitsu_casting:
            asset_name = asset['asset_name']
            asset_data = self.get_asset_data(asset_name)
            asset_data['nb_occurrences'] = asset['nb_occurences']
            casting[asset_name] = asset_data

        return casting

    def get_asset_type(self, kitsu_asset_type):
        if not self.asset_types.has_key(kitsu_asset_type):
            return kitsu_asset_type

        return self.asset_types.get_key(kitsu_asset_type)

    def get_asset_family(self, kitsu_asset_family):
        if not self.asset_families.has_key(kitsu_asset_family):
            return kitsu_asset_family

        return self.asset_families.get_key(kitsu_asset_family)
    
    def get_task(self, entity_data, task_type_name):
        entity = self.get_entity(entity_data)
        
        if entity is None:
            self.root().session().log_error("Invalid Kitsu entity")
            return None
        
        return self._kitsu_api().get_task(entity, task_type_name)
    
    def get_task_types(self, file_name):
        task_types = []

        for pattern, type_names in self.task_type_files.get().items():
            if not isinstance(type_names, list):
                type_names = [type_names]
            
            if fnmatch.fnmatch(pattern, file_name):
                task_types += type_names
        
        return task_types
    
    def get_entity_data(self, contextual_settings):
        kitsu_api = self.root().project().kitsu_api()
        entities_data = {
            'shot': ['shot', 'sequence'],
            'asset': ['asset_name'],
        }
        
        entity_data = {}
        
        for entity_type, entity_keys in entities_data.items():
            for key in entity_keys:
                entity_data[key] = contextual_settings.get(key, None)
            
            if all(v is not None for v in entity_data.values()):
                entity_data.update(dict(entity_type=entity_type))
                return entity_data
            else:
                entity_data = {}
        
        return None
    
    def get_kitsu_entity(self, entity_data):
        entity_type = entity_data['entity_type']
        
        if entity_type == 'shot':
            return self._kitsu_api().get_shot_data(entity_data['shot'], entity_data['sequence'])
        elif entity_type == 'asset':
            return self._kitsu_api().get_asset_data(entity_data['asset_name'])
        else:
            return None


class KitsuTaskStatus(PresetChoiceValue):
    
    DEFAULT_EDITOR = 'choice'
    
    def choices(self):
        return self.root().project().kitsu_api().get_task_statutes()


class UpdateKitsuSettings(flow.Action):

    _kitsu_object = flow.Parent(2)

    def needs_dialog(self):
        return False

    def run(self, button):
        self._kitsu_object.update_kitsu_settings()


class UpdateItemsKitsuSettings(flow.Action):

    _kitsu_map = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        for item in self._kitsu_map.mapped_items():
            item.update_kitsu_settings()

        self._kitsu_map.touch()


class KitsuSetting(flow.values.Value):
    pass


class KitsuSettings(flow.Map):

    clear_settings = flow.Child(ClearMapAction)
    update_settings = flow.Child(UpdateKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return KitsuSetting

    def columns(self):
        return ["Name", "Value"]

    def _fill_row_cells(self, row, item):
        row["Name"] = item.name()
        row["Value"] = item.get()

    def update(self, settings):
        try:
            settings["kitsu_name"] = settings.pop("name")
        except KeyError:
            pass

        for name, value in settings.items():
            try:
                kitsu_setting = self.get_mapped(name)
            except flow.exceptions.MappedNameError:
                kitsu_setting = self.add(name)

            kitsu_setting.set(value)

        self.touch()


class OpenInBrowser(RunAction):

    ICON = ("icons.libreflow", "firefox")

    _url = flow.Parent()

    def runner_name_and_tags(self):
        return "Firefox", ["Browser"]

    def extra_argv(self):
        return [self._url.get()]

    def allow_context(self, context):
        return context and context.endswith(".inline")

    def needs_dialog(self):
        return False


class Url(flow.values.ComputedValue):

    open_in_browser = flow.Child(OpenInBrowser)


class KitsuObject(flow.Object):
    """
    Abstract class representing a Kitsu entity.

    Subclasses must implement the *kitsu_dict* and *compute_child_value* methods.
    """

    kitsu_settings = flow.Child(KitsuSettings).ui(hidden=True)
    kitsu_url = flow.Computed(computed_value_type=Url).ui(hidden=True)
    kitsu_id = flow.Param().ui(editable=False).ui(hidden=True)

    def kitsu_setting_names(self):
        """
        Returns the list of object's settings names, as a subset of the keys
        of the dictionary returned by *kitsu_dict*.

        Returning None will skip name filtering on *kitsu_dict* result
        in *get_kitsu_settings*.
        """
        return None

    def kitsu_dict(self):
        """
        Must be implemented to return a dictionary of parameters related
        to the Kitsu entity.

        It should simply consists in calling the appropriate Gazu
        function given the object's *kitsu_id*.
        """
        raise NotImplementedError()

    def get_kitsu_settings(self):
        settings = self.kitsu_dict()
        names = self.kitsu_setting_names()

        if names is None:
            return settings

        return {name: settings[name] for name in names}

    def update_kitsu_settings(self):
        self.kitsu_settings.update(self.get_kitsu_settings())


class KitsuMap(flow.Map):
    @classmethod
    def mapped_type(cls):
        return KitsuObject


class EntityType(flow.values.ChoiceValue):

    CHOICES = ["Assets", "Shots"]


class SyncFromKitsu(flow.Action):

    ICON = ("icons.libreflow", "sync_arrow")

    entity_type = flow.Param("Assets", EntityType)
    from_index = flow.IntParam(0).ui(label="From")
    to_index = flow.IntParam(10).ui(label="To")

    def get_buttons(self):
        self.message.set("<h3>Synchronize entities from Kitsu</h3>")

        return ["Synchronize", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        project = self.root().project()
        project_kitsu_id = project.kitsu_id.get()

        import time

        start_time = time.time()
        i = 0

        if self.entity_type.get() == "Shots":
            kitsu_sequences = gazu.shot.all_sequences_for_project(project_kitsu_id)[
                self.from_index.get() : self.to_index.get()
            ]
            sequences = project.sequences

            # Pull sequences
            for kitsu_sequence in kitsu_sequences:
                try:
                    sequence = sequences.add(kitsu_sequence["name"])
                except flow.exceptions.MappedNameError:
                    # Ignore sequence already mapped
                    continue

                sequence_id = kitsu_sequence["id"]
                sequence.kitsu_id.set(sequence_id)
                sequence.description.set(kitsu_sequence["description"])
                sequence.update_kitsu_settings()

                # Pull shots
                kitsu_shots = gazu.shot.all_shots_for_sequence(sequence_id)
                shots = sequence.shots

                for kitsu_shot in kitsu_shots:
                    try:
                        shot = shots.add(kitsu_shot["name"])
                    except flow.exceptions.MappedNameError:
                        # Ignore shot already mapped
                        continue

                    shot.kitsu_id.set(kitsu_shot["id"])
                    shot.description.set(kitsu_shot["description"])
                    shot.update_kitsu_settings()

                    i += 1

                shots.touch()

            sequences.touch()

            elapsed_time = float(time.time() - start_time)
            self.root().session().log_debug(
                "Elapsed time: {:.4f} min. ({:.4f} min. per shot) ({} shots)".format(
                    elapsed_time / 60.0, elapsed_time / (60.0 * float(i)), i
                )
            )

        elif self.entity_type.get() == "Assets":
            kitsu_assets = gazu.asset.all_assets_for_project(project_kitsu_id)[
                self.from_index.get() : self.to_index.get()
            ]
            assets = project.asset_lib
            i = 0

            for kitsu_asset in kitsu_assets:
                try:
                    asset = assets.add(kitsu_asset["name"])
                except (flow.exceptions.MappedNameError, TypeError) as e:
                    if isinstance(e, flow.exceptions.MappedNameError):
                        # Asset is already mapped
                        i += 1
                        continue

                    try:
                        asset = assets.add("asset{:04d}".format(i))
                    except flow.exceptions.MappedNameError:
                        i += 1
                        continue

                asset.kitsu_id.set(kitsu_asset["id"])
                asset.description.set(kitsu_asset["description"])
                asset.update_kitsu_settings()

                i += 1

            assets.touch()


class KitsuProject(KitsuObject):

    kitsu_name = flow.Param("").watched().ui(hidden=True)
    kitsu_url = flow.Computed().ui(hidden=True)
    kitsu_id = flow.Computed().ui(hidden=True)

    kitsu_api = flow.Child(KitsuAPIWrapper).ui(hidden=True)
    sync_from_kitsu = flow.Child(SyncFromKitsu).injectable().ui(label="Synchronize", hidden=True)

    def kitsu_dict(self):
        project_name = self.kitsu_name.get()
        if not project_name:
            project_name = self.name()

        return gazu.project.get_project_by_name(project_name)

    def child_value_changed(self, child_value):
        if child_value is self.kitsu_name:
            self.kitsu_id.touch()
            self.kitsu_url.touch()

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_id:
            project_dict = self.kitsu_dict()
            child_value.set(project_dict["id"])
        elif child_value is self.kitsu_url:
            child_value.set(
                "%s/productions/%s"
                % (self.kitsu_api.get_server_url(), self.kitsu_id.get())
            )


class KitsuShot(KitsuObject):

    # def kitsu_setting_names(self):
    #     return ['name', 'description', 'nb_frames', 'data']

    def kitsu_dict(self):
        return gazu.shot.get_shot(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/shots/%s"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )


class KitsuSequence(KitsuObject):
    def kitsu_dict(self):
        return gazu.shot.get_sequence(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/shots?search=%s"
                % (self.root().project().kitsu_url.get(), self.name())
            )


class KitsuAsset(KitsuObject):
    def kitsu_dict(self):
        return gazu.asset.get_asset(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/assets/%s"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )
