from typing import List
from sql_metadata import Parser
from source_analyser.utils import get_short_path, get_string_with_substituted_global_variables, prettify_path, read_file
import abc


class View(abc.ABC):
    @abc.abstractmethod
    def generate_code_for_notebook(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractproperty
    def KEYS_TO_SELECT(self):
        raise NotImplementedError


class TableView(View):
    # "property_table": {
    #   "tableName" : "egdp_dwh_supply.lodging_profile_eg",
    #   "databaseName": "egdp_dwh_supply",
    #   "databaseType" : "HIVE",
    #   "properties" : {}
    # }

    KEYS_TO_SELECT = (
        "tableName",
        # "databaseName",
        "databaseType",
    )

    def __init__(self, view_name: str, table: dict) -> None:
        self.table = table
        self.view_name = view_name

    def __str__(self) -> str:
        tmp = []
        for k, v in self.table.items():
            if k not in self.KEYS_TO_SELECT:
                continue
            tmp.append(f"\t{k: <12} --> {v}")
        return self.view_name + "\n" + "\n".join(tmp)

    def __repr__(self) -> str:
        return self.__str__()

    def generate_code_for_notebook(self) -> str:
        raw = f"create_view_from_table(name='{self.view_name}', table='{self.table['tableName']}')"
        return raw


class SqlView:
    def __init__(self, path: str, global_variables={}) -> None:
        self.path = prettify_path(path=path)
        self.global_variables = global_variables
        self.short_path = get_short_path(path)
        self.raw_data = self.fetch_data()
        self.data = Parser(self.raw_data)

    def fetch_data(self):
        lines = []
        raw_data = read_file(self.path)
        for line in raw_data.split("\n"):
            line = line.strip()
            if line.startswith("--"):
                continue
            lines.append(line)
        data = "\n".join(lines)
        return get_string_with_substituted_global_variables(
            data, self.global_variables
        )

    def get_tables(self) -> List[str]:
        try:
            return [i for i in self.data.tables if "." in i]
        except Exception as e:
            print(
                f"# Warning! can not analyse the SQl file {self.path}, skipping it"
            )
            return []

    def prettify_table_views(self) -> str:
        return "TableViews:\n" + "\n".join(self.get_tables())

    def __str__(self) -> str:
        return "\n".join(
            (
                f"absolute path --> {self.path}",
                # f"short path    --> {self.short_path}",
                ("\n" + self.prettify_table_views() if self.get_tables else ""),
            )
        )

    def __repr__(self) -> str:
        return self.__str__()


class SourceView(View):
    # "fileFormat": "",
    #   "filePath": "#{destinationBasePath}/postprocessing/parquetWithCrossOppy/",
    #   "fileName": "",
    #   "fileType": "PARQUET",
    #   "s3Bucket" : "#{destBucketName}",
    #   "dateFormatInPath" :["yyyy-MM-dd"],
    #   "readLatest" : true
    KEYS_TO_SELECT = ("filePath", "fileType", "dateFormatInPath")

    def __init__(self, view_name: str, table: dict) -> None:
        self.table = table
        self.view_name = view_name

    def __str__(self) -> str:
        tmp = []
        for k, v in self.table.items():
            if k not in self.KEYS_TO_SELECT:
                continue
            tmp.append(f"\t{k: <12} --> {v}")
        return self.view_name + "\n" + "\n".join(tmp)

    def __repr__(self) -> str:
        return self.__str__()

    def generate_code_for_notebook(self) -> str:
        path = self.table.get("filePath")
        date_format = self.table.get("dateFormatInPath", [])
        file_type = self.table.get("fileType").lower()
        delimiter = self.table.get("delimiter", ",").lower()
        raw = f"create_view_from_file(name='{self.view_name}', path=get_latest_dir_path('{path}', {len(date_format)}), file_type='{file_type}', delimiter='{delimiter}')"
        return raw


class TransformationView(View):
    # {
    #   "dfName": "sdf_hotel_view",
    #   "queryLocation": "#{configBasePath}/preprocessing/prediction/transformation/sdf_hotel.sql",
    #   "hiveVars" : {
    #     "scoringDate" :  "%sql select ADD_MONTHS(date_format(current_date,'yyyy-MM-dd'), -12 * ( year(current_date) - 2019  ))"
    #   }
    # }
    KEYS_TO_SELECT = ""

    def __init__(self, view_name: str, table: dict, query: SqlView = None) -> None:
        self.table = table
        self.view_name = view_name
        self.query = query

    def __str__(self) -> str:
        tmp = []
        for k, v in self.table.items():
            if k not in self.KEYS_TO_SELECT:
                continue
            tmp.append(f"\t{k: <12} --> {v}")
        tmp.append(f"\t{'queryLocation': <12} --> {self.query.path}")
        return self.view_name + "\n" + "\n".join(tmp)

    def __repr__(self) -> str:
        return self.__str__()

    def generate_code_for_notebook(self) -> str:
        raw = f"""query='''\n{self.query.raw_data}\n'''\ncreate_view_from_sql(name='{self.view_name}', sql=query)"""
        return raw


class OutputView(View):
    # "outputLocation": {
    #     "currentDistinctRowNumOppy_view" : {
    #       "fileFormat": "",
    #       "filePath": "#{destinationBasePath}/#{combinedCrossOppyInputPath}/#{snapShotDate}",
    #       "fileName": "",
    #       "fileType": "PARQUET"
    #     }
    #   }
    KEYS_TO_SELECT = ("filePath", "fileType")

    def __init__(self, view_name: str, table: dict) -> None:
        self.table = table
        self.view_name = view_name

    def __str__(self) -> str:
        tmp = []
        for k, v in self.table.items():
            if k not in self.KEYS_TO_SELECT:
                continue
            tmp.append(f"\t{k: <12} --> {v}")
        return self.view_name + "\n" + "\n".join(tmp)

    def __repr__(self) -> str:
        return self.__str__()

    def generate_code_for_notebook(self) -> str:
        print_statement = (
            f"""print("Running SQL Query for {self.view_name} {'*'*10}")"""
        )
        return f"""{print_statement}\ncreate_view_from_sql("{self.view_name}_run", "select * from {self.view_name}").show(n=1, vertical=True)"""
