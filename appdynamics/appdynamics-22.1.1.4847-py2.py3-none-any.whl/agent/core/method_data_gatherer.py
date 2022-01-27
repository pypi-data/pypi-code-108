import re
import functools

from appdynamics.lib import execute_getter_chain
from collections import namedtuple

from appdynamics.agent.core import pb

_DataSources = namedtuple('DateSources',
                          ('invoked_object', 'method_parameter', 'return_value'))


class MethodDataGatherer(object):

    def __init__(self, method_data_gatherer_config, gatherer_id):
        self.id = gatherer_id
        self.module = None
        self.cls = None
        self.method = None
        self.match_conditions = _DataSources([], [], [])
        self.data_to_collect = _DataSources([], [], [])
        self.enabled_for_snapshots = False
        self.enabled_for_analytics = False
        self._parse_config_data(method_data_gatherer_config)

    def _parse_config_data(self, config_data):
        """Parse the protobuf object to the desired format
        """
        self.module, self.cls = (config_data.probe.phpDefinition
                                 .classMatch.classNameCondition.matchStrings[0].rsplit('.', 1))
        self.method = config_data.probe.phpDefinition.methodMatch.methodNameCondition.matchStrings[0]
        self._parse_match_conditions(config_data)
        self._parse_data_collector_pb(config_data)
        self.enabled_for_analytics = config_data.enabledForAnalytics
        self.enabled_for_snapshots = config_data.enabledForApm

    def _parse_match_conditions(self, config_data):
        """Parses match conditions from protobuf object into self.match_conditions

        self.match_conditions.return_value will contain conditions on return value
        self.match_conditions.method_parameter will contain conditions on method parameter
        self.match_conditions.invoked_object will contain conditions on invoked object
        """
        if config_data.probe.phpDefinition.methodMatch.HasField('matchCondition'):
            for operand in config_data.probe.phpDefinition.methodMatch.matchCondition.andOp.operands:
                op_condition = operand.stringMatchOp.condition
                iterator = operand.stringMatchOp.input
                # Extract getter chain from the protobuf
                # Getter chain -> getInfo().name.do[0]
                getter_chain = ''
                while iterator.type == pb.ExpressionNode.GETTER:
                    getter_chain = '.' + iterator.getterOp.field + getter_chain
                    iterator = iterator.getterOp.base

                # Creating a partial as *args and **kwargs for computing the entity will be passed later
                match_method = functools.partial(self._check_entity_satisfies_match_condition, getter_chain,
                                                 iterator.entityValue, op_condition)
                if iterator.entityValue.type == pb.EntityCollector.RETURN_VALUE:
                    self.match_conditions.return_value.append(match_method)
                elif iterator.entityValue.type == pb.EntityCollector.PARAMETER:
                    self.match_conditions.method_parameter.append(match_method)
                elif iterator.entityValue.type == pb.EntityCollector.INVOKED_OBJECT:
                    self.match_conditions.invoked_object.append(match_method)

    def _parse_data_collector_pb(self, config_data):
        """Parses data to collect from protobuf object into self.data_to_collect

        self.data_to_collect.return_value will contain methods which collect data from return value
        self.data_to_collect.method_parameter will contain methods which collect data from method_parameter
        self.data_to_collect.invoked_object will contain methods which collect data from invoked object
        """
        for data_to_collect in config_data.methodDataToCollect:
            # Extract getter chain from the protobuf
            # Getter chain -> "getInfo().name.do[0]"
            iterator = data_to_collect.data
            getter_chain = ''
            while iterator.type == pb.ExpressionNode.GETTER:
                getter_chain = '.' + iterator.getterOp.field + getter_chain
                iterator = iterator.getterOp.base

            # Creating a partial as *args and **kwargs for computing the entity will be passed later
            getter_method = functools.partial(self._get_entity, getter_chain, iterator.entityValue)
            if iterator.entityValue.type == pb.EntityCollector.RETURN_VALUE:
                self.data_to_collect.return_value.append({'name': data_to_collect.name, 'getter': getter_method})
            elif iterator.entityValue.type == pb.EntityCollector.PARAMETER:
                self.data_to_collect.method_parameter.append({'name': data_to_collect.name, 'getter': getter_method})
            elif iterator.entityValue.type == pb.EntityCollector.INVOKED_OBJECT:
                self.data_to_collect.invoked_object.append({'name': data_to_collect.name, 'getter': getter_method})

    def _get_entity(self, getter_chain, entity_value, *args, **kwargs):
        """Internal method which will return the value after executing getter_chain on the required
        entity (return_value, method parameter or invoked object)

        - To be used as a partial inside _parse_data_collector_pb, where the entity to compute upon will be
          passed later inside the method wrapper
        """
        entity = None  # The value on which the computation will happen
        if entity_value.type == pb.EntityCollector.PARAMETER:
            entity = args[entity_value.parameterIndex]
        if (entity_value.type == pb.EntityCollector.RETURN_VALUE
                or entity_value.type == pb.EntityCollector.INVOKED_OBJECT):
            # handler will be called like handle(invoked_object), so invoked_object = args[0]
            entity = args[0]
        try:
            return str(execute_getter_chain(entity, getter_chain))
        except:
            return ''

    def _check_entity_satisfies_match_condition(self, getter_chain, entity_value, condition, *args, **kwargs):
        """Internal method which checks whether the entity satisfies the match condition or not

        - To be used as a partial, where the entity to compute upon will be passed later
          inside the method wrapper
        """
        entity = self._get_entity(getter_chain, entity_value, *args, **kwargs)
        return self._check_entity_against_condition(entity, condition)

    @staticmethod
    def _check_entity_against_condition(entity, condition):
        """Internal method which checks if a value satisfies the passed condition
        """
        # if condition.isNot is True, `condition.isNot XOR rhs` returns the opposite of the rhs
        # if condition.isNot is False, `condition.isNot XOR rhs` returns the rhs
        if condition.type == pb.StringMatchCondition.EQUALS:
            return condition.isNot ^ (entity == condition.matchStrings[0])
        if condition.type == pb.StringMatchCondition.STARTS_WITH:
            return condition.isNot ^ entity.startswith(condition.matchStrings[0])
        if condition.type == pb.StringMatchCondition.ENDS_WITH:
            return condition.isNot ^ entity.endswith(condition.matchStrings[0])
        if condition.type == pb.StringMatchCondition.CONTAINS:
            return condition.isNot ^ (condition.matchStrings[0] in entity)
        if condition.type == pb.StringMatchCondition.MATCHES_REGEX:
            return condition.isNot ^ bool(re.compile(condition.matchStrings[0]).search(entity))
        if condition.type == pb.StringMatchCondition.IS_IN_LIST:
            return condition.isNot ^ (entity in condition.matchStrings[0].split(','))
        if condition.type == pb.StringMatchCondition.IS_NOT_EMPTY:
            return condition.isNot ^ (not not entity)
