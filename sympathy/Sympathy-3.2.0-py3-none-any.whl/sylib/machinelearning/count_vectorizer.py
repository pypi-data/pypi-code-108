# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
from sylib.machinelearning.descriptors import Descriptor


class CountVectorizerDescriptor(Descriptor):

    def post_fit(self, skl):
        vocabulary = skl.vocabulary_
        reversed = {index: label for label, index in vocabulary.items()}
        self.set_y_names([reversed[i] for i in range(len(reversed))])
