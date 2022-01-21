from .datastorage import DataStorage


class Mongo(DataStorage):

    def __init__(self, args):
        super().__init__(args)
        user = self.args['mongoUser']
        password = self.args['mongoPassword']
        ip = self.args['mongoUri'].split(":")[0] 
        port = self.args['mongoUri'].split(":")[1] 
        self.uri = "mongodb://" + user + ":" + password + "@" + ip + ":" + port + "/"


    # overriding abstract method
    def load_dataset(self, spark, read_all=True, input_dest=None, header=True):

        if input_dest is None:
            input_dest = self.args["input-dataset"]
   
        db = input_dest.split["."][0]
        collection = input_dest.split["."][1]

        df = spark.read.format("com.mongodb.spark.sql.DefaultSource")\
            .option("uri", self.uri).option("database", db).option("collection", collection)\
            .load()
        return df


    # overriding abstract method
    def save_dataset(self, df, output_dest=None):

        if output_dest is None:
            output_dest = self.args["output-dataset"]
       
        db = output_dest.split["."][0]
        collection = output_dest.split["."][1]

        df.write.format("com.mongodb.spark.sql.DefaultSource").mode("append")\
            .option("uri", self.uri).option("database", db).option("collection", collection)\
            .save()
