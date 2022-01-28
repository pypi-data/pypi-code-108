from libreflow import baseflow
from kabaret import flow


import time
import timeago
import datetime

from .file import CreateTrackedFileAction, CreateTrackedFolderAction, Revision, FileSystemMap, PublishFileAction
from .lib import AssetLib
from .runners import DefaultRunners
from .film import Films

from libreflow import _version as libreflow_version
from libreflow.thesiren import _version as libreflowthesiren_version
from packaging import version


class ProjectSettings(baseflow.ProjectSettings):
    publish_ok_files = flow.Param("").ui(editable=False)
    libreflow_version = flow.Param("0.0.0").ui(editable=False)
    libreflow_siren_version = flow.Param("0.0.0").ui(editable=False)



class User(baseflow.users.User):
    last_visit = flow.Computed()
    libreflow_version = flow.Computed().ui(label="libreflow") 
    librewflow_siren_version = flow.Computed().ui(label="libreflow.thesiren") 
    _last_visit = flow.IntParam(0)
    _last_libreflow_used_version = flow.Param(None)
    _last_libreflow_thesiren_used_version = flow.Param(None)

    def compute_child_value(self, child_value):
        if child_value is self.last_visit:
            if self._last_visit.get() == 0:
                child_value.set("never")
            else:
                
                last_connection = datetime.datetime.fromtimestamp(self._last_visit.get())
                now = datetime.datetime.now()
                child_value.set(timeago.format(last_connection, now))
        elif child_value is self.libreflow_version:
            from packaging import version
            requiered_version = version.parse(self.root().project().admin.project_settings.libreflow_version.get())
            user_current_version = self._last_libreflow_used_version.get()
            if not user_current_version:
                child_value.set("Unknown")
            else:
                user_current_version = version.parse(user_current_version)
                if requiered_version > user_current_version:
                    child_value.set("%s (!)" % str(user_current_version))
                else:
                    child_value.set("%s" % str(user_current_version))
        elif child_value is self.librewflow_siren_version:
            from packaging import version
            requiered_version = version.parse(self.root().project().admin.project_settings.libreflow_siren_version.get())
            user_current_version = self._last_libreflow_thesiren_used_version.get()
            if not user_current_version:
                child_value.set("Unknown")
            else:
                user_current_version = version.parse(user_current_version)
                if requiered_version > user_current_version:
                    child_value.set("%s (!)" % str(user_current_version))
                else:
                    child_value.set("%s" % str(user_current_version))


class CheckUsersAction(flow.Action):
    def get_buttons(self):
        return ['Cancel']

    def needs_dialog(self):
        return False

    def run(self, button):
        project = self.root().project()
        users = project.admin.users
        print("\n                       #### USERS LAST CONNECTIONS AND VERSIONS ####")
        head = "|         user         |   last seen    |          libreflow         |      libreflow.thesiren    |"
        
        h = "" 
        for i in range(0,len(head)):
            h+= "-"
        print(h)
        print(head)
        print(h)

        for u in users.mapped_items():
            name = u.name()


            print("| %-20s | %14s | %-26s | %-26s |" % (name,
                    u.last_visit.get(),
                    u.libreflow_version.get(),
                    u.librewflow_siren_version.get(),
                    ))

        print(h + "\n")


class Project(baseflow.Project,  flow.InjectionProvider):
    films = flow.Child(Films).ui(expanded=True)
    asset_lib = flow.Child(AssetLib).ui(label="Asset Library")
    admin = flow.Child(baseflow.Admin)

    _check_users = flow.Child(CheckUsersAction)

    # BOUHHHHHHHH :
    sequences = flow.Child(baseflow.film.Sequences).ui(hidden=True)

    def update_user_last_visit(self):
        user_login = self.get_user()
        requieredVersion = self.get_requiered_versions()

        if not user_login or not requieredVersion:
            return

        users = self.admin.users

        if user_login not in users.mapped_names():
            return
        user = users[user_login]

        user._last_visit.set(time.time())
        for v in requieredVersion:
            if v[0] == "libreflow.thesiren":
                user._last_libreflow_thesiren_used_version.set(v[1])
            elif v[0] == "libreflow":
                user._last_libreflow_used_version.set(v[1])

    def get_requiered_versions(self):
        '''
        return a list of dependencies
        [dependecyName, currentVersion, requieredVersion, updateNeeded(0:no|1:yes minor|2: yes major)],[]
        '''
        versions = []

        libreflow_cur_version = version.parse(libreflow_version.get_versions()["version"])
        libreflow_req_version = version.parse(self.admin.project_settings.libreflow_version.get())
        
        if libreflow_cur_version < libreflow_req_version \
                and ((libreflow_cur_version.major < libreflow_req_version.major) or \
                    (libreflow_cur_version.minor < libreflow_req_version.minor)):
            # VERY IMPORTANT UPDATE
            libreflow_needs_update = 2
        elif libreflow_cur_version < libreflow_req_version:
            # MINOR UPDATE
            libreflow_needs_update = 1
        else:
            # NO UDPATE
            libreflow_needs_update = 0

        versions.append(["libreflow", str(libreflow_cur_version), str(libreflow_req_version), libreflow_needs_update])
        
        libreflow_sir_cur_version = version.parse(libreflowthesiren_version.get_versions()["version"])
        libreflow_sir_req_version = version.parse(self.admin.project_settings.libreflow_siren_version.get())

        if libreflow_sir_cur_version < libreflow_sir_req_version \
                and ((libreflow_sir_cur_version.major < libreflow_sir_req_version.major) or \
                    (libreflow_sir_cur_version.minor < libreflow_sir_req_version.minor)):
            # VERY IMPORTANT UPDATE
            libreflow_sir_needs_update = 2
        elif libreflow_sir_cur_version < libreflow_sir_req_version:
            # MINOR UPDATE
            libreflow_sir_needs_update = 1
        else:
            # NO UDPATE
            libreflow_sir_needs_update = 0

       
        versions.append(["libreflow.thesiren", str(libreflow_sir_cur_version), str(libreflow_sir_req_version), libreflow_sir_needs_update])
    
        for v in versions:
            print(v)
        return versions

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == "libreflow.baseflow.file.CreateTrackedFileAction":
            return CreateTrackedFileAction
        elif slot_name == "libreflow.baseflow.file.CreateTrackedFolderAction":
            return CreateTrackedFolderAction
        elif slot_name == "libreflow.baseflow.file.Revision":
            return Revision
        elif slot_name == "libreflow.baseflow.file.FileSystemMap":
            return FileSystemMap
        elif slot_name == "libreflow.baseflow.runners.DefaultRunners":
            return DefaultRunners
        elif slot_name == "libreflow.baseflow.ProjectSettings":
            return ProjectSettings
        elif slot_name == "libreflow.baseflow.file.PublishFileAction":
            return PublishFileAction
        elif slot_name == "libreflow.baseflow.users.User":
            return User

