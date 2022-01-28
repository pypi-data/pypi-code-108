import logging

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connection
from transliterate import translit

from one_c.models.entities import Field
from one_c.models.entity_1c import Entity_1c
from one_c.models.one_c_params_entity_view import One_c_params_entity_view

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    entities = settings.ONE_C_ENTITIES()

    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def qutes_str(self, str):
        return f"'{str}'"

    def uncapitalize(self, str):
        return str[0:1].lower() + str[1:]

    def handle(self, *args, **options):

        try:
            fields = []
            sql = []
            # sql1 = []
            for entity in Entity_1c.objects.filter():
                entity_code = translit(entity.code, reversed=True).replace("'", '')

                m_view_name = f'{self.dbl_qutes_str(entity_code + "_mview")}'

                sql.append(f'DROP MATERIALIZED VIEW IF EXISTS {m_view_name};')
                sql.append(f'CREATE MATERIALIZED VIEW {m_view_name} AS SELECT d.ref, d.entity_id,')
                sql.append(f'$FIELDS')

                for param in One_c_params_entity_view.objects.filter(entity=entity):
                    used_field = self.entities.get_field(entity.id, param.code)

                    if used_field:
                        if used_field.type == Field.string():
                            item = f'(SELECT string_agg(dp.value, {self.qutes_str(", ")}) FROM ducument_param_1c_view dp JOIN one_c_param_type pt ON pt.id = dp.type_id WHERE dp.document_id = d.ref AND pt.code::text = ' \
                                f'{self.qutes_str(param.code)}::text) AS {self.dbl_qutes_str(self.uncapitalize(used_field.translited_alias))}'
                        elif used_field.type == Field.uuid():
                            if param.code != 'Ref':
                                item = f'(SELECT case when dp.value_uuid::text = {self.qutes_str("00000000-0000-0000-0000-000000000000")} then null else dp.value_uuid end as value_uuid FROM ducument_param_1c_view dp JOIN one_c_param_type pt ON pt.id = dp.type_id WHERE dp.document_id = d.ref AND pt.code::text = ' \
                                    f'{self.qutes_str(param.code)}::text) AS {self.dbl_qutes_str(self.uncapitalize(used_field.translited_alias))}'
                            else:
                                item = None
                        elif used_field.type == Field.int():
                            item = f'(SELECT dp.value_int FROM ducument_param_1c_view dp JOIN one_c_param_type pt ON pt.id = dp.type_id WHERE dp.document_id = d.ref AND pt.code::text = ' \
                                f'{self.qutes_str(param.code)}::text) AS {self.dbl_qutes_str(self.uncapitalize(used_field.translited_alias))}'
                        elif used_field.type == Field.float():
                            item = f'(SELECT dp.value_float FROM ducument_param_1c_view dp JOIN one_c_param_type pt ON pt.id = dp.type_id WHERE dp.document_id = d.ref AND pt.code::text = ' \
                                f'{self.qutes_str(param.code)}::text) AS {self.dbl_qutes_str(self.uncapitalize(used_field.translited_alias))}'
                        elif used_field.type == Field.boolean():
                            item = f'(SELECT dp.value_boolean FROM ducument_param_1c_view dp JOIN one_c_param_type pt ON pt.id = dp.type_id WHERE dp.document_id = d.ref AND pt.code::text = ' \
                                f'{self.qutes_str(param.code)}::text) AS {self.dbl_qutes_str(self.uncapitalize(used_field.translited_alias))}'
                        else:
                            raise Exception(f'Unknown type: {used_field.type}')

                        if item:
                            fields.append(item)

                sql.append(f'FROM one_c_document_1c d WHERE d.entity_id = {entity.id} WITH NO DATA;')
                sql.append(f'REFRESH MATERIALIZED VIEW {m_view_name};')

                sql_str = '\n'.join(sql).replace('$FIELDS', ',\n'.join(fields))

                with connection.cursor() as cursor:
                    logger.debug(f'\n{sql_str}')
                    cursor.execute(sql_str)
                    logger.debug(f'Created all')

        except Exception as ex:
            raise ex
