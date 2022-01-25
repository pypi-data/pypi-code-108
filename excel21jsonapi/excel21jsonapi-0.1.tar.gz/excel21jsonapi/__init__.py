import xlrd
#excel21jsonapi.create(r"C:\Users\Ritesh Singh\OneDrive\Documents\Projects\Data science for business\excel21jsonapi\excel21jsonapi\example\sample.xls")
def create(file_path):
    try:
        wb = xlrd.open_workbook(file_path)
        sheet=wb.sheet_by_index(0)
    except Exception:
        print(Exception)
        return "Error: Cannot read the excel."
    response = []
    for i in range(1,sheet.nrows):
        value = {}
        for j in range(0,sheet.ncols):
            print("i is {} j i{}".format(i,j))
            temp = {}
            try:
                data = str(sheet.celll_value(i,j))
                temp[sheet.cell_value(0,j)]=data
                value.update(temp)
            except Exception:
                pass
        response.append(value)
    return response
