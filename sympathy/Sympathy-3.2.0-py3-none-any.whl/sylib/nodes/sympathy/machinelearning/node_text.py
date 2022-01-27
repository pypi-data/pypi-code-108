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
import sklearn
import sklearn.feature_extraction

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.count_vectorizer import CountVectorizerDescriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringListType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import StringType
from sylib.machinelearning.descriptors import UnionType


class CountVectorizer(SyML_abstract, node.Node):
    name = 'Text Count Vectorizer'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'count_vectorizer.svg'
    description = (
        'Convert a collection of text documents to a matrix of token counts')
    nodeid = 'org.sysess.sympathy.machinelearning.count_vectorizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = CountVectorizerDescriptor()
    descriptor.name = name
    info = [
        [
            "Model",
            {'name': 'encoding',
             'dispname': 'Encoding',
             'type': StringType(default='utf-8')},
            {'name': 'decode_error',
             'dispname': 'Decoding error behavior',
             'type': StringSelectionType(['strict', 'ignore', 'replace'],
                                         default='strict')},
            {'name': 'strip_accents',
             'dispname': 'Strip accents',
             'type': UnionType([StringSelectionType(['ascii', 'unicode']),
                                NoneType()], default=None)},
            {'name': 'lowercase',
             'dispname': 'Lowercase',
             'type': BoolType(default=True)},
        ],
        [   
            "Advanced",
            {'name': 'analyzer',
             'dispname': 'Analyzer',
             'type': StringSelectionType(['word', 'char', 'char_wb'],
                                         default='word')},
            {'name': 'ngram_range',
             'dispname': 'N-gram range',
             'type': IntListType(min_value=1, min_length=2, max_length=2,
                                 default=[1, 3])},
            {'name': 'stop_words',
             'dispname': 'Stop words',
             'type': UnionType([StringSelectionType('english'),
                                StringListType(min_length=1),
                                NoneType()], default='english')},
            {'name': 'max_df',
             'dispname': 'Maximum document frequency',
             'type': UnionType([
                 IntType(min_value=0),
                 FloatType(min_value=0.0, max_value=1.0)], default=1.0)},
            {'name': 'min_df',
             'dispname': 'Minimum document frequency',
             'type': UnionType([
                 IntType(min_value=0),
                 FloatType(min_value=0.0, max_value=1.0)], default=0.0)},
            {'name': 'max_features',
             'dispname': 'Maximum features',
             'type': UnionType([IntType(min_value=1),
                                NoneType()], default=None)},
            {'name': 'binary',
             'dispname': 'Binary',
             'type': BoolType(default=False)},
            #{'name': 'token_pattern',
            #  'type': UnionType([StringType(), NoneType()], default=None)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.feature_extraction.text.CountVectorizer)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'vocabulary_', 'stop_words_'
        ]], doc_class=sklearn.feature_extraction.text.CountVectorizer)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([])
    outputs = Ports([ModelPort('Model', 'model')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        model = node_context.output['model']
        desc = self.__class__.descriptor
        model.set_desc(desc)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        skl = sklearn.feature_extraction.text.CountVectorizer(**kwargs)

        model.set_skl(skl)
        model.save()
