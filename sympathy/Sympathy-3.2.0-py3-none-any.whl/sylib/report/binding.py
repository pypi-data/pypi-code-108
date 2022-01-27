# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

import weakref


def assert_property(p):
    assert hasattr(p, 'get')
    assert hasattr(p, 'set')


def create_and_apply_hook(property_, binding_context):
    hook = _SetHook(property_, binding_context)
    property_.set = hook
    return hook


def remove_hook(hook):
    """
    Remove hook from function composition and fix setters such that
    the chain is unbroken.
    """
    # Traverse through all setters in function composition assuming that
    # all setters are SetHook-classes except for the last one which is
    # something else.
    #
    # Hook3(Hook2(Hook1(f_setter)))
    #
    # Removing Hook2 should give
    #
    # Hook3(Hook1(f_setter))
    #
    # which means that before removal we have:
    #
    # Hook1.previous_setter = f_setter
    # Hook2.previous_setter = Hook1
    # Hook3.previous_setter = Hook2
    #
    # and after removal of Hook2 we have:
    #
    # Hook1.previous_setter = f_setter
    # Hook3.previous_setter = Hook1
    #
    def iter_setters():
        setter_ = hook.property.set
        while isinstance(setter_, _SetHook):
            yield setter_
            setter_ = setter_.previous_setter
        yield setter_

    setter_list = list(iter_setters())
    index = setter_list.index(hook)
    if index > 0:
        setter_list[index - 1].previous_setter = setter_list[index + 1]
    else:
        hook.property.set = setter_list[index + 1]


class _SetHook(object):
    """Hook to trigger a notification of bindings.

    The hook stores the previous setter function while replacing it with
    the hook itself which emulates a function through __call__. Similar to
    function composition, but with a "notify" side-effect.
    """

    def __init__(self, property_, binding_context):
        assert_property(property_)
        assert isinstance(binding_context, BindingContext)
        self.property = property_
        self.previous_setter = property_.set
        self.context = weakref.ref(binding_context)

    def __call__(self, value):
        self.previous_setter(value)
        self.context().notify(self.property)


class PropertyWrapper(object):
    """Class implementing property interface."""

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def get(self):
        return self.getter()

    def set(self, value):
        self.setter(value)


class BindingContext(object):
    """Manager for data bindings."""

    def __init__(self):
        """Constructor."""
        # By using weak references keys delete themselves when an object is
        # garbage collected.
        self.bindings = weakref.WeakKeyDictionary()

    def notify(self, source_property):
        """
        Notify all listeners to source_property and update their values.
        :param source_property: Property where data originates from.
        """
        assert_property(source_property)
        value = source_property.get()
        if source_property in self.bindings:
            for target in (x for x in self.bindings[source_property]
                           if x != source_property):
                target.set(value)

    def register(self, source_property, target_property):
        """
        Register binding between source_item and target_item.
        :param source_property: Getter to bind from.
        :param target_property: Setter to bind to.
        """
        assert_property(source_property)
        assert_property(target_property)
        assert source_property != target_property
        if source_property in self.bindings:
            self.bindings[source_property].add(target_property)
        else:
            new_set = weakref.WeakSet({target_property})
            self.bindings[source_property] = new_set
        target_property.set(source_property.get())

    def unregister_source(self, source_property):
        pass

    def unregister_target(self, target_property):
        """
        Unregister all binding to target_item.
        :param target_property: Target item which binding targets.
        """
        # TODO(stefan): Is this necessary when everything is based on weak
        #               references?
        assert_property(target_property)
        for source_property in self.bindings:
            try:
                self.bindings[source_property].remove(target_property)
            except (KeyError, ValueError):
                pass

    def wrap_and_bind(self, source_property, target_getter, target_setter):
        """
        Convenience method for wrapping a target into a PropertyWrapper and
        registering the binding in the binding context.
        :param source_property: Source property.
        :param target_getter: Target setter function.
        :param target_setter: Target getter function.
        :returns: Target property wrapper.
        """
        create_and_apply_hook(source_property, self)
        wrapper = PropertyWrapper(target_getter, target_setter)
        self.register(source_property, wrapper)
        return wrapper
