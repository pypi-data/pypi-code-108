from streng.phd.building_models.model2d_older.etabs_input import EtabsModel2d

model = EtabsModel2d(input_excel_filename=r'4orofo.xlsm')
model.etabs_filename = 'testfile.e2k'

model.etabs_write_file()

print(model.show_tabulate_input('beam_loads'))
print(model.show_tabulate_input('node_loads'))


