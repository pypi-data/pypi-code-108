class Parameters(object):
    DEFAULT_IDP_URL = "https://idp.s3i.vswf.dev/"
    DEFAULT_IDP_REALM = "KWH"
    DEFAULT_BROKER_HOST = "rabbitmq.s3i.vswf.dev"
    DEFAULT_BROKER_VHOST = "s3i"
    DEFAULT_REPO_WWS_URL = "wss://ditto.s3i.vswf.dev/ws/2"
    DEFAULT_REPO_URL = "https://ditto.s3i.vswf.dev/api/2/"
    DEFAULT_DIR_URL = "https://dir.s3i.vswf.dev/api/2/"
    DEFAULT_REPO_SNYC_FREQ = 1  # Hz
    DEFAULT_DIR_SYNC_FREQ = 0
    DEFAULT_THING_SYNC_FREQ = 50

    def __init__(self,
                 idp_url=None,
                 idp_realm=None,
                 broker_host=None,
                 broker_vhost=None,
                 repo_url=None,
                 repo_wws_url=None,
                 dir_url=None,
                 repo_sync_freq=None,
                 dir_sync_freq=None,
                 thing_sync_freq=None
                 ):

        self.__idp_url = idp_url
        self.__idp_realm =idp_realm
        self.__broker_host = broker_host
        self.__broker_vhost = broker_vhost
        self.__repo_url = repo_url
        self.__repo_wws_url = repo_wws_url
        self.__dir_url = dir_url
        self.__repo_sync_freq = repo_sync_freq
        self.__dir_sync_freq = dir_sync_freq
        self.__thing_sync_freq = thing_sync_freq

        if self.__idp_url is None:
            self.__idp_url = self.DEFAULT_IDP_URL

        if self.__idp_realm is None:
            self.__idp_realm = self.DEFAULT_IDP_REALM

        if self.__broker_host is None:
            self.__broker_host = self.DEFAULT_BROKER_HOST

        if self.__broker_vhost is None:
            self.__broker_vhost = self.DEFAULT_BROKER_VHOST

        if self.__repo_url is None:
            self.__repo_url = self.DEFAULT_REPO_URL

        if self.__repo_wws_url is None:
            self.__repo_wws_url = self.DEFAULT_REPO_WWS_URL

        if self.__dir_url is None:
            self.__dir_url = self.DEFAULT_DIR_URL

        if self.__repo_url is None:
            self.__repo_url = self.DEFAULT_REPO_URL

        if self.__repo_sync_freq is None:
            self.__repo_sync_freq = self.DEFAULT_REPO_SNYC_FREQ

        if self.__dir_sync_freq is None:
            self.__dir_sync_freq = self.DEFAULT_DIR_SYNC_FREQ

        if self.__thing_sync_freq is None:
            self.__thing_sync_freq = self.DEFAULT_THING_SYNC_FREQ

    @property
    def idp_url(self):
        return self.__idp_url

    @idp_url.setter
    def idp_url(self, value):
        self.__idp_url = value

    @property
    def idp_realm(self):
        return self.__idp_realm

    @idp_realm.setter
    def idp_realm(self, value):
        self.__idp_realm = value

    @property
    def broker_host(self):
        return self.__broker_host

    @broker_host.setter
    def broker_host(self, value):
        self.__broker_host = value

    @property
    def broker_vhost(self):
        return self.__broker_vhost

    @broker_vhost.setter
    def broker_vhost(self, value):
        self.__broker_vhost = value

    @property
    def repo_url(self):
        return self.__repo_url

    @repo_url.setter
    def repo_url(self, value):
        self.__repo_url = value

    @property
    def repo_wws_url(self):
        return self.__repo_wws_url

    @repo_wws_url.setter
    def repo_wws_url(self, value):
        self.__repo_wws_url = value

    @property
    def dir_url(self):
        return self.__dir_url

    @dir_url.setter
    def dir_url(self, value):
        self.__dir_url = value

    @property
    def repo_sync_freq(self):
        return self.__repo_sync_freq

    @repo_sync_freq.setter
    def repo_sync_freq(self, value):
        self.__repo_sync_freq = value

    @property
    def dir_sync_freq(self):
        return self.__dir_sync_freq

    @dir_sync_freq.setter
    def dir_sync_freq(self, value):
        self.__dir_sync_freq = value

    @property
    def thing_sync_freq(self):
        return self.__thing_sync_freq

    @thing_sync_freq.setter
    def thing_sync_freq(self, value):
        self.__thing_sync_freq = value
