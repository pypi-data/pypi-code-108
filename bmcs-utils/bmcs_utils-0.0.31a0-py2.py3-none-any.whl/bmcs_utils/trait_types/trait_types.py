import traits.api as tr
from bmcs_utils.editors import \
    IntEditor, BoolEditor, FloatEditor, FloatRangeEditor, \
    ProgressEditor, ButtonEditor, ArrayEditor, \
    TextEditor

class TraitBase:
    def get_sub_nodes(self):
        """Let the trait extract the subnodes from its model
        """
        return []

# Specialized traits
class Int(TraitBase, tr.BaseInt):
    editor_factory = IntEditor


class Bool(TraitBase, tr.BaseBool):
    editor_factory = BoolEditor


class Float(TraitBase, tr.BaseFloat):
    editor_factory = FloatEditor


class Range(TraitBase, tr.BaseRange):
    editor_factory = FloatRangeEditor


class Str(TraitBase, tr.Str):
    editor_factory = TextEditor


class Array(TraitBase, tr.Array):
    editor_factory = ArrayEditor


### deprecated -- delete
class Progress(TraitBase, tr.BaseFloat):
    editor_factory = ProgressEditor

    def init(self):
        self.notify = []

    def add_notify(self, callback):
        self.notify.append(callback)

    def post_setattr(self, object_, name, value):
        for callback in self.notify:
            callback(value)

class Button(TraitBase, tr.Button):
    editor_factory = ButtonEditor

