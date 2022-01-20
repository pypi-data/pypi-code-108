
from twisted.internet.defer import Deferred

from .widgets.colors import color_set_alpha
from .widgets.marquee import MarqueeLabel

from .basemixin import BaseGuiMixin
from .config import ConfigMixin


class MarqueeInterrupted(Exception):
    pass


class MarqueeBusy(Exception):
    def __init__(self, now_playing, collision_count):
        self.now_playing = now_playing
        self.collision_count = collision_count

    def __repr__(self):
        return "<MarqueeBusy Now Playing {0}" \
               "".format(self.now_playing)


class MarqueeGuiMixin(ConfigMixin, BaseGuiMixin):
    _gui_marquee_bgcolor = None
    _gui_marquee_color = None

    def __init__(self, *args, **kwargs):
        super(MarqueeGuiMixin, self).__init__(*args, **kwargs)
        self._gui_marquee = None
        self._marquee_text = None
        self._marquee_deferred = None
        self._marquee_end_call = None
        self._marquee_collision_count = 0

    def marquee_show(self):
        self.gui_footer_show()

    def marquee_hide(self):
        self.gui_footer_hide()

    def marquee_play(self, text, duration=None, loop=True):
        if self._marquee_deferred:
            self._marquee_collision_count += 1
            if self._marquee_collision_count > 30:
                self.marquee_stop(forced=True)
            raise MarqueeBusy(self._marquee_text,
                              self._marquee_collision_count)
        self._marquee_collision_count = 0
        self.gui_marquee.text = text
        self.marquee_show()

        if duration:
            self._gui_marquee.start(loop=loop)
            self._marquee_end_call = self.reactor.callLater(duration, self.marquee_stop)
        else:
            self._gui_marquee.start(callback=self.marquee_stop)
        self._marquee_deferred = Deferred()
        return self._marquee_deferred

    def marquee_stop(self, forced=False):
        self._gui_marquee.stop()
        self.log.info("End Offset by {0} collisions."
                      "".format(self._marquee_collision_count))
        self._marquee_collision_count = 0
        self.marquee_hide()

        if self._marquee_end_call and self._marquee_end_call.active():
            self._marquee_end_call.cancel()

        if self._marquee_deferred:
            self._marquee_deferred.callback(forced)
            self._marquee_deferred = None

    @property
    def gui_marquee(self):
        if not self._gui_marquee:
            params = {'bgcolor': (self._gui_marquee_bgcolor or
                                  color_set_alpha(self.gui_color_2, 0.6)),
                      'color': [1, 1, 1, 1],
                      'font_size': '32sp'}
            if self.config.text_font_name:
                params['font_name'] = self.config.text_font_name
            self._gui_marquee = MarqueeLabel(text='Marquee Text', **params)

            self.gui_footer.add_widget(self._gui_marquee)
            self.marquee_hide()
        return self._gui_marquee

    def gui_setup(self):
        super(MarqueeGuiMixin, self).gui_setup()
        _ = self.gui_marquee
