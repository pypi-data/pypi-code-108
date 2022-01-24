import traits.api as tr
from bmcs_utils.editors import \
    IntEditor, BoolEditor, FloatEditor, FloatRangeEditor, \
    ProgressEditor, ButtonEditor, SelectionEditor

# Specialized traits
class Int(tr.BaseInt):
    editor_factory = IntEditor


class Bool(tr.BaseBool):
    editor_factory = BoolEditor


class Float(tr.BaseFloat):
    editor_factory = FloatEditor


class Range(tr.BaseRange):
    editor_factory = FloatRangeEditor


### deprecated -- delete
class Progress(tr.BaseFloat):
    editor_factory = ProgressEditor

    def init(self):
        self.notify = []

    def add_notify(self, callback):
        self.notify.append(callback)

    def post_setattr(self, object_, name, value):
        for callback in self.notify:
            callback(value)

class Button(tr.Button):
    editor_factory = ButtonEditor

class Selection(tr.TraitType):
    editor_factor = SelectionEditor

    def init(self):
        print(self._metadata)