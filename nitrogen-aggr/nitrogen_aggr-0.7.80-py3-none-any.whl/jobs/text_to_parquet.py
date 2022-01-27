import re
import pyspark.sql.functions as F
from dependencies.exception import exception_handler
from jobs.etl_job_base import EtlJobBase
from constants.constants_configs import Config as Constant_Config

# from dependencies.unit_test_data_factory import unit_test_data_factory


class TextToParquet(EtlJobBase):
    @exception_handler
    def extract_data(self):

        if self.config[Constant_Config.STEP_CONFIG]["filetype"] == "fixed-width":
            data = self.spark.read.text(
                 self.config[Constant_Config.STEP_CONFIG]["input_source"]
            )
        elif self.config[Constant_Config.STEP_CONFIG]["filetype"] == "csv":
            delimiter = self.config[Constant_Config.STEP_CONFIG]["delimiter"] or ","
            data = self.spark.read.csv(
                self.config[Constant_Config.STEP_CONFIG]["input_source"],
                sep=delimiter,
                header=self.config[Constant_Config.STEP_CONFIG]["header_row"],
                ignoreLeadingWhiteSpace=True,
                ignoreTrailingWhiteSpace=True,
            )
        else:
            self.log.error(
                f"Invalid fileyype: {self.config[Constant_Config.STEP_CONFIG]['filetype']}"
            )
            self.log.error(
                "text_to_parquet accepts only 'fixed-width' and 'csv' as valid filetypes."
            )
            raise IOError

        return data

    @exception_handler
    # @unit_test_data_factory
    def transform_data(self, data):

        # Parse fixed-width files
        if self.config[Constant_Config.STEP_CONFIG]["filetype"] == "fixed-width":
            data = self.parse_fixed_width(data)
        # Select & Rename Columns
        keep_cols_dict = {}
        for k, v in self.config[Constant_Config.STEP_CONFIG][
            "input_to_output_cols"
        ].items():
            # Skip metadata columns & columns with no specified output col name
            if (not re.fullmatch(r".*\{.*\}.*", k)) and (v is not None):
                keep_cols_dict[k] = v
        data = data.select(list(keep_cols_dict.keys()))
        for k, v in keep_cols_dict.items():
            data = data.withColumnRenamed(k, v)
        # Add metadata
        data = self.add_metadata(data)

        return data

    @exception_handler
    def load_data(self, output_data):
        if self.config[Constant_Config.STEP_CONFIG]["partition"] is not None:
            output_data.write.option("maxRecordsPerFile", 100000).option(
                "header", "true"
            ).parquet(
                self.config[Constant_Config.STEP_CONFIG]["output_location"],
                mode="append",
                partitionBy=self.config[Constant_Config.STEP_CONFIG]["partition"],
            )
        else:
            output_data.write.mode("overwrite").option("header", "true").parquet(
                self.config[Constant_Config.STEP_CONFIG]["output_location"]
            )
        return None

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
            help="S3 input file location",
        )
        parser.add_argument(
            "--output-location",
            action="store",
            type=str,
            required=True,
            help="S3 output file location",
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
        config[Constant_Config.STEP_CONFIG]["output_location"] = args["output_location"]
        config[Constant_Config.STEP_CONFIG]["metadata"] = {}

        return config

    def parse_fixed_width(self, data_fw):
        """
        Parse fixed width text documents
        Fixed width column lengths and information given in {step}.yaml
        :params input_file_loc: location of input file
        :return data_fw: fixed width text file parsed and transformed into spark df
        """
        for k in self.config[Constant_Config.STEP_CONFIG][
            "input_to_output_cols"
        ].keys():
            # skip metadata columns
            if not re.fullmatch(r".*\{.*\}.*", k):
                assert (
                    self.config[Constant_Config.STEP_CONFIG]["fixed_width_col_lengths"][
                        k
                    ]
                    > 0
                )
        cursor = 1
        assert len(data_fw.columns) == 1
        column_name = data_fw.columns[0]
        for k, v in self.config[Constant_Config.STEP_CONFIG][
            "fixed_width_col_lengths"
        ].items():
            data_fw = data_fw.withColumn(k, data_fw[column_name].substr(cursor, v))
            cursor += v
        data_fw = data_fw.select(
            [
                i
                for i in self.config[Constant_Config.STEP_CONFIG][
                    "fixed_width_col_lengths"
                ].keys()
            ]
        )

        return data_fw

    def add_metadata(self, df):
        """
        Add metadata fields to SSD dataframe according to whether metadata field present in output-loop yaml
        :params df: SSD dataframe created by outputloop
        :params output_loop: yaml config from step yaml file for SSD output loop
        :returns df: SSD dataframe with metadata added
        """
        # Metadata columns: source, job_id, created_at, client
        for k, v in self.config[Constant_Config.STEP_CONFIG][
            "input_to_output_cols"
        ].items():
            if re.fullmatch(r".*\{.*\}.*", k):
                if k == "{SOURCE}":
                    df = df.withColumn(
                        "cad_source_name",
                        F.lit(self.config[Constant_Config.STEP_CONFIG]["input_source"]),
                    )
                if k == "{CLIENT}":
                    df = df.withColumn("cad_client", F.lit(self.config["client"]))
                if k == "{CREATED_AT}":
                    df = df.withColumn("cad_created_at", F.lit(F.current_timestamp()))
                if k == "{JOB_ID}":
                    df = df.withColumn("cad_job_id", F.lit(self.config["job_id"]))
        return df


if __name__ == "__main__":
    text_to_parquet = TextToParquet()
    text_to_parquet.main()
