from rox.server.flags.rox_flag import RoxFlag
from rox.core.entities.rox_string import RoxString
from rox.core.entities.rox_int import RoxInt
from rox.core.entities.rox_double import RoxDouble


class ServerEntitiesProvider:
    def create_flag(self, default_value):
        return RoxFlag(default_value)

    def create_string(self, default_value, options):
        return RoxString(default_value, options)

    def create_int(self, default_value, options):
        return RoxInt(default_value, options)

    def create_double(self, default_value, options):
        return RoxDouble(default_value, options)
