# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


class Features:
    features = dict()
    """
    struct:

    feature_name: `dict`
        - description: `django.utils.translation.gettext`
        - priority: `int`

    """
    active_features = set()
    _latest_feature = None

    def define_feature(self, name, description=None, activate=False, priority=1):
        # if name in self.features:
        #     raise Exception("Feature %s alreadey exists" % name)
        self.features[name] = dict(description=description, priority=priority)
        self._latest_feature = name
        if activate:
            self.activate(name)
        return self

    def activate(self, name=None, priority=1):
        if name is None:
            name = self._latest_feature
        if name not in self.features:
            raise Exception("Feature %s does not exist." % name)
        if priority < self.features[name]['priority']:
            return
        self.features[name]['priority'] = priority
        self.active_features.add(name)

    def deactivate(self, name, priority=1):
        if name not in self.features:
            raise Exception("Feature %s does not exist." % name)
        if priority < self.features[name]['priority']:
            return
        self.features[name]['priority'] = priority
        self.active_features.remove(name)

    def has_feature(self, name):
        if name in self.active_features:
            return True
        return False

    def get_description(self, name):
        if name not in self.features:
            raise Exception("Feature %s does not exist." % name)
        return self.features[name]['description']

    def set_description(self, name, description):
        if name not in self.features:
            raise Exception("Feature %s does not exist." % name)
        self.features[name]['description'] = description

LINO_FEATURES = Features()

def has_feature(self, name):
    return self.features.has_feature(name)

def define_feature(self, *args, **kwargs):
    self.features.define_feature(*args, **kwargs)

def activate_feature(self, name, priority=1):
    self.features.activate(name, priority)

def deactivate_feature(self, name, priority=1):
    self.features.deactivate(name, priority)

def set_feature_description(self, name, description):
    self.features.set_description(name, description)

def get_feature_description(self, name):
    self.features.get_description(name)

FEATURES_HOOKS = dict(
    features = LINO_FEATURES,
    has_feature = has_feature,
    define_feature = define_feature,
    activate_feature = activate_feature,
    deactivate_feature = deactivate_feature,
    set_feature_description = set_feature_description,
    get_feature_description = get_feature_description
)
