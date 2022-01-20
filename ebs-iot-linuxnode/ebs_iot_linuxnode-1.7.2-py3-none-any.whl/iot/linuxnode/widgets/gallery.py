

import math

from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout

from kivy.properties import BooleanProperty
from kivy.properties import StringProperty
from kivy.animation import Animation

from .colors import ColorBoxLayout
from .image import StandardImage


class ImageGallery(ColorBoxLayout):
    visible = BooleanProperty(False)
    transition = StringProperty('in_out_elastic')

    def __init__(self, parent_layout=None, animation_vector=(0, 1),
                 exit_retrace=False, **kwargs):
        self.parent_layout = parent_layout
        self._animation_vector = animation_vector
        self._exit_retrace = exit_retrace

        self._animation_layer = None
        self._exit_animation = None
        self._entry_animation = None
        self._anim_distance_x = None
        self._anim_distance_y = None
        self._animation_distance = None

        super(ImageGallery, self).__init__(bgcolor=[0, 0, 0, 1], **kwargs)

        self.bind(visible=self._set_visibility)
        self.bind(size=self._calculate_animation_distance)
        self.bind(transition=self._reset_transitions)

        self._image = None

    def _set_visibility(self, *args):
        if self.visible:
            self.show()
        else:
            self.hide()

    def show(self):
        self.parent_layout.add_widget(self)

    def hide(self):
        self.clear_widgets()
        self._image = None
        self.animation_layer.clear_widgets()
        self._animation_layer = None
        self._reset_transitions()
        self.parent_layout.clear_widgets()

    def _reset_transitions(self, *args):
        self._exit_animation = None
        self._entry_animation = None

    def _calculate_animation_distance(self, *args):
        self._anim_distance_x = (self._animation_vector[0] * self.width)
        self._anim_distance_y = (self._animation_vector[1] * self.height)
        self._animation_distance = math.sqrt(self._anim_distance_x ** 2 + self._anim_distance_y ** 2)
        self._reset_transitions()

    @property
    def animation_distance(self):
        if not self._animation_distance:
            self._calculate_animation_distance()
        return self._animation_distance

    @property
    def animation_layer(self):
        if not self._animation_layer:
            self._animation_layer = RelativeLayout()
            self.parent_layout.add_widget(self.animation_layer,
                                          len(self.parent_layout.children) - 1)
        return self._animation_layer

    @property
    def exit_animation(self):
        if not self._exit_animation:
            _ = self.animation_distance

            def _when_done(_, instance):
                if not self._animation_layer:
                    return
                self.animation_layer.remove_widget(instance)
                if hasattr(instance, 'stop'):
                    instance.stop()

            if self._exit_retrace:
                sgn = -1
            else:
                sgn = 1
            self._exit_animation = Animation(y=self.pos[1] + sgn * self._anim_distance_y,
                                             x=self.pos[0] + sgn * self._anim_distance_x,
                                             t=self.transition, duration=2)
            self._exit_animation.bind(on_complete=_when_done)
        return self._exit_animation

    @property
    def entry_animation(self):
        if not self._entry_animation:
            _ = self.animation_distance

            def _when_done(_, instance):
                if not self._animation_layer:
                    return
                self.animation_layer.remove_widget(instance)
                instance.size_hint = (1, 1)
                self.add_widget(instance)
            self._entry_animation = Animation(y=self.pos[1], x=self.pos[0],
                                              t=self.transition, duration=2)
            self._entry_animation.bind(on_complete=_when_done)
        return self._entry_animation

    def _detach_image(self):
        if self._image:
            if self._image.parent == self:
                self.remove_widget(self._image)
            elif self._image.parent == self.animation_layer:
                self.animation_layer.remove_widget(self._image)

    @property
    def current(self):
        return self._image

    @current.setter
    def current(self, value):
        if value is None:
            self.visible = False
            self._detach_image()
            self._image = None
            return

        if self._image:
            pos = self._image.pos
            self._detach_image()
            self._image.size_hint = (None, None)
            self._image.pos = pos
            self.animation_layer.add_widget(self._image)
            self.exit_animation.start(self._image)

        if isinstance(value, Widget):
            self._image = value
        else:
            self._image = StandardImage(source=value, allow_stretch=True,
                                        keep_ratio=True, anim_delay=0.08)

        if not self.visible:
            self.add_widget(self._image)
            self.visible = True
            return

        self._image.size_hint = (None, None)
        self._image.size = self.size
        self._image.pos = (self.pos[0] - self._anim_distance_x,
                           self.pos[1] - self._anim_distance_y)
        self.animation_layer.add_widget(self._image)
        self.entry_animation.start(self._image)
        self.clear_widgets()
