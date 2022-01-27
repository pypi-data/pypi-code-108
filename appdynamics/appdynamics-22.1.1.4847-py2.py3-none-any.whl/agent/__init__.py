# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Bootstrap the agent instance.

"""

from __future__ import unicode_literals
import hashlib
import logging
import os
import shutil
import sys

from appdynamics import get_version, get_agent_version, get_agent_version_file
from appdynamics.lang import import_module
from appdynamics.agent.core.logs import setup_logger
from appdynamics.pep425tags import get_abbr_impl, get_impl_ver, get_abi_tag


def hash(s):
    return hashlib.sha256(s.encode()).hexdigest()


# Les fossoyeurs de l'esperance affutent leurs longs couteaux.
def make_virtual_bindeps_package():
    """Workaround for lack of Python 2.x ABI.

    The embedded zmq libraries are specific to cp27m, cp27mu, etc. builds
    because they look for the UTF8/UTF16 string versions. Unfortunately, we
    have no way of specifying the Python ABI as part of the dependencies, so
    we can't take the correct precompiled version.

    Instead, we have bindeps ship the wide and narrow Unicode versions, and
    then construct a "virtual" bindeps package by symlinking the right
    version. We have to do this instead of just aliasing the import because
    there's otherwise no way to deal with the "appdynamics_bindes.zmq"
    imports inside the zmq code.

    """

    from appdynamics import config

    # Get the location of the actual package in the current Python env.
    src_root = get_bindeps_location()

    abi = get_abi_tag()
    pyver = '%s%s-%s' % (get_abbr_impl(), get_impl_ver(), abi)
    src_hash = hash(src_root)

    # Here's where things start to get freaky. We need to avoid sharing our
    # virtual package because it might point to a virtualenv that has since
    # been destroyed, obliterating our links. We also need to avoid sharing
    # virtual packages for different versions of the agent. This accomplishes
    # both by using the actual location of the real package as part of the
    # name of the location of our virtual package.
    prefix = "%s-%s" % (pyver, src_hash)

    dest_root = os.path.join(config.AGENT_BASE_DIR, 'lib', prefix, 'site-packages')
    dest = os.path.join(dest_root, 'appdynamics_bindeps')
    tombstone = os.path.join(dest, 'TOMBSTONE')

    tombstone_version = get_version(tombstone, noisy=False)
    agent_version = get_agent_version(noisy=False)

    if tombstone_version == 'unknown' or tombstone_version != agent_version:
        # This gets really weird because we could be racing other processes
        # trying to build the virtual package. Even if we know we are losing
        # the race, it's better to keep racing to ensure that at the end, the
        # virtual package is completely built.
        try:
            make_virtual_bindeps_destination(dest)
            zmq_target = 'zmq-' + abi

            for fn in os.listdir(src_root):
                link_virtual_bindeps_package(src_root, fn, dest, zmq_target)

            try:
                # Mark the virtual package as being completely built.
                shutil.copyfile(get_agent_version_file(), tombstone)
            except:
                pass
        except:
            logging.exception('AppDynamics Python agent startup failed making virtual package')

    sys.path.insert(0, dest_root)


def get_bindeps_location():
    import appdynamics_bindeps
    location = os.path.dirname(appdynamics_bindeps.__file__)
    del sys.modules['appdynamics_bindeps']
    return location


def make_virtual_bindeps_destination(dest):
    try:
        os.makedirs(dest)
    except:
        # Someone else beat us to the punch.
        if not os.path.exists(dest):
            raise


def link_virtual_bindeps_package(src_root, fn, dest, zmq_target):
    if fn != zmq_target and fn.startswith('zmq'):
        # A zmq package, but not the one we want to link
        return

    if fn == zmq_target:
        link_dest = os.path.join(dest, 'zmq')
    else:
        link_dest = os.path.join(dest, fn)

    src = os.path.join(src_root, fn)

    try:
        os.symlink(src, link_dest)
    except:
        # Someone else beat us to the punch.
        if not os.path.exists(link_dest):
            raise


def import_zmq():
    try:
        __import__('appdynamics_bindeps.zmq')
    except ImportError:
        make_virtual_bindeps_package()


import_zmq()


from appdynamics import config
from appdynamics.agent.core.logs import configure_logging
from appdynamics.agent.core.agent import Agent
from appdynamics.agent.interceptor import BT_INTERCEPTORS, add_hook

_agent = None


def configure(environ=None):
    agent_config = config.parse_environ()
    if environ:
        agent_config.update(config.parse_environ(environ))

    config.merge(agent_config)
    configure_logging()

    return config.validate_config(agent_config)


def bootstrap(agent=None):
    try:
        global _agent

        _agent = agent or Agent()
        hook = add_hook(_agent)

        for mod, patch in BT_INTERCEPTORS:
            hook.call_on_import(mod, patch)

        _agent.module_interceptor = hook
        return _agent
    except:
        setup_logger('appdynamics.agent').exception('Error bootstrapping AppDynamics agent; disabling.')
        return None


def get_agent_instance():
    if _agent is None:
        return bootstrap()
    else:
        return _agent


def load_sitecustomize():
    # Load the customer's 'sitecustomize' module if it exists.

    # We have to be very careful here.  If 'sitecustomize' doesn't exist in
    # `sys.modules` when this function returns, a KeyError is raised on Python
    # 3.3 when running inside a virtualenv.  There is no way to catch the
    # exception without patching 'site.py', so we have to leave our own
    # sitecustomize module around if there are no others to load.
    mod = sys.modules.pop('sitecustomize', None)
    try:
        mod = import_module('sitecustomize')
    except ImportError:
        pass
    sys.modules.update(sitecustomize=mod)
