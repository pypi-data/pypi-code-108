"""
Document Extend
"""
import typing
import warnings

from elasticsearch_dsl import Document, Index, Q, Search, connections, field
from pydantic import BaseModel
from wisdoms_dapr import exceptions, types

import elasticsearch


class ExtendDocument(Document):
    """Extend ElasticSearch Document"""

    class Extend:
        """扩展参数配置
        Parameters:
            unique/unique_together 仅对关键字类型（Keyword)起作用，如果非关键字类型则直接跳过

            unique: str/list/tuple 唯一字段
            unique_together: iter   要求一起唯一
            auto_now_fields: 当对象使用save时自动更新为当前时间
            auto_now_add_fields: 当对象首次创建时更新为当前时间
        """
        unique = ''
        unique_together = []
        # auto_now_fields = []
        # auto_now_add_fields = []

    def _get_extend_settings(self):
        """获取extend参数"""
        return {
            key: getattr(self.Extend, key)
            for key in dir(self.Extend)
            if not key.startswith('__') and not callable(getattr(self.Extend, key)) and getattr(self.Extend, key)
        }

    @classmethod
    def get_document_index(cls):
        """获取文档索引"""
        return cls._index

    @classmethod
    def get_document_mapping_dict(cls, attrs_list=None):
        """获取文档Mapping

        Args:
            attrs_list: 属性列表 None/list
        """
        index = cls.get_document_index()
        index_name = index._name

        # 获取doc type
        if hasattr(index, '_get_doc_type'):
            index_type = index._get_doc_type()
        else:
            index_type = None
        index_mappings = index.get_mapping()

        # print('Index attrs:', index_type, index_mappings)

        # 获取mapping
        if index_type:
            _mappings = index_mappings[index_name]['mappings'][index_type]['properties']
        else:
            _mappings = index_mappings[index_name]['mappings']['properties']

        if not attrs_list:
            return _mappings
        else:
            return {attr: _mappings[attr] for attr in attrs_list if attr in _mappings}

    @classmethod
    def get_type_attrs(cls, attr_type, attrs_list=None, recurse=True):
        """获取指定类型属性名列表

        Args:
            attr_type: elasticsearch 属性类型（小写）
            attrs_list: 属性列表，当为None时从全部属性获取，为列表时获取列表的属性
            recurse: 是否递归进行查找

        Returns:
            满足type类型的属性名列表，如果是`multi-fields`类型将会返回`attr.field_name`形式

        Warnings:
            如果没有功能问题，请不要试着修改此函数，程序可能比较难理解，使用递归实现
        """
        attr_dict = cls.get_document_mapping_dict()

        def _get_type_attrs(attr_obj, _attr_type, _attrs_list, _recurse):
            """
            获取指定`type`类型的属性，包括`multi-fields`属性
            Args:
                attr_obj:
                _attr_type:
                _attrs_list:
                _recurse:
                以上参数是此类方法的参数值，为了将函数变量包含在局部环境内

            Returns:
                满足type类型的属性名列表，如果是`multi-fields`类型将会返回`attr.field_name`形式
            """
            attr_names_list = []
            attr_name = []

            def _get_type_attr_from_dict(_attr_dict, attr_name):
                for attr, value in _attr_dict.items():
                    if ((_attrs_list and attr in _attrs_list) or attr_name) or _attrs_list is None:
                        if value['type'] == _attr_type:
                            # print('type == attr_type')
                            attr_name.append(attr)
                        else:
                            if _recurse and 'fields' in value:
                                # print('call type attr from dict > 1 times.')
                                attr_name_sub = attr_name.copy()
                                attr_name_sub.append(attr)
                                _get_type_attr_from_dict(value['fields'], attr_name_sub)

                            continue
                        # print('attr_names_list append string list:', attr_name)
                        attr_names_list.append('.'.join(attr_name))
                        attr_name.clear() # 清空列表

            _get_type_attr_from_dict(attr_obj, attr_name=attr_name)
            return attr_names_list

        return _get_type_attrs(attr_dict, attr_type, attrs_list, recurse)

    def _get_unique_keyword_list(self, unique_attrs):
        """检查关键字属性，返回过滤后的列表

        """
        if unique_attrs:
            return self.get_type_attrs('keyword', unique_attrs)
        else:
            return None

    @staticmethod
    def get_total_value(res):
        """获取total value --- 为了同时兼容es6和es7

        :param res: es search response
        """

        total = res.hits.total
        if hasattr(total, 'value'):
            return total.value
        else:
            return total

    def _check_term_unique(self, term, term_value):
        """检查term查询是否存在，返回True/False"""
        search_result = self.search().query('term', **{term: term_value}).execute()

        result_total = self.get_total_value(search_result)
        if result_total > 0:
            if getattr(self, 'meta', None) and getattr(self.meta, 'id', None):
                # 判断当前id是否存在于查询结果中，存在这跳过
                # print(search_result.hits.hits)
                for hit in search_result.hits.hits:
                    if hit['_id'] == self.meta.id:
                        if result_total > 1:
                            warnings.warn(f'unique field {term} exists {result_total} repeat record.')
                        return True

            return False
        else:
            return True

    def _check_terms_unique_together(self, terms):
        """检查多个terms查询是否唯一存在"""
        if terms:
            query_list = []
            for term in terms:
                query_list.append(Q('term', **{term: getattr(self, term.split('.')[0])}))
            q = Q('bool', must=query_list)

            res = self.search().query(q).execute()
            total = self.get_total_value(res)
            if total > 0:
                return False
            else:
                return True
        return None

    def unique_together_check(self):
        """"""
        pass

    def _check(self, args, kwargs, *, is_update=False):
        """检查限制条件"""

        extend_settings = self._get_extend_settings()
        # print(extend_settings)

        if 'unique' in extend_settings:
            # 获取unique属性列表
            unique_attrs = (
                extend_settings['unique'] if isinstance(extend_settings['unique'], list)
                or isinstance(extend_settings['unique'], tuple) else [extend_settings['unique']]
            )

            # 判断对象是否为关键字类型属性
            unique_attrs = self._get_unique_keyword_list(unique_attrs)

            # 依次判断属性是否存在和结果是否已经存在
            if unique_attrs:
                for attr in unique_attrs:
                    term_name = attr.split('.')[0]
                    if attr in self or term_name in self:
                        term_value = kwargs.get(term_name) if is_update else getattr(self, term_name, None)
                        if is_update and term_value == getattr(self, term_name, None):
                            pass
                        else:
                            if not self._check_term_unique(term=attr, term_value=term_value):
                                # 引发异常跳过后面检查
                                raise exceptions.UniqueException('记录创建冲突'.format(attr))

        if 'unique_together' in extend_settings:
            # 判断多个字段的唯一性
            unique_attrs = extend_settings['unique_together']

            # 判断属性是否都存在，如果都存在才有效，否则直接引发异常
            for attr in unique_attrs:
                if attr not in self:
                    raise exceptions.UniqueTogetherException('唯一条件内容缺失，无效的创建请求！')

            new_unique_attrs = self._get_unique_keyword_list(unique_attrs)
            if new_unique_attrs and len(new_unique_attrs) == len(unique_attrs):
                if not self._check_terms_unique_together(new_unique_attrs):
                    raise exceptions.UniqueTogetherException('类似文档已存在，无法创建新的文档')
            else:
                raise ValueError('`unique_together`可迭代参数列表必须都为`Keyword`或`Keyword`型Text类型字段名或不能为空')

        # if 'auto_now_add_fields' in extend_settings and not is_update:
        #     self._auto_now_add_fields_action(extend_settings['auto_now_add_fields'], kwargs, is_update=is_update)
        #
        # # 从kwargs中移除auto now add fields
        # if is_update:
        #     self._remove_auto_time_fields(extend_settings['auto_now_add_fields'], kwargs, is_update)
        #
        # if 'auto_now_fields' in extend_settings:
        #     self._auto_now_fields_action(extend_settings['auto_now_fields'], kwargs, is_update=is_update)

    def save(self, *args, is_check=True, **kwargs):
        """保存时根据不同扩展参数进行判断

        Args:
            is_check: bool 保存时是否进行条件检查
        """
        # print('# document save:', self, dir(self), args, is_check, kwargs)
        if is_check:
            self._check(args, kwargs)

        return super().save(*args, **kwargs)

    def update(self, *args, is_check=True, **kwargs):
        """document update"""
        # print('# document update:', self, dir(self), is_check, kwargs)
        if is_check:
            self._check(args, kwargs, is_update=True)

        # print(self, self.updated_time, kwargs, args)
        return super().update(*args, **kwargs)

    @classmethod
    def _check_fields_type(cls, fields, field_type, *, raise_exception=True):
        """检查fields是否为列表且存在于document mapping之中"""
        if not any(map(lambda x: isinstance(fields, x), [list, tuple, set])):
            return False

        mapping = cls.get_document_mapping_dict()

        not_exist_fields = []
        type_error_fields = []
        for field in fields:
            if field not in mapping:
                not_exist_fields.append(field)
            else:
                if mapping[field]['type'] != field_type:
                    type_error_fields.append(field)

        if len(not_exist_fields) == 0 and len(type_error_fields) == 0:
            return True
        else:
            if raise_exception:
                raise exceptions.ServiceErrorException(
                    f"{','.join(not_exist_fields)} total {len(not_exist_fields)} not exist in mapping, "
                    f"{','.join(type_error_fields)} total {len(type_error_fields)} not match field type `{field_type}`."
                )
            else:
                return False

    def get_document_dict(self):
        """在用户保存后，获取用户属性字典

        Warnings:
            此方法不适合在document保存后调用，因为此时文档可能出现无法搜索的问题
        """
        # 判断用户是否已经保存
        if 'id' in self.meta:
            # print(self.__class__.get_document_by_id(self.meta.id))
            return self.__class__.term_query_search_by_id(self.meta.id)
        else:
            # 提示当前文档还未保存
            raise exceptions.ServiceErrorException("Current document object doesn't save, can't get document id.")

    @classmethod
    def get_document_by_id(cls, document_id, *, raise_exception=False):
        """通过文档ID获取文档

        Args:
            document_id: 文档ID
            raise_exception: 是否触发异常
        """
        try:
            doc = cls.get(id=document_id)
        except elasticsearch.exceptions.NotFoundError:
            if raise_exception:
                raise exceptions.ObjectDoesNotExist
            else:
                return None
        else:
            return doc

    @classmethod
    def update_document(cls, id, data, *, exclude_id: bool = True) -> 'ExtendDocument':
        if exclude_id:
            data.pop('id', None)

        doc = cls.get_document_by_id(document_id=id, raise_exception=True)
        doc.update(**data)
        return doc

    @staticmethod
    def _search_item_to_dict(search_item):
        """将搜索项转换为字典"""
        item_content = search_item['_source']
        print(item_content)
        if 'id' not in item_content:
            # raise ServiceErrorException('无法正确插入id')
            item_content['id'] = search_item['_id']
        return item_content

    @staticmethod
    def get_dict_list_from_search_result(search_result):
        """从搜索结果获取字典"""
        result = search_result.hits.hits
        if len(result) > 0:
            return [ExtendDocument._search_item_to_dict(item) for item in result]
        else:
            return []

    @classmethod
    def term_query_search(cls, query_terms, *, to_dict=False):
        """通过查询字典进行查询"""
        query = Q()
        for term in query_terms:
            query &= Q('term', **{term: query_terms[term]})

        print(query.to_dict())
        search = Search(index=cls.Index.name).query(query)
        result = search.execute()

        if to_dict:
            return cls.get_dict_list_from_search_result(result)
        else:
            return result.hits.hits

    @classmethod
    def term_query_search_by_id(cls, id, *, to_dict=True):
        result = cls.term_query_search({'_id': id}, to_dict=to_dict)
        if result:
            return result[0]
        else:
            return None

    @classmethod
    def get_document_by_term_search(cls, query_term, raise_exception=False):
        documents = cls.term_query_search(query_terms=query_term, to_dict=True)
        if not len(documents):
            if raise_exception:
                raise exceptions.ObjectDoesNotExist
            else:
                return None
        elif len(documents) > 1:
            raise exceptions.MultiObjectReturnException
        else:
            return cls.get_document_by_id(documents[0]['id'])

    @classmethod
    def get_document_by_query(cls, query: Q, raise_exception: bool = False):
        """通过查询获取文档"""

        search = cls.search().query(query)[:2]
        result = None
        for index, doc in enumerate(search):
            if index == 0:
                result = doc
            else:
                if raise_exception:
                    raise exceptions.DBException(msg='get multi documents by query')
                else:
                    return None

        if not result and raise_exception:
            raise exceptions.DBException(msg='not found query document')

        return result

    @classmethod
    def flush_index(cls):
        """刷新索引数据"""

        cls._index.flush()

    @classmethod
    def create_or_update_document(cls, data: dict) -> typing.Tuple['ExtendDocument', bool]:
        """创建或者更新文档
        
        当id存在时，通过id查找并更新对应的文档
        当id不存在时，创建文档

        :return {
            data: return data dict,
            created: bool, if created return True else return False
        }
        """

        created = False
        if 'id' in data and data['id']:
            # 更新文档
            doc = cls.get_document_by_id(document_id=data['id'], raise_exception=True)
            data.pop('id')
            res = doc.update(**data, is_check=True)
        else:
            # 创建文档
            doc = cls(**data)
            res = doc.save(is_check=True)
            created = True

        return res, created

    @classmethod
    def delete_documents(cls, ids: typing.Union[typing.List[str], str]):
        """删除文档"""

        if ids and not isinstance(ids, list):
            ids = [ids]

        query = Q('ids', **{'values': ids})
        search = Search(index=cls.Index.name).query(query)
        res = search.delete()
        return res

    def to_schema_dict(self, schema: typing.Optional[typing.Type[BaseModel]] = None, **schema_kwargs) -> dict:
        """Convert to schema dict"""

        data = self.to_id_dict()

        if not schema:
            return data

        return schema(**data).dict(**schema_kwargs)

    def to_id_dict(self) -> dict:
        """Convert to dict include id in dict"""

        data = self.to_dict()
        try:
            doc_id = self.meta.id
        except AttributeError:
            return data
        else:
            data['id'] = doc_id

        return data


def init_document_index(document_cls, connection=None, *, delete_on_conflict=False):
    """初始化文档索引

    判断当前库是否存在同名的Index，不存在则进行初始化

    Args:
        document_cls: 文档类
        connection: es连接
        delete_on_conflict: 是否当冲突时删除重建
    """

    if connection:
        c = connection
    else:
        try:
            c = connections.get_connection()
            print(c)
        except KeyError as e:
            raise exceptions.ServiceErrorException("No find a valid connection.")

    indexes_dict = c.indices.get_alias()
    index_names = tuple(indexes_dict.keys())
    index_alias_names = []
    for index in indexes_dict:
        index_alias_names.extend(list(indexes_dict[index]['aliases'].keys()))
    index_alias_names = tuple(index_alias_names)

    # print(index_names, index_alias_names)

    # 获取文档类的索引名称
    try:
        document_index_name = document_cls.Index.name
    except AttributeError:
        raise AttributeError("Document `{}` doesn't have `Index.name` attribute".format(document_cls))
    else:
        # 判断索引是否已存在
        if document_index_name in index_names or document_index_name in index_alias_names:
            # print('document `{}` index exist.'.format(document_index_name))
            if delete_on_conflict:
                Index(name=document_index_name, using=c).delete()
                # print('[Conflict Delete]: document `{}` index deleted.'.format(document_index_name))
            else:
                return

        document_cls.init()
        # print('document `{}` index created.'.format(document_index_name)


# Elasticsearch and Meta Fields Mapping
META_FIELD_ELASTICSEARCH_MAPPING = {
    types.AllMetaFieldTypes.BOOL.value: field.Boolean,
    types.AllMetaFieldTypes.STRING.value: field.Keyword,
    types.AllMetaFieldTypes.TEXT.value: field.Text,
    types.AllMetaFieldTypes.BINARY.value: field.Binary,
    types.AllMetaFieldTypes.INT.value: field.Integer,
    types.AllMetaFieldTypes.FLOAT.value: field.Float,
    types.AllMetaFieldTypes.OBJECT.value: field.Object,
    types.AllMetaFieldTypes.NESTED.value: field.Nested,
    types.AllMetaFieldTypes.DATE.value: field.Date,
    types.AllMetaFieldTypes.IP.value: field.Ip,
    types.AllMetaFieldTypes.GEO_POINT.value: field.GeoPoint,
}
META_FIELD_ELASTICSEARCH_TYPE_MAPPING = {k: v.name for k, v in META_FIELD_ELASTICSEARCH_MAPPING.items()}
ELASTICSEARCH_META_FIELD_TYPE_MAPPING = dict(
    zip(META_FIELD_ELASTICSEARCH_TYPE_MAPPING.values(), META_FIELD_ELASTICSEARCH_TYPE_MAPPING.keys())
)
# 内置全局变量
MODEL_CREATED_TIME_FIELD_NAME = 'created_time'
MODEL_MODIFIED_TIME_FIELD_NAME = 'modified_time'


class SchemaDocument(Document):
    """Schema Document"""

    class Schema:
        """
        Schema Info

        :attr meta: schema Meta
        :attr fields: fields settings
        """

        pass

    @classmethod
    def get_all_model_fields(cls, *, include_type_obj: bool = False, include_schema: bool = False) -> dict:
        """获取mapping下面的fields

        :param include_type_obj: 是否包含字段类型
        :param include_schema: 是否包含schema字段信息
        """

        def _get_all_model_fields(doc_class, include_type_obj: bool = False, include_schema: bool = False):

            result = {}
            properties = doc_class._doc_type.mapping.properties._params.get('properties')
            if not properties:
                return result

            schema = None
            if include_schema:
                schema = getattr(doc_class, 'Schema', None)

            for k, v in properties.items():
                result[k] = {'type': v.name}

                if include_type_obj:
                    result[k]['type_obj'] = v

                # 获取schema field
                if schema:
                    result[k]['schema'] = getattr(schema, 'fields', {}).get(k)

                if v.name in [field.Object.name, field.Nested.name]:
                    result[k]['fields'] = _get_all_model_fields(
                        v._doc_class, include_type_obj=include_type_obj, include_schema=include_schema
                    )

            return result

        # 添加创建时间字段
        result = _get_all_model_fields(doc_class=cls, include_type_obj=include_type_obj, include_schema=include_schema)
        if MODEL_CREATED_TIME_FIELD_NAME not in result:
            result[MODEL_CREATED_TIME_FIELD_NAME] = {
                'type': field.Date.name,
                'type_obj': field.Date(),
                'schema': {
                    'dump_only': True
                }
            }
        else:
            if result[MODEL_CREATED_TIME_FIELD_NAME]['type'] != field.Date.name:
                raise TypeError(f"model `{MODEL_CREATED_TIME_FIELD_NAME}` field must be date type.")

        # 添加编辑时间字段
        if MODEL_MODIFIED_TIME_FIELD_NAME not in result:
            result[MODEL_MODIFIED_TIME_FIELD_NAME] = {
                'type': field.Date.name,
                'type_obj': field.Date(),
                'schema': {
                    'dump_only': True
                }
            }
        else:
            if result[MODEL_MODIFIED_TIME_FIELD_NAME]['type'] != field.Date.name:
                raise TypeError(f"model `{MODEL_MODIFIED_TIME_FIELD_NAME}` field must be date type.")

        return result

    @classmethod
    def get_model_metadata(cls) -> dict:
        """导出模型元数据

        数据结构同meta model和meta field model
        """

        def _get_fields_metadata(fields: dict, result_list: list, prefix: str = None):
            """
            获取字段元数据

            :param fields: 所有模型的字段
            :param result_list: 提取后的结构列表
            :param prefix: 字段前缀
            :return:
            """

            for field_name, item in fields.items():
                if not item.get('type'):
                    continue

                meta_field_name = field_name if not prefix else str(prefix) + '.' + field_name
                field_type = ELASTICSEARCH_META_FIELD_TYPE_MAPPING.get(item['type'])
                if not field_type:
                    raise exceptions.ServiceException(msg=f"elasticsearch {item['type']} not meta field mapping")

                meta = {
                    'model_name': cls.Index.name,
                    'name': meta_field_name,
                    'alias': "",
                    'field_type': field_type,
                    'order': 0,
                    'searchable': False,
                    'model_settings': {
                                                           # TODO: model settings
                    },
                    'schema_settings': item.get('schema'),
                    'is_valid': True,
                    'description': None
                }
                result_list.append(meta)

                if item['type'] in [field.Object.name, field.Nested.name] and item['fields']:
                    _get_fields_metadata(fields=item['fields'], result_list=result_list, prefix=meta_field_name)

        meta_model_fields = []
        all_model_fields = cls.get_all_model_fields(include_type_obj=True, include_schema=True)
        _get_fields_metadata(fields=all_model_fields, result_list=meta_model_fields)

        metadata = {
            'meta_model': {
                'model_name': cls.Index.name,
                'model_settings': {
                    'elasticsearch_settings': {
                        "index": {k: v
                                  for k, v in cls.Index.__dict__.items() if not k.startswith('__')}
                    }
                },
                'schema_settings': {
                    'unknown': 'exclude'
                },
                'is_valid': True,
                'description': cls.__doc__
            },
            'meta_model_fields': meta_model_fields
        }

        return metadata

    @classmethod
    def export_metadata(cls, init: bool = True):

        # 初始化模型
        if init:
            cls.init()

        # 获取模型元数据
        metadata = cls.get_model_metadata()

        # 发送至微服务保存
        # logger.info(f"{cls.Index.name} model metadata: {metadata}")
        # r = caller(service='common', method='import_model_metadata', raise_exception=True)(metadata)
        # logger.info(f"export metadata result: {r}")
