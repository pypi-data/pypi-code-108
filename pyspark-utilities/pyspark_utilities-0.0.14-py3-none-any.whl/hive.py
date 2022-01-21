from .datastorage import DataStorage

import os


class Hive(DataStorage):

    # overriding abstract method
    def load_dataset(self, spark, read_all=True, input_dest='', header=True):

        input_columns = self.args["input-columns"] if "input-columns" in self.args else "*"

        if input_dest == '':
            input_dataset = self.args["input-dataset"]
        else:
            input_dataset = input_dest

        # To manage supervised algorithms
        if "labelCol" in self.args:
            label_col = self.args["labelCol"]
            columns_list = input_columns.split(",")
            if label_col not in columns_list:
                columns_list.append(label_col)
            input_columns = ','.join(columns_list)

        if read_all:
            df = spark.sql("SELECT * FROM " + input_dataset)
        else:
            df = spark.sql("SELECT " + input_columns + " FROM " + input_dataset)

        # rename column
        for column in input_columns.split(","):
            df = df.withColumnRenamed(column.lower(), column)
        return df

    # overriding abstract method
    def save_dataset(self, df, output_dest):

        if output_dest == '':
            output_dataset = self.args["output-dataset"]
        else:
            output_dataset = output_dest

        os.environ["HADOOP_USER_NAME"] = self.args["hiveHadoopUserName-output-dataset"]

        df.write.mode("overwrite").saveAsTable(output_dataset)
