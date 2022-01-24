

import os
from kivy.uix.video import Video
from twisted.internet.defer import Deferred

from .widgets.image import StandardImage
from .widgets.colors import ColorBoxLayout
from .widgets.pdfplayer import PDFPlayer

from .log import NodeLoggingMixin
from .background import OverlayWindowGuiMixin
from .externalplayer import ExternalMediaPlayer
from .externalplayer import BackdropManager


class MediaPlayerBusy(Exception):
    def __init__(self, now_playing, collision_count):
        self.now_playing = now_playing
        self.collision_count = collision_count

    def __repr__(self):
        return "<MediaPlayerBusy Now Playing {0}" \
               "".format(self.now_playing)


class MediaPlayerMixin(NodeLoggingMixin):
    _media_extentions_image = ['.png', '.jpg', '.bmp', '.gif', '.jpeg']
    _media_extentions_video = []

    def __init__(self, *args, **kwargs):
        super(MediaPlayerMixin, self).__init__(*args, **kwargs)
        self._media_player_deferred = None
        self._mediaplayer_now_playing = None
        self._end_call = None
        self._mediaplayer_collision_count = 0

    def media_play(self, content, duration=None, loop=False, interval=None):
        # Play the media file at filepath. If loop is true, restart the media
        # when it's done. You probably would want to provide a duration with
        # an image or with a looping video, not otherwise.
        if self._mediaplayer_now_playing:
            self._mediaplayer_collision_count += 1
            if self._mediaplayer_collision_count > 30:
                self.media_stop(forced=True)
            raise MediaPlayerBusy(self._mediaplayer_now_playing,
                                  self._mediaplayer_collision_count)
        self._mediaplayer_collision_count = 0
        if hasattr(content, 'filepath'):
            content = content.filepath
        if not os.path.exists(content):
            self.log.warn("Could not find media to play at {filepath}",
                          filepath=content)
            return
        if duration:
            self._end_call = self.reactor.callLater(duration, self.media_stop)
        self._mediaplayer_now_playing = os.path.basename(content)
        self.gui_bg_pause()
        if os.path.splitext(content)[1] in self._media_extentions_image:
            self.log.debug("Showing image {filename}",
                           filename=os.path.basename(content))
            self._media_play_image(content)
        elif os.path.splitext(content)[1] in ['.pdf']:
            self.log.debug("Showing pdf {filename}",
                           filename=os.path.basename(content))
            self._media_play_pdf(content, interval=interval)
        else:
            self.log.debug("Starting video {filename}",
                           filename=os.path.basename(content))
            self._media_play_video(content, loop)
        self._media_player_deferred = Deferred()
        return self._media_player_deferred

    def _media_play_image(self, filepath):
        raise NotImplementedError

    def _media_play_pdf(self, filepath, interval=None):
        raise NotImplementedError

    def _media_play_video(self, filepath, loop=False):
        raise NotImplementedError

    def media_stop(self, forced=False):
        self.log.info("End Offset by {0} collisions."
                      "".format(self._mediaplayer_collision_count))
        self._mediaplayer_collision_count = 0

        def _resume_bg():
            if not self._mediaplayer_now_playing:
                self.gui_bg_resume()
                self.gui_mediaview.make_transparent()
        self.reactor.callLater(1.5, _resume_bg)

        if self._end_call and self._end_call.active():
            self._end_call.cancel()

        if self._mediaplayer_now_playing:
            self._mediaplayer_now_playing = None

        if self._media_player_deferred:
            self._media_player_deferred.callback(forced)
            self._media_player_deferred = None

    def stop(self):
        self.media_stop(forced=True)
        super(MediaPlayerMixin, self).stop()


class MediaPlayerGuiMixin(OverlayWindowGuiMixin):
    def __init__(self, *args, **kwargs):
        super(MediaPlayerGuiMixin, self).__init__(*args, **kwargs)
        self._media_player_external = None
        self._media_player_backdrop = BackdropManager()
        self._media_playing = None
        self._gui_mediaview = None

    def _media_play_image(self, filepath):
        self._media_playing = StandardImage(source=filepath,
                                            allow_stretch=True,
                                            keep_ratio=True)
        self.gui_mediaview.add_widget(self._media_playing)

    def _media_play_pdf(self, filepath, interval=None):
        self._media_playing = PDFPlayer(source=filepath,
                                        temp_dir=self.temp_dir)
        if interval:
            self._media_playing.interval = interval
        self.gui_mediaview.add_widget(self._media_playing)

    def _media_play_video(self, *args, **kwargs):
        if self.config.video_external_player:
            self._media_play_video_omxplayer(*args, **kwargs)
        else:
            self._media_play_video_native(*args, **kwargs)

    def _media_play_video_native(self, filepath, loop=False):
        if loop:
            eos = 'loop'
        else:
            eos = 'stop'
        self._media_playing = Video(source=filepath, state='play',
                                    eos=eos, allow_stretch=True)
        self._media_playing.opacity = 0
        self.gui_mediaview.make_opaque()

        def _while_playing(*_):
            self._media_playing.opacity = 1
        self._media_playing.bind(texture=_while_playing)

        def _when_done(*_):
            self.media_stop()
        self._media_playing.bind(eos=_when_done)

        self.gui_mediaview.add_widget(self._media_playing)

    def _media_play_video_omxplayer(self, filepath, loop=False):
        geometry = self.geometry_transform(
            self.gui_mediaview.x, self.gui_mediaview.y,
            self.gui_mediaview.width, self.gui_mediaview.height
        )
        self._media_playing = ExternalMediaPlayer(
            filepath, geometry,
            self.media_stop, self, layer=None, loop=False,
            dbus_name='org.mpris.MediaPlayer2.omxplayer2',
            orientation=self.config.orientation
        )

    def media_stop(self, forced=False):
        print("Stopping Media : {0}".format(self._media_playing))
        if isinstance(self._media_playing, Video):
            self._media_playing.unload()
        elif isinstance(self._media_playing, ExternalMediaPlayer):
            self._media_playing.force_stop()
            self._media_playing = None
        elif isinstance(self._media_playing, StandardImage):
            pass
        elif isinstance(self._media_playing, PDFPlayer):
            self._media_playing.stop()
        self.gui_mediaview.clear_widgets()
        MediaPlayerMixin.media_stop(self, forced=forced)

    def stop(self):
        if self._media_player_backdrop:
            self._media_player_backdrop.close()
        super(MediaPlayerGuiMixin, self).stop()

    @property
    def gui_mediaview(self):
        if self._gui_mediaview is None:
            self._gui_mediaview = ColorBoxLayout(bgcolor=(0, 0, 0, 0))
            self.gui_main_content.add_widget(self._gui_mediaview)
            
            if self.config.video_show_backdrop:
                geometry = self.geometry_transform(
                    self.gui_mediaview.x, self.gui_mediaview.y,
                    self.gui_mediaview.width, self.gui_mediaview.height
                )
                self._media_player_backdrop.start(
                    self.config.video_backdrop_dispmanx_layer,
                    *geometry
                )

                def _backdrop_geometry(widget, _):
                    new_geometry = self.geometry_transform(
                        widget.x, widget.y, widget.width, widget.height
                    )
                    self._media_player_backdrop.set_geometry(*new_geometry)
                self.gui_mediaview.bind(size=_backdrop_geometry,
                                        pos=_backdrop_geometry)

            def _child_geometry(widget, _):
                if isinstance(self._media_playing, ExternalMediaPlayer):
                    new_geometry = self.geometry_transform(
                        widget.x, widget.y, widget.width, widget.height
                    )
                    self._media_playing.set_geometry(*new_geometry)
            self.gui_mediaview.bind(size=_child_geometry,
                                    pos=_child_geometry)
        return self._gui_mediaview

    def gui_setup(self):
        super(MediaPlayerGuiMixin, self).gui_setup()
        _ = self.gui_mediaview
