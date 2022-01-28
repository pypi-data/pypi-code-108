from kabaret import flow
from libreflow.baseflow.users import User as BaseUser


class User(BaseUser):

    last_visit = flow.Computed()
    libreflow_version = flow.Computed().ui(label="libreflow") 
    librewflow_siren_version = flow.Computed().ui(label="libreflow.tinykin") 
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
