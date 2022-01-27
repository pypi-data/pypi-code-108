from django.contrib.auth.models import User

import reversion


reversion.register(User)
