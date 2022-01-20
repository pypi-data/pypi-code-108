# -*- coding: utf-8 -*-
class Visible(object):

    class runtime(object):
        create_func = 'set_runtime'

    class setup(object):
        create_func = 'set_setup'

    class hidden(object):
        create_func = 'set_hidden'

    class common(object):
        create_func = 'set_common'


class Access(object):

    class read_only(object):
        create_func = 'set_read_only'

    class read_write(object):
        create_func = 'set_read_write'


class Priority(object):

    class trivial(object):
        create_func = 'set_trivial'

    class minor(object):
        create_func = 'set_minor'

    class major(object):
        create_func = 'set_major'

    class critical(object):
        create_func = 'set_critical'

    class blocker(object):
        create_func = 'set_blocker'

