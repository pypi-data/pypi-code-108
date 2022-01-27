import os
import pandas as pd

class Unificator :
    class bcolors :
        FAIL = '\033[1;91m'
        WARNING = '\033[1;93m'
        SUCCESS = '\033[1;32m'
        ENDC = '\033[1;37m'

    def __init__(self, print_df = True):
        self.print_df = print_df
        self.ROOTDIR = "../"
        self.paths = []
        self.semicolon_csvs = []
        self.coma_csvs = []
        self.comparisson = []
        self.comparisson_type = []
        self.sorting()
        self.updating_csvs(self.paths)

    def sorting(self):
        for subdir, dirs, files in os.walk(self.ROOTDIR):
            for file in files :
                path = os.path.join(subdir,file)
                if path[-4:]==".csv":
                    csv = open(path, "r")
                    last_line =csv.readlines()[-1]
                    try :
                        second_to_last_line = csv.readlines()[-2]
                    except :
                        second_to_last_line = ''
                    if ";" in last_line :
                        self.semicolon_csvs.append(path)
                        self.paths.append(path)

                    else :
                        # is it a one column Data frame with "," as decimal seperator
                        number_of_commas = last_line.count(",")
                        if number_of_commas > 1 or number_of_commas == 0 :
                            self.coma_csvs.append(path)
                            self.paths.append(path)

                        else:
                            self.semicolon_csvs.append(path)
                            self.paths.append(path)

    def updating_csvs(self,paths):
        for i in range(len(paths)):
            path = self.paths[i]
            name = path.rsplit("\\")[-1]
            if path in self.coma_csvs :
                print("\n {} : separator = \",\" only needs to update the headers \n".format(name))
                original = pd.read_csv(path,sep=",",engine="python")
                original.fillna("", inplace=True)
                if self.print_df:
                    print("The original dataframe : \n", original.head())
                original.columns = self.update_headers(original)
                if self.print_df:
                    print("The updated dataframe : \n",original.head())
                print(f"{self.bcolors.SUCCESS}Successfully updated " + name + f"{self.bcolors.ENDC}")
                original.to_csv(path, index=False)
            if path in self.semicolon_csvs :
                print("\n {} : separator = \";\" \n".format(name))
                check  = pd.read_csv(path,sep=';',engine="python")
                counter = 0
                sci_notation = 0
                for col in check.columns :
                    for x in check[col] :
                        if isinstance(x,str):
                            if ',' in x :
                                counter+=1
                            if 'e' in x :
                                sci_notation+=1

                        else :
                            pass
                print(counter)
                print(sci_notation)
                if counter >= 1 :
                    print('the decimal separator = \',\'')
                    original = pd.read_csv(path,sep=';',decimal=',',engine="python")
                    original.fillna("", inplace=True)
                    if self.print_df:
                        print("The updated dataframe : \n",original.head())
                    original.columns = self.update_headers(original)
                    updated = original.copy()
                    if sci_notation >= 1:
                        self.update_entries(updated)
                    if sci_notation == 0 :
                        pass
                    if self.print_df :
                        print("The updated dataframe : \n",updated.head())
                    self.compare(original_df=original,updated_df=updated, name=name)
                    # updated.to_csv(r'C:\Users\Lenovo\Desktop\simses save\Nouveau dossier/' + name, index=False)
                    updated.to_csv(path, index=False)

                if counter ==0 :
                    print('the decimal separator = \'.\'')
                    original = pd.read_csv(path,sep=';',decimal='.',engine="python",encoding="utf-8-sig")
                    original.fillna("", inplace=True)
                    if self.print_df:
                        print("The updated dataframe : \n",original.head())
                    original.columns = self.update_headers(original)
                    updated = original.copy()
                    self.update_entries(updated)
                    if self.print_df :
                        print("The updated dataframe : \n",updated.head())
                    self.compare(original_df=original,updated_df=updated, name=name)
                    updated.to_csv(path, index=False)




    def update_headers(self,df):
        header = []
        for col in df.columns :
            if "Unnamed:" in col :
                    header.append("")
            else :
                try :
                    header.append(col.replace(",","."))
                    if ";" in header[-1]:
                        header[-1] = header[-1].replace(";",",")
                    #stopping the mangle_dupe_cols,
                    #aka the automatic renaming of pandas of columns with the same name
                    if header[-1]==header[-2]+".1":
                        header[-1]=header[-2]
                except :
                    pass
        return header

    def update_entries(self, df):
        for col in df:
            try:
                df[col] = [x.replace(',', '.') for x in df[col]]
            except:
                pass

    def compare(self, original_df, updated_df,name):
        elements_original=[]
        elements_updated=[]
        original_types = original_df.copy()
        updated_types = updated_df.copy()

        for col in original_types.columns:
            original_types[col] = [type(x) for x in original_types[col]]
        for col in updated_types.columns:
            updated_types[col] = [type(x) for x in updated_types[col]]

        for col in original_df.columns:
            for x in original_df[col]:
                try :
                    elements_original.append(x.replace(",","."))
                except :
                    elements_original.append(x)

        for col in updated_df.columns:
            for x in updated_df[col]:
                elements_updated.append(x)

        if elements_original==elements_updated and original_types.equals(updated_types):
            print(f"{self.bcolors.SUCCESS}Successfully updated " + name + f"{self.bcolors.ENDC}")
        else:
            print(f"{self.bcolors.FAIL}Failed updating " + name + f"{self.bcolors.ENDC}")
            print(original_df.compare(updated_df))
            print(original_types.compare(updated_types))


instance = Unificator(print_df = False)