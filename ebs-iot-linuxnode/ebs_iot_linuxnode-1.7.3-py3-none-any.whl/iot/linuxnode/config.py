

# foundation    ()
# backdrop      1
# background    2
# backdrop      3
# video         4
# app           5


import os
import pkg_resources
from six.moves.configparser import ConfigParser
from appdirs import user_config_dir


class IoTNodeConfig(object):
    _appname = 'iotnode'
    _root = os.path.abspath(os.path.dirname(__file__))
    _roots = [_root]
    _config_file = os.path.join(user_config_dir(_appname), 'config.ini')
    _sys_config_file = os.path.join('/etc/raspap/custom.ini')

    def __init__(self):
        self._config = ConfigParser()
        print("Reading Config File {}".format(self._config_file))
        self._config.read(self._config_file)
        self._sys_config = ConfigParser()
        print("Reading System Config File {}".format(self._sys_config_file))
        self._sys_config.read(self._sys_config_file)
        self._config_apply_init()
        print("EBS IOT Linux Node, version {0}".format(self.linuxnode_version))

    @property
    def linuxnode_version(self):
        return pkg_resources.get_distribution('ebs-iot-linuxnode').version

    def _config_apply_init(self):
        self._apply_display_layer()

    def _write_config(self):
        with open(self._config_file, 'w') as configfile:
            self._config.write(configfile)

    def _check_section(self, section):
        if not self._config.has_section(section):
            self._config.add_section(section)
            self._write_config()

    # Paths
    @property
    def app_root(self):
        return self._root

    @property
    def app_resources(self):
        return os.path.join(self.app_root, 'resources')

    @property
    def roots(self):
        return self._roots

    def get_path(self, filepath):
        for root in self._roots:
            if os.path.exists(os.path.join(root, filepath)):
                return os.path.join(root, filepath)
        return filepath

    # Platform
    @property
    def platform(self):
        return self._config.get('platform', 'platform', fallback=None)

    # Debug
    @property
    def debug(self):
        return self._config.getboolean('debug', 'debug', fallback=False)

    @property
    def gui_log_display(self):
        return self._config.getboolean('debug', 'gui_log_display', fallback=False)

    @property
    def gui_log_level(self):
        return self._config.get('debug', 'gui_log_level', fallback='info')

    # Display
    @property
    def fullscreen(self):
        return self._config.getboolean('display', 'fullscreen', fallback=True)

    @property
    def portrait(self):
        return self._config.getboolean('display', 'portrait', fallback=False)

    @portrait.setter
    def portrait(self, value):
        self._check_section('display')
        self._config.set('display', 'portrait', "yes" if value else "no")
        self._write_config()

    @property
    def flip(self):
        return self._config.getboolean('display', 'flip', fallback=False)

    @flip.setter
    def flip(self, value):
        self._check_section('display')
        self._config.set('display', 'flip', "yes" if value else "no")
        self._write_config()

    @property
    def orientation(self):
        rv = 0
        if self.portrait is True:
            rv += 90
        if self.flip:
            rv += 180
        return rv

    def orientation_update(self):
        from kivy.config import Config
        Config.set('graphics', 'rotation', self.orientation)

    @property
    def overlay_mode(self):
        return self._config.getboolean('display', 'overlay_mode', fallback=False)

    @property
    def sidebar_width(self):
        return self._config.getfloat('display', 'sidebar_width', fallback=0.3)

    @property
    def sidebar_height(self):
        rv = self._config.getfloat('display', 'sidebar_height', fallback=0.0)
        if not rv:
            rv = self.sidebar_width
        return rv

    @property
    def show_foundation(self):
        return self._config.getboolean('display-rpi', 'show_foundation', fallback=True)

    @property
    def dispmanx_foundation_layer(self):
        return self._config.getint('display-rpi', 'dispmanx_foundation_layer', fallback=1)

    @property
    def foundation_image(self):
        return self._config.get('display-rpi', 'foundation_image', fallback=None)

    @property
    def background(self):
        return self._config.get('display', 'background', fallback='images/background.png')

    @background.setter
    def background(self, value):
        self._check_section('display')
        self._config.set('display', 'background', value)
        self._write_config()

    @property
    def background_external_player(self):
        if self.platform == 'rpi':
            return self._config.getboolean('display-rpi', 'background_external_player', fallback=False)

    @property
    def background_dispmanx_layer(self):
        return self._config.getint('display-rpi', 'background_dispmanx_layer', fallback=2)

    @property
    def app_dispmanx_layer(self):
        if self.platform != 'rpi':
            raise AttributeError("dispmanx layer is an RPI thing")
        return self._config.getint('display-rpi', 'dispmanx_app_layer', fallback=5)

    def _apply_display_layer(self):
        if self.platform == 'rpi':
            os.environ.setdefault('KIVY_BCM_DISPMANX_LAYER', str(self.app_dispmanx_layer))

    # ID
    @property
    def node_id_getter(self):
        return self._config.get('id', 'getter', fallback='uuid')

    @property
    def node_id_interface(self):
        return self._config.get('id', 'interface', fallback=None)

    @property
    def node_id_override(self):
        return self._config.get('id', 'override', fallback=None)

    @property
    def node_id_display(self):
        return self._config.getboolean('id', 'display', fallback=False)

    @property
    def node_id_display_frequency(self):
        return self._config.getint('id', 'display_frequency', fallback=0)

    @property
    def node_id_display_duration(self):
        return self._config.getint('id', 'display_duration', fallback=15)

    # Networks
    @property
    def network_interface_wifi(self):
        return self._config.get('network', 'wifi', fallback='wlan0')

    @property
    def network_interface_ethernet(self):
        return self._config.get('network', 'ethernet', fallback='eth0')

    @property
    def network_interfaces(self):
        return [self.network_interface_wifi, self.network_interface_ethernet]

    # HTTP
    @property
    def http_max_concurrent_requests(self):
        return self._config.getint('http', 'max_concurrent_requests', fallback=1)

    @property
    def http_max_background_downloads(self):
        return self._config.getint('http', 'max_background_downloads', fallback=1)

    @property
    def http_max_concurrent_downloads(self):
        return self._config.getint('http', 'max_concurrent_downloads', fallback=1)

    @property
    def http_proxy_host(self):
        return self._sys_config.get('NetworkProxyConfiguration', 'host', fallback=None)

    @property
    def http_proxy_port(self):
        return self._sys_config.getint('NetworkProxyConfiguration', 'port', fallback=0)

    @property
    def http_proxy_user(self):
        return self._sys_config.get('NetworkProxyConfiguration', 'user', fallback=None)

    @property
    def http_proxy_pass(self):
        return self._sys_config.get('NetworkProxyConfiguration', 'pass', fallback=None)

    @property
    def http_proxy_enabled(self):
        return self.http_proxy_host is not None

    @property
    def http_proxy_auth(self):
        if not self.http_proxy_user:
            return None
        if not self.http_proxy_pass:
            return self.http_proxy_user
        return "{0}:{1}".format(self.http_proxy_user, self.http_proxy_pass)

    @property
    def http_proxy_url(self):
        url = self.http_proxy_host
        if self.http_proxy_port:
            url = "{0}:{1}".format(url, self.http_proxy_port)
        if self.http_proxy_auth:
            url = "{0}@{1}".format(self.http_proxy_auth, url)
        return url

    # Resource Manager
    @property
    def resource_prefetch_retries(self):
        return self._config.getint('resources', 'prefetch_retries', fallback=3)
    
    @property
    def resource_prefetch_retry_delay(self):
        return self._config.getint('resources', 'prefetch_retry_delay', fallback=5)

    # Cache
    @property
    def cache_max_size(self):
        return self._config.getint('cache', 'max_size', fallback='10000000')

    # Video
    @property
    def video_external_player(self):
        if self.platform == 'rpi':
            return self._config.getboolean('video-rpi', 'external_player', fallback=False)

    @property
    def video_dispmanx_layer(self):
        if self.platform == 'rpi':
            return self._config.getint('video-rpi', 'dispmanx_video_layer', fallback=4)

    @property
    def video_show_backdrop(self):
        if self.platform == 'rpi':
            return self._config.getboolean('video-rpi', 'show_backdrop', fallback=False)

    @property
    def video_backdrop_dispmanx_layer(self):
        if self.platform == 'rpi':
            return self._config.getint('video-rpi', 'dispmanx_video_layer', fallback=1)

    # Browser
    @property
    def browser_show_default(self):
        return self._config.getboolean('browser', 'show_default', fallback=False)

    @browser_show_default.setter
    def browser_show_default(self, value):
        self._check_section('browser')
        if value:
            value = 'yes'
        else:
            value = 'no'
        self._config.set('browser', 'show_default', value)
        self._write_config()

    @property
    def browser_default_url(self):
        return self._config.get('browser', 'default_url', fallback='http://www.google.com')

    @browser_default_url.setter
    def browser_default_url(self, value):
        self._check_section('browser')
        self._config.set('browser', 'default_url', value)
        self._write_config()

    # Fonts
    @property
    def text_font_name(self):
        return self.get_path(self._config.get('text', 'font_name', fallback=None)
)
    @property
    def text_use_fcm(self):
        return self._config.getboolean('text', 'use_fcm', fallback=False)
    
    @property
    def text_fcm_system(self):
        return self._config.getboolean('text', 'fcm_system', fallback=True)
    
    @property
    def text_fcm_fonts(self):
        return self.get_path(self._config.get('text', 'fcm_fonts', fallback=None))


class ConfigMixin(object):
    def __init__(self, *args, **kwargs):
        global current_config
        self._config = current_config
        super(ConfigMixin, self).__init__(*args, **kwargs)

    @property
    def config(self) -> IoTNodeConfig:
        return self._config
