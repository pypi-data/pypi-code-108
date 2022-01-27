"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""

import os
from flask_script import Command


class GetMigrationsDirCommand(Command):
    def run(self):
        import MicroserviceApiIdentity
        print(os.path.join(MicroserviceApiIdentity.__path__[0], "migrations"))
