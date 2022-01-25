from pathlib import Path
from json.decoder import JSONDecodeError
from typing import Any, Dict, Iterable, List, Tuple
from source_analyser.utils import (
    BAKWAS,
    get_short_path,
    get_string_with_substituted_global_variables,
    read_file,
    prettify_path
)
from source_analyser.views import SqlView, TransformationView, TableView, SourceView, OutputView
import json_minify
import json
from collections import OrderedDict


class Pipeline:
    def __init__(
        self,
        path: str,
        sqls: Dict[str, SqlView] = [],
        global_variables={},
        *args,
        **kwargs,
    ) -> None:
        self.path = prettify_path(path=path)
        self.global_variables = global_variables
        self.short_path = get_short_path(path)
        self.data = self.fetch_data()
        self.tables = list(self.get_tables())
        self.sources = list(self.get_sources())
        self.transformations = list(self.get_transformations(sqls=sqls))
        self.outputs = list(self.get_outputs())

    def parse_views(self, key_name: str) -> Iterable[Tuple[str, dict]]:
        tables_dict = self.data.get(key_name, dict())
        for name, table in tables_dict.items():
            yield name, table

    def fetch_data(self) -> Dict[str, Any]:
        raw_data = read_file(self.path)
        gv_replaced = get_string_with_substituted_global_variables(
            raw_data, self.global_variables
        )
        data = json_minify.json_minify(gv_replaced)
        if data:
            try:
                data = json.loads(data, object_pairs_hook=OrderedDict)
                return data
            except JSONDecodeError as e:
                print("Could not load json for pipline at")
                print(self.path)
                print(data)
                print(e)
                raise e
        else:
            print(f"#Warning!, skipping {self.path} file as no json was found")
            return {}

    def get_transformations(self, sqls) -> Iterable[TransformationView]:
        transformations = self.data.get("transformations", list())
        for entry in transformations:
            view_name, table = entry["dfName"], entry
            tmp_path = str(Path(table["queryLocation"]))
            used_sql_name = tmp_path.split("/")[-1]

            assert (
                len(sqls[used_sql_name]) > 0
            ), f"No sql file exists with name {used_sql_name}"

            matched_sqls = self._match_sqls(tmp_path, sqls[used_sql_name])
            if len(matched_sqls) == 0:
                raise ValueError(
                    f"Did not found and SQLView for {tmp_path} in {self.path}"
                )
            if len(matched_sqls) > 1:
                raise ValueError(
                    f"Duplicate SQLView to Found for {tmp_path} in {self.path} as there are {list(map(lambda x:x.path, matched_sqls))} sqls"
                )
            yield TransformationView(
                view_name=view_name, table=table, query=matched_sqls[0]
            )

    @staticmethod
    def _get_path_score(p1, p2) -> int:
        p1 = reversed(p1.split("/"))
        p2 = reversed(p2.split("/"))
        sm = 0
        for a, b in zip(p1, p2):
            if a == b:
                sm += 1
            else:
                break
        return sm

    def _match_sqls(self, path: str, sqls: List[SqlView]) -> List[SqlView]:
        mx_sql = max(sqls, key=lambda x: self._get_path_score(path, x.path))
        mx_score = self._get_path_score(path, mx_sql.path)
        return list(
            filter(lambda x: mx_score == self._get_path_score(path, x.path), sqls)
        )

    def get_tables(self) -> Iterable[TableView]:
        for view_name, table in self.parse_views(key_name="tableSources"):
            yield TableView(view_name=view_name, table=table)

    def prettify_table_views(self) -> str:
        return "TableViews:\n" + "\n\n".join(map(lambda x: x.__str__(), self.tables))

    def get_sources(self) -> Iterable[SourceView]:
        for view_name, table in self.parse_views(key_name="sources"):
            yield SourceView(view_name=view_name, table=table)

    def get_outputs(self) -> Iterable[OutputView]:
        for view_name, table in self.parse_views(key_name="outputLocation"):
            yield OutputView(view_name=view_name, table=table)

    def prettify_source_views(self) -> str:
        return "SoureViews:\n" + "\n\n".join(map(lambda x: x.__str__(), self.sources))

    def prettify_sql_views(self) -> str:
        return "SQL:\n" + "\n\n".join(map(lambda x: x.__str__(), self.sqls))

    def prettify_transformation_views(self) -> str:
        return "Transformations:\n" + "\n\n".join(
            map(lambda x: x.__str__(), self.transformations)
        )

    def __str__(self) -> str:

        return "\n".join(
            (
                f"absolute path --> {self.path}",
                # f"short path    --> {self.short_path}",
                ("\n" + self.prettify_table_views() if self.tables else ""),
                ("\n" + self.prettify_source_views() if self.sources else ""),
                (
                    "\n" + self.prettify_transformation_views()
                    if self.transformations
                    else ""
                ),
            )
        )

    def __repr__(self) -> str:
        return self.__str__()

    def prettify_tables_code_for_notebook(self) -> str:
        return "\n".join(map(lambda x: x.generate_code_for_notebook(), self.tables))

    def prettify_sources_code_for_notebook(self) -> str:
        return "\n".join(map(lambda x: x.generate_code_for_notebook(), self.sources))

    def prettify_output_code_for_notebook(self) -> str:
        return "\n#%%\n".join(
            map(lambda x: x.generate_code_for_notebook(), self.outputs)
        )

    def prettify_transformations_code_for_notebook(self) -> str:
        return "\n#%%\n".join(
            map(
                lambda x: f"# Using query from: {x.query.short_path}\n{x.generate_code_for_notebook()}",
                self.transformations,
            )
        )

    def generate_notebook(self) -> str:
        to_merge = (
            "#%%",
            "# Utility functions",
            BAKWAS,
            "#%%",
            "# Creating Table Views",
            self.prettify_tables_code_for_notebook(),
            "#%%",
            "# Sources Table Views",
            self.prettify_sources_code_for_notebook(),
            "#%%",
            self.prettify_transformations_code_for_notebook(),
            "\n\n\n\n#%%",
            "# Outputs",
            # self.prettify_output_code_for_notebook(),
        )
        return "\n".join(to_merge)
