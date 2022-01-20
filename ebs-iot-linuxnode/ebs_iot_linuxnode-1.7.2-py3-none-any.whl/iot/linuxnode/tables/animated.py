

import gc
from collections import OrderedDict

from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout

from ebs.iot.linuxnode.animations.composite import CompositeAnimationManager

from .translatable import TranslatableRenderableTable


class AnimatedTable(TranslatableRenderableTable):
    def __init__(self, node, spec):
        self._current_entries = OrderedDict()
        self._animations = CompositeAnimationManager()
        self._animation_layer = None
        self._animation_lock = False
        super(AnimatedTable, self).__init__(node, spec)

    @property
    def active_entries(self):
        raise NotImplementedError

    def _build_title(self):
        raise NotImplementedError

    @property
    def animation_layer(self):
        if not self._animation_layer:
            self._animation_layer = RelativeLayout()
            self._gui_table_entries_container.add_widget(self._animation_layer)
        return self._animation_layer

    def _calculate_animation_distance(self, idx_source=None, idx_destination=None):
        if idx_source is None or idx_destination is None:
            ad_x = self._gui_table_entries.width
            ad_y = 0
        else:
            ad_x = 0
            ad_y = (idx_source - idx_destination) * self.row_pitch
        return ad_x, ad_y

    def _entry_pos(self, idx):
        return 0, self._gui_table_entries.height - (idx + 1) * self.row_pitch + 10

    def _entry_size(self):
        return self._gui_table_entries.width, self.row_pitch - 10

    def _delay_exit(self, idx):
        return Animation(d=0.1 * idx)

    def _delay_entry(self, idx):
        return Animation(d=0.1 * idx + 0.8)

    def _detach_entry(self, entry_bin):
        if entry_bin.parent == self._gui_table_entries:
            pos = entry_bin.pos
            self._gui_table_entries.remove_widget(entry_bin)
            entry_bin.pos = pos
            self.animation_layer.add_widget(entry_bin)

    def _detach_entries(self, entries):
        for tags, entry_bin in entries.items():
            self._detach_entry(entry_bin)
        self.log.debug("Detached {0} Entries, Remaining T={1},A={2} Entries"
                       "".format(len(entries),
                                 len(self._gui_table_entries.children),
                                 len(self.animation_layer.children)))

    def _exit_animation(self, idx):
        x, y = self._entry_pos(idx)
        dx, dy = self._calculate_animation_distance(idx, None)
        animation = Animation(x=x + dx, y=y + dy,
                              t='in_cubic', duration=1.)
        return animation

    def _destroy_dangling_entities(self):
        for instance in self.animation_layer.children:
            if hasattr(instance, 'stop'):
                instance.stop()
        self.animation_layer.clear_widgets()

    def _preposition_entry(self, idx, entry_bin):
        x, y = self._entry_pos(idx)
        dx, dy = self._calculate_animation_distance(None, idx)
        entry_bin.pos = x - dx, y - dy
        self.animation_layer.add_widget(entry_bin)

    def _position_entry(self, idx, entry_bin):
        entry_bin.pos = self._entry_pos(idx)
        self.animation_layer.add_widget(entry_bin)

    def _entry_animation(self, idx):
        px, py = self._entry_pos(idx)
        animation = Animation(x=px, y=py, t='out_cubic', duration=1.)
        return animation

    def _transfer_animation(self, idx):
        px, py = self._entry_pos(idx)
        animation = Animation(x=px, y=py, t='in_out_cubic', duration=1.)
        return animation

    def _still_animation(self):
        animation = Animation(d=1.)
        return animation

    def _attach_entry(self, entry_bin):
        self.animation_layer.remove_widget(entry_bin)
        self._gui_table_entries.add_widget(entry_bin)

    def _attach_entries(self, entries):
        for tags, entry_bin in entries.items():
            self._attach_entry(entry_bin)
        self.log.debug("Attached {0} Entries, Remaining T={1},A={2} Entries"
                       "".format(len(entries),
                                 len(self._gui_table_entries.children),
                                 len(self.animation_layer.children)))

    def _entries_change_handler(self, _, value):
        pass

    def _alternate_fallback_handler(self, _, entries):
        if self._gui_fallback:
            if not len(entries):
                if self._gui_table in self._gui_table_container.children:
                    self._gui_table_container.remove_widget(self._gui_table)
                if self._gui_fallback not in self._gui_table_container.children:
                    self._gui_table_container.add_widget(self._gui_fallback)
            else:
                if self._gui_fallback in self.gui_table_container.children:
                    self._gui_table_container.remove_widget(self._gui_fallback)
                if self._gui_table not in self.gui_table_container.children:
                    self._gui_table_container.add_widget(self._gui_table)

    def _build_entries(self, entries):
        rv = OrderedDict()
        for entry in entries:
            tags = [getattr(entry, x) for x in self.spec.dedup_keys]
            tags.append(self.language)
            tags = tuple(tags)
            entry_bin = entry.build(self.palette)
            entry_bin.size_hint = (None, None)
            entry_bin.size = self._entry_size()
            rv[tags] = entry_bin
        return rv

    def redraw_entries(self, entries):
        if self._animation_lock:
            self.log.warn("Animation lock is active! Force breaking.")

        self.log.debug("Redrawing Table, Got {0} Entries".format(len(entries)))
        self._alternate_fallback_handler(None, entries)
        self._detach_entries(self._current_entries)
        new_entries = self._build_entries(entries)
        deferred_tags = OrderedDict()

        self._animations.clear()

        for idx, (tags, entry_bin) in enumerate(self._current_entries.items()):
            if tags in new_entries.keys():
                deferred_tags[tags] = (idx, entry_bin)
                continue
            animation = self._delay_exit(idx) + self._exit_animation(idx)
            self._animations.add(animation, entry_bin)

        for idx, (tags, entry_bin) in enumerate(new_entries.items()):
            if tags in deferred_tags.keys():
                oidx, oentry_bin = deferred_tags[tags]
                self.animation_layer.remove_widget(oentry_bin)
                self._position_entry(oidx, entry_bin)
                if oidx < idx:
                    animation = self._delay_entry(idx) + self._transfer_animation(idx)
                else:
                    animation = self._transfer_animation(idx)
                self._animations.add(animation, entry_bin)
                continue
            self._preposition_entry(idx, entry_bin)
            animation = self._delay_entry(idx) + self._entry_animation(idx)
            self._animations.add(animation, entry_bin)

        def _finish():
            self._animation_lock = False
            self._attach_entries(self._current_entries)
            self._destroy_dangling_entities()
            gc.collect()

        self._current_entries = new_entries

        if len(self._animations):
            self._animations.when_done(_finish)
            self._animation_lock = True
            self._animations.start()
        else:
            _finish()
