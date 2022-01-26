# -*- coding: utf-8 -*-
#
# Macro that pulls a checklist template from a wiki page, and renders it as
# a checklist in a ticket description.
#
import json, time
import pkg_resources
from pkg_resources import resource_filename

from trac.core import implements, Component
from trac.env import IEnvironmentSetupParticipant
from trac.config import Option
from trac.db.api import DatabaseManager
from trac.db.schema import Table, Column

from trac.web.chrome import ITemplateProvider, add_stylesheet, add_script, add_script_data
from trac.web.api  import IRequestHandler, IRequestFilter

from trac.wiki.macros import WikiMacroBase
from trac.wiki.model import WikiPage
from trac.wiki.formatter import format_to_html
from trac.util.html import unescape

# database schema version / updates (stored in "system" table)
PLUGIN_NAME = 'TracChecklist'
PLUGIN_VERSION = 1

class ChecklistMacro(WikiMacroBase):
    """Loads checklist template from wiki page, display it in ticket description.

    Implements the following trac extensions points:

        ITemplateProvider - registers templates used by this plugin

    https://trac.edgewall.org/wiki/TracDev/PluginDevelopment/ExtensionPoints/
    """
    _description = "Inserts a checklist sourced from a wiki page template."
    implements(ITemplateProvider)

    def get_htdocs_dirs(self):
        return [('checklist', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'htdocs')]

    def expand_macro(self, formatter, name, content):
        """Expand the macro into the desired checklist.

        self.env    : https://trac.edgewall.org/browser/trunk/trac/env.py
        self.config : https://trac.edgewall.org/browser/trunk/trac/config.py

        formatter.resource : id of the ticket calling the macro
        formatter.href     : url info (base, path_safe, etc.)
        formatter.wiki     : https://trac.edgewall.org/browser/trunk/trac/wiki/api.py
        formatter.context  : metadata on the called page with the macro in it
        formatter.req      : web request that called the page with the macro

        name        : the name of the macro being called (Checklist)
        content     : the page name string, provided as the argument
        """

        # get current checklist state from db
        '''
        realm     : wiki, ticket, etc.
        resource  : id of page calling the macro
        checklist : name of checklist called by macro
        status    = ? (JSON encoded checkbox status)
        '''
        query  = ("SELECT status FROM checklist WHERE " +
                  "realm     = '"+ str(formatter.resource.realm) +"' AND " +
                  "resource  = '"+ str(formatter.resource.id   ) +"' AND " +
                  "checklist = '"+ str(content                 ) +"' ")

        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute(query)
            row = cursor.fetchone()

            if not row:
                check_dict = {}
            else:
                check_dict = json.loads(row[0])

        # get the template wiki page (create if needed)
        root = Option('checklist', 'template_root', default='TracChecklist',
                    doc="wiki page root for checklist templates")

        root = self.config.get('checklist', 'template_root')
        name = str(root) + '/' + content
        name = name.replace('//','/')
        page = WikiPage(self.env, name)

        if page.exists == False:
            return("CHECKLIST ERROR: \n template '" + name + "' does not exist.")

        # strip wiki page header & convert to html
        wiki = page.text[page.text.find('----')+4:]
        html = format_to_html(self.env, formatter.context, wiki)

        # parse template for steps
        # steps start with [x] and end with \\, which converts to <br />
        check_index = 0
        check_start = html.find('[x]')

        while check_start > -1:
            check_end   = html.find('<br />',check_start)+6
            check_step  = 'step_' + str(check_index)
            check_label = html[check_start+3:check_end]

            check_box   = ("<label class='container'>" + check_label +
                           "<input type='checkbox' " +
                           "name='step_" + str(check_index) + "' " +
                           "value='done' ")

            if check_step in check_dict:
                check_box += "checked"

            check_box += "><span class='checkmark'></span></label>"
            html = html[0:check_start] + check_box + html[check_end:]

            check_index +=1
            check_start = html.find('[x]')

        # template header info + form
        dest  = formatter.req.href('/checklist/update')
        head  = "<form class='checklist' method='post' action='"+dest+"'> \n"
        head += "   <div class='source'>                                  \n"
        head += ("       TracChecklist: <a href='" + formatter.req.href("/wiki/" + name) +
                 "'>" + name + "</a>\n")
        head += "   </div>"

        # template footer / form
        backpath   = formatter.req.href(formatter.req.path_info)
        form_token = formatter.req.form_token
        realm      = str(formatter.resource.realm)
        resource   = str(formatter.resource.id   )
        checklist  = str(content                 )

        foot  = "<input type='hidden' name='__backpath__' value='" + backpath   + "'>\n"
        foot += "<input type='hidden' name='__FORM_TOKEN' value='" + form_token + "'>\n"
        foot += "<input type='hidden' name='realm'        value='" + realm      + "'>\n"
        foot += "<input type='hidden' name='resource'     value='" + resource   + "'>\n"
        foot += "<input type='hidden' name='checklist'    value='" + checklist  + "'>\n"
        foot += "<br>"
        foot += "<input class='button' type='submit' value='Save Checklist'> \n"
        foot += "</form>"

        # add stylesheet definitions to the page
        # note pattern is 'checklist/filename.ext' (no htdocs dir)
        add_stylesheet(formatter.req,'checklist/checklist.css')

        # assemble output
        out = unescape(head + html + foot)

        # return the final output
        return out


class ChecklistUpdate(Component):
    """Handles item check off and instance saving.

    Implements the following trac extensions point: IRequestHandler
    https://trac.edgewall.org/wiki/TracDev/PluginDevelopment/ExtensionPoints/
    """
    _description = "Handles checklist updates, submit & save."
    implements(IRequestHandler)

    def match_request(self, req):
        match = req.path_info.endswith('checklist/update')
        return match

    def process_request(self, req):
        """saves updated checklist state to the database.

        Args:
            req (object): web request that called the page with the macro
        """
        try:

            # get form data and new status as JSON string
            args      = dict(req.args)
            backpath  = args['__backpath__']
            realm     = args['realm']
            resource  = args['resource']
            checklist = args['checklist']
            steps     = {k:v for k,v in args.iteritems() if k.startswith('step')}
            status    = json.dumps(steps)

            # save to db
            query   = ("REPLACE INTO checklist (realm,resource,checklist,status) " +
                       "VALUES ('" + realm + "','" + resource + "','" + checklist +
                       "','" + status + "')")

            self.env.db_transaction(query)
            buffer = "OK"

            if backpath is not None:
                req.send_response(302)
                req.send_header('Content-Type', 'text/plain')
                req.send_header('Location', backpath)
                req.send_header('Content-Length', str(len(buffer)))
                req.end_headers()
                req.write(buffer)
            else:
                req.send_response(200)
                req.send_header('Content-Type', 'text/plain')
                req.send_header('Content-Length', str(len(buffer)))
                req.end_headers()
                req.write(buffer)

        except Exception as e:

            buffer = "ERROR:" + str(e)
            req.send_response(500)
            req.send_header('Content-type', 'text/plain')
            req.send_header('Content-Length', str(len(buffer)))
            req.end_headers()
            req.write(buffer)


class ChecklistInsert(Component):
    """Adds dropdown selector in ticket description edit box to insert a checklist.

    Implements the following trac extensions point:

        ITemplateProvider - registers templates used by this plugin
        IRequestFilter - alters ticket display (trac.web.api.IRequestFilter)

    https://trac.edgewall.org/wiki/TracDev/PluginDevelopment/ExtensionPoints/
    https://trac.edgewall.org/wiki/TracDev/PortingFromGenshiToJinja#ReplacingITemplateStreamFilter
    """
    _description = "Adds dropdown selector in ticket description edit box to insert a checklist."
    implements(ITemplateProvider, IRequestFilter)

    def get_htdocs_dirs(self):
        return [('checklist', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'htdocs')]

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, metadata):
        """Adds checklist drop-down selector in ticket description edit box.

        Args:
            req      (obj): web request object
            template (str): web template that called this function
            data     (obj): ticket attributes
            metadata (obj): ticket attributes

        Returns:
            template (str): unchanged from input
            data     (obj): unchanged from input
            metadata (obj): unchanged from input
        """
        # only alter specific ticket templates
        self.log.debug("TracChecklist #### template: %s", template)
        if template in ['ticket.html']:

            # list of available checklist templates (pages) under root wiki page
            templates = []
            root = Option('checklist', 'template_root', default='TracChecklist',
                        doc="wiki page root for checklist templates")
            root      = self.config.get('checklist', 'template_root')
            query     = ("SELECT name FROM wiki WHERE version = 1 AND " +
                         "name LIKE '%"+ root +"%' ")

            with self.env.db_query as db:
                cursor = db.cursor()
                cursor.execute(query)
                for row in cursor.fetchall():
                    if row[0] != root:
                        templates.append(row[0].replace(root+'/',''))

            # add new ticket components (CSS, jquery, template list)
            add_stylesheet(req, 'checklist/menu.css')
            add_script_data(req, { 'templates': templates } )
            add_script(req, 'checklist/menu.js')

        return (template, data, metadata)


class ChecklistSetup(Component):
    """Handles environment upgrdes / setup.

    Implements the following trac extensions points:

        IEnvironmentSetupParticipant - updates environment for plugin use

    https://trac.edgewall.org/wiki/TracDev/PluginDevelopment/ExtensionPoints/
    """
    _description = "Handles environment setup / upgrades."
    implements(IEnvironmentSetupParticipant)

    def environment_created(self):
        self.log.debug("creating environment for TracChecklist plugin.")
        # Same work is done for environment created and upgraded
        self.upgrade_environment()

    def environment_needs_upgrade(self):
        dbm = DatabaseManager(self.env)
        ver = dbm.get_database_version(PLUGIN_NAME)
        needs_upgrade = dbm.needs_upgrade(PLUGIN_VERSION, PLUGIN_NAME)
        self.log.debug("TracChecklist plugin v%s - upgrade needed: %s", ver, needs_upgrade)
        if needs_upgrade:
            self.log.info("environment requires upgrade for TracChecklist plugin.")
        return needs_upgrade

    def upgrade_environment(self):
        dbm = DatabaseManager(self.env)
        ver = dbm.get_database_version(PLUGIN_NAME)
        self.log.info("upgrading environment for TracChecklist plugin from v%s to v%s.", ver, PLUGIN_VERSION)

        # check if this is first use (table does not exist)
        if ver == 0:

            #create the database checklist table
            SCHEMA = [ Table('checklist', key=('realm','resource','checklist')) [
                        Column('realm'    , type='text'),
                        Column('resource' , type='text'),
                        Column('checklist', type='text'),
                        Column('status'   , type='text')] ]

            self.log.info("creating checklist table ...")
            dbm.create_tables(SCHEMA)

            # create the wiki root page from file
            page = str(pkg_resources.resource_string(__name__, 'plugin.wk'))
            tstamp = int(time.time() * 1000000)
            query = "INSERT INTO wiki (name, version, time, author, text) "
            query += "VALUES ('TracChecklist', 1, %s, 'trac', %s)"
            self.log.info("creating checklist wiki root ...")
            self.env.db_transaction(query, (tstamp, page))

            # update version number in the 'system' table for this plugin
            dbm.set_database_version(PLUGIN_VERSION, PLUGIN_NAME)

        else:
            dbm.upgrade(PLUGIN_VERSION, PLUGIN_NAME, 'checklist.upgrades')