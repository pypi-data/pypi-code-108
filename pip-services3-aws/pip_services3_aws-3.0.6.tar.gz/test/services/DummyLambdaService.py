# -*- coding: utf-8 -*-
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import DataPage, FilterParams, PagingParams
from pip_services3_commons.refer import Descriptor, IReferences
from pip_services3_commons.validate import FilterParamsSchema, PagingParamsSchema, ObjectSchema

from pip_services3_aws.services.LambdaService import LambdaService
from test.Dummy import Dummy
from test.DummySchema import DummySchema
from test.IDummyController import IDummyController


class DummyLambdaService(LambdaService):
    _controller: IDummyController = None

    def __init__(self):
        super(DummyLambdaService, self).__init__('dummies')
        self._dependency_resolver.put('controller',
                                      Descriptor('pip-services-dummies', 'controller', 'default', '*', '*'))

    def set_references(self, references: IReferences):
        super().set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def __get_page_by_filter(self, params: dict) -> DataPage:
        return self._controller.get_page_by_filter(
            params.get('correlation_id'),
            FilterParams(params['filter']),
            PagingParams(params['paging'])
        )

    def __get_one_by_id(self, params: dict) -> Dummy:
        return self._controller.get_one_by_id(
            params.get('correlation_id'),
            params.get('dummy_id')
        )

    def __create(self, params: dict) -> Dummy:
        return self._controller.create(
            params.get('correlation_id'),
            params['dummy']
        )

    def __update(self, params: dict):
        return self._controller.update(
            params.get('correlation_id'),
            params['dummy']
        )

    def __delete_by_id(self, params: dict):
        return self._controller.delete_by_id(
            params.get('correlation_id'),
            params['dummy_id']
        )

    def register(self):
        self._register_action(
            'get_dummies',
            ObjectSchema(True).with_optional_property("filter", FilterParamsSchema())
                .with_optional_property("paging", PagingParamsSchema()),
            self.__get_page_by_filter
        )

        self._register_action(
            'get_dummy_by_id',
            ObjectSchema(True)
                .with_optional_property("dummy_id", TypeCode.String),
            self.__get_one_by_id
        )

        self._register_action(
            'create_dummy',
            ObjectSchema(True)
                .with_required_property("dummy", DummySchema()),
            self.__create
        )

        self._register_action(
            'update_dummy',
            ObjectSchema(True)
                .with_required_property("dummy", DummySchema()),
            self.__update
        )

        self._register_action(
            'delete_dummy',
            ObjectSchema(True)
                .with_optional_property("dummy_id", TypeCode.String),
            self.__delete_by_id
        )
