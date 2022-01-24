# Copyright 2019 StreamSets Inc.

import base64
import collections
import inflection
import json
import logging
import re
import textwrap
from datetime import datetime
from uuid import uuid4
from decimal import Decimal

import dpath

from .models import Configuration
from .utils import format_log, get_params, pipeline_json_encoder, SeekableList, st_value_reader

logger = logging.getLogger(__name__)

dpath.options.ALLOW_EMPTY_STRING_KEYS = True

# This is a dictionary mapping stage names to attribute aliases. As an example, if a particular
# stage had a label updated in a more recent ST release, the older attribute name should be mapped
# to the newer one.
STAGE_ATTRIBUTE_ALIASES = {
}

StageConfigurationProperty = collections.namedtuple('StageConfigurationProperty',
                                                    ['config_name'])

ServiceConfigurationProperty = collections.namedtuple('ServiceConfigurationProperty',
                                                      ['service_name', 'config_name'])


def get_dpath_compatible_field_path(field_path):
    """Converts ST field path to a dpath compatible path.

    Helpful when ST field path have index based access for lists or when they have glob patterns.
    """
    # Following regex converts ST specific field paths
    # with list indexes such as from [2]/east/HR[0]/employeeName to dpath specific 2/east/HR/0/employeeName
    # or with globs such as from /Division[*]/Employee[*]/SSN to dpath specific /Division/*/Employee/*/SSN
    dpath_compatible = re.sub(r'\[([0-9*]+)]', r'/\1', field_path)
    return dpath_compatible


class Stage:
    """Pipeline stage.

    Args:
        stage: JSON representation of the pipeline stage.
        label (:obj:`str`, optional): Human-readable stage label. Default: ``None``.

    Attributes:
        configuration (:py:class:`streamsets.sdk.models.Configuration`): The stage configuration.
        services (:obj:`dict`): If supported by the stage, a dictionary mapping a service name to
            an instance of :py:class:`streamsets.sdk.models.Configuration`.
    """
    def __init__(self, stage, label=None):
        self._data = stage

        self.configuration = Configuration(self._data['configuration'])

        self.instance_name = stage['instanceName']
        self.stage_name = stage['stageName']
        self.stage_version = stage['stageVersion']
        self.stage_type = stage['uiInfo']['stageType']

        if 'services' in self._data:
            self.services = {service['service']: Configuration(service['configuration'])
                             for service in self._data['services']}

        # Add a docstring to show stage attributes when help() is run on a Stage instance.
        # Attributes will be printed in two columns.
        attrs_ = list(sorted(self._attributes.keys()))
        split = int(len(attrs_)/2)

        self.__class__.__doc__ = textwrap.dedent(
            '''
            Stage: {label}

            Attributes:
            {attributes}
            '''
        ).format(label=label,
                 attributes='\n'.join('{:<60}{:<60}'.format(first, second)
                                      for first, second in zip(attrs_[:split], attrs_[split:])))

    @property
    def label(self):
        """:obj:`str`: The stage's label."""
        return self._data['uiInfo']['label']

    @label.setter
    def label(self, value):
        self._data['uiInfo']['label'] = value

    @property
    def _attributes(self):
        """This property acts as a placeholder to ensure that __getattr__ and __setattr__ logic works for
        generic instances of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        return {}

    @property
    def library(self):
        """Get the stage's library.

        Returns:
            The stage library as a :obj:`str`.
        """
        return self._data['library']

    @library.setter
    def library(self, library):
        self._data['library'] = library

    @property
    def output_lanes(self):
        """Get the stage's list of output lanes.

        Returns:
            A :obj:`list` of output lanes.
        """
        return self._data['outputLanes']

    @property
    def event_lanes(self):
        """Get the stage's list of event lanes.

        Returns:
            A :obj:`list` of event lanes.
        """
        return self._data['eventLanes']

    @property
    def stage_on_record_error(self):
        """The stage's on record error configuration value."""
        return self.configuration['stageOnRecordError']

    @stage_on_record_error.setter
    def stage_on_record_error(self, value):
        self.configuration['stageOnRecordError'] = value

    @property
    def stage_required_fields(self):
        """The stage's required fields configuration value."""
        return self.configuration['stageRequiredFields']

    @stage_required_fields.setter
    def stage_required_fields(self, value):
        self.configuration['stageRequiredFields'] = value

    @property
    def stage_record_preconditions(self):
        """The stage's record preconditions configuration value."""
        return self.configuration['stageRecordPreconditions']

    @stage_record_preconditions.setter
    def stage_record_preconditions(self, value):
        self.configuration['stageRecordPreconditions'] = value

    def add_output(self, *other_stages, event_lane=False):
        """Connect output of this stage to another stage.

        The __rshift__ operator (`>>`) has been overloaded to invoke this method.

        Args:
            other_stage (:py:class:`streamsets.sdk.st_models.Stage`): Stage object.

        Returns:
            This stage as an instance of :py:class:`streamsets.sdk.st_models.Stage`).
        """
        # We deviate from the algorithm that ST uses (https://git.io/vShnt) and rather use just UUID. This is to
        # avoid generating the same time based id when the script runs too fast.
        lane = ('{}OutputLane{}'.format(self._data['instanceName'], str(uuid4())).replace('-', '_')
                if not event_lane
                else '{}_EventLane'.format(self._data['instanceName']))
        if not event_lane:
            self._data['outputLanes'].append(lane)
        else:
            self._data['eventLanes'].append(lane)
        for other_stage in other_stages:
            other_stage._data['inputLanes'].append(lane)

        return self

    def set_attributes(self, **attributes):
        """Set one or more stage attributes.

        Args:
            **attributes: Attributes to set.

        Returns:
            This stage as an instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        logger.debug('Setting attributes for stage %s (%s) ...',
                     self.instance_name,
                     ', '.join(['{}={}'.format(attribute, value) for attribute, value in attributes.items()]))
        for attribute, value in attributes.items():
            setattr(self, attribute, value)

        return self

    def __getattr__(self, name):
        if name in self._attributes:
            attribute_value = self._attributes.get(name)
            config_properties = [attribute_value] if not isinstance(attribute_value, list) else attribute_value
            for config_property in config_properties:
                if (isinstance(config_property, StageConfigurationProperty) and
                        config_property.config_name in self.configuration):
                    return self.configuration[config_property.config_name]
                elif (isinstance(config_property, ServiceConfigurationProperty) and
                        config_property.service_name in getattr(self, 'services', {})):
                    return self.services[config_property.service_name][config_property.config_name]
        elif self.__class__.__name__ in STAGE_ATTRIBUTE_ALIASES:
            stage_attribute_aliases = STAGE_ATTRIBUTE_ALIASES.get(self.__class__.__name__)
            if name in stage_attribute_aliases:
                return getattr(self, stage_attribute_aliases[name])

        raise AttributeError('Could not find configuration properties referenced by attribute "{}."'.format(name))

    def __setattr__(self, name, value):
        # We override __setattr__ to enable dynamically creating setters for attributes that
        # aren't stored in the normal instance dictionary.
        if name in self._attributes:
            attribute_value = self._attributes.get(name)
            config_properties = [attribute_value] if not isinstance(attribute_value, list) else attribute_value

            # Using a state variable like this isn't very Pythonic, but we can't use a for-else
            # here because we want to update every possible config in the list, which means
            # we don't want to break out early.
            found_config = False
            for config_property in config_properties:
                if (isinstance(config_property, StageConfigurationProperty)
                        and config_property.config_name in self.configuration):
                    found_config = True
                    self.configuration[config_property.config_name] = value
                elif (isinstance(config_property, ServiceConfigurationProperty) and
                        config_property.service_name in getattr(self, 'services', {})):
                    found_config = True
                    self.services[config_property.service_name][config_property.config_name] = value
            if not found_config:
                # If we haven't found any key, then something is definitely wrong
                raise ValueError('Could not find configuration properties '
                                 'referenced by attribute "{}".'.format(name))
        elif (self.__class__.__name__ in STAGE_ATTRIBUTE_ALIASES and
                name in STAGE_ATTRIBUTE_ALIASES[self.__class__.__name__]):
            setattr(self, STAGE_ATTRIBUTE_ALIASES[self.__class__.__name__][name], value)
        else:
            # If we got this far and haven't found the name to be an attribute, assume
            # it's an instance attribute.
            super().__setattr__(name, value)

    def __contains__(self, item):
        for config_property in self._data:
            if config_property.get(self.property_key) == item:
                return True
        return False

    def __dir__(self):
        return sorted(list(dir(object)) + list(self.__dict__.keys()) + list(self._attributes.keys()))

    def __ge__(self, other):
        # This method override results in overloading the >= operator to allow us to connect the
        # event lane of one Stage to the input lane of another.

        if isinstance(other, list):
            self.add_output(*other, event_lane=True)
        else:
            self.add_output(other, event_lane=True)
        # Python treats `a >= b >= c` as `a >= b and b >= c`, so return True to ensure that chained
        # connections propagate all the way through.
        return True

    def __repr__(self):
        repr_metadata = ['instance_name']
        return '<{} ({})>'.format(self.__class__.__name__,
                                  ', '.join('{}={}'.format(key, getattr(self, key)) for key in repr_metadata))

    def __rshift__(self, other):
        # Support for `a >> b >> c`. Support chaining unless connecting to a list.
        if isinstance(other, list):
            self.add_output(*other)
        else:
            self.add_output(other)
        return other if not isinstance(other, list) else None


class PipelineBuilder:
    """Class with which to build ST pipelines.

    This class allows a user to programmatically generate an ST pipeline. Instead of instantiating this
    class directly, most users should use :py:meth:`streamsets.sdk.Transformer.get_pipeline_builder`.

    Args:
        pipeline (:obj:`dict`): Python object representing an empty pipeline. If created manually, this
            would come from creating a new pipeline in ST and then exporting it before doing any
            configuration.
        definitions (:obj:`dict`): The output of ST's definitions endpoint.
    """
    MAX_STAGE_INSTANCES = 1000
    STAGE_TYPES = {'origin': 'SOURCE',
                   'destination': 'TARGET',
                   'executor': 'EXECUTOR',
                   'processor': 'PROCESSOR'}

    def __init__(self, pipeline, definitions):
        self._pipeline = pipeline
        # Set the underlying ID in self._pipeline to None to ensure that each instance of
        # :py:class:`streamsets.sdk.st_models.PipelineBuilder` gets a unique ID when
        # :py:meth:`streamsets.sdk.st_models.PipelineBuilder.build` is called.
        Pipeline(self._pipeline).id = None

        self._definitions = definitions
        self._all_stages = self._generate_all_stages(self._definitions)

    @staticmethod
    def _generate_all_stages(definitions):
        all_stages = {}

        REPLACE_BAD_CHARS_ARGS = [r'[\s-]+', r'_']
        REPLACE_AMPERSAND_ARGS = [r'&', r'and']
        REPLACE_PER_SEC_ARGS = [r'/sec', r'_per_sec']
        REPLACE_PAREN_UNITS_ARGS = [r'_\((.+)\)', r'_in_\1']

        def get_attribute(config_definition):
            config_name = config_definition['name']
            # Most stages have labels, which we use as attribute names after sanitizing and standardizing
            # (i.e. converting to lowercase, replacing spaces and dashes with underscores, and converting
            # parenthesized units into readable strings).
            label = config_definition.get('label')
            if label:
                attribute_name = re.sub(*REPLACE_PAREN_UNITS_ARGS,
                                        string=re.sub(*REPLACE_PER_SEC_ARGS,
                                                      string=re.sub(*REPLACE_AMPERSAND_ARGS,
                                                                    string=re.sub(*REPLACE_BAD_CHARS_ARGS,
                                                                                  string=label.lower()))))
            else:
                attribute_name = inflection.underscore(config_definition['fieldName'])
            return attribute_name, config_name

        # For various reasons, a few configurations don't lend themselves to easy conversion
        # from their labels; the overrides handle those edge cases.
        STAGE_CONFIG_OVERRIDES = {
        }

        for stage_definition in definitions['stages']:
            stage_name = stage_definition['name']
            attributes = collections.defaultdict(list)
            for config_definition in stage_definition['configDefinitions']:
                attribute_name, config_name = get_attribute(config_definition)
                attributes[attribute_name].append(StageConfigurationProperty(config_name=config_name))
            # Default empty list when getting services to support pre-service framework STs.
            for service in stage_definition.get('services', []):
                service_name = service['service']
                for service_definition in definitions['services']:
                    if service_definition['provides'] == service_name:
                        break
                else:
                    raise Exception('Could not find definition of service {}.'.format(service_name))
                for config_definition in service_definition['configDefinitions']:
                    attribute_name, config_name = get_attribute(config_definition)
                    attributes[attribute_name].append(ServiceConfigurationProperty(service_name=service_name,
                                                                                   config_name=config_name))

            if stage_name in STAGE_CONFIG_OVERRIDES:
                attributes.update(STAGE_CONFIG_OVERRIDES[stage_name])

            all_stages[stage_name] = type(stage_name,
                                          (_Stage, ),
                                          {'_attributes': attributes})
        return all_stages

    def import_pipeline(self, pipeline, **kwargs):
        """Import a pipeline into the PipelineBuilder.

        Args:
            pipeline (:obj:`dict`): Exported pipeline.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelineBuilder`.
        """
        # Always regenerate the pipeline id unless regenerate_id is specified as False.
        if kwargs.get('regenerate_id') is None or kwargs.get('regenerate_id'):
            pipeline['pipelineConfig']['info']['pipelineId'] = None
        self._pipeline = pipeline
        return self

    def build(self, title='Pipeline'):
        """Build the pipeline.

        Args:
            title (:obj:`str`, optional): Pipeline title to use. Default: ``'Pipeline'``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        if not self._pipeline['pipelineConfig']['errorStage']:
            # Note: Transformer does not have error stage capability. Uncomment below when needed.
            # logger.warning("PipelineBuilder missing error stage. Will use 'Discard.'")
            # self.add_error_stage(label='Discard')
            pass

        self._auto_arrange()
        self._update_graph()

        pipeline = (_Pipeline)(pipeline=self._pipeline, all_stages=self._all_stages)
        # Generate pipeline ID in the same way as ST does (https://git.io/fNQGM). Note that
        # we only do this if the pipeline ID is unset to avoid generating a new one
        # when a builder is simply rebuilt.
        if pipeline.id is None:
            pipeline.id = '{}{}'.format(re.sub(r'[\W]|_', r'', title), uuid4())
        pipeline.title = title
        self._pipeline['pipelineConfig']['title'] = title
        return pipeline

    def add_data_drift_rule(self, *data_drift_rules):
        """Add one or more data drift rules to the pipeline.

        Args:
            *data_drift_rules: One or more instances of :py:class:`streamsets.sdk.st_models.DataDriftRule`.
        """
        for data_drift_rule in data_drift_rules:
            self._pipeline['pipelineRules']['driftRuleDefinitions'].append(data_drift_rule._data)

    def add_data_rule(self, *data_rules):
        """Add one or more data rules to the pipeline.

        Args:
            *data_rules: One or more instances of :py:class:`streamsets.sdk.st_models.DataRule`.
        """
        for data_rule in data_rules:
            self._pipeline['pipelineRules']['dataRuleDefinitions'].append(data_rule._data)

    def add_metric_rule(self, *metric_rules):
        """Add one or more metric rules to the pipeline.

        Args:
            *data_rules: One or more instances of :py:class:`streamsets.sdk.st_models.MetricRule`.
        """
        for metric_rule in metric_rules:
            self._pipeline['pipelineRules']['metricsRuleDefinitions'].append(metric_rule._data)

    def add_stage(self, label=None, name=None, type=None, library=None):
        """Add a stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. ``type`` and ``library``
        may also be used to select a particular stage if ambiguities exist. If ``type`` and/or ``library``
        are omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): ST stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): ST stage name to use when selecting stage from
                definitions. Default: ``None``.
            type (:obj:`str`, optional): ST stage type to use when selecting stage from
                definitions (e.g. `origin`, `destination`, `processor`, `executor`). Default: ``None``.
            library (:obj:`str`, optional): ST stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             type=type, library=library)
                                           if stage.definition.get('errorStage') is False)
        self._pipeline['pipelineConfig']['stages'].append(stage_instance)
        return self._all_stages.get(stage_instance['stageName'], Stage)(stage=stage_instance,
                                                                        label=stage_label)

    def add_error_stage(self, label=None, name=None, library=None):
        """Add an error stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. If ``library`` is
        omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): ST stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): ST stage name to use when selecting stage from
                definitions. Default: ``None``.
            library (:obj:`str`, optional): ST stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             library=library)
                                           if stage.definition.get('errorStage') is True)
        self._pipeline['pipelineConfig']['errorStage'] = stage_instance
        self._set_pipeline_configuration('badRecordsHandling', self._stage_to_configuration_name(stage_instance))
        return self._all_stages.get(stage_instance['stageName'],
                                    Stage)(stage=stage_instance, label=stage_label)

    def add_start_event_stage(self, label=None, name=None, library=None):
        """Add start event stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. If ``library`` is
        omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): ST stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): ST stage name to use when selecting stage from
                definitions. Default: ``None``.
            library (:obj:`str`, optional): ST stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             library=library)
                                           if stage.definition.get('pipelineLifecycleStage') is True)
        self._pipeline['pipelineConfig']['startEventStages'] = [stage_instance]
        self._set_pipeline_configuration('startEventStage', self._stage_to_configuration_name(stage_instance))
        return self._all_stages.get(stage_instance['stageName'],
                                    Stage)(stage=stage_instance, label=stage_label)

    def add_stop_event_stage(self, label=None, name=None, library=None):
        """Add stop event stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. If ``library`` is
        omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): ST stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): ST stage name to use when selecting stage from
                definitions. Default: ``None``.
            library (:obj:`str`, optional): ST stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             library=library)
                                           if stage.definition.get('pipelineLifecycleStage') is True)
        self._pipeline['pipelineConfig']['stopEventStages'] = [stage_instance]
        self._set_pipeline_configuration('stopEventStage', self._stage_to_configuration_name(stage_instance))
        return self._all_stages.get(stage_instance['stageName'],
                                    Stage)(stage=stage_instance, label=stage_label)

    def add_stats_aggregator_stage(self, label=None, name=None, library=None):
        """Add a stats aggregator stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. If ``library`` is
        omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): ST stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): ST stage name to use when selecting stage from
                definitions. Default: ``None``.
            library (:obj:`str`, optional): ST stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             library=library)
                                           if stage.definition.get('statsAggregatorStage') is True)
        self._pipeline['pipelineConfig']['statsAggregatorStage'] = stage_instance
        self._set_pipeline_configuration('statsAggregatorStage', self._stage_to_configuration_name(stage_instance))
        return self._all_stages.get(stage_instance['stageName'],
                                    Stage)(stage=stage_instance, label=stage_label)

    def _stage_to_configuration_name(self, stage):
        """Generate stage full name in a way that is expected in pipeline's configuration."""
        return '{}::{}::{}'.format(stage['library'], stage['stageName'], stage['stageVersion'])

    def _set_pipeline_configuration(self, name, value):
        """Set given configuration name in the pipeline configuration."""
        Configuration(self._pipeline['pipelineConfig']['configuration'])[name] = value

    def _get_stage_data(self, label=None, name=None, type=None, library=None):
        # When traversing through the stage definitions, match either the stage label or stage name
        # and then, if specified, the stage library. Also note that we call each individual stage
        # definition simply "stage" from here on out and differentiate that from "stage instance,"
        # which exists in a particular pipeline. This is done to fall in line with ST's usage in
        # its source code.
        if label and name:
            raise Exception('Use `label` or `name`, not both.')
        elif not label and not name:
            raise Exception('Either `label` or `name` must be specified.')

        stages = [stage for stage in self._definitions['stages']
                  if ((label and stage['label'] == label or name and stage['name'] == name)
                      and (not library or stage['library'] == library)
                      and (not type or stage['type'] == PipelineBuilder.STAGE_TYPES.get(type, type)))]
        if not stages:
            raise Exception('Could not find stage ({}).'.format(label or name))
        return [collections.namedtuple('StageData', ['definition',
                                                     'instance'])(definition=stage,
                                                                  instance=self._get_new_stage_instance(stage))
                for stage in stages]

    def _auto_arrange(self):
        # A port of pipelineService.js's autoArrange (https://git.io/vShBI).
        x_pos = 60
        y_pos = 50
        stages = self._pipeline['pipelineConfig']['stages']
        lane_y_pos = {}
        lane_x_pos = {}

        for stage in stages:
            y = (lane_y_pos.get(stage['inputLanes'][0], 0)
                 if len(stage['inputLanes'])
                 else y_pos)
            x = (lane_x_pos.get(stage['inputLanes'][0], 0) + 220
                 if len(stage['inputLanes'])
                 else x_pos)

            if len(stage['inputLanes']) > 1:
                m_x = 0
                for input_lane in stage['inputLanes']:
                    if lane_x_pos.get(input_lane, 0) > m_x:
                        m_x = lane_x_pos.get(input_lane, 0)
                x = m_x + 220

            if lane_y_pos.get(stage['inputLanes'][0] if stage['inputLanes'] else None):
                lane_y_pos[stage['inputLanes'][0]] += 150

            if not y:
                y = y_pos

            if len(stage['outputLanes']) > 1:
                for i, output_lane in enumerate(stage['outputLanes']):
                    lane_y_pos[output_lane] = y - 10 + (130 * i)
                    lane_x_pos[output_lane] = x

                if y == y_pos:
                    y += 30 * len(stage['outputLanes'])
            else:
                if len(stage['outputLanes']):
                    lane_y_pos[stage['outputLanes'][0]] = y
                    lane_x_pos[stage['outputLanes'][0]] = x

                if len(stage['inputLanes']) > 1 and y == y_pos:
                    y += 130

            if len(stage['eventLanes']):
                lane_y_pos[stage['eventLanes'][0]] = y + 150
                lane_x_pos[stage['eventLanes'][0]] = x

            stage['uiInfo']['xPos'] = x
            stage['uiInfo']['yPos'] = y

            x_pos = x + 220

    def _update_graph(self):
        # A port of pipelineHome.js's updateGraph (https://git.io/v97Ys).

        # For now, we're just implementing the metadata initialization needed for label support.
        self._pipeline['pipelineConfig']['metadata'] = {'labels': []}

    def _get_new_stage_instance(self, stage):
        # A port of pipelineService.js's getNewStageInstance (https://git.io/vSh2u).
        stage_instance = {
            'instanceName': self._get_stage_instance_name(stage),
            'library': stage['library'],
            'stageName': stage['name'],
            'stageVersion': stage['version'],
            'configuration': [],
            'uiInfo': {
                'description': '',
                'label': self._get_stage_label(stage),
                'xPos': None,
                'yPos': None,
                'stageType': stage['type']
            },
            'inputLanes': [],
            'outputLanes': [],
            'eventLanes': []
        }

        stage_instance['configuration'] = [self._set_default_value_for_config(config_definition,
                                                                              stage_instance)
                                           for config_definition in stage['configDefinitions']]

        # services were introduced to pipeline configurations in ST 3.0.0.
        if self._pipeline['pipelineConfig']['schemaVersion'] >= 5:
            stage_instance['services'] = [
                {'service': service_definition['provides'],
                 'serviceVersion': service_definition['version'],
                 'configuration': [self._set_default_value_for_config(config_definition, None)
                                   for config_definition
                                   in service_definition['configDefinitions']]}
                for service in stage['services']
                for service_definition in self._definitions['services']
                if service_definition['provides'] == service['service']
            ]

            # Propagate RUNTIME configuration injected by the stage.
            for stage_instance_service in stage_instance['services']:
                for service in stage['services']:
                    if stage_instance_service['service'] == service['service']:
                        Configuration(stage_instance_service['configuration']).update(service['configuration'])

        return stage_instance

    def _get_stage_instance_name(self, stage):
        # A port of pipelineService.js's getStageInstanceName (https://git.io/vSpj1).
        stage_name = stage['label'].replace(' ', '').replace('/', '')

        if stage['errorStage']:
            return '{}_ErrorStage'.format(stage_name)
        elif stage['statsAggregatorStage']:
            return '{}_StatsAggregatorStage'.format(stage_name)
        else:
            # Breaking slightly from the logic of the Javascript version, all we need to do is find
            # the first instanceName that doesn't already exist in the pipeline. Here's a O(n) way
            # to do it.
            similar_instances = set(stage_instance['instanceName']
                                    for stage_instance
                                    in self._pipeline['pipelineConfig']['stages'])

            # Add one since `range` is exclusive on end value.
            for i in range(1, PipelineBuilder.MAX_STAGE_INSTANCES + 1):
                # `{:0>2}` is Python magic for zero padding single-digit numbers on the left.
                new_instance_name = '{}_{:0>2}'.format(stage_name, i)
                if new_instance_name not in similar_instances:
                    break
            else:
                raise Exception("Couldn't find unique instanceName "
                                "after {} attempts.".format(PipelineBuilder.MAX_STAGE_INSTANCES))
            return new_instance_name

    def _get_stage_label(self, stage):
        # A port of pipelineService.js's getStageLabel (https://git.io/vSpbX).
        if stage['errorStage']:
            return 'Error Records - {}'.format(stage['label'])
        elif stage['statsAggregatorStage']:
            return 'Stats Aggregator - {}'.format(stage['label'])
        else:
            similar_instances = sum(stage['label'] in stage_instance['uiInfo']['label']
                                    for stage_instance
                                    in self._pipeline['pipelineConfig']['stages'])
            return '{} {}'.format(stage['label'], similar_instances + 1)

    def _set_default_value_for_config(self, config_definition, stage_instance):
        # A port of pipelineService.js's setDefaultValueForConfig method (https://git.io/vSh3W).
        config = {
            'name': config_definition['name'],
            'value': config_definition['defaultValue']
        }

        if config_definition['type'] == 'MODEL':
            if (config_definition['model']['modelType'] == 'FIELD_SELECTOR_MULTI_VALUE'
                    and not config['value']):
                config['value'] = []
            # We don't follow the logic for PREDICATE as that assumes that the stage already have output lanes.
            # However this is called at the time of stage initialization on our side and the stage output lanes
            # does not exists until user explicitly connects stages together.
            elif config_definition['model']['modelType'] == 'LIST_BEAN':
                config['value'] = [
                    {self._set_default_value_for_config(model_config_definition,
                                                        stage_instance)['name']:
                     self._set_default_value_for_config(model_config_definition,
                                                        stage_instance).get('value')
                     for model_config_definition in config_definition['model']['configDefinitions']
                     if (self._set_default_value_for_config(model_config_definition,
                                                            stage_instance).get('value')
                         is not None)}
                ]
        elif config_definition['type'] == 'BOOLEAN' and config['value'] is None:
            config['value'] = False
        elif config_definition['type'] == 'LIST' and not config['value']:
            config['value'] = []
        elif config_definition['type'] == 'MAP' and not config['value']:
            config['value'] = []

        return config


class Pipeline:
    """ST pipeline.

    This class provides abstractions to make it easier to interact with a pipeline before it's
    imported into ST.

    Args:
        pipeline (:obj:`dict`): A Python object representing the serialized pipeline.
        all_stages (:py:obj:`dict`, optional): A dictionary mapping stage names to
            :py:class:`streamsets.sdk.st_models.Stage` instances. Default: ``None``.
    """
    def __init__(self, pipeline, all_stages=None):
        self._data = pipeline
        self._all_stages = all_stages or {}

    @property
    def configuration(self):
        """Get pipeline's configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.models.Configuration`.
        """
        return Configuration(self._data['pipelineConfig']['configuration'])

    @property
    def id(self):
        """Get the pipeline id.

        Returns:
            The pipeline id as a :obj:`str`.
        """
        schema_version = self._data['pipelineConfig']['schemaVersion']
        return (self._data['pipelineConfig']['info']['pipelineId']
                if schema_version > 2
                else self._data['pipelineConfig']['info']['name'])

    @id.setter
    def id(self, id):
        self._data['pipelineConfig']['info']['name'] = id
        schema_version = self._data['pipelineConfig']['schemaVersion']
        if schema_version > 2:
            self._data['pipelineConfig']['info']['pipelineId'] = id
            self._data['pipelineConfig']['pipelineId'] = id

    @property
    def title(self):
        """Get the pipeline title.

        Returns:
            The pipeline title as a :obj:`str`.
        """
        return self._data['pipelineConfig']['title']

    @title.setter
    def title(self, name):
        self._data['pipelineConfig']['title'] = name

    @property
    def delivery_guarantee(self):
        """Get the delivery guarantee.

        Returns:
            The delivery guarantee as a :obj:`str`.
        """
        return self.configuration['deliveryGuarantee']

    @delivery_guarantee.setter
    def delivery_guarantee(self, value):
        self.configuration['deliveryGuarantee'] = value

    @property
    def rate_limit(self):
        """Get the rate limit (records/sec).

        Returns:
            The rate limit as a :obj:`str`.
        """
        return self.configuration['rateLimit']

    @rate_limit.setter
    def rate_limit(self, value):
        self.configuration['rateLimit'] = value

    @property
    def parameters(self):
        """Get the pipeline parameters.

        Returns:
            A :obj:`dict` of parameter key-value pairs.
        """
        return {parameter['key']: parameter['value'] for parameter in self.configuration['constants']}

    def add_parameters(self, **parameters):
        """Add pipeline parameters.

        Args:
            **parameters: Keyword arguments to add.
        """
        for key, value in parameters.items():
            self.configuration['constants'].append({'key': key, 'value': value})

    @property
    def metadata(self):
        """Get the pipeline metadata.

        Returns:
            Pipeline metadata as a Python object.
        """
        return self._data['pipelineConfig']['metadata']

    @property
    def origin_stage(self):
        """Get the pipeline's origin stage.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Stage`.
        """
        return self.stages.get(stage_type='SOURCE')

    def __iter__(self):
        for stage in self.stages:
            yield stage

    def __getitem__(self, key):
        return self.stages[key]

    def __repr__(self):
        repr_metadata = ['id', 'title']
        return '<{} ({})>'.format(self.__class__.__name__,
                                  ', '.join('{}={}'.format(key, getattr(self, key)) for key in repr_metadata))

    @property
    def stages(self):
        return SeekableList(self._all_stages.get(stage['stageName'],
                                                 Stage)(stage=stage, label=stage['stageName'])
                            for stage in self._data['pipelineConfig']['stages']
                            if 'instanceName' in stage and 'stageName' in stage)

    @property
    def error_stage(self):
        error_stage = self._data['pipelineConfig']['errorStage']
        return (self._all_stages.get(error_stage['stageName'],
                                     Stage)(stage=error_stage, label=error_stage['stageName'])
                if error_stage else None)

    def pprint(self):
        """Pretty-print the pipeline's JSON representation."""
        print(json.dumps(self._data, indent=4, default=pipeline_json_encoder))


class DataRule:
    """Pipeline data rule.

    Args:
        stream (:obj:`str`): Stream to use for data rule. An entry from a Stage instance's `output_lanes` list
            is typically used here.
        label (:obj:`str`): Rule label.
        condition (:obj:`str`, optional): Data rule condition. Default: ``None``.
        sampling_percentage (:obj:`int`, optional): Default: ``5``.
        sampling_records_to_retain (:obj:`int`, optional): Default: ``10``.
        enable_meter (:obj:`bool`, optional): Default: ``True``.
        enable_alert (:obj:`bool`, optional): Default: ``True``.
        alert_text (:obj:`str`, optional): Default: ``None``.
        threshold_type (:obj:`str`, optional): One of ``count`` or ``percentage``. Default: ``'count'``.
        threshold_value (:obj:`int`, optional): Default: ``100``.
        min_volume (:obj:`int`, optional): Only set if ``threshold_type`` is ``percentage``. Default: ``1000``.
        send_email (:obj:`bool`, optional): Default: ``False``.
        active (:obj:`bool`, optional): Enable the data rule. Default: ``False``.
    """
    def __init__(self, stream, label, condition=None, sampling_percentage=5, sampling_records_to_retain=10,
                 enable_meter=True, enable_alert=True, alert_text=None, threshold_type='count', threshold_value=100,
                 min_volume=1000, send_email=False, active=False):
        # We deviate from the algorithm that ST uses (https://git.io/v97ZJ) and rather use just UUID. This is to
        # avoid generating the same time based id when the script runs too fast.
        self._data = {'id': str(uuid4()),
                      'label': label,
                      'lane': stream,
                      'condition': condition,
                      'samplingPercentage': sampling_percentage,
                      'samplingRecordsToRetain': sampling_records_to_retain,
                      'alertEnabled': enable_alert,
                      'alertText': alert_text,
                      'thresholdType': threshold_type.upper(),
                      'thresholdValue': threshold_value,
                      'minVolume': min_volume,
                      'sendEmail': send_email,
                      'meterEnabled': enable_meter,
                      'enabled': active}

    @property
    def active(self):
        """Returns if the rule is active or not.

        Returns:
            A :obj:`bool`.
        """
        return self._data['enabled']


class DataDriftRule:
    """Pipeline data drift rule.

    Args:
        stream (:obj:`str`): Stream to use for data rule. An entry from a Stage instance's `output_lanes` list
            is typically used here.
        label (:obj:`str`): Rule label.
        condition (:obj:`str`, optional): Data rule condition. Default: ``None``.
        sampling_percentage (:obj:`int`, optional): Default: ``5``.
        sampling_records_to_retain (:obj:`int`, optional): Default: ``10``.
        enable_meter (:obj:`bool`, optional): Default: ``True``.
        enable_alert (:obj:`bool`, optional): Default: ``True``.
        alert_text (:obj:`str`, optional): Default: ``'${alert:info()}'``.
        send_email (:obj:`bool`, optional): Default: ``False``.
        active (:obj:`bool`, optional): Enable the data rule. Default: ``False``.
    """
    def __init__(self, stream, label, condition=None, sampling_percentage=5, sampling_records_to_retain=10,
                 enable_meter=True, enable_alert=True, alert_text='${alert:info()}', send_email=False, active=False):
        # We deviate from the algorithm that ST uses (https://git.io/v97ZJ) and rather use just UUID. This is to
        # avoid generating the same time based id when the script runs too fast.
        self._data = {'id': str(uuid4()),
                      'label': label,
                      'lane': stream,
                      'condition': condition,
                      'samplingPercentage': sampling_percentage,
                      'samplingRecordsToRetain': sampling_records_to_retain,
                      'alertEnabled': enable_alert,
                      'alertText': alert_text,
                      'sendEmail': send_email,
                      'meterEnabled': enable_meter,
                      'enabled': active}

    @property
    def active(self):
        """The rule is active.

        Returns:
            A :obj:`bool`.
        """
        return self._data['enabled']


class MetricRule:
    """Pipeline Metric Rule.

    Args:
        alert_text (:obj:`str`): Alert Text to be displayed.
        metric_type (:obj:`str`, optional): Type of metric. Default: ``'COUNTER'``.
        metric_id (:obj:`str`, optional): Id of the metric. e.g. ``'stage.Trash_01.outputRecords.counter'``.
        metric_element (:obj:`str`, optional): Element of metric. e.g. ``'COUNTER_COUNT'``.
        condition (:obj:`str`, optional): Data rule condition. Default: ``'${value() > 1000}'``.
        send_email (:obj:`bool`, optional): Default: ``False``.
        active (:obj:`bool`, optional): Enable the data rule. Default: ``False``.
    """
    def __init__(self, alert_text, metric_type='COUNTER', metric_id=None, metric_element=None,
                 condition='${value() > 1000}', send_email=False, active=False):
        # We deviate from the algorithm that ST uses and rather use just UUID. This is to
        # avoid generating the same time based id when the script runs too fast.
        params = get_params(parameters=locals(), exclusions=('self', 'active'))
        self._data = params
        self._data.update({'id': str(uuid4()),
                           'enabled': active})

    @property
    def active(self):
        """The rule is active.

        Returns:
            A :obj:`bool`.
        """
        return self._data['enabled']


class Log:
    """Model for ST logs.

    Args:
        log (:obj:`list`): A list of dictionaries (JSON representation) of the log.
    """
    def __init__(self, log):
        self._data = log

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return format_log(self._data)

    # TODO the after_time and before_time to just return a different instance
    # of the class "log" and let user to call str() on it
    def after_time(self, timestamp):
        """Returns log happened after the time specified.

        Args:
            timestamp (:obj:`str`): Timestamp in the form `'2017-04-10 17:53:55,244'`.

        Returns:
            The formatted log as a :obj:`str`.
        """
        return format_log(filter(lambda x: x.get('timestamp') and x.get('timestamp') > timestamp, self._data))

    def before_time(self, timestamp):
        """Returns log happened before the time specified.

        Args:
            timestamp (:obj:`str`): Timestamp in the form `'2017-04-10 17:53:55,244'`.

        Returns:
            The formatted log as a :obj:`str`.
        """
        return format_log(filter(lambda x: x.get('timestamp') and x.get('timestamp') < timestamp, self._data))


class Batch:
    """Snapshot batch.

    Args:
        batch: Python object representation of the snapshot batch.
    """
    def __init__(self, batch):
        self._data = batch
        self.stage_outputs = {stage_output['instanceName']: StageOutput(stage_output)
                              for stage_output in self._data}

    def __getitem__(self, arg):
        return self.stage_outputs[arg]


class StageOutput:
    """Snapshot batch's stage output.

    Args:
        stage_output: Python object representation of the stage output.
    """
    def __init__(self, stage_output):
        self._data = stage_output
        self.output_lanes = {lane: [Record(record)
                                    for record in records]
                             for lane, records in self._data['output'].items()}
        self.error_records = [Record(record) for record in self._data['errorRecords']]
        if 'eventRecords' in self._data:
            self.event_records = [Record(record) for record in self._data['eventRecords']]
        self.instance_name = self._data['instanceName']

    @property
    def output(self):
        """Gets the stage output's output.

        If the stage contains multiple lanes, use :py:attr:`streamsets.sdk.st_models.StageOutput.output_lanes`.

        Raises:
            An instance of :py:class:`Exception` if the stage contains multiple lanes.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Record`.
        """
        if len(self.output_lanes) != 1:
            raise Exception('Stage has multiple output lanes, '
                            'use StageOutput.output_lanes instead.')

        return list(self.output_lanes.values())[0]

    def __repr__(self):
        # Taken wholesale from http://bit.ly/2ogOvZE.
        return "StageOutput[instance='{0}' lanes='{1}']".format(self.instance_name,
                                                                list(self.output_lanes.keys()))


class MetricGauge:
    """Metric gauge.

    Args:
        gauge (:obj:`dict`): Python object representation of a metric gauge.
    """
    def __init__(self, gauge):
        self._data = gauge

    @property
    def value(self):
        """Get the metric gauge's value.

        Returns:
            The metric gauge's value as a :obj:`str`.
        """
        return self._data["value"]


class MetricCounter:
    """Metric counter.

    Args:
        counter (:obj:`dict`): Python object representation of a metric counter.
    """
    def __init__(self, counter):
        self._data = counter

    @property
    def count(self):
        """Get the metric counter's count.

        Returns:
            The metric counter's count as an :obj:`int`.
        """
        return self._data["count"]


class MetricHistogram:
    """Metric histogram.

    Args:
        histogram (:obj:`dict`): Python object representation of a metric histogram.
    """
    def __init__(self, histogram):
        self._data = histogram


class MetricTimer:
    """Metric timer.

    Args:
        timer (:obj:`dict`): Python object representation of a metric timer.
    """
    def __init__(self, timer):
        self._data = timer

    @property
    def count(self):
        """Get the metric timer's count.

        Returns:
            The metric timer's count as an :obj:`int`.
        """
        return self._data["count"]


class MetricMeter:
    """Metric meter.

    Args:
        timer (:obj:`dict`): Python object representation of a metric meter.
    """
    def __init__(self, meter):
        self._data = meter

    def __getitem__(self, key):
        return self._data[key]


class Metrics:
    """Metrics.

    Args:
        metrics (:obj:`dict`): Python object representation of metrics.
    """
    def __init__(self, metrics):
        self._data = metrics

    def gauge(self, name):
        """Get the metric gauge from metrics.

        Args:
            name (:obj:`str`): Gauge name.

        Returns:
            The metric gauge as an instance of :py:class:`streamsets.sdk.st_models.MetricGauge`.
        """
        return MetricGauge(self._data["gauges"][name])

    def counter(self, name):
        """Get the metric counter from metrics.

        Args:
            name (:obj:`str`): Counter name.

        Returns:
            The metric counter as an instance of :py:class:`streamsets.sdk.st_models.MetricCounter`.
        """
        return MetricCounter(self._data["counters"][name])

    def histogram(self, name):
        """Get the metric histogram from metrics.

        Args:
            name (:obj:`str`): Histogram name.

        Returns:
            The metric histogram as an instance of :py:class:`streamsets.sdk.st_models.MetricHistogram`.
        """
        return MetricHistogram(self._data["histograms"][name])

    def timer(self, name):
        """Get the metric timer from metrics.

        Args:
            name (:obj:`str`): Timer namer.

        Returns:
            The metric timer as an instance of :py:class:`streamsets.sdk.st_models.MetricTimer`.
        """
        return MetricTimer(self._data["timers"][name])

    def meter(self, name):
        """Get the metric meter from metrics.

        Args:
            name (:obj:`str`): Meter name.

        Returns:
            The metric meter as an instance of :py:class:`streamsets.sdk.st_models.MetricMeter`.
        """
        return MetricMeter(self._data["meters"][name])


class HistoryEntry:
    """Pipeline history entry.

    Args:
        entry (:obj:`dict`): Python object representation of the history entry.
    """
    def __init__(self, entry):
        self._data = entry

    @property
    def metrics(self):
        """Get pipeline history entry's metrics.

        Returns:
            The pipeline history entry's metrics as an instance of :py:class:`streamsets.sdk.st_models.Metrics`.
        """
        return Metrics(json.loads(self._data["metrics"]))

    def __getitem__(self, key):
        return self._data[key]


class History:
    """Pipeline history.

    Args:
        history (:obj:`dict`): Python object representation of the pipeline history.

    Attributes:
        entries (:obj:`list`): A list of :py:class:`streamsets.sdk.st_models.HistoryEntry` instances.
    """
    def __init__(self, history):
        self._data = history
        self.entries = [HistoryEntry(entry) for entry in history]

    @property
    def latest(self):
        """Get pipeline history's latest entry.

        Returns:
            The most recent pipeline history entry as an instance of :py:class:`streamsets.sdk.st_models.HistoryEntry`.
        """
        # It seems that our history file is sorted with most recent entries at the beginning.
        return self.entries[0]

    def __len__(self):
        return len(self.entries)


class Field:
    """Field.

    Args:
        data (:obj:`dict`): Python object representation of the field.

    Attributes:
        attributes (:obj:`dict`): Python object representation of the field attributes.
        type (:obj:`str`): Field datatype.
        value: A typed representation of the field value.
    """
    def __init__(self, data):
        self._data = data
        self.type = data.get('type', None)
        self.value = data.get('value', None)
        self.raw_value = self.value
        self.attributes = data.get('attributes', None)
        if self.value and self.type:
            if self.type in ('SHORT', 'INTEGER', 'LONG'):
                self.value = int(self.value)
            elif self.type in ('DATE', 'DATETIME', 'TIME'):
                self.value = datetime.utcfromtimestamp(self.value/1000)
            elif self.type == 'BYTE':
                self.value = str(self.value).encode()
            elif self.type in ('DOUBLE', 'FLOAT'):
                self.value = float(self.value)
            elif self.type == 'BYTE_ARRAY':
                self.value = base64.b64decode(self.value)
            elif self.type == 'DECIMAL':
                self.value = Decimal(str(self.value))
            else:  # covers 'CHAR', 'STRING', 'BOOLEAN' and any other
                self.value = self.value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other

    def __getattr__(self, name):
        if name in self.__dict__['_data']:
            return self.__dict__['_data'].get(name)

        raise AttributeError('Could not find Field attribute "{}."'.format(name))


class RecordHeader:
    """Record Header.

    Args:
        header (:obj:`dict`): Python object representation of the record header.
    """
    def __init__(self, header):
        self._data = header

    def __getitem__(self, name):
        if name == 'values':
            logger.warning('This field has been superseded by RecordHeader.values and may be removed in a future'
                           ' release.')
        return self._data[name]

    @property
    def values(self):
        return self._data['values']


class Record:
    """Record.

    Args:
        record (:obj:`dict`): Python object representation of the record.

    Attributes:
        header (:obj:`dict`): An instance of :py:class:`streamsets.sdk.st_models.RecordHeader`.
        value (:obj:`dict`): Python object representation of the record value.
        value2: A typed representation of the record value.
    """
    def __init__(self, record):
        self._data = record
        self.header = RecordHeader(self._data.get('header'))
        self.field = self._field_reader(self._data.get('value'))

    @property
    def value(self):
        logger.warning('This attribute has been superseded by Record.field and may be removed in a future release.')
        return self._data.get('value')

    def _field_reader(self, value):
        """Parse ST Record value (Record JSON in dict format for example) and convert to ST implied Fields.

        Args:
            value: ST Record value.

        Returns:
            Field based value.
        """
        # Note: check instance of OrderedDict before dict to avoid superfluous
        # check of OrderedDict getting evaluated for dict
        if isinstance(value, collections.OrderedDict):
            return collections.OrderedDict([(value['dqpath'].split('/')[-1], self._field_reader(value))
                                            for key, value in value.items()])
        elif isinstance(value, dict):
            if 'type' in value and 'value' in value:
                if value['value'] is None:
                    return Field(value)
                elif value['type'] == 'LIST_MAP':
                    return self._field_reader(collections.OrderedDict([(key, value['value'][key])
                                                                       for key in range(len(value['value']))]))
                elif value['type'] in ('LIST', 'MAP'):
                    return self._field_reader(value['value'])
                else:
                    return Field(value)
            else:
                return {key: self._field_reader(value) for key, value in value.items()}
        elif isinstance(value, list):
            return [self._field_reader(item) for item in value]
        else:
            return Field(value)

    def get_field_data(self, path):
        """Given a field path string (similar to XPath), get :py:class:`streamsets.sdk.st_models.Field`.
        Example:
            get_field_data(path='[2]/east/HR/employeeName').

        Args:
            path (:obj:`str`): field path string.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Field`.
        """
        return dpath.util.get(self.field, get_dpath_compatible_field_path(path))

    def get_field_attributes(self, path):
        """Given a field path string (similar to XPath), get :py:class:`streamsets.sdk.st_models.Field` attributes.
        Example:
            get_field_attributes(path='[2]/east/HR/employeeName').

        Args:
            path (:obj:`str`): field path string.

        Returns:
            :py:class:`streamsets.sdk.st_models.Field` attributes.
        """
        return dpath.util.get(self.field, get_dpath_compatible_field_path(path)).attributes

    def __repr__(self):
        repr_metadata = ['field']
        return '<{} ({})>'.format(self.__class__.__name__,
                                  ', '.join('{}={}'.format(key, getattr(self, key)) for key in repr_metadata))


class User:
    """User.

    Args:
        user (:obj:`dict`): Python object representation of the user.
    """
    def __init__(self, user):
        self._data = user

    @property
    def name(self):
        """Get user's name.

        Returns:
            User name as a :obj:`str`.
        """
        return self._data['user']

    @property
    def roles(self):
        """Get user's roles.

        Returns:
            User roles as a :obj:`str`.
        """
        return self._data["roles"]

    @property
    def groups(self):
        """Get user's groups.

        Returns:
            User groups as a :obj:`str`.
        """
        return self._data["groups"]


class Preview:
    """Preview.

    Args:
        pipeline_id (:obj:`str`): Pipeline ID.
        previewer_id (:obj:`str`): Previewer ID.
        preview (:obj:`dict`): Python object representation of the preview.

    Attributes:
        issues (:obj:`dict`): An instance of :py:class:`streamsets.sdk.st_models.Issues`.
        preview_batches (:obj:`list`): A list of :py:class:`streamsets.sdk.st_models.Batch` instances.
    """
    def __init__(self, pipeline_id, previewer_id, preview):
        self.pipeline_id = pipeline_id
        self.previewer_id = previewer_id
        self._data = preview
        self.issues = Issues(self._data.get('issues') or {})
        self.preview_batches = [Batch(preview_batch)
                                for preview_batch in self._data['batchesOutput']]

    def __getitem__(self, key):
        return self.preview_batches[0][key]

    def __iter__(self):
        for preview_batch in self.preview_batches:
            yield preview_batch

    def __len__(self):
        return len(self.preview_batches)


class Issues:
    """Issues encountered for pipelines as well as stages.

    Args:
        issues (:obj:`dict`): Python object representation of the issues.

    Attributes:
        issues_count (:obj:`int`): The number of issues.
        pipeline_issues (:obj:`list`): A list of :py:class:`streamsets.sdk.st_models.Issue` instances.
        stage_issues (:obj:`dict`): A dictionary mapping stage names to instances of
            :py:class:`streamsets.sdk.st_models.Issue`.
    """
    def __init__(self, issues):
        self._data = issues
        self.issues_count = self._data.get('issueCount')
        self.pipeline_issues = [Issue(pipeline_issue)
                                for pipeline_issue in self._data.get('pipelineIssues', [])]
        self.stage_issues = {stage_name: [Issue(stage_issue)
                                          for stage_issue in stage_issues]
                             for stage_name, stage_issues in
                             self._data.get('stageIssues', {}).items()}


class Issue:
    """Issue encountered for a pipeline or a stage.

    Args:
        issue (:obj:`dict`): Python object representation of the issue.
    """
    def __init__(self, issue):
        self._data = issue
        self.count = self._data['count']
        self.level = self._data['level']
        self.instance_name = self._data['instanceName']
        self.config_group = self._data['configGroup']
        self.config_name = self._data['configName']
        self.additional_info = self._data['additionalInfo']
        self.message = self._data['message']


class Alert:
    """Pipeline alert.

    Args:
        alert (:obj:`dict`): Python object representation of a pipeline alert.
    """
    def __init__(self, alert):
        self._data = alert

    @property
    def pipeline_id(self):
        """Get alert's pipeline ID.

        Returns:
            The pipeline ID as a :obj:`str`.
        """
        return self._data['pipelineName']

    @property
    def alert_texts(self):
        """Get alert's alert texts.

        Returns:
            The alert's alert texts as a :obj:`str`.
        """
        return self._data['gauge']['value']['alertTexts']

    @property
    def label(self):
        """Get alert's label.

        Returns:
            The alert's label as a :obj:`str`.
        """
        return self._data['ruleDefinition']['label']


class Alerts:
    """Container for list of alerts with filtering capabilities.

    Args:
        alerts (:obj:`dict`): Python object representation of alerts.

    Attributes:
        alerts (:obj:`list`): A list of :py:class:`streamsets.sdk.st_models.Alert` instances.
    """
    def __init__(self, alerts):
        self._data = alerts
        self.alerts = [Alert(i) for i in self._data]

    def for_pipeline(self, pipeline):
        """Get alerts for the specified pipeline.

        Args:
            pipeline (:obj:`str`): The pipeline for which to get alerts.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Alerts`.
        """
        return Alerts([a for a in self.alerts if a.pipeline_id == pipeline.id])

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)


class BundleGenerator:
    """Bundle generator.

    Args:
        data (:obj:`dict`): Python object representation of the bundle generator.
    """
    def __init__(self, data):
        self._data = data


class BundleGenerators:
    """Container for list of bundle generators with searching capabilities.

    Args:
        data (:obj:`dict`): Python object representation of the bundle generators.

    Attributes:
        generators (:obj:`dict`): A dictionary mapping bundle generator IDs to instances of
            :py:class:`streamsets.sdk.st_models.BundleGenerator`.
    """
    def __init__(self, data):
        self._data = data
        self.generators = {i['id']: BundleGenerator(i) for i in self._data}

    def __len__(self):
        return len(self._data)

    def __getitem__(self, name):
        return self.generators.get(name)


class PipelineAcl:
    """Represents a pipeline ACL.

    Args:
        pipeline_acl (:obj:`dict`): JSON representation of a pipeline ACL.

    Attributes:
        permissions (:py:class:`streamsets.sdk.st_models.PipelinePermissions`): Pipeline Permissions object.
    """
    def __init__(self, pipeline_acl):
        self._data = pipeline_acl
        self.permissions = PipelinePermissions(self._data['permissions'])

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)


class PipelinePermission:
    """A container for a pipeline permission.

    Args:
        pipeline_permission (:obj:`dict`): A Python object representation of a pipeline permission.
    """
    def __init__(self, pipeline_permission):
        self._data = pipeline_permission

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


class PipelinePermissions:
    """Container for list of permissions for a pipeline.

    Args:
        pipeline_permissions (:obj:`dict`): A Python object representation of pipeline permissions.

    Attributes:
        permissions (:obj:`list`): A list of :py:class:`streamsets.sdk.st_models.PipelinePermission` instances.
    """
    def __init__(self, pipeline_permissions):
        self._data = pipeline_permissions
        self.permissions = [PipelinePermission(i) for i in self._data]

    def __getitem__(self, key):
        return self.permissions[key]

    def __iter__(self):
        for permission in self.permissions:
            yield permission

    def __len__(self):
        return len(self.permissions)


# We define module-level attributes to allow users to extend certain
# ST classes and have them used by other classes without the need to override
# their methods (e.g. allow the Pipeline class to be extended and be built using a
# non-extended PipelineBuilder class).
_Pipeline = Pipeline
_Stage = Stage
