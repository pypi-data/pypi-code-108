"""AnaClient is the SDK module for connecting to Rendered.ai's Platform API."""


from os import environ


class AnaClient:

    def __init__(self, workspaceId=None, environment='prod', email=None, password=None, local=False, verbose=None):
        import pyrebase, getpass, time, base64, json, traceback, os
        import anatools.client.envs as envs
        from anatools.api import AnaAPI
        self.verbose = verbose
        if environment not in ['dev','test','prod','infra']: 
            print("Invalid environment argument, must be 'infra', 'dev', 'test' or 'prod'.")
            return None
        encodedbytes = envs.envs.encode('ascii')
        decodedbytes = base64.b64decode(encodedbytes)
        decodedenvs = json.loads(decodedbytes.decode('ascii'))
        envdata = decodedenvs[environment]
        self.__firebase = pyrebase.initialize_app(envdata)
        self.__url = envdata['graphURL']
        self.__auth = self.__firebase.auth()
        self.__timer = int(time.time())
        self.__password = password
        self.email = email
        self.environment = environment
        self.local = local
        self.organizations = {}
        self.workspaces ={}
        self.channels = {}
        
        loggedin = False
        if not self.email:
            print(f'Enter your credentials for the {envdata["name"]}.') 
            self.email = input('Email: ')
        if not self.__password:
            failcount = 1
            while not loggedin:
                self.__password = getpass.getpass()
                try:
                    self.__user = self.__auth.sign_in_with_email_and_password(self.email, self.__password)
                    loggedin = True
                except:
                    if failcount < 5:
                        print('\rInvalid password, please enter your password again.')
                        failcount += 1
                    else:
                        print(f'\rInvalid password, consider resetting your password at {envdata["website"]}/forgot-password.')
                        return
        if not loggedin:
            try:
                self.__user = self.__auth.sign_in_with_email_and_password(self.email, self.__password)
                loggedin = True
            except:
                if self.verbose == 'debug': traceback.print_exc()
                print(f'Failed to login to {envdata["name"]} with email ({email}).')
                return
        self.__uid = self.__user['localId']
        self.__headers = {'uid':self.__uid, 'idtoken':self.__user['idToken']}
        self.__logout = False
        if self.verbose == 'debug': 
            print(self.__uid)
            print(self.__user['idToken'])
        if local:
            os.environ['NO_PROXY'] = '127.0.0.1'
            self.__url = 'http://127.0.0.1:3000'
            print("Local is set to",self.__url)
        self.ana_api = AnaAPI(self.__url, self.__headers, self.verbose)

        self.workspaces = self.get_workspaces()
        self.organizations = self.get_organizations()
        if not self.organizations:
            print("No organizations available. Email us at admin@rendered.ai for support or fill out the form at https://rendered.ai/#contact.")
            return

        self.get_channels()

        if workspaceId:     
            self.workspace = workspaceId
            for workspace in self.workspaces:
                if self.workspace == workspace['workspaceId']:
                    self.organization = workspace['organizationId']
            if self.organization is None:
                print("The workspaceId provided is invalid, please choose one of the following:")
                for workspace in self.workspaces:
                    print(workspace["workspaceId"])
                self.workspace = None
                return
        else:
            if len(self.workspaces) > 0:
                self.workspace = self.workspaces[0]['workspaceId']
                self.organization = self.workspaces[0]['organizationId']
            
            else:
                self.workspace = None
                self.organization = self.organizations[0]['organizationId']
            print(f'These are your organizations and workspaces:')
            for organization in self.organizations:
                print(f"    {organization['name']+' Organization'[:44]:<44}  {organization['organizationId']:<50}")
                for workspace in self.workspaces:
                    if workspace["organizationId"] == organization["organizationId"]:
                        print(f"\t{workspace['name'][:40]:<40}  {workspace['workspaceId']:<50}")

        if verbose: print(f'Signed into {envdata["name"]} with {self.email}.')
        if not self.workspaces:
            print("No workspaces available. You can create a new workspace with the create_workspace method or email us at admin@rendered.ai for support or fill out the form at https://rendered.ai/#contact.")
        else:
            print(f'The current workspaces is: {self.workspace}')


    def refresh_token(self):
        import time
        from anatools.api import AnaAPI
        if int(time.time())-self.__timer > int(self.__user['expiresIn']):
            self.__timer = int(time.time())
            self.__user = self.__auth.sign_in_with_email_and_password(self.email, self.__password)
            self.__headers = {'uid':self.__uid, 'idtoken':self.__user['idToken']}
            self.ana_api = AnaAPI(self.__url, self.__headers, self.verbose)


    def check_logout(self):
        if self.__logout: print('You are currently logged out, login to access the Ana tool.'); return True
        self.refresh_token()
        return False


    def logout(self):
        """Logs out of the ana sdk and removes credentials from ana.
        """
        if self.check_logout(): return
        self.__logout = True
        del self.__password, self.__firebase, self.__url, self.__auth, self.__user, self.__uid, self.__headers


    def login(self, email=None, password=None):
        """Log in to the SDK. 
        
        Parameters
        ----------
        workspaceId: str
            ID of the workspace to log in to. Uses default if not specified.
        environment: str
            Environment to log into. Defaults to production.
        email: str
            Email for the login. Will prompt if not provided.
        password: str
            Password to login. Will prompt if not provided.
        local: bool
            Used for development to indicate pointing to local API.
        verbose: str
            Flag to turn on verbose logging. Use 'debug' to view log output.
        
        """
        self.__init__(self.workspace, self.environment, email, password, self.local, self.verbose)

    
    from .organizations import get_organization, set_organization, get_organizations, edit_organization, get_organization_members, add_organization_member, edit_organization_member, remove_organization_member, get_organization_limits, set_organization_limit, get_organization_usage
    from .workspaces    import get_workspace, set_workspace, get_workspaces, create_workspace, edit_workspace, delete_workspace, get_workspace_guests, add_workspace_guest, remove_workspace_guest, get_workspace_limits, set_workspace_limit
    from .graphs        import get_staged_graphs, create_staged_graph, edit_staged_graph, delete_staged_graph, download_staged_graph, get_default_graph, set_default_graph
    from .datasets      import get_datasets, create_dataset, edit_dataset, delete_dataset, download_dataset, cancel_dataset
    from .channels      import get_channels, get_managed_channels, create_managed_channel, edit_managed_channel, add_channel_access, remove_channel_access, deploy_managed_channel, get_deployment_status
    from .volumes       import get_volumes, get_managed_volumes, create_managed_volume, edit_managed_volume, delete_managed_volume, add_volume_access, remove_volume_access, get_volume_data, download_volume_data, upload_volume_data, delete_volume_data
    from .analytics     import get_analytics, get_analytics_types, create_analytics, delete_analytics
    from .annotations   import get_annotations, get_annotation_formats, get_annotation_maps, create_annotation, download_annotation, delete_annotation 
    from .gan           import get_gan_models, get_gan_dataset, create_gan_dataset, delete_gan_dataset
