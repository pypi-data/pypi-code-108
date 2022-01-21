import re
from dependencies.exception import exception_handler
from jobs.etl_job_base import EtlJobBase
import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql.utils import AnalysisException
from constants.constants_configs import Config as Constant_Config

# from dependencies.unit_test_data_factory import unit_test_data_factory


class JSONToParquet(EtlJobBase):
    @exception_handler
    def get_custom_argparse_configs(self, parser):
        """
        :params parser: the arg parse object to add custom CLI params to
        :return parser:
        """
        parser.add_argument(
            "--input-source",
            action="store",
            type=str,
            required=False,
            help="if input source need be specified",
        )
        parser.add_argument(
            "--output-loop-location",
            action="store",
            type=str,
            required=True,
            help="S3 location where to write outputloop files.  Suffix of the output SSD table name will be appended to this path",
        )
        return parser

    @exception_handler
    def add_custom_config_fields(self, config, args):
        """
        Overloading to add custom config fields
        :params config: config object created in get_base_argparse_configs
        :params args: args given to argparse, used in creating custom config pieces
        :return config: new config object with desired custom fields
        """

        config[Constant_Config.STEP_CONFIG]["input_source"] = args["input_source"]
        config[Constant_Config.STEP_CONFIG]["output_loop_location"] = args[
            "output_loop_location"
        ]
        config[Constant_Config.STEP_CONFIG]["metadata"] = {}

        if "837" in config["step_name"]:
            config[Constant_Config.STEP_CONFIG]["file_type"] = "837"
        elif "834" in config["step_name"]:
            config[Constant_Config.STEP_CONFIG]["file_type"] = "834"
        elif "rx" in config["step_name"]:
            config[Constant_Config.STEP_CONFIG]["file_type"] = "rx"

        return config

    @exception_handler
    def create_output_loop(self, df, output_loop):
        """
        Create SSD tables based on output_loop specified in YAML
        :params df: SSD dataframe created by outputloop
        :params output_loop: yaml config from step yaml file for SSD output loop
        :returns df: SSD dataframe
        """
        # TODO: in create_output_loop, check to make sure each field is part of the schema. drop or error if not.
        df_loop = df
        self.log.info(f"WORKING ON {output_loop['name']} OUTPUT LOOP")
        self.config[Constant_Config.STEP_CONFIG]["metadata"][output_loop["name"]] = []
        if output_loop["list_key"] is not None:
            # Renaming doesnt work with nested structs. If i keep a top level struct with the same name, nested references will not refer to the exploded column.
            df_loop = df_loop.withColumn(
                output_loop["list_key"].split(".")[-1] + "_exp",
                F.explode(df_loop[output_loop["list_key"]]),
            )
        for field in output_loop["fields"].keys():
            field_info = output_loop["fields"][field]
            if output_loop["list_key"] is not None:
                field_info["src_field"] = field_info["src_field"].replace(
                    output_loop["list_key"],
                    output_loop["list_key"].split(".")[-1] + "_exp",
                )
            # Check if field refers to metadata, to be added later
            if re.fullmatch(r".*\{.*\}.*", field_info["src_field"]):
                self.config[Constant_Config.STEP_CONFIG]["metadata"][
                    output_loop["name"]
                ].append(field)
                df_loop = df_loop.withColumn(field, F.lit(None))
            else:
                if "alt_src_field" in field_info.keys():
                    field_info["alt_src_field"] = field_info["alt_src_field"].replace(
                        output_loop["list_key"],
                        output_loop["list_key"].split(".")[-1] + "_exp",
                    )
                    # TODO: add try except for if src or alt_src are in schema
                    df_loop = df_loop.withColumn(
                        field,
                        F.coalesce(
                            df_loop[field_info["src_field"]],
                            df_loop[field_info["alt_src_field"]],
                        ),
                    )
                else:
                    try:
                        if "src_type" in field_info:
                            df_loop = df_loop.withColumn(
                                field, df_loop[field_info["src_field"]].cast(field_info['src_type'])
                            )
                        else:
                            df_loop = df_loop.withColumn(
                                field, df_loop[field_info["src_field"]]
                            )
                    except Exception:
                        self.log.warn(
                            f"{self.config[Constant_Config.STEP_CONFIG]['file_type']} from {self.config[Constant_Config.STEP_CONFIG]['input_source']} does not have field {field_info['src_field']}; set as Null"
                        )
                        print(field_info)
                        src_type = field_info['src_type'] if 'src_type' in field_info else 'string'
                        src_default = field_info['src_default'] if 'src_default' in field_info else None
                        df_loop = df_loop.withColumn(field,  F.lit(None if src_default=='null' else src_default).cast(src_type))
                        pass
        return df_loop.select(list(output_loop["fields"].keys()))

    @exception_handler
    def collapse_stupid_lists(self, df, output_loop):
        """
        Several of the fields in the json doc are the same but with different suffixes, _01..._12.
        We want to collapse all of these into a single field
        :params df: SSD dataframe created by outputloop
        :params output_loop: yaml config from step yaml file for SSD output loop
        :returns df: SSD dataframe with stupid lists collapsed
        """
        # Get All the stupid list columns; map to output column name
        stupid_list_cols = {}
        for k, v in output_loop["fields"].items():
            if re.search(r"_\d\d$", v["src_field"]):
                stupid_list_cols[v["src_field"]] = k
            if "alt_src_field" in v.keys():
                if re.search(r"_\d\d$", v["alt_src_field"]):
                    stupid_list_cols[v["alt_src_field"]] = k
        # Create Column Sets (columns that will go together)
        stupid_column_sets = {}
        for stupid_in_col, stupid_out_col in stupid_list_cols.items():
            try:
                assert re.search(r"_\d\d$", stupid_out_col)
            except AssertionError:
                self.log.warn(
                    f"{stupid_out_col} should have same suffix pattern as {stupid_in_col}"
                )
            if (
                re.split(r"_\d\d$", stupid_out_col, maxsplit=1)[0]
                in stupid_column_sets.keys()
            ):
                stupid_column_sets[
                    re.split(r"_\d\d$", stupid_out_col, maxsplit=1)[0]
                ].append(stupid_out_col)
            else:
                stupid_column_sets[
                    re.split(r"_\d\d$", stupid_out_col, maxsplit=1)[0]
                ] = [stupid_out_col]

        # Aggregate stupid list columns and delete originals
        for stupid_col_root, stupid_out_cols in stupid_column_sets.items():
            for stupid_out_col in list(stupid_out_cols):
                if df.schema[stupid_out_col].dataType == T.StringType():
                    df = df.withColumn(
                        stupid_out_col,
                        F.split(F.col(stupid_out_col), ",").cast(
                            T.ArrayType(T.StringType())
                        ),
                    )
                df = df.withColumn(
                    stupid_out_col,
                    F.coalesce(F.col(stupid_out_col), F.array().cast("array<string>")),
                )
            df = df.withColumn(
                stupid_col_root, F.array_remove(F.flatten(F.array(stupid_out_cols)), "")
            )
            df = df.drop(*stupid_out_cols)

        return df

    def add_metadata(self, df, output_loop):
        """
        Add metadata fields to SSD dataframe according to whether metadata field present in output-loop yaml
        :params df: SSD dataframe created by outputloop
        :params output_loop: yaml config from step yaml file for SSD output loop
        :returns df: SSD dataframe with metadata added
        """
        # Metadata columns: source, job_id, created_at
        metadata_fields = list(
            self.config[Constant_Config.STEP_CONFIG]["metadata"][output_loop["name"]]
        )
        if "cad_source_name" in metadata_fields:
            df = df.withColumn(
                "cad_source_name",
                F.lit(self.config[Constant_Config.STEP_CONFIG]["input_source"]),
            )
        if "cad_client" in metadata_fields:
            df = df.withColumn("cad_client", F.lit(self.config["client"]))
        if "cad_created_at" in metadata_fields:
            df = df.withColumn("cad_created_at", F.lit(F.current_timestamp()))
        if "cad_job_id" in metadata_fields:
            df = df.withColumn("cad_job_id", F.lit(self.config["job_id"]))
        return df

    @exception_handler
    def extract_data(self):
        """Load test_data from Parquet file format.
        :param spark: Spark session object.
        :return: Spark DataFrame.
        """
        # self.log.info(self.config[Constant_Config.STEP_CONFIG]["input_source"])
        df = self.spark.read.format("json").option('dropFieldIfAllNull', True).load(
            self.config[Constant_Config.STEP_CONFIG]["input_source"]
        )
        self.log.info(
            f"Writing json data from {self.config[Constant_Config.STEP_CONFIG]['input_source']}"
        )
        return df

    @exception_handler
    # @unit_test_data_factory
    def transform_data(self, df, output_loop):
        """Transform original dataset.
        :param df: Input DataFrame.
        :return: Transformed DataFrame.
        """
        # Run check on loop_key existence - if no list key, do not load ssd table.
        if output_loop["list_key"] is not None:
            try:
                df.select(output_loop["list_key"])
            except AnalysisException:
                # return
                self.log.warn(
                    f"List key {output_loop['list_key']} does not exist in {self.config[Constant_Config.STEP_CONFIG]['input_source']}"
                )
                self.log.warn(
                    f"Cannot write {output_loop['name']} for job {self.config['job_id']} to SSD"
                )
                return None
        df_transformed = self.create_output_loop(df, output_loop)
        df_transformed = self.collapse_stupid_lists(df_transformed, output_loop)
        df_transformed = self.add_metadata(df_transformed, output_loop)
        return df_transformed

    @exception_handler
    def load_data(self, df, output_loop):
        """Collect test_data locally and write to CSV.
        :param df: DataFrame to print.
        :return: None
        """
        loop_outpath = f"{self.config[Constant_Config.STEP_CONFIG]['output_loop_location']}/{output_loop['name']}"
        if len(output_loop["partition"]) > 0:
            df.printSchema()
            df.write.parquet(
                loop_outpath,
                mode="append",
                partitionBy=output_loop["partition"],
            )
        else:
            df.write.parquet(loop_outpath, mode="overwrite", compression="gzip")
        self.log.info(
            f"Succeeded writing json data for loop {output_loop['name']} to {loop_outpath}"
        )
        return None

    @exception_handler
    def run_etl(self):
        """
        Overloading run_etl to run transform & load on each separate output-loop/SSD table
        """
        for k, v in self.config[Constant_Config.STEP_CONFIG].items():
            self.log.info(f"{k}:")
            self.log.info(v)
        data = self.extract_data()
        for output_loop in self.config[Constant_Config.STEP_CONFIG]["outputs"]:
            data_transformed = self.transform_data(data, output_loop)
            if data_transformed is not None:
                self.load_data(data_transformed, output_loop)

        return


if __name__ == "__main__":
    run_json_to_pq = JSONToParquet()
    run_json_to_pq.main()
