"""
Initialize the basic flask server with acrive directory authentification
"""
import requests

# global store for an update scheduler controlled by the updateCrontab entry
autoUpdateScheduler = None


def SecureFlask(appName, dashApps=None, plotApi=None, updateApi=None, updateCrontab=None):
    print(" # Init SecureFlask: {0}".format(appName))
    # basic imports
    from os import path, environ
    from json import dumps
    from datetime import datetime as dt
    import uuid
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    global autoUpdateScheduler

    # check if uwsgi is in use
    useUwsgi = True
    try:
        import uwsgi
    except:
        useUwsgi = False

    #import configuration
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read('/defaults.cfg')
    # create the Flask app
    from flask import Flask, session, redirect, url_for, request, send_file, make_response
    from flask_cors import CORS, cross_origin
    flaskApp = Flask(appName)
    CORS(flaskApp, support_credentials=True)

    flaskApp.config.update(
        TESTING=cfg.getboolean('Flask', 'debug', fallback=True),
        SECRET_KEY=cfg.get('Flask', 'secret_key',
                           fallback='5vqUQ6MsEmvZpAsQBYpppxA8gsLQSv'),
        SESSION_COOKIE_PATH="/",
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True,
    )

    scheme = cfg.get('Flask', 'scheme', fallback='http')

    # use HOST from the environment or from the config
    host = environ.get('SERVER_HOST', cfg.get(
        'Flask', 'host', fallback='localhost'))

    # use the PORT from the environment or take 5000
    port = int(environ.get('INTERNAL_PORT', 5000))
    # load the static server port from the config file
    staticPort = int(cfg.get('Ports', 'static', fallback='5000'))
    # load the static server port from the config file
    backendPort = int(cfg.get('Ports', 'backend', fallback='4440'))

    # handle OAuth login
    ###################
    from authlib.integrations.flask_client import OAuth
    oauth = OAuth(flaskApp)

    # get important variables from config
    consumer_key = cfg.get('OAuth', 'app_client', fallback='')
    consumer_secret = cfg.get('OAuth', 'app_secret', fallback='')
    tenant_name = cfg.get('OAuth', 'app_tenant', fallback='')

    # auth = oauth.remote_app(
    #     'microsoft',
    #     consumer_key=consumer_key,
    #     consumer_secret=consumer_secret,
    #     client_kwargs={'scope': 'User.Read'},
    #     base_url='https://graph.microsoft.com/v1.0/',
    #     request_token_url=None,
    #     access_token_method='POST',
    #     access_token_url=str.format(
    #         'https://login.microsoftonline.com/{0}/oauth2/v2.0/token', tenant_name),
    #     authorize_url=str.format(
    #         'https://login.microsoftonline.com/{0}/oauth2/v2.0/authorize', tenant_name)
    # )

    microsoft = oauth.register(
        'microsoft',
        client_id=consumer_key,
        client_secret=consumer_secret,
        client_kwargs={'scope': 'User.Read'},
        api_base_url='https://graph.microsoft.com/v1.0/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url=str.format(
            'https://login.microsoftonline.com/{0}/oauth2/v2.0/token', tenant_name),
        authorize_url=str.format(
            'https://login.microsoftonline.com/{0}/oauth2/v2.0/authorize', tenant_name)
    )

    # extract the token from current session
    # @auth.tokengetter
    # def get_session_token():
    #     return session.get('auth_token')

    # register login page
    import uuid

    @flaskApp.route('/login', methods=['POST', 'GET'])
    def login():

        # shortcut to read user if token alreay available
        if 'auth_token' in session:
            return redirect(url_for('readuser', _external=True, _scheme=scheme))

        redirect_uri = url_for('authorized', _external=True)
        resp = make_response(oauth.microsoft.authorize_redirect(redirect_uri))

        return resp

    # login user if authorization is ok, then redirect ro read user variables

    @flaskApp.route('/login/authorized')
    def authorized():

        token = oauth.microsoft.authorize_access_token()
        user = oauth.microsoft.parse_id_token(token)

        session['user'] = user
        session['auth_token'] = token

        if'targetApp' in session:
            target = url_for(session['targetApp'],
                             _external=True, _scheme=scheme)
            session.pop('targetApp', None)
            return redirect(target)
        else:
            return "{}"

    # logout session
    @flaskApp.route('/logout', methods=['POST', 'GET'])
    def logout():
        session.pop('auth_token', None)
        session.pop('state', None)
        session.pop('user', None)
        return "{}"

    # put user credentials into session variables
    @flaskApp.route('/readuser')
    def readuser():
        #me = oauth.get('me')
        # print("readuser")
        token = session['auth_token']["access_token"]
        # print(token)
        res = requests.get("https://graph.microsoft.com/v1.0/me",
                           headers={"Authorization": f"Bearer {token}"})
        # print(res.content)
        return res.json()

    if updateApi is not None:

        # check if updateApi needs a mongo db connection
        if hasattr(updateApi, 'registerMongo'):
            # import pymongo, make the connection and register it in the updateApi
            from flask_pymongo import PyMongo
            print("# Init Mongo DB")
            flaskApp.config['MONGO_URI'] = cfg.get(
                'Flask', 'mongodb', fallback='mongo')
            mongo = PyMongo(flaskApp)
            updateApi.registerMongo(mongo)

        # add the interface to trigger app data reload
        @flaskApp.route("/updateApi", methods=['POST', 'GET'])
        def routeUpdateApi():
            if useUwsgi:
                uwsgi.reload()
            else:
                updateApi.refresh()
            return "{}"

        # check if init is needed
        if hasattr(updateApi, 'init'):
            print("call init")
            updateApi.init()

    # login_required wrapper for all dash views to check authorization token
    from functools import wraps

    def login_required(appName, func):
        @cross_origin(supports_credentials=True)
        @wraps(func)
        def decorated_view(*args, **kwargs):

            if "initial-data" in request.cookies:
                session["initial-data"] = request.cookies["initial-data"]
            else:
                session["initial-data"] = None

            if 'auth_token' in session:
                return func(*args, **kwargs)
            else:
                session['targetApp'] = appName
                return redirect(url_for('login', _external=True, _scheme=scheme))
        return decorated_view

    if dashApps is not None:
        # register all apps
        ##################
        # imports
        from flask.helpers import get_root_path
        import dash
        from dash.dependencies import Input
        from dash.dependencies import Output
        import dash_html_components as html
        try:
            from . import dash_core_components as dcc
        except:
            import dash_core_components as dcc
        import os
        import json

        # loop all the available dash dirs
        for d in dashApps:
            # Meta tags for viewport responsiveness
            meta_viewport = {
                "name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

            print(
                " #   add {0} on http://{1}:{2}{3}".format(d.title, host, port, d.url))

            assetsPath = os.path.join(get_root_path(__name__), 'assets')
            print(assetsPath)

            # register app in backend

            external_port = os.getenv("EXTERNAL_PORT", 5000)
            try:
                sendData = json.dumps(
                    {"port": external_port,
                     "path": d.url,
                     "group": d.group,
                     "shortName": d.title,
                     "longName": d.longTitle,
                     "public": d.public,
                     "icon": d.icon}
                )
                print(sendData)
                res = requests.post("https://backend:5000/appreg",
                                    data=sendData,
                                    headers={
                                        "Content-Type": "application/json"},
                                    verify=False)
                print(res)
            except:
                print("Not able to register app!")

            # create a new dash app
            newDashApp = dash.Dash(__name__,
                                   server=flaskApp,
                                   url_base_pathname=d.url,
                                   assets_folder=assetsPath,
                                   meta_tags=[meta_viewport]
                                   )

            # if gui needs a special initialization
            if hasattr(d, "init_layout"):
                d.init_layout()

            # if gui needs a special flask inits
            if hasattr(d, "init_flask"):
                d.init_flask(flaskApp)

            # if gui needs to suppress callback exceptions
            if hasattr(d, "suppress_callback_exceptions"):
                newDashApp.config['suppress_callback_exceptions'] = d.suppress_callback_exceptions

            # if gui hast a special template
            if hasattr(d, "index_string"):
                newDashApp.index_string = d.index_string

            # we use an extra server for static common style files
            newDashApp.scripts.config.serve_locally = True

            # fill it with the data from the imported dash app library
            newDashApp.title = d.title

            if hasattr(d, "header"):
                headerDiv = [

                    html.Div([
                        d.header,  # <-- load the header information
                    ], className="d-flex justify-content-center w-100"),
                    html.Div(
                        className="d-flex justify-content-right small text-muted", id="headerRight"),
                    html.Div(id="headerRightDummy")
                ]
            else:
                headerDiv = []

            # fill this div with the main gui elements
            mainDivs = [
            ]

            # add the config menu if needed
            if hasattr(d, "configMenu"):
                # button to open
                headerDiv.insert(0,
                                 html.Button(
                                     html.Div(" ", className="editIcon"),
                                     id="openConfigMenu",
                                     className="configMenuButton"
                                 ))

                # the mooving configuration menu on the left side:
                mainDivs.append(
                    html.Div([
                        html.Button(html.Div(" ", className="closeIcon"), id="closeConfigMenu",
                                    className="configMenuButton"
                                    ),
                        d.configMenu  # <-- load the plot configuration menu on the left
                    ], className="configMenu configMenu-hide", id="configMenu")
                )

            # add the param menu if needed
            if hasattr(d, "paramMenu"):
                # button to open
                headerDiv.append(
                    html.Button(
                        html.Div(" ", className="paramIcon"),
                        id="openParamMenu",
                        className="paramMenuButton"
                    ))

                # the mooving parameter menu on the right side:
                mainDivs.append(
                    html.Div([
                        html.Button(html.Div(" ", className="closeIcon"), id="closeParamMenu",
                                    className="paramMenuButton"
                                    ),
                        d.paramMenu  # <-- load the plot parameter menu on the right
                    ], className="paramMenu paramMenu-hide", id="paramMenu")
                )

            # add the main element
            if hasattr(d, "main"):
                mainDivs.append(
                    # the main content of the app
                    html.Div([
                        d.main,  # <-- the main content of the app
                        dcc.Store(id='initial-app-state'),
                        dcc.Store(id='internal-user')
                    ], className="main")
                )

            # generate the app layout
            if hasattr(d, "applayout"):
                newDashApp.layout = d.applayout
            else:
                newDashApp.layout = html.Div([
                    # an unique session id
                    html.Div("", id='session-id',
                             style={'display': 'none'}),

                    # the header with the button to open the config menu
                    html.Div(headerDiv, className="d-flex flex-row header"),

                    *mainDivs
                ])

            # register custom callbacks
            d.register_callbacks(newDashApp)

            # register header date callback load a session
            if useUwsgi:
                @newDashApp.callback([
                    Output('headerRight', 'children'),
                    Output('initial-app-state', 'data'),
                    Output('session-id', 'children'),
                    Output('internal-user', 'data')
                ],
                    [Input('headerRightDummy', 'children')]
                )
                def calcLeftHeader(aux):
                    # create dash internal session_id
                    session_id = str(uuid.uuid4())

                    # load initial data from session
                    initial_data = {}
                    try:
                        if "initial-data" in session:
                            initial_data = json.loads(session["initial-data"])
                    except:
                        pass

                    user = {}
                    try:
                        if "user" in session and session["user"] is not None:
                            user = session['user']
                        else:
                            token = session['auth_token']["access_token"]
                            res = requests.get(
                                "https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {token}"})

                            user = res.content.decode()
                            session['user'] = user
                    except:
                        pass

                    startTime = dt.utcfromtimestamp(uwsgi.started_on)
                    return (
                        [html.P("Last Update", className="text-right mr-2"),
                         html.P(startTime.strftime("%Y-%m-%d %H:%M:%S"))],
                        initial_data,
                        session_id,
                        user)
            else:
                @newDashApp.callback([
                    Output('headerLeft', 'children'),
                    Output('initial-app-state', 'data'),
                    Output('session-id', 'children'),
                    Output('internal-user', 'data')
                ],
                    [Input('headerLeftDummy', 'children')])
                def calcLeftHeaderB(aux):
                    # create dash internal session_id
                    session_id = str(uuid.uuid4())

                    # load initial data from session
                    initial_data = {}
                    try:
                        if "initial-data" in session:
                            initial_data = json.loads(session["initial-data"])
                    except:
                        pass

                    user = {}
                    try:
                        if "user" in session and session["user"] is not None:
                            user = session['user']
                        else:
                            token = session['auth_token']["access_token"]
                            res = requests.get(
                                "https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {token}"})

                            user = res.content.decode()
                            session['user'] = user
                    except:
                        pass

                    return [], initial_data, session_id, user

            if scheme == "https":
                # apply the login_required wrapper, which redirects to the login page if needed
                for view_func in newDashApp.server.view_functions:
                    if view_func.startswith(newDashApp.config.url_base_pathname):
                        newDashApp.server.view_functions[view_func] = login_required(
                            d.url, newDashApp.server.view_functions[view_func])

    # store the initial-data probposed from the frontend
    # this is used to restore an initial app state
    @flaskApp.route("/post", methods=['POST'])
    @cross_origin(supports_credentials=True)
    def post_data():
        params = request.get_json()

        response = flaskApp.response_class(
            response="{}",
            mimetype='application/json',
            status=200
        )
        data = params["data"]
        response.set_cookie(
            'initial-data', json.dumps(data), max_age=10)

        return response

    # clear the initial data
    @flaskApp.route("/clear", methods=['POST'])
    @cross_origin(supports_credentials=True)
    def clear_data():

        response = flaskApp.response_class(
            response="{}",
            mimetype='application/json',
            status=200
        )
        response.set_cookie('initial-data', '', max_age=0)

        return response

    if plotApi is not None:
        from plotly.utils import PlotlyJSONEncoder
        # add the plot interface to collect plots only

        @flaskApp.route("/plotApi", methods=['POST'])
        def routePlotApi():
            print(request)
            params = request.get_json()
            output = plotApi.router(params)
            if useUwsgi:
                outputString = dumps(output, cls=PlotlyJSONEncoder)
                return "{{\"plots\": {},\"timestamp\": {}}}".format(outputString, uwsgi.started_on)
            else:
                outputString = dumps(output, cls=PlotlyJSONEncoder)
                return "{{\"plots\": {},\"timestamp\": {}}}".format(outputString, dt.now().timestamp())

        import plotly.graph_objs as go
        import plotly.io as pio
        import io

        @flaskApp.route("/plotPng", methods=['POST'])
        def routePlotPng():
            print(request)
            params = request.get_json()
            data = plotApi.router(params)
            fig = go.Figure(data)
            fig.layout['height'] = 650
            fig.layout['width'] = 1155
            img_bytes = pio.to_image(fig, format='png')
            return send_file(io.BytesIO(img_bytes), mimetype='image/png', as_attachment=True, attachment_filename='output.png')

        if updateCrontab is not None:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger

            global autoUpdateScheduler

            startNeeded = False
            if autoUpdateScheduler == None:
                # add an automatic refreshing feature
                autoUpdateScheduler = BackgroundScheduler()
                startNeeded = True
            else:
                # remove the old update task
                autoUpdateScheduler.remove_all_jobs()

            crontabTrigger = CronTrigger.from_crontab(updateCrontab)

            def autorunUpdateApi():
                if useUwsgi:
                    uwsgi.reload()
                else:
                    updateApi.refresh()
            autoUpdateScheduler.add_job(
                autorunUpdateApi, crontabTrigger, id='auto_update_job')

            if startNeeded:
                print("start new restart scheduler")
                autoUpdateScheduler.start()

    return flaskApp, host, port, login_required
