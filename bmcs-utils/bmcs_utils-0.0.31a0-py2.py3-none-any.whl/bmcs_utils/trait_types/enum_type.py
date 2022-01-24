#-------------------------------------------------------------------------
#
# Copyright (c) 2009, IMB, RWTH Aachen.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in simvisage/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.simvisage.com/licenses/BSD.txt
#
# Thanks for using Simvisage open source!
#
# Created on Aug 7, 2009 by: rchx

from traits.api import TraitType, TraitError
from bmcs_utils.editors import EnumTypeEditor

import traits.api as tr

class Enum(TraitType):
    """Polymorphic instance - can accommodate the values
    of specified classes. Instances of the classes are created upon key assignement
    Unused instances are kept in cache."""
    editor_factory = EnumTypeEditor

    def __init__(self, options = [], **metadata):
        # validate that these are trait types
        self.options = [value for value in options]
        metadata.update({'options': options})
        super(Enum, self).__init__(**metadata)

    def validate(self, object, name, key):
        ''' Set the trait value '''
        if not (key in self.options):
            raise TraitError('value %s not in %s' % (key, self.options))
        return key

    def get_default_value(self):
        '''Take the first class to construct the value'''
        key = self.options[0]
        return (0, key)
