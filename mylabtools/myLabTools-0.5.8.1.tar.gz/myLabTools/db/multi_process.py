from myLabTools.db.mongodb import  MongoDB
from tqdm import tqdm

class MultiProcess:
    def __init__(self,db_config_params = {
                    "host":'localhost',
                    "port":27017,
                    "db_name":"cnki"
                },
        input_table_name  = "data",
        output_table_name = "data_v2"
    ):

        self.db = MongoDB(**db_config_params)
        self.input_table_name = input_table_name
        self.output_table_name = output_table_name
    def process_row_data(self,row):
        return row

    def process_v1(
        self,
        total_process,
        this_process
        ):
        print("total process",total_process,"this process",this_process)
        for batch_data in tqdm(
            self.db.select_all_batch_v3(
                table_name=self.input_table_name)
                ):
            data = []
            i = 0
            for row in batch_data:
                try:
                    if i % total_process == this_process:
                        new_row = self.process_row_data(row)
                        data.append(new_row)
                    i = i+1
                except :
                    i = i+1
                    continue
            self.db.bulk_insert(data=data,table_name=self.output_table_name)
    def process_v2(
        self,
        total_process,
        this_process,
        row_process_func = lambda row : row
        ):
        print("total process",total_process,"this process",this_process)
        for batch_data in tqdm(
            self.db.select_all_batch_v3(
                table_name=self.input_table_name)
                ):
            data = []
            i = 0

            for row in batch_data:
                try:
                    if i % total_process == this_process:
                        new_row = row_process_func(row)
                        data.append(new_row)
                    i = i+1
                except :
                    i = i+1
                    continue
                
            self.db.bulk_insert(data=data,table_name=self.output_table_name)
    
def mp_main():
    mp = MultiProcess()
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--total_process", help="total process num", type=int)
    parser.add_argument("--this_process", help="this process num", type=int)
    args = parser.parse_args()
    mp.process_v1(args.total_process,args.this_process)
