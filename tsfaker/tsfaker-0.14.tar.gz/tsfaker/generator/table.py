import logging
import os
from typing import Optional, Dict

import numpy as np
import pandas as pd
from tableschema import Field
from tableschema import Schema

from tsfaker.exceptions import TypeNotImplementedError, ResourceMissing
from tsfaker.generator import column
from tsfaker.generator.foreign_key import ForeignKeyCatalog, ForeignKeyGenerator
from tsfaker.io.schema import INPUT_DESCRIPTOR, OUTPUT_FILE, NAME
from tsfaker.io.utils import smart_open_write, replace_dash


class TableGenerator:
    def __init__(self, schema: Schema, nrows: int, resource_name_to_path_or_schema: Dict[str, str] = None,
                 foreign_key_catalog: ForeignKeyCatalog = None, random_seed: int = 42):
        self.schema = schema
        self.input_descriptor = self.schema.descriptor.get(INPUT_DESCRIPTOR)
        self.output_file = self.schema.descriptor.get(OUTPUT_FILE)
        self.name = self.schema.descriptor.get(NAME)
        logging.debug("Initializing table generator for {}".format(self.name))
        self.nrows = nrows
        self.resource_name_to_path_or_schema = resource_name_to_path_or_schema or dict()
        self.random_seed = random_seed
        self.foreign_key_catalog = foreign_key_catalog or ForeignKeyCatalog(
            resource_name_to_path_or_schema=resource_name_to_path_or_schema)
        self.foreign_key_columns = dict()
        self.set_foreign_keys_columns()

    def generate_output_csv(self, dry_run: bool, pretty: bool, overwrite: bool, separator: str):
        self.resource_name_to_path_or_schema[self.name] = self.output_file

        if self.output_file and self.output_file != '-':
            if os.path.exists(self.output_file) and not overwrite:
                logging.warning("Output file '{}' already exists. Use '--overwrite' option if you want to."
                                .format(self.output_file))
                return

        logging.info("Data generated from descriptor '{}' will be written on '{}'"
                     .format(replace_dash(self.input_descriptor, 'STDIN'), replace_dash(self.output_file, 'STDOUT')))

        if dry_run:
            return

        table_string = self.get_string(pretty, separator)

        with smart_open_write(self.output_file) as f:
            f.write(table_string)

    def get_string(self, pretty, separator=',') -> Optional[str]:
        df = self.get_dataframe()
        if pretty:
            return df.to_string()
        else:
            return df.to_csv(index=False, sep=separator)

    def get_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(data=self.get_array(), columns=self.schema.field_names)

    def get_array(self) -> np.array:
        logging.debug('Generate numpy array for table {}'.format(self.name))
        columns = []
        for field in self.schema.fields:
            column_array = self.get_column_array(field)
            columns.append(column_array)

        if len(columns) == 1:
            return columns[0]
        else:
            return np.concatenate(columns, axis=1)

    def get_column_array(self, field: Field) -> np.ndarray:
        logging.debug('Get column array for field {}'.format(field.name))
        if field.name in self.foreign_key_columns:
            return self.foreign_key_columns[field.name]

        if 'enum' in field.constraints:
            self.random_seed += 1
            generator = column.Enum(self.nrows, type=field.type, **field.constraints, random_seed=self.random_seed)
            return generator.get_2d_array()

        field_type = field.type.lower()
        generator_class = column.tstype_to_generator_class.get(field_type, None)
        if generator_class is None:
            raise TypeNotImplementedError("Type '{}' is not implemented yet.".format(field.type))
        self.random_seed += 1
        arguments = field.constraints
        arguments['format'] = field.format
        arguments['trueValues'] = field.descriptor.get('trueValues')
        arguments['falseValues'] = field.descriptor.get('falseValues')
        generator = generator_class(self.nrows, **arguments, random_seed=self.random_seed)
        return generator.get_2d_array()

    def set_foreign_keys_columns(self):
        logging.debug("Set foreign keys columns for table {}".format(self.name))
        for foreign_key in self.schema.foreign_keys:
            resource_name = foreign_key['reference']['resource']
            if resource_name not in self.resource_name_to_path_or_schema:
                raise ResourceMissing("'{}' resource not found for descriptor '{}'. Use --resources option.".
                                      format(resource_name, self.schema))

            self.random_seed += 1
            foreign_key_generator = ForeignKeyGenerator(
                self.nrows,
                fields=foreign_key['fields'],
                resource_name=resource_name,
                resource_fields=foreign_key['reference']['fields'],
                foreign_key_catalog=self.foreign_key_catalog,
                random_seed=self.random_seed
            )

            for field in foreign_key_generator.fields:
                generator = column.ForeignKey(field, foreign_key_generator)
                self.foreign_key_columns[field] = generator.get_2d_array()
