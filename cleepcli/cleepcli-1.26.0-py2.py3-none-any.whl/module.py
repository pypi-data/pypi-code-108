#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import Console
import logging
from . import config
import shutil
import re

class Module():
    """
    Module class
    """

    GIT_IGNORE = """**/*.pyc
**/.coverage
**/.coveralls.yml
docs/*.zip
docs/*.txt
docs/*.xml
docs/source
docs/_build
.vscode
**/*.swp
"""
    CHANGELOG = """# Changelog

## [UNRELEASED] - YYYY-MM-DD
### Added
- First release

    """
    DESC_SKEL = """{
    \\"icon\\": \\"help-circle-outline\\",
    \\"global\\": {
        \\"js\\": [\\"%(MODULE_NAME)s.service.js\\"],
        \\"html\\": [],
        \\"css\\": []
    },
    \\"config\\": {
        \\"js\\": [\\"%(MODULE_NAME)s.config.js\\"],
        \\"html\\": [\\"%(MODULE_NAME)s.config.html\\"],
        \\"css\\": []
    }
}
    """
    ANGULAR_SERVICE_SKEL = """/**
 * %(MODULE_NAME_CAPITALIZED)s service.
 * Handle %(MODULE_NAME)s application requests.
 * Service is the place to store your application content (it is a singleton) and
 * to provide your application functions.
 */
angular
.module('Cleep')
.service('%(MODULE_NAME)sService', ['\$rootScope', 'rpcService',
function(\$rootScope, rpcService) {
    var self = this;

    /**
     * Call backend execute_command command
     */
    self.executeCommand = function() {
        return rpcService.sendCommand('execute_command', '%(MODULE_NAME)s');
    };

    /**
     * Call backend configure_value command
     */
    self.configureValue = function(value) {
        return rpcService.sendCommand('configure_value', '%(MODULE_NAME)s', {
            'value': value,
        });
    };

    /**
     * Catch an.app.event event
     */
    /*\$rootScope.\$on('an.app.event', function(event, uuid, params) {
        console.log('Event an.app.event received with parameters:', parameters);
    });*/
}]);"""
    ANGULAR_CONTROLLER_SKEL = """/**
 * %(MODULE_NAME_CAPITALIZED)s config component
 * Handle %(MODULE_NAME)s application configuration
 * If your application doesn't need configuration page, delete this file and its references into desc.json
 */
angular
.module('Cleep')
.directive('%(MODULE_NAME)sConfigComponent', ['\$rootScope', 'cleepService', 'toastService', '%(MODULE_NAME)sService',
function(\$rootScope, cleepService, toastService, %(MODULE_NAME)sService) {

    var %(MODULE_NAME)sConfigController = function() {
        var self = this;
        // use this config variable in all your app (controller and view) to always have up-to-date config values
        self.config = {};
        self.message = 'message';
        self.checkbox = true;
        self.slider = 25;

        /**
         * Init component
         */
        self.\$onInit = function() {
            // get module config
            cleepService.getModuleConfig('%(MODULE_NAME)s');
        };

        /**
         * Keep app configuration in sync
         */
        \$rootScope.\$watch(function() {
            return cleepService.modules['%(MODULE_NAME)s'].config;
        }, function(newVal, oldVal) {
            if(newVal && Object.keys(newVal).length) {
                Object.assign(self.config, newVal);
            }
        });

        self.setMessage = function() {
            %(MODULE_NAME)sService.configureValue(self.message)
                .then(function(response) {
                    console.log('Response:', response);
                    if (response.error) {
                        toastService.error('Command failed: ' + response.message);
                        return;
                    }
                    toastService.success('Command succeed');
                })
                .finally(function() {
                    cleepService.reloadModuleConfig('%(MODULE_NAME)s');
                });
        };

        self.executeCommand = function() {
            %(MODULE_NAME)sService.executeCommand()
                .finally(function() {
                    cleepService.reloadModuleConfig('%(MODULE_NAME)s');
                });
        };

        self.updateCheckbox = function() {
            %(MODULE_NAME)sService.configureValue(self.checkbox)
                .finally(function() {
                    cleepService.reloadModuleConfig('%(MODULE_NAME)s');
                });
        };

        self.setSlider = function() {
            %(MODULE_NAME)sService.configureValue(self.slider)
                .finally(function() {
                    cleepService.reloadModuleConfig('%(MODULE_NAME)s');
                });
        };
    };

    return {
        templateUrl: '%(MODULE_NAME)s.config.html',
        replace: true,
        scope: true,
        controller: %(MODULE_NAME)sConfigController,
        controllerAs: '%(MODULE_NAME)sCtl',
    };
}]);"""
    ANGULAR_CONTROLLER_TEMPLATE_SKEL = """<div layout=\\"column\\" layout-padding ng-cloak>

    <md-list ng-cloak>

        <!-- A configuration section. It is a good way to make separation between different kind of parameters -->
        <md-subheader class=\\"md-no-sticky\\">A section header</md-subheader>

        <!-- list item with single line description -->
        <md-list-item>
            <!-- generic cleep icon, use it as default line icon -->
            <md-icon md-svg-icon=\\"chevron-right\\"></md-icon>
            <p>One line description</p>
        </md-list-item>

        <!-- list item with double line description -->
        <md-list-item class=\\"md-2-line\\">
            <md-icon md-svg-icon=\\"chevron-right\\"></md-icon>
            <div class=\\"md-list-item-text\\">
                <h3>Two line description</h3>
                <p>Sub line uses smallest font</p>
            </div>
        </md-list-item>

        <!-- list item with button -->
        <md-list-item>
            <md-icon md-svg-icon=\\"chevron-right\\"></md-icon>
            <p>Button</p>
            <md-button ng-click=\\"%(MODULE_NAME)sCtl.executeCommand()\\" class=\\"md-raised md-primary md-secondary\\">
                <md-icon md-svg-icon=\\"cog\\"></md-icon>
                Button label
            </md-button>
        </md-list-item>

        <!-- list item with text input -->
        <md-list-item>
            <md-icon md-svg-icon=\\"chevron-right\\"></md-icon>
            <p>Text input</p>
            <md-input-container md-no-float class=\\"md-secondary no-margin\\" layout=\\"row\\" layout-align=\\"start center\\" layout-padding>
                <div class=\\"no-md-error\\">
                    <input ng-model=\\"%(MODULE_NAME)sCtl.message\\" placeholder=\\"message\\" aria-label=\\"Message\\" class=\\"no-margin\\">
                </div>
                <md-button ng-click=\\"%(MODULE_NAME)sCtl.setMessage()\\" class=\\"md-raised md-primary\\">
                    <md-icon md-svg-icon=\\"pencil\\"></md-icon>
                </md-button>
            </md-input-container>
        </md-list-item>

        <!-- list item with checkbox -->
        <md-list-item>
            <md-icon md-svg-icon=\\"chevron-right\\"></md-icon>
            <p>Checkbox</p>
            <md-checkbox
                class=\\"md-secondary\\"
                ng-model=\\"%(MODULE_NAME)sCtl.checkbox\\"
                ng-change=\\"%(MODULE_NAME)sCtl.updateCheckbox()\\"
                aria-label=\\"Checkbox\\"
            >
            </md-checkbox>
        </md-list-item>

        <!-- list item with slider -->
        <md-list-item>
            <md-icon md-svg-icon=\\"chevron-right\\"></md-icon>
            <p>Slider</p>
            <div class=\\"md-secondary\\">
                <md-slider
                    ng-model=\\"%(MODULE_NAME)sCtl.slider\\"
                    ng-model-options=\\"{debounce: 1000}\\"
                    ng-change=\\"%(MODULE_NAME)sCtl.setSlider()\\"
                    min=\\"0\\"
                    max=\\"100\\"
                    aria-label=\\"Slider\\"
                    md-discrete
                >
                </md-slider>
            </div>
        </md-list-item>

    </md-list>

</div>
    """
    PYTHON_MODULE_SKEL = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.exception import MissingParameter, InvalidParameter, CommandError
from cleep.core import CleepModule
from cleep.common import CATEGORIES

class %(MODULE_NAME_CAPITALIZED)s(CleepModule):
    \\"\\"\\"
    %(MODULE_NAME_CAPITALIZED)s application
    \\"\\"\\"
    MODULE_AUTHOR = 'TODO'
    MODULE_VERSION = '0.0.0'
    MODULE_DEPS = []
    MODULE_DESCRIPTION = 'TODO'
    MODULE_LONGDESCRIPTION = 'TODO'
    MODULE_TAGS = []
    MODULE_CATEGORY = CATEGORIES.APPLICATION
    MODULE_URLINFO = 'https://www.google.com'
    MODULE_URLHELP = None
    MODULE_URLSITE = None
    MODULE_URLBUGS = None

    MODULE_CONFIG_FILE = '%(MODULE_NAME)s.conf'
    DEFAULT_CONFIG = {}

    def __init__(self, bootstrap, debug_enabled):
        \\"\\"\\"
        Constructor

        Args:
            bootstrap (dict): bootstrap objects
            debug_enabled: debug status
        \\"\\"\\"
        CleepModule.__init__(self, bootstrap, debug_enabled)

    def _configure(self):
        \\"\\"\\"
        Configure module.
        Use this function to configure your variables and local stuff that is not blocking.
        At this time other applications are not started and all your command requests will fail.
        \\"\\"\\"
        pass

    def _on_start(self):
        \\"\\"\\"
        Start module.
        Use this function to start your tasks.
        At this time all applications are started and should respond to your command requests.
        \\"\\"\\"
        pass

    def _on_stop(self):
        \\"\\"\\"
        Stop module
        Use this function to stop your tasks and close your external connections.
        \\"\\"\\"
        pass

    def on_event(self, event):
        \\"\\"\\"
        Event received

        Args:
            event (MessageRequest): event data
        \\"\\"\\"
        # execute here actions when you receive a specific event:
        #  - on time event => cron task
        #  - on alert event => send email or push message
        #  - ...
        pass

    def execute_command(self):
        \\"\\"\\"
        This is a simple command execution

        Returns:
            bool: returns always True
        \\"\\"\\"
        self.logger.info('execute_command called')
        return True

    def configure_value(self, value):
        \\"\\"\\"
        This function is an example of how to pass value from frontend to backend

        Args:
            value (any): a value
        \\"\\"\\"
        self.logger.info('set_value called with param value=%%s' %% value)

    def _unexposed_command(self):
        \\"\\"\\"
        A function that starts with _ if not exposed to outside. But it can be used inherited class
        \\"\\"\\"
        self.logger.info('Unexposed function')

    def __another_unexposed_command(self):
        \\"\\"\\"
        A function that starts with __ if not exposed to outside. This kind of function is also declared as private in Python
        and cannot be used elsewhere than in this class itself.
        \\"\\"\\"
        self.logger.info('Another unexposed function')
"""
    TEST_DEFAULT = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
import sys
sys.path.append('../')
from backend.%(MODULE_NAME)s import %(MODULE_NAME_CAPITALIZED)s
from cleep.exception import InvalidParameter, MissingParameter, CommandError, Unauthorized
from cleep.libs.tests import session
from mock import Mock, patch

# You can launch all your tests manually using this command:
#   python3 -m unittest test_%(MODULE_NAME)s.Test%(MODULE_NAME_CAPITALIZED)s
# or a specific test with command:
#   python3 -m unittest test_%(MODULE_NAME)s.Test%(MODULE_NAME_CAPITALIZED)s.test__on_configure
# You can get tests coverage with command:
#   coverage run --omit="*/lib/python*/*","test_*" --concurrency=thread test_%(MODULE_NAME)s.py; coverage report -m -i
# or you can simply use developer application that allows you to perform all tests and coverage directly from web interface
class Test%(MODULE_NAME_CAPITALIZED)s(unittest.TestCase):

    def setUp(self):
        # change here logging.CRITICAL to logging.DEBUG to enable logging during tests writings
        logging.basicConfig(level=logging.FATAL, format='%%(asctime)s %%(name)s:%%(lineno)d %%(levelname)s : %%(message)s')
        self.session = session.TestSession(self)

    def tearDown(self):
        # clean session
        self.session.clean()

    def init(self, start=True):
        \\"\\"\\"
        Call this function at beginning of every test cases. By default it starts your app, but if you specify start=False,
        the application must be started manually which is useful in some cases like testing _on_configure app function.
        \\"\\"\\"
        # next line instanciates your module, overwriting all useful stuff to isolate your module for tests
        self.module = self.session.setup(%(MODULE_NAME_CAPITALIZED)s)
        if start:
            self.session.start_module(self.module)

    # Write your tests here defining functions starting with \\"test_\\"
    # See official documentation https://docs.python.org/3/library/unittest.html
    # def test__on_configure(self):
    #   self.init(start=False)
    #   # create your mocks...
    #
    #   self.module._on_configure()
    #
    #   # check your mocks

    # Write another test. A test case always starts with \\"test_\\"
    # def test_my_function(self):
    #   self.init()
    #   # create your mocks
    #
    #   result = self.module.my_function()
    #
    #   # checks your mocks or function result

# do not remove code below, otherwise test won't run
if __name__ == '__main__':
    unittest.main()
    """
    DOCS_CONF_PY = """# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.abspath('../'))

project = ''
copyright = ''
author = ''
version = ''
release = ''
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
]
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    '**/*.pyc',
]
add_module_names = False
pygments_style = None
html_static_path = [
    '_static',
]
html_css_files = [
    '_static/cleep.css',
]
html_theme = 'sphinx_rtd_theme'
todo_include_todos = True
html_theme_options = {
    'prev_next_buttons_location': None,
    'style_external_links': True,
    'style_nav_header_background': '#607d8b',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 6,
    'includehidden': False,
}

def setup(app):
    app.add_css_file('cleep.css')
    """
    DOCS_INDEX_RST = """%(TITLE)s
%(LINE)s

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   source/modules

Indices and tables
==================

* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`
    """
    DOCS_CLEEP_CSS = """.wy-nav-side {
    background: #90a4ae !important;
}
.wy-side-nav-search {
    background: #607d8b !important;
}
.rst-content dl:not(.docutils) dt {
    color: #d32f2f !important;
    background: #ffcdd2 !important;
    border-top: solid 3px #b71c1c !important;
 }
.rst-content dl:not(.docutils) dl dt {
    border: none !important;
    border-left: solid 3px #d32f2f !important;
    background: #eceff1 !important;
    color: #607d8b !important;
}
a:visited, a:hover {
    color: #d32f2f;
}
a {
    color: #000000;
}
a:visited.icon.icon-home, a.icon.icon-home {
    color: #FFFFFF !important;
}
a:hover.icon.icon-home {
    color: #d32f2f;
}
.wy-menu-vertical header,.wy-menu-vertical p.caption {
    color: #000000;
}
    """

    def __init__(self):
        """
        Constructor
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, module_name):
        """
        Create module skeleton

        Args:
            module_name (string): module name
        """
        module_name = re.sub('[^0-9a-zA-Z]+', '', module_name).lstrip('0123456789').lower()
        self.logger.debug('Module name to create: %s' % module_name)
        path = os.path.join(config.MODULES_SRC, module_name)
        self.logger.info('Creating module "%s" in "%s"' % (module_name, path))
        
        if os.path.exists(path):
            self.logger.error('Module "%s" already exists in "%s"' % (module_name, path))
            return False

        title = 'Welcome to %s\'s documentation!' % module_name.capitalize()
        templates = {
            'ANGULAR_SERVICE': self.ANGULAR_SERVICE_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'ANGULAR_CONTROLLER': self.ANGULAR_CONTROLLER_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'ANGULAR_CONTROLLER_TEMPLATE': self.ANGULAR_CONTROLLER_TEMPLATE_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DESC': self.DESC_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'PYTHON_MODULE': self.PYTHON_MODULE_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'TEST_DEFAULT': self.TEST_DEFAULT % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DOCS_CONF_PY': self.DOCS_CONF_PY % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DOCS_INDEX_RST': self.DOCS_INDEX_RST % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize(), 'TITLE': title, 'LINE': '='*len(title)},
            'DOCS_CLEEP_CSS': self.DOCS_CLEEP_CSS,
            'CHANGELOG': self.CHANGELOG,
            'GIT_IGNORE': self.GIT_IGNORE,
        }

        c = Console()
        resp = c.command("""
/bin/mkdir -p "%(MODULE_DIR)s/backend"
/usr/bin/touch "%(MODULE_DIR)s/backend/__init__.py"
/bin/echo "%(PYTHON_MODULE)s" > %(MODULE_DIR)s/backend/%(MODULE_NAME)s.py
/bin/mkdir -p "%(MODULE_DIR)s/frontend"
/bin/echo "%(DESC)s" > %(MODULE_DIR)s/frontend/desc.json
/bin/echo "%(ANGULAR_SERVICE)s" > %(MODULE_DIR)s/frontend/%(MODULE_NAME)s.service.js
/bin/echo "%(ANGULAR_CONTROLLER)s" > %(MODULE_DIR)s/frontend/%(MODULE_NAME)s.config.js
/bin/echo "%(ANGULAR_CONTROLLER_TEMPLATE)s" > %(MODULE_DIR)s/frontend/%(MODULE_NAME)s.config.html
/bin/mkdir -p "%(MODULE_DIR)s/tests"
/usr/bin/touch "%(MODULE_DIR)s/tests/__init__.py"
/bin/echo "%(TEST_DEFAULT)s" > %(MODULE_DIR)s/tests/test_%(MODULE_NAME)s.py
/bin/mkdir -p "%(MODULE_DIR)s/docs"
/bin/echo "%(DOCS_CONF_PY)s" > %(MODULE_DIR)s/docs/conf.py
/bin/echo "%(DOCS_INDEX_RST)s" > %(MODULE_DIR)s/docs/index.rst
/bin/mkdir -p "%(MODULE_DIR)s/docs/_static"
/bin/echo "%(DOCS_CLEEP_CSS)s" > %(MODULE_DIR)s/docs/_static/cleep.css
/bin/echo "%(CHANGELOG)s" > %(MODULE_DIR)s/CHANGELOG.md
/bin/echo "%(GIT_IGNORE)s" > %(MODULE_DIR)s/.gitignore
""" % {
            'MODULE_DIR': path,
            'MODULE_NAME': module_name,
            'DESC': templates['DESC'],
            'ANGULAR_SERVICE': templates['ANGULAR_SERVICE'],
            'ANGULAR_CONTROLLER': templates['ANGULAR_CONTROLLER'],
            'ANGULAR_CONTROLLER_TEMPLATE': templates['ANGULAR_CONTROLLER_TEMPLATE'],
            'PYTHON_MODULE': templates['PYTHON_MODULE'],
            'TEST_DEFAULT': templates['TEST_DEFAULT'],
            'DOCS_CONF_PY': templates['DOCS_CONF_PY'],
            'DOCS_INDEX_RST': templates['DOCS_INDEX_RST'],
            'DOCS_CLEEP_CSS': templates['DOCS_CLEEP_CSS'],
            'CHANGELOG': templates['CHANGELOG'],
            'GIT_IGNORE': templates['GIT_IGNORE'],
        }, 10)
        if resp['error'] or resp['killed']:
            self.logger.error('Error occured while creating application: %s' % ('killed' if resp['killed'] else resp['stderr']))
            shutil.rmtree(path)
            return False
        
        self.logger.info('Done')
        return True

    def delete(self, module_name):
        """
        Delete installed files for specified  module

        Args:
            module_name (string): module name
        """
        #build all module paths
        paths = [
            os.path.join(config.MODULES_DST, module_name),
            os.path.join(config.MODULES_HTML_DST, module_name),
            os.path.join(config.MODULES_SCRIPTS_DST, module_name),
        ]
        self.logger.info('Deleting module "%s" in "%s"' % (module_name, paths))
        
        deleted = False
        for path in paths:
            if os.path.exists(path):
                shutil.rmtree(path)
                self.logger.debug('Directory "%s" deleted' % path)
                deleted = True

        if not deleted:
            self.logger.info('Nothing has been deleted')

        return True

