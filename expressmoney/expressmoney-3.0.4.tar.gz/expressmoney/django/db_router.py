class AuthRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    AUTH_DB = 'auth_db'
    route_app_labels = {'auth', 'contenttypes', 'admin'}

    def db_for_read(self, model, **_hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        model_meta = getattr(model, '_meta')
        if model_meta.app_label in self.route_app_labels:
            return self.AUTH_DB
        return None

    def db_for_write(self, model, **_hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        model_meta = getattr(model, '_meta')
        if model_meta.app_label in self.route_app_labels:
            return self.AUTH_DB
        return None

    def allow_relation(self, obj1, obj2, **_hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        obj1_meta = getattr(obj1, '_meta')
        obj2_meta = getattr(obj2, '_meta')
        if (
                obj1_meta.app_label in self.route_app_labels or
                obj2_meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, _model_name=None, **_hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == self.AUTH_DB
        return None
