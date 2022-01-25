import xlwings as xw

def paste_data_and_get_range(source_path, source_sheet_name, source_range,
        dest_path, dest_sheet_name, dest_range=None, 
        results_sheet=None, results_range=None):

    if dest_range==None:
        dest_range = source_range

    source_wb = xw.Book(source_path)
    dest_wb = xw.Book(dest_path)

    source_sheet = source_wb.sheets[source_sheet_name]
    dest_sheet = dest_wb.sheets[dest_sheet_name]

    my_values = source_sheet.range(source_range).options(ndim=2).value 
    dest_sheet.range(dest_range).value = my_values

    dest_wb.save()
    dest_wb.app.quit()

    if results_sheet !=None:
        return dest_wb.sheets[results_sheet].range(results_range).options(ndim=2).value 


