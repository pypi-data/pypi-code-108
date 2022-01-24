# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality for managing :term:`notification messages <notification
message>`.

See :doc:`/specs/notify`.

"""

from lino.api import ad, _
from lino.core.utils import is_devserver
try:
    import redis
except ImportError:
    redis = None
try:
    import channels
except ImportError:
    channels = None


class Plugin(ad.Plugin):

    verbose_name = _("Messages")
    needs_plugins = ['lino.modlib.users', 'lino.modlib.memo']
    media_name = 'js'

    use_websockets = False
    use_push_api = False
    # Beware: The key pair used here are supposed to be used only in a
    # development environment and the keys are publicly available on the
    # internet and are not to be used in a production environment.
    vapid_private_key = "3W2nQ-o07lGlP8qs-STuUrTioCC7KxPVG7SNOSy2A4Y"
    vapid_public_key = "BCPMIR93gv_Di_AHL4i-zew3hB9I5ebPXihpKX44dgsxYxVymMZ79EK4_LIO7fN6d_UwUbz611Uiz7amJN1q2Wg"
    vapid_admin_email = "sharifmehedi24@gmail.com"

    remove_after = 2*7  # two weeks
    keep_unseen = True
    mark_seen_when_sent = False

    def on_init(self):
        if self.use_websockets:
            if channels is None:
                # if channels is not installed, we cannot use it as a plugin
                # because even :manage:`install` would fail.
                return
            self.needs_plugins.append('channels')

    def on_plugins_loaded(self, site):
        assert self.site is site
        if self.use_websockets:
            sd = site.django_settings
            # the dict which will be used to create settings
            cld = {}
            sd['CHANNEL_LAYERS'] = {"default": cld}
            #if not DJANGO2:
            #    cld["ROUTING"] = "lino.modlib.notify.routing.channel_routing"
            #    cld["BACKEND"] = "asgiref.inmemory.ChannelLayer"
            #else:
            sd['ASGI_APPLICATION'] = "lino.modlib.notify.routing2.application"
            cld["BACKEND"] = "channels_redis.core.RedisChannelLayer"
            cld['CONFIG'] = {"hosts": [("localhost", 6379)], }
            if False:  # not is_devserver():
                cld['BACKEND'] = "asgi_redis.RedisChannelLayer"
                cld['CONFIG'] = {"hosts": [("localhost", 6379)], }

    def get_requirements(self, site):
        if self.use_websockets:
            yield 'channels'
            # yield 'asgiref'
            yield 'channels_redis'
            if False:  # not is_devserver():
                yield 'asgi_redis'
        if self.use_push_api:
            yield 'pywebpush'


    def get_used_libs(self, html=None):
        if self.use_websockets:
            try:
                import channels
                version = channels.__version__
            except ImportError:
                version = self.site.not_found_msg
            yield ("Channels", version, "https://github.com/django/channels")

    def get_patterns(self):
        if self.use_push_api:
            from django.urls import re_path as url
            from . import views
            yield url(r'pushsubscription', views.PushSubscription.as_view())
            # yield url(r'testpush', views.TestPush.as_view())

    def get_js_includes(self, settings, language):
        if self.use_websockets:
            if settings.DEBUG:
                yield self.build_lib_url(('push.js/push.min.js'))
            else:
                yield self.build_lib_url(('push.js/push.js'))

    def setup_main_menu(self, site, user_type, m):
        p = site.plugins.office
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('notify.MyMessages')

    def setup_explorer_menu(self, site, user_type, m):
        p = site.plugins.system
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('notify.AllMessages')

    def get_head_lines(self, site, request):
        if self.use_push_api:
            yield """<script type="text/javascript">
                window.addEventListener('click', () => {
                    Notification.requestPermission((status) => {
                        console.log('Notification Permission Status: ', status);
                        if (status === 'granted' && !window.subscribed
                            && 'serviceWorker' in navigator) {
                            navigator.serviceWorker.ready.then((reg) => {
                                reg.pushManager.getSubscription().then((sub) => {
                                    if (sub === null) {
                                        reg.pushManager.subscribe({
                                            userVisibleOnly: true,
                                            applicationServerKey: """ + '"' + self.vapid_public_key + '"' + """,
                                        }).then((sub) => {
                                            fetch(`pushsubscription?sub=${
                                                JSON.stringify(sub)}&lang=${
                                                navigator.userLanguage
                                                || navigator.language}&userAgent=${
                                                navigator.userAgent}`);
                                            window.subscribed = true;
                                        });
                                    }
                                });
                            });
                        }
                    });
                });
            </script>"""

        if not self.use_websockets:
            return
        from lino.utils.jsgen import py2js
        user_name = "anony"
        if request.user.is_authenticated:
            user_name = request.user.username
        site_title = site.title or 'Lino-framework'
        if self.site.default_ui == 'lino_react.react':
            js_to_add = """
        <script type="text/javascript">
            window.Lino = window.Lino || {}
            window.Lino.useWebSockets = true;
        </script>
            """
        else:
            js_to_add = ("""
        <script type="text/javascript">
        Ext.onReady(function() {
            // Note that the path doesn't matter for routing; any WebSocket
            // connection gets bumped over to WebSocket consumers
            var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
            var ws_path = window.location.pathname + "lino/";
            console.log("Connecting to " + ws_path);
            var webSocketBridge = new channels.WebSocketBridge();
            var username = '%s' ;
            webSocketBridge.connect();
            lino_connecting = function() {
                console.log("lino connecting ...");
                webSocketBridge.send({
                            "command": "user_connect",
                            "username": username
                        });
            }
            webSocketBridge.socket.addEventListener('open', function() {
                lino_connecting();
            });
            // Helpful debugging
            webSocketBridge.socket.onclose = function () {
                console.log("Disconnected from chat socket");
            }

            onGranted = console.log("onGranted");
            onDenied = console.log("onDenied");
            // Ask for permission if it's not already granted
            Push.Permission.request(onGranted,onDenied);

            webSocketBridge.listen(function(action, stream) {
                try {
                    Push.create( %s , {
                        body: action['body'],
                        icon: '/static/img/lino-logo.png',
                        onClick: function () {
                            window.focus();
                            """ + site.kernel.default_renderer.reload_js() + """
                            this.close();
                        }
                    });
                    if (false && Number.isInteger(action["id"])){
                        webSocketBridge.stream('lino').send({message_id: action["id"]})
                        webSocketBridge.send(JSON.stringify({
                                        "command": "seen",
                                        "message_id": action["id"],
                                    }));
                                }
                    }
                catch(err) {
                    console.log(err.message);
                }
            })});
        // end of onReady()"
        </script>
            """) % (user_name, py2js(site_title))
        yield js_to_add

    def get_dashboard_items(self, user):
        if user.is_authenticated:
            # yield ActorItem(
            #     self.models.notify.MyMessages, header_level=None)
            yield self.site.models.notify.MyMessages
