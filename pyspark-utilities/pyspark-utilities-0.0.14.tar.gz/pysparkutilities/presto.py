from .datastorage import DataStorage


class Presto(DataStorage):

    # Initialize Presto Python Driver

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

        if "prestoPassword-input-dataset" in self.args and self.args["prestoPassword-input-dataset"] not in ['', "", "''"]:

            if read_all:
                df = spark.read.format("jdbc").option("driver", "com.facebook.presto.jdbc.PrestoDriver"). \
                    option("url", "jdbc:presto://"+self.args["prestoHost-input-dataset"]+":"+self.args["prestoPort-input-dataset"]+"/"+self.args["prestoDb-input-dataset"]).option("dbtable", "(SELECT * FROM " + input_dataset + ")"). \
                    option("user", self.args["prestoUser-input-dataset"]). \
                    option('password', self.args["prestoPassword-input-dataset"]).load()
            else:
                df = spark.read.format("jdbc").option("driver", "com.facebook.presto.jdbc.PrestoDriver"). \
                    option("url", "jdbc:presto://"+self.args["prestoHost-input-dataset"]+":"+self.args["prestoPort-input-dataset"]+"/"+self.args["prestoDb-input-dataset"]).option("dbtable", "(SELECT " + input_columns + " FROM " + input_dataset + ")"). \
                    option("user", self.args["prestoUser-input-dataset"]). \
                    option('password', self.args["prestoPassword-input-dataset"]).load()

        else:
            if read_all:
                df = spark.read.format("jdbc").option("driver", "com.facebook.presto.jdbc.PrestoDriver"). \
                    option("url", "jdbc:presto://"+self.args["prestoHost-input-dataset"]+":"+self.args["prestoPort-input-dataset"]+"/"+self.args["prestoDb-input-dataset"]).option("dbtable", "(SELECT * FROM " + input_dataset + ")"). \
                    option("user", self.args["prestoUser-input-dataset"]).load()
            else:
                df = spark.read.format("jdbc").option("driver", "com.facebook.presto.jdbc.PrestoDriver"). \
                    option("url", "jdbc:presto://"+self.args["prestoHost-input-dataset"]+":"+self.args["prestoPort-input-dataset"]+"/"+self.args["prestoDb-input-dataset"]).option("dbtable", "(SELECT " + input_columns + " FROM " + input_dataset + ")"). \
                    option("user", self.args["prestoUser-input-dataset"]).load()

        # rename column
        for column in input_columns.split(","):
            df = df.withColumnRenamed(column.lower(), column)
        return df

    # overriding abstract method
    def save_dataset(self, df, output_dest):
        pass
