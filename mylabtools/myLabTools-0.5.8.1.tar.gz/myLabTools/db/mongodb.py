import pymongo
import bson
import json

class MongoDB:
    def __init__(self,host = "127.0.0.1",port = 27017,
                                db_name = "cnki",
                                username = "",pwd = "",
                                batch_size = 10000):
        
        self.client = pymongo.MongoClient(host=host, port=port)
        if len(username) > 0:
            admin = self.client["admin"]
            admin.authenticate(username, pwd)

        self.db = self.client[db_name]
        self.batch_size = batch_size
        self.db_name = db_name
        print("MongoDB : connect to {} success !!".format(host))

    def get_records_num(self,table_name,query = "all"):
        table = self.get_table(table_name=table_name)
        if query == "all":
            return table.find().count()
        else:
            return table.find(query).count()
        
  
    def search_table(self,table_name,query = "all",batch_size = None):
        records_num = self.get_records_num(table_name,query)
        print("select {} from {} result num is {}".format(str(query),table_name,str(records_num)))

        table = self.get_table(table_name=table_name)
        if batch_size is None:
            batch_size = self.batch_size
        
        for page_i in range((records_num // batch_size ) + 1):
            print("selet page {}".format(page_i))
            skip = page_i * batch_size
            if query =="all":
                yield table.find().limit(batch_size).skip(skip=skip)
            else:
                yield table.find(query).limit(batch_size).skip(skip=skip)
    def find_batch(self,table_name,query = None):
        table = self.get_table(table_name=table_name)
        if query is None:
            for batch_data in table.find_raw_batches():
                data = bson.decode_all(batch_data)
                yield data
        else:
            for batch_data in table.find_raw_batches(query):
                data = bson.decode_all(batch_data)
                yield data

    def get_table(self,table_name):
        table = self.db[table_name]
        return table
    
    def query(self,table_name,query = {},field_names_list = ['*']):
        table = self.get_table(table_name=table_name)
        fields = {}
        for f in field_names_list:
            fields[f] = 1
        fields["_id"] = 0
        return table.find(query,fields)

    def bulk_insert(self,data,table_name):
        table = self.get_table(table_name=table_name)
        if len(data) > 0:
            for i in range(0, len(data), self.batch_size):
                temp = data[i:i + self.batch_size]
                table.insert_many(temp)
                print("MongoDb : insert {} to {}-{} success".format(len(temp),self.db_name,table_name))
        else:
            print("MongoDb : empty data!!")
    def select_all_batch_v2(self,table_name,field_names_list = ['*'], query = {}):
        '''
        对数据表中的数据按照batch_size 进行遍历
        '''
        fields = {}
        for f in field_names_list:
            fields[f] = 1
        fields["_id"] = 0

        table = self.db[table_name]
        for batch_data in table.find_raw_batches(query,fields):
            data = bson.decode_all(batch_data)
            yield data
    def select_all_batch_v3(self,table_name, query = {}):
        '''
        对数据表中的数据按照batch_size 进行遍历
        '''
        table = self.db[table_name]
        for batch_data in table.find_raw_batches(query):
            data = bson.decode_all(batch_data)
            yield data
    
    def select_iter(self,table_name,field_names_list = ['*'], query = {}):
        '''
        对数据表中的数据按照batch_size 进行遍历
        '''
        fields = {}
        for f in field_names_list:
            fields[f] = 1
        fields["_id"] = 0

        table = self.db[table_name]
        for row in table.find(query,fields):
            temp_row = []
            for f in field_names_list:
                temp_row.append(row[f])
            yield temp_row
    def get_sample_data(self,table_name,first_k = 5,
        output_file = False
        ):
        table = self.db[table_name]
        return_data = []
        fields = []
        for batch_data in table.find_raw_batches({}):
            data = bson.decode_all(batch_data)
            for row in data[:3]:
                del row["_id"]
                fields = list(row.keys())
                return_data.append(row)
            break
        if output_file:
            json.dump(
                return_data,
                open("./"+table_name + "-demo-first-" + str(first_k) + ".json",
                "w+",
                encoding="utf-8"),
                indent=4,
                ensure_ascii=False
                )
        return fields

if __name__ == "__main__":
    cnki_data_db = MongoDB(db_name="cnki")
