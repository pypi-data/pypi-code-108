from source_analyser.pipeline import Pipeline
from source_analyser.views import SqlView
from source_analyser.utils import (
    get_global_variables,
    get_files_by_ext,
    SEPERATOR,
    does_path_exists,
    read_file,
)
import collections
import json_minify
import json
from typing import Iterable, Tuple, Dict, Any, List
from itertools import chain
from collections import defaultdict, OrderedDict


class Opportunity:
    def __init__(
        self,
        config_paths: Tuple[str],
        global_variables_path: str = "",
        global_variables: dict = {},
        *args,
        **kwargs,
    ) -> None:
        assert (type(config_paths) == tuple) or (
            type(config_paths) == list
        ), "Give config_paths as list/tuple of paths"

        for config_path in config_paths:
            assert does_path_exists(config_path), f"{config_path} does not exists"
        self.config_paths = config_paths

        if global_variables_path:
            assert does_path_exists(
                global_variables_path
            ), f"{global_variables_path} does not exists"
            self.global_variables = get_global_variables(global_variables_path)
        elif global_variables:
            self.global_variables = global_variables
        else:
            raise Exception("Give either global_variables_path or global_variables")

        self.sqls = list(self._get_sqls())
        self.pipelines = list(self._get_pipelines())

    def get_global_variables(self, path: str) -> Dict[str, Any]:
        raw_data = read_file(path)
        data = json_minify.json_minify(raw_data)
        data = json.loads(data, object_pairs_hook=OrderedDict)
        return data["GlobalVariables"]

    def _get_sqls(self) -> Iterable[SqlView]:
        for file in self.get_files_path_by_ext("sql"):
            yield SqlView(file, global_variables=self.global_variables)

    def _get_pipelines(self) -> Iterable[Pipeline]:
        sqls_dict = collections.defaultdict(list)
        for sql in self.sqls:
            sql_file_name = sql.path.split("/")[-1]
            sqls_dict[sql_file_name].append(sql)

        for file in self.get_files_path_by_ext("json"):
            yield Pipeline(file, sqls_dict, global_variables=self.global_variables)

    def get_files_path_by_ext(self, ext) -> Iterable[str]:
        for _path in self.config_paths:
            for _, file_path in get_files_by_ext(_path, ext):
                yield file_path

    def show_pipeline(self) -> None:
        for pipeline in chain(self.pipelines):
            if not pipeline.tables:
                continue
            print(SEPERATOR)
            print(pipeline)

    def show_sqls(self) -> None:
        for sql in chain(self.sqls):
            if not sql.get_tables():
                continue
            print(SEPERATOR)
            print(sql)

    def get_unique_tables(self) -> Dict[str, List[dict]]:
        unique_tables = defaultdict(list)

        for pipeline in self.pipelines:
            for table in pipeline.tables:
                unique_tables[table.table["tableName"]].append((pipeline, table))

        # find stand alone / directly used tables inside sql
        for sql in self.sqls:
            for table in sql.get_tables():
                unique_tables[table].append((sql, table))

        return unique_tables

    def get_unique_sources(self) -> Dict[str, List[dict]]:
        unique_sources = defaultdict(list)
        for pipeline in self.pipelines:
            for source in pipeline.sources:
                unique_sources[source.table["filePath"]].append(
                    (pipeline, source.table)
                )
        return unique_sources

    def show_unique_tables(self) -> None:
        for key, it in self.get_unique_tables().items():
            print(SEPERATOR)
            print(key)
            for pipe, tb in it:
                print("\t" + pipe.short_path)

    def show_unique_sources(self) -> None:
        for key, it in self.get_unique_sources().items():
            print(SEPERATOR)
            print(key)
            for pipe, tb in it:
                print("\t" + pipe.short_path)
