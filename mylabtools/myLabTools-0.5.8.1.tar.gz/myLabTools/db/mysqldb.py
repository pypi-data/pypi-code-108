import pymysql

class MysqlDB:
    def __init__(self, db_name , host = "localhost" , port = 3306,user = "root",pwd = "root",charset="utf8mb4",batch_size = 100000):
        self.db = pymysql.connect(host,user,pwd, db_name,port = port ,charset="utf8mb4")
        self.cursor = self.db.cursor()
        self.batch_size = batch_size
    def bulk_insert(self,data,sql_str,table_name):
        for i in range(0,len(data),self.batch_size):
            temp = data[i:i+self.batch_size]
            # import pdb; pdb.set_trace()

            self.cursor.executemany(sql_str,temp)
            print("insert {} {} records success".format(table_name,len(temp)))
            self.db.commit()
    def select_from_db(self,sql_str):
        self.cursor.execute(sql_str)
        results = list(self.cursor.fetchall())
        return  results
        
    def select_all(self,sql_str):
        self.cursor.execute(sql_str)
        for row in self.cursor.fetchall():
            yield row
    def select_all_batch(self,batch_size,total_num,sql_str):
        for i in range(0,total_num,batch_size):
            self.cursor.execute(sql_str.format(str(int(i)), str(int(batch_size))))
            results = list(self.cursor.fetchall())
            yield results

    def select_all_batch_v2(self,table_name,batch_size = 1000,field_names_list = ['*'], where_condition = None):
        '''
        对数据表中的数据按照batch_size 进行遍历
        '''
        total_num = 0
        sql_str_1 = "select count(*) from {} ".format(table_name)
        if where_condition:
            sql_str_1 = sql_str_1 +  " where " + where_condition
        total_num = self.select_from_db(sql_str_1)
        total_num = total_num[0][0]
        print("%s total num is %d" % (sql_str_1,total_num))


        if field_names_list == ["*"]:
            sql_str_2 = "select * from {}".format(table_name)
        else:
            sql_str_2 = "select `{}` from {} ".format("`  , `".join(field_names_list),table_name)

        
        if where_condition:
            sql_str_2 = sql_str_2 + " where " + where_condition
        sql_str_2 = sql_str_2 + " limit {} , {}"

        for i in range(0,total_num,batch_size):
            self.cursor.execute(sql_str_2.format(str(int(i)), str(int(batch_size))))
            results = list(self.cursor.fetchall())
            yield results

    def get_table_all_fields(self,table_name):
        sql = "show full columns from {}".format(table_name)
        f = []
        for row in self.select_from_db(sql_str=sql):
            f.append(row[0])
        return f