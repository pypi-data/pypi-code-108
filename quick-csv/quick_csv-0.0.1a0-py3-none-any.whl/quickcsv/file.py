import csv

def qc_read(csv_path,fields=None,func_row=None,func_row_field=None):
    if fields==None:
        return quick_read_csv_model(csv_path,func_row=func_row)
    else:
        return quick_read_csv(csv_path,fields,func_row=func_row,func_row_field=func_row_field)

def qc_write(save_path,list_rows=None,encoding='utf-8'):
    return quick_save_csv(save_path=save_path,list_rows=list_rows,encoding=encoding)

def qc_twrite(file_path,str,encoding='utf-8',mode='w'):
    f_out=open(file_path,mode,encoding=encoding)
    f_out.write(str)
    f_out.close()

def qc_tread(file_path,encoding='utf-8',mode='r'):
    f_in=open(file_path,mode,encoding=encoding)
    result=f_in.read()
    return result

def quick_read_csv(csv_path,fields,func_row=None,func_row_field=None):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        list_result=[]
        for row in reader:
            l=[]
            if func_row!=None:
                func_row(row)
            for f in fields:
                if func_row_field!=None:
                    func_row_field(f,row[f])
                l.append(row[f])
            list_result.append(l)
        return list_result

def quick_read_csv_model(csv_path,encoding='utf-8',func_row=None):
    with open(csv_path, newline='',encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        list_result=[]
        for row in reader:
            if func_row!=None:
                func_row(row)
            list_result.append(row)
        return list_result

def quick_save_csv(save_path,field_names=None,list_rows=None,encoding='utf-8',mode='w'):
    if field_names==None:
        field_names=[]
        if len(list_rows)==0:
            raise Exception("To infer the field names of data, please ensure the list is NOT empty.")
        model=list_rows[0]
        for k in model.keys():
            field_names.append(k)
    print(field_names)
    with open(save_path, mode, newline='',encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        if list_rows!=None:
            for row in list_rows:
                dict_model = {}
                for f in field_names:
                    dict_model[f]=row[f]
                writer.writerow(dict_model)

def quick_remove_unicode(str,encoding='gbk',decoding='gbk'):
    string_encode = str.encode(encoding, "ignore")
    string_decode = string_encode.decode(decoding)
    return string_decode