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
import sklearn.base
import sklearn.exceptions
import sklearn.pipeline

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.pipeline import PipelineDescriptor
from sylib.machinelearning.abstract_nodes import SyML_abstract


class Pipeline(node.Node):
    name = 'Pipeline'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'pipeline.svg'
    description = 'Applies one model on the output of another'
    nodeid = 'org.sysess.sympathy.machinelearning.pipeline'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('models', 'models', n=(2, ))])
    outputs = Ports([ModelPort('Output model', 'out-model')])

    descriptor = PipelineDescriptor()
    descriptor.name = name
    descriptor.set_info([])

    parameters = node.parameters()
    parameters.set_string(
        'names', value='', label='Model names',
        description=(
            'Comma separated list of model names, eg. Rescale, SVC. '
            'If fewer names are given than models then default names '
            'will be used.'))
    parameters.set_boolean(
        'flatten', value=True, label='Flatten',
        description=(
            'Flattens multiple pipeline objects into a single pipeline '
            'containing all models'))

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        models = node_context.input.group('models')
        names_raw = node_context.parameters['names'].value
        flatten = node_context.parameters['flatten'].value

        name_list = [x.strip() for x in names_raw.split(', ')]
        name_list = list(filter(lambda x: x != "", name_list))
        if len(name_list) < len(models):
            for i in range(len(name_list), len(models)):
                model = models[i]
                model.load()
                desc = model.get_desc()
                name_list.append(desc.name)
        else:
            name_list = name_list[:len(models)]

        descs = []
        skls = []
        names = []
        for i, model in enumerate(models):
            model.load()
            desc = model.get_desc()
            if flatten and isinstance(desc, PipelineDescriptor):
                names += [tpl[0] for tpl in desc.models]
                descs += [tpl[1] for tpl in desc.models]
                skls += [tpl[2] for tpl in desc.models]
            else:
                names.append(name_list[i])
                descs.append(model.get_desc())
                skls.append(model.get_skl())

        skl = sklearn.pipeline.Pipeline(list(zip(names, skls)))
        desc = self.__class__.descriptor.new(skl)
        out_model.set_desc(desc)
        out_model.set_skl(skl)
        desc.set_steps(names, descs)
        out_model.save()


class SplitPipeline(node.Node):
    name = 'Pipeline decomposition'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'pipeline_split.svg'
    description = 'Pick out given model from a fitted pipeline'
    nodeid = 'org.sysess.sympathy.machinelearning.pipeline_split'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('model', 'model')])
    outputs = Ports([ModelPort('Output model', 'out-model')])

    parameters = node.parameters()
    parameters.set_string(
        'name', value='A', label='Model name or index',
        description=(
            'Index (0 to N) or name of model to pick out from pipeline'))

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        model = node_context.input['model']
        name = node_context.parameters['name'].value

        model.load()
        desc = model.get_desc()

        out_desc = None, None
        try:
            index = int(name)
            _, out_desc, out_skl = list(desc.get_models())[index]
        except ValueError:
            for n, d, s in desc.get_models():
                if n == name:
                    out_desc, out_skl = d, s
                    break

        if out_desc is not None:
            out_model.set_desc(out_desc)
            out_model.set_skl(out_skl)
            out_model.save()
