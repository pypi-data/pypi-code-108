import logging
import os
import shutil

from django.conf import settings
from django.core.management import BaseCommand

from code_generator.core.writer_model import WriterModel
from one_c.models.entities import Field
from one_c.models.entity_1c import Entity_1c

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Создание мат вьюшек для документов из 1С"

    entities = settings.ONE_C_ENTITIES()

    def fill_space(self, qty):
        res = ''
        while True:
            res += ' '
            qty -= 1
            if qty == 0:
                return res

    def uncapitalize(self, _str):
        if not isinstance(_str, str):
            _str = str(_str)
        return _str[0:1].lower() + _str[1:]

    def capitalize(self, _str):
        if not isinstance(_str, str):
            _str = str(_str)
        return _str[0:1].upper() + _str[1:]

    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def qutes_str(self, str):
        return f"'{str}'"

    def handle(self, *args, **options):
        try:
            if not os.path.exists(settings.ONE_C_DIR):
                raise Exception(f'Path: {settings.ONE_C_DIR} not exists.')

            if not os.path.exists(settings.BASE_PATH_ONEC_TEMPLATE):
                raise Exception(f'Path: {settings.BASE_PATH_ONEC_TEMPLATE} not exists.')

            group_replace_map = dict(
                ITEMS=[],
                GROUP_NAME="OneC",
                ICON="Common.ur_entity",
                TITLE="Пользователи",
                TITLE_BUTTON="1С",
            )

            isc_replace_map = dict(
                ITEMD_EDITOR=[]
            )

            common_urls_file = f'{settings.ONE_C_DIR}{os.sep}common_urls.py'
            writerCommonUrls = WriterModel(path_output=common_urls_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}common_urls.pmd')

            isc_fields = isc_replace_map.get('ITEMD_EDITOR')
            isc_fields.append(f'{self.fill_space(2)}readonly {group_replace_map.get("GROUP_NAME")} : {group_replace_map.get("GROUP_NAME")}Statics;')
            isc_output_file = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}Isc.ts'
            writerIsc = WriterModel(path_output=isc_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}Isc.pmd')

            group_items = group_replace_map.get('ITEMS')
            group_output_file = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}groups{os.sep}group_one_c.ts'
            writerGroup = WriterModel(path_output=group_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}group.pmd')

            groups_output_dir = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}groups'
            if os.path.exists(groups_output_dir):
                shutil.rmtree(groups_output_dir)
            os.makedirs(groups_output_dir)

            model_output_dir = f'{settings.ONE_C_DIR}{os.sep}models'
            if os.path.exists(model_output_dir):
                shutil.rmtree(model_output_dir)
            os.makedirs(model_output_dir)

            views_output_dir = f'{settings.ONE_C_DIR}{os.sep}views'
            if os.path.exists(views_output_dir):
                shutil.rmtree(views_output_dir)
            os.makedirs(views_output_dir)

            urls_output_dir = f'{settings.ONE_C_DIR}{os.sep}urls'
            if os.path.exists(urls_output_dir):
                shutil.rmtree(urls_output_dir)
            os.makedirs(urls_output_dir)

            datasource_output_dir = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}datasources'
            if os.path.exists(datasource_output_dir):
                shutil.rmtree(datasource_output_dir)
            os.makedirs(datasource_output_dir)

            list_grid_editor_output_dir = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}editors'
            if os.path.exists(list_grid_editor_output_dir):
                shutil.rmtree(list_grid_editor_output_dir)
            os.makedirs(list_grid_editor_output_dir)

            menu_item_output_dir = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}menu_items'
            if os.path.exists(menu_item_output_dir):
                shutil.rmtree(menu_item_output_dir)
            os.makedirs(menu_item_output_dir)

            lookup_fields_output_dir = f'{settings.ONE_C_DIR}{os.sep}ts{os.sep}lookup_fields'
            if os.path.exists(lookup_fields_output_dir):
                shutil.rmtree(lookup_fields_output_dir)
            os.makedirs(lookup_fields_output_dir)

            common_urls_map = dict(
                LIST_PATH=[]
            )
            common_urls = common_urls_map.get('LIST_PATH')

            for entity in sorted(Entity_1c.objects.filter(), key=lambda record: record.code):

                model_name = f'{entity.translited_code}_model'
                model_caption = f'"{entity.code}"'
                common_urls.append(f'{self.fill_space(4)}path({self.qutes_str("logic/")}, include({self.qutes_str("kaf_pas.k_one_c.urls." + self.uncapitalize(entity.translited_code))})),')

                model_output_file = f'{model_output_dir}{os.sep}{self.uncapitalize(entity.translited_code)}.py'
                views_output_file = f'{views_output_dir}{os.sep}{self.uncapitalize(entity.translited_code)}.py'
                urls_output_file = f'{urls_output_dir}{os.sep}{self.uncapitalize(entity.translited_code)}.py'

                datasource_output_file = f'{datasource_output_dir}{os.sep}{self.uncapitalize(entity.translited_code)}.ts'
                list_grid_editor_output_file = f'{list_grid_editor_output_dir}{os.sep}{self.uncapitalize(entity.translited_code)}.ts'
                menu_item_output_file = f'{menu_item_output_dir}{os.sep}{self.uncapitalize(entity.translited_code)}.ts'
                lookup_fields_output_file = f'{lookup_fields_output_dir}'
                lookup_fields_output_file_ext = '.ts'

                writerModel = WriterModel(path_output=model_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}model.pmd')
                writerViews = WriterModel(path_output=views_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}views.pmd')
                writerUrls = WriterModel(path_output=urls_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}urls.pmd')

                writerDatasource = WriterModel(path_output=datasource_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}datasource.pmd')
                writerTreeEditor = WriterModel(path_output=list_grid_editor_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}tree_grid_editor.pmd')
                writerMenuItem = WriterModel(path_output=menu_item_output_file, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}menu_item.pmd')
                writerLookUpItem = WriterModel(path_output=lookup_fields_output_file, output_file_ext=lookup_fields_output_file_ext, template_path=f'{settings.BASE_PATH_ONEC_TEMPLATE}{os.sep}templates{os.sep}look_up_field.pmd')

                field_mapping = [
                    ('entity_id', 'record.entity.id'),
                    ('entity__code', 'record.entity.code'),
                ]

                field_mapping.extend([((self.uncapitalize(item.translited_alias), f'record.{self.uncapitalize(item.translited_record_path)}')) for item in self.entities.get_fields(entity.id)])

                # Не передвигать !!!
                model_replace_map = dict(
                    QUERY_SET='''def get_range_rows1(self, request, function=None):
        request = DSRequest(request=request)
        self.alive_only = False
        return self.get_range_rows(start=request.startRow, end=request.endRow, function=function, json=request.json)''',
                    NAME_MODEL=model_name,
                    FIELDS_MAPPING=f'dict({",".join([f"{item[0]}={item[1]}" for item in field_mapping])})',
                    FIELDS=[
                        f'{self.fill_space(4)}entity = ForeignKeyProtect(Entity_1c)',
                    ],
                    IMPORTS=[
                        'from one_c.models.base_model import Base_model',
                        'from django.db.models import UUIDField, TextField, IntegerField, FloatField, BooleanField, BigIntegerField',
                        'from isc_common.fields.related import ForeignKeyProtect',
                        'from one_c.models.entity_1c import Entity_1c',
                        'from isc_common.http.DSRequest import DSRequest',
                    ],
                    _STR_='f"(ref: {self.ref}, entity: {self.entity})"',
                    META=[
                        f'{self.fill_space(8)}managed = False',
                        f'{self.fill_space(8)}db_table = "{entity.translited_code}_mview"'
                    ]
                )

                view_replace_map = dict(
                    PACKAGE_MODEL_MANAGER=f'from kaf_pas.k_one_c.models.{self.uncapitalize(entity.translited_code)} import {entity.translited_code}_model, {entity.translited_code}_modelManager',
                    NAME_MODEL=model_name,
                )

                url_replace_map = dict(
                    PACKAGE_MODEL=f'from kaf_pas.k_one_c.views import {self.uncapitalize(entity.translited_code)}',
                    PACKAGE_VIEW=entity.translited_code,
                    LPACKAGE_VIEW=self.uncapitalize(entity.translited_code),
                    NAME_MODEL=model_name,
                )

                datasource_replace_map = dict(
                    NAME_MODEL=model_name,
                    NAME_PARAM=entity.translited_code,
                    FIELDS=[]
                )

                tree_grid_editor_replace_map = dict(
                    NAME_MODEL=model_name,
                    NAME_CAPTION=model_caption,
                    ITEMS_TYPE=[
                        'new MiTreeRefresh(),'
                        'new MiTreeCopyValue(),'
                    ],
                    parentIdField='parent',
                    idField='ref',
                    PERMISSIONS=''
                )

                menu_item_replace_map = dict(
                    NAME_MODEL=model_name,
                    NAME_PARAM=entity.code,
                    ICON="Common.ur_entity"
                )

                isc_fields.append(f'{self.fill_space(2)}readonly {model_name} : {model_name}Statics;')

                group_items.append(f'{self.fill_space(48)}get_{model_name}(ownerApp),')
                # group_items.append(f'{self.fill_space(56)}<MenuSSItem>{{isSeparator: true}},')

                model_fields = model_replace_map.get('FIELDS')
                datasource_fields = datasource_replace_map.get('FIELDS')

                for used_field in self.entities.get_fields(entity.id):
                    if used_field:
                        if not used_field.only_datasource:
                            if used_field.foreign_key:
                                model_fields.append(f'{self.fill_space(4)}{self.uncapitalize(used_field.translited_name)} = {str(used_field.foreign_key)}')
                            elif used_field.type == Field.string():
                                model_fields.append(f'{self.fill_space(4)}{self.uncapitalize(used_field.translited_name)} = TextField(primary_key={self.capitalize(used_field.primary_key)})')
                            elif used_field.type == Field.uuid():
                                model_fields.append(f'{self.fill_space(4)}{self.uncapitalize(used_field.translited_name)} = UUIDField(primary_key={self.capitalize(used_field.primary_key)})')
                            elif used_field.type == Field.boolean():
                                model_fields.append(f'{self.fill_space(4)}{self.uncapitalize(used_field.translited_name)} = BooleanField()')
                            elif used_field.type == Field.int():
                                model_fields.append(f'{self.fill_space(4)}{self.uncapitalize(used_field.translited_name)} = IntegerField(primary_key={self.capitalize(used_field.primary_key)})')
                            elif used_field.type == Field.float():
                                model_fields.append(f'{self.fill_space(4)}{self.uncapitalize(used_field.translited_name)} = FloatField()')
                            else:
                                raise Exception(f'{used_field.type} is unknown type.')

                        if used_field.type == Field.boolean():
                            datasource_fields.append(f'{self.fill_space(12)}{"booleanField"}(' +
                                                     f'"{self.uncapitalize(used_field.translited_alias)}", ' +
                                                     f'"{used_field.title}", ' +
                                                     f'{self.uncapitalize(used_field.required)},' +
                                                     f'{self.uncapitalize(used_field.hidden)},' +
                                                     f'{self.uncapitalize(used_field.canEdit)},' +
                                                     f'{self.uncapitalize(used_field.canFilter)},' +
                                                     f'{self.uncapitalize(used_field.canGroupBy)},' +
                                                     f'{used_field.index}),')
                        elif used_field.type == Field.uuid():
                            datasource_fields.append(f'{self.fill_space(12)}{"uuidField"}(' +
                                                     f'"{self.uncapitalize(used_field.translited_alias)}", ' +
                                                     f'"{used_field.title}", ' +
                                                     f'{self.uncapitalize(used_field.required)},' +
                                                     f'{self.uncapitalize(used_field.primary_key)},' +
                                                     f'{used_field.length[0]},' +
                                                     f'{self.uncapitalize(used_field.hidden)},' +
                                                     f'{self.uncapitalize(used_field.canEdit)},' +
                                                     f'{self.uncapitalize(used_field.canFilter)},' +
                                                     f'{used_field.align},' +
                                                     f'{self.uncapitalize(used_field.canGroupBy)},' +
                                                     f'{used_field.index}),')
                        elif used_field.type == Field.string():
                            datasource_fields.append(f'{self.fill_space(12)}{"nameField"}(' +
                                                     f'"{self.uncapitalize(used_field.translited_alias)}", ' +
                                                     f'"{used_field.title}", ' +
                                                     f'{self.uncapitalize(used_field.required)},' +
                                                     f'{self.uncapitalize(used_field.primary_key)},'
                                                     f'{used_field.length[0]},' +
                                                     f'{self.uncapitalize(used_field.hidden)},' +
                                                     f'{self.uncapitalize(used_field.canEdit)},' +
                                                     f'{self.uncapitalize(used_field.canFilter)},' +
                                                     f'{used_field.align},' +
                                                     f'{self.uncapitalize(used_field.canSort)},' +
                                                     f'{self.uncapitalize(used_field.canGroupBy)},' +
                                                     f'{used_field.index}),')
                        elif used_field.type == Field.float():
                            datasource_fields.append(f'{self.fill_space(12)}{"floatField"}(' +
                                                     f'"{self.uncapitalize(used_field.translited_alias)}", ' +
                                                     f'"{used_field.title}", ' +
                                                     f'{self.uncapitalize(used_field.required)},' +
                                                     f'{self.uncapitalize(used_field.primary_key)},'
                                                     f'{self.uncapitalize(used_field.hidden)},' +
                                                     f'{self.uncapitalize(used_field.canEdit)},' +
                                                     f'{self.uncapitalize(used_field.canFilter)},' +
                                                     f'{used_field.align},' +
                                                     f'{self.uncapitalize(used_field.format)},' +
                                                     f'{self.uncapitalize(used_field.canGroupBy)},' +
                                                     f'{used_field.index}),')
                        elif used_field.type == Field.int():
                            datasource_fields.append(f'{self.fill_space(12)}{"integerField"}(' +
                                                     f'"{self.uncapitalize(used_field.translited_alias)}", ' +
                                                     f'"{used_field.title}", ' +
                                                     f'{self.uncapitalize(used_field.required)},' +
                                                     f'{self.uncapitalize(used_field.primary_key)},'
                                                     f'{self.uncapitalize(used_field.hidden)},' +
                                                     f'{self.uncapitalize(used_field.canEdit)},' +
                                                     f'{self.uncapitalize(used_field.canFilter)},' +
                                                     f'{used_field.align},' +
                                                     f'{self.uncapitalize(used_field.format)},' +
                                                     f'{self.uncapitalize(used_field.canGroupBy)}),')

                        if used_field.lookup:
                            lookup_fields_replace_map = dict(
                                NAME_MODEL=model_name,
                                U_NAME_MODEL=self.uncapitalize(model_name),
                                NAME_PARAM=self.uncapitalize(used_field.translited_name),
                                TITLE=used_field.title,
                            )

                            writerLookUpItem.output_file_name = f'{self.uncapitalize(entity.translited_code)}_{self.uncapitalize(used_field.translited_name)}'
                            writerLookUpItem.write_entity(replace_map=lookup_fields_replace_map)

                logger.debug(f'Write: {model_output_file}')

                writerCommonUrls.write_entity(replace_map=common_urls_map)
                writerModel.write_entity(replace_map=model_replace_map)
                writerViews.write_entity(replace_map=view_replace_map)
                writerUrls.write_entity(replace_map=url_replace_map)
                writerDatasource.write_entity(replace_map=datasource_replace_map)
                writerTreeEditor.write_entity(replace_map=tree_grid_editor_replace_map)
                writerMenuItem.write_entity(replace_map=menu_item_replace_map)

            writerIsc.write_entity(replace_map=isc_replace_map)
            writerGroup.write_entity(replace_map=group_replace_map)

        except Exception as ex:
            raise ex
