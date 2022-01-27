


import pandas as pd
from os import walk
from sas7bdat import SAS7BDAT

class SasDbReader:
    """
    Brief: read a sas data base folder and store the data in a structured python dictionary
    """

    def __init__(self, dirpath):
        """
        @param dirpath | String | Directory path where to look for database files, subfolders are also scanned
        """
        self.dirpath = dirpath
        self.all_files = None
        self.res_data = None
        self.run_data_gathering()
        self.prepare_field_map()


    def prepare_field_map(self):
        """
        Brief: build the map "self.all_keys" between fields (example: 'SAENDT_e') and their descriptions (example: 'end date (1st line of treatment) (estimated)')
        The map also contains the list of tables where each field appears
        self.all_keys is accessed through the methods self.search_field and self.search_field_description
        """
        
        all_keys = {}
        for c in self.res_data.keys():
            aux = self.res_data[c]['detail_fields']
            all_keys.update({k: [r.lower(), c] for k,r in aux.items()})
            
        self.__all_keys = all_keys
        


    def search_field_description(self, st_f, location=False, only_location=False):
        """
        Brief: search method for getting the description of a particular field
        @param location      | Boolean | return or not the locations alongside the descriptions
        @param only_location | Boolean | if True, return only the locations (table names)
        """
        if location:
            return {v: r for v,r in self.__all_keys.items() if st_f in r[0]}
        elif only_location:
            return {v: r[1] for v,r in self.__all_keys.items() if st_f in r[0]}
        else:
            return {v: r[0] for v,r in self.__all_keys.items() if st_f in r[0]}

    def search_field(self, st_f, location=False, only_location=False):
        """
        Brief: get the field name from a description
        @param location      | Boolean | return or not the locations alongside the field name
        @param only_location | Boolean | if True, return only the locations (table names)
        """
        if location:
            return {v: r for v,r in self.__all_keys.items() if st_f.lower() in v.lower()}
        elif only_location:
            return {v: r[0] for v,r in self.__all_keys.items() if st_f.lower() in v.lower()}
        else:
            return {v: r[0] for v,r in self.__all_keys.items() if st_f.lower() in v.lower()}

    def __get_list_files__(self, extension=".sas7bdat"):
        """
        get the list of files beneath the dirpath folder
        @param extension | String | file extension filter
        @sets the all_files attribute
        """
        all_files = []
        for (dirpath, dirnames, filenames) in walk(self.dirpath):
            all_files.extend([(dirpath , fname) for fname in filenames])

        if extension:
            all_files = [f for f in all_files if f[-1].endswith(extension)]
        
        self.all_files = all_files
    
    @staticmethod
    def __get_database__(filepath):
        """
        read the sas file located at the filepath
        @param filepath: the file to read
        @returns a pandas DataFrame of the sas table
        """
        res = pd.read_sas(filepath, encoding="unicode_escape")
        
        return res

    @staticmethod
    def __get_details_fields__(filepath):
        """
        read sas file columns details
        @param filepath | String
        """
        with SAS7BDAT(filepath, encoding='utf8') as reader:
            x = reader.header
            rr = x.__repr__()
            rr = rr.split('\n')
            for i, r in enumerate(rr):
                if '-----------' in r:
                    dashed_line_ind = i
                    v = r.split(' ')
                    values = [len(d) for d in v]
                    vx = [sum(values[:j])+j for j in range(len(values))]
                    break
            labels = [e for e in rr[dashed_line_ind-1].split(' ') if e!='']
            rr = rr[i+1:]
            rrx = []
            vx.append(1000)
            for r in rr:
                rx = [r[vx[j]:vx[j+1]].strip() for j in range(len(vx)-1)]
                rrx.append(rx)
            
            columns_map = {v[1]: v[-1] for v in rrx if v[1]!=''}
            detailed_column_characteristics = pd.DataFrame({label: [v[i] for v in rrx] for i, label in enumerate(labels)}).set_index('Num')
            return columns_map, detailed_column_characteristics

            
    def list_all_columns(self, detail_fields=True, all_characteristics=False):
        """

        """
        keys = list(self.res_data.keys())
        for k in keys:
            detail_fields_c = self.res_data[k]['detail_fields_characteristics']
            print('-'*80)
            print("table name: ", k)
            
            if all_characteristics:
                print('columns (all characteristics):')
                print(detail_fields_c)
            elif detail_fields:
                print('columns (detailed):')
                print(list(detail_fields_c['Label']))
            else:
                print('columns (code name):')
                print(list(detail_fields_c['Name']))
        
        

    def run_data_gathering(self):
        """
        scans  dirpath and extracts the sas data bases
        @sets the rest_data attribute of the class
        """
        res_data = {}
        field_map = {}
        field_map_rev = {}
        self.__get_list_files__()

        for file_d in self.all_files:
            filepath = '/'.join(file_d)
            res_aux = self.__get_database__(filepath)
            res_detail_fields, detailed_column_characteristics = self.__get_details_fields__(filepath)
            data_title = file_d[1].rsplit('.',1)[0]
            struct_aux = {
                'relative_path': filepath,
                'detail_fields': res_detail_fields,
                'detail_fields_characteristics': detailed_column_characteristics,
                'data': res_aux
            }
            list_fields = list(res_aux.columns)
            field_map[data_title] = list_fields
            for field in list_fields:
                if field in field_map_rev:
                    field_map_rev[field].append(data_title)
                else:
                    field_map_rev[field] = [data_title]
                
            res_data[data_title] = struct_aux
        self.field_map = field_map
        self.field_map_rev = field_map_rev
        
        self.res_data =  res_data




