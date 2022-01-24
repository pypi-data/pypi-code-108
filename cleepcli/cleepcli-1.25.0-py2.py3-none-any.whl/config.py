#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    import cleep
except:
    class cleep:
        __file__ = None

DEFAULT_MODULES = ['system', 'parameters', 'cleepbus', 'audio', 'network']
MODULES_REPO_URL = {
    'system': 'https://github.com/tangb/cleepmod-system.git',
    'parameters': 'https://github.com/tangb/cleepmod-parameters.git',
    'cleepbus': 'https://github.com/tangb/cleepmod-cleepbus.git',
    'audio': 'https://github.com/tangb/cleepmod-audio.git',
    'network': 'https://github.com/tangb/cleepmod-network.git',
    'update': 'https://github.com/tangb/cleepmod-update.git',
}

PRIVATE_REPO = True
REPO_PRIVATE_URL = 'https://$GIT_USERNAME@bitbucket.org/tangb/cleep.git'
REPO_PUBLIC_URL = 'https://github.com/tangb/cleep.git' # not available yet
REPO_DIR = '/root/cleep-dev'

CORE_SRC = '%s/cleep' % REPO_DIR
CORE_DST = os.path.dirname(cleep.__file__) if cleep.__file__ else None

HTML_SRC = '%s/html' % REPO_DIR
HTML_DST = '/opt/cleep/html'

MODULES_SRC = '%s/modules' % REPO_DIR
MODULES_DST = '%s/modules' % CORE_DST
MODULES_HTML_DST = '%s/js/modules' % HTML_DST
MODULES_SCRIPTS_DST = '/opt/cleep/scripts'

BIN_SRC = '%s/bin' % REPO_DIR
BIN_DST = '/usr/bin'

MEDIA_SRC = '%s/medias' % REPO_DIR
MEDIA_DST = '/opt/cleep'

