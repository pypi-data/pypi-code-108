""" This file is to do unit tests for all the functions and classes of Python module.

To execute this, it is recommended to install the requirement file:

pip install -r requirements.txt
"""
import os
import unittest
from typing import List

from mysutils.tmp import removable_files
from tqdm import tqdm

from filedatasource import CsvWriter, CsvReader, ExcelWriter, ExcelReader, Mode, ReadMode, DataWriter, DataReader, \
    open_reader, open_writer, excel2list, excel2dict, csv2dict, csv2objects, objects2csv, dict2csv, list2csv, csv2list, \
    save, load, convert, load_lists, sheets, objects2excel
from filedatasource.builder import equals, save_objs, load_dicts, load_objs, save_dicts, save_lists
from filedatasource.csvfile import open_file
from filedatasource.datafile import DataSourceError

DATA_FILE = 'data.csv'
COMPRESSED_FILE = 'data.csv.gz'
EXCEL_FILE = 'data.xlsx'
XLS_FILE = 'data.xls'


def write_registers(writer) -> None:
    writer.write_row(a=1, b=2, c=3)
    writer.write_row(a=2, b=4, c=7)
    writer.write_row(a=3, b=6, c=15)
    writer.write_dict({'a': 4, 'b': 8, 'c': 31})


class Employee(object):
    @property
    def surname(self) -> str:
        return self.__surname

    @property
    def name(self) -> str:
        return self.__name

    @property
    def full_name(self) -> str:
        return self.name + ' ' + self.surname

    def __init__(self, name: str, surname: str):
        self.__name = name
        self.__surname = surname

    def __eq__(self, other: 'Employee') -> bool:
        return self.name == other.name and self.surname == other.surname


class Example(object):
    def __init__(self, a: int, b: int, c: int):
        self.a, self.b, self.c = a, b, c


lists = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
dicts = [
    {'a': 10, 'b': 11, 'c': 12},
    {'a': 13, 'b': 14, 'c': 15}
]
objects = [
    Example(16, 17, 18),
    Example(19, 20, 21),
    Example(22, 23, 24)
]
employees = [
    Employee('John', 'Smith'),
    Employee('Alice', 'Cooper'),
    Employee('Bob', 'Dylan')
]
employees_dict = [
    {'name': 'John', 'surname': 'Smith', 'full_name': 'John Smith'},
    {'name': 'Alice', 'surname': 'Cooper', 'full_name': 'Alice Cooper'},
    {'name': 'Bob', 'surname': 'Dylan', 'full_name': 'Bob Dylan'}
]
employees_list = [
    ['John', 'Smith', 'John Smith'],
    ['Alice', 'Cooper', 'Alice Cooper'],
    ['Bob', 'Dylan', 'Bob Dylan']
]


class TestWriter(CsvWriter):
    @property
    def fieldnames(self) -> List[str]:
        return ['a', 'b', 'c']


def list_to_int(lists: List[List[str]]) -> List[List[int]]:
    r = []
    for lst in lists:
        r.append([int(x) for x in lst])
    return r


class MyTestCase(unittest.TestCase):
    def test_write_csv_dict(self) -> None:
        with CsvWriter(DATA_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.assertEqual(len(writer), 0)
            write_registers(writer)
            self.assertEqual(len(writer), 4)
        self.assertTrue(os.path.exists(DATA_FILE))
        with CsvReader(DATA_FILE) as reader:
            for obj in tqdm(reader):
                pass
        self.assertEqual(obj.b, '8')
        os.remove(DATA_FILE)

    def test_write_csv_obj(self) -> None:
        with CsvWriter(COMPRESSED_FILE, fieldnames=Employee) as writer:
            writer.write(Employee('John', 'Smith'))
            writer.write(Employee('Maria', 'Ortega'))
        with CsvReader(COMPRESSED_FILE) as reader:
            obj = next(reader)
            self.assertEqual(obj.name, 'John')
            self.assertEqual(obj.surname, 'Smith')
            obj = next(reader)
            self.assertEqual(obj.name, 'Maria')
            self.assertEqual(obj.surname, 'Ortega')
            with self.assertRaises(StopIteration):
                reader.read()
        os.remove(COMPRESSED_FILE)

    def test_write_excel(self) -> None:
        with ExcelWriter(EXCEL_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.assertEqual(len(writer), 0)
            write_registers(writer)
            self.assertEqual(len(writer), 4)
        self.assertTrue(os.path.exists(EXCEL_FILE))
        with ExcelReader(EXCEL_FILE) as reader:
            for obj in tqdm(reader):
                pass
        self.assertEqual(obj.b, 8)
        os.remove(EXCEL_FILE)

    def test_import(self) -> None:
        with CsvWriter(DATA_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.assertEqual(len(writer), 0)
            write_registers(writer)
            self.assertEqual(len(writer), 4)
        self.assertTrue(os.path.exists(DATA_FILE))
        with CsvReader(DATA_FILE) as reader:
            with ExcelWriter(EXCEL_FILE, fieldnames=reader.fieldnames) as writer:
                writer.import_reader(reader)
        self.assertTrue(os.path.exists(EXCEL_FILE))
        os.remove(DATA_FILE)
        os.remove(EXCEL_FILE)
        with ExcelWriter(EXCEL_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.assertEqual(len(writer), 0)
            write_registers(writer)
            self.assertEqual(len(writer), 4)
        self.assertTrue(os.path.exists(EXCEL_FILE))
        with ExcelReader(EXCEL_FILE) as reader:
            with CsvWriter(DATA_FILE, fieldnames=reader.fieldnames) as writer:
                writer.import_reader(reader)
        self.assertTrue(os.path.exists(DATA_FILE))
        os.remove(DATA_FILE)
        os.remove(EXCEL_FILE)

    def test_dict_2_object(self) -> None:
        d = {'1': 1, 'G&S': 2}
        with CsvWriter(DATA_FILE, fieldnames=d) as writer:
            writer.write_dict(d)
            writer.write_list(list(d.values()))
        with CsvReader(DATA_FILE) as reader:
            for obj in reader:
                pass
        self.assertEqual(obj.n1, '1')
        self.assertEqual(obj.G_S, '2')
        os.remove(DATA_FILE)

    def test_lists(self) -> None:
        with CsvWriter(DATA_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.__write_lists_writer(writer)
        with CsvReader(DATA_FILE) as reader:
            self.check_lists_reader(reader)
        with CsvReader(DATA_FILE) as reader:
            self.check_dicts_reader(reader)
        with CsvReader(DATA_FILE) as reader:
            self.check_objects_reader(reader)
        os.remove(DATA_FILE)

    def check_lists_csv(self, lists: List[List[int]]) -> None:
        self.assertEqual(len(lists), 8)
        self.assertListEqual(lists[0], ['1', '2', '3'])
        self.assertListEqual(lists[7], ['22', '23', '24'])

    def check_lists_reader(self, reader: DataReader) -> None:
        lists = reader.read_lists()
        if isinstance(reader, CsvReader):
            self.check_lists_csv(lists)
        else:
            self.check_lists_excel(lists)

    def check_lists_excel(self, lists: List[List[int]]):
        self.assertEqual(len(lists), 8)
        self.assertListEqual(lists[0], [1, 2, 3])
        self.assertListEqual(lists[7], [22, 23, 24])

    def check_dicts_reader(self, reader: DataReader) -> None:
        dicts = reader.read_rows()
        if isinstance(reader, CsvReader):
            self.check_dicts_csv(dicts)
        else:
            self.check_dicts_excel(dicts)

    def check_dicts_csv(self, dicts: List[dict]) -> None:
        self.assertEqual(len(dicts), 8)
        self.assertDictEqual(dicts[0], {'a': '1', 'b': '2', 'c': '3'})
        self.assertDictEqual(dicts[7], {'a': '22', 'b': '23', 'c': '24'})

    def check_dicts_excel(self, dicts: List[dict]) -> None:
        self.assertEqual(len(dicts), 8)
        self.assertDictEqual(dicts[0], {'a': 1, 'b': 2, 'c': 3})
        self.assertDictEqual(dicts[7], {'a': 22, 'b': 23, 'c': 24})

    def check_objects_reader(self, reader: DataReader) -> None:
        objs = reader.read_objects()
        if isinstance(reader, CsvReader):
            self.check_objects_csv(objs)
        else:
            self.check_objects_excel(objs)

    def check_objects_csv(self, objs) -> None:
        self.assertEqual(len(objs), 8)
        self.assertEqual(objs[0].a, '1')
        self.assertEqual(objs[0].b, '2')
        self.assertEqual(objs[0].c, '3')
        self.assertEqual(objs[7].b, '23')
        self.assertEqual(objs[7].c, '24')

    def check_objects_excel(self, objs) -> None:
        self.assertEqual(len(objs), 8)
        self.assertEqual(objs[0].a, 1)
        self.assertEqual(objs[0].b, 2)
        self.assertEqual(objs[0].c, 3)
        self.assertEqual(objs[7].b, 23)
        self.assertEqual(objs[7].c, 24)

    @staticmethod
    def __write_lists_writer(writer: DataWriter) -> None:
        writer.write_lists(lists)
        writer.write_dicts(dicts)
        writer.write_objects(objects)

    def test_read_modes(self) -> None:
        with CsvWriter(DATA_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.__write_lists_writer(writer)
        with CsvReader(DATA_FILE, mode=ReadMode.DICT) as reader:
            for obj in reader:
                pass
        self.assertDictEqual(obj, {'a': '22', 'b': '23', 'c': '24'})
        with CsvReader(DATA_FILE, mode=ReadMode.LIST) as reader:
            for obj in reader:
                pass
        self.assertListEqual(obj, ['22', '23', '24'])
        with CsvReader(DATA_FILE, mode=ReadMode.OBJECT) as reader:
            for obj in reader:
                pass
        self.assertEqual(obj.b, '23')
        self.assertEqual(obj.c, '24')
        os.remove(DATA_FILE)

    def test_append(self) -> None:
        with TestWriter(COMPRESSED_FILE) as writer:
            self.assertEqual(len(writer), 0)
            writer.write_lists(lists)
            self.assertEqual(len(writer), 3)
        with TestWriter(COMPRESSED_FILE, mode=Mode.APPEND) as writer:
            self.assertEqual(len(writer), 3)
            writer.write_dicts(dicts)
            self.assertEqual(len(writer), 5)
        with CsvReader(COMPRESSED_FILE, mode=ReadMode.OBJECT) as reader:
            self.assertListEqual(reader.read_list(), ['1', '2', '3'])
            self.assertEqual(len(reader), 5)
            for obj in reader:
                pass
        self.assertEqual(obj.b, '14')
        self.assertEqual(obj.c, '15')

    def test_xls_xlsx(self) -> None:
        with ExcelWriter(EXCEL_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.__write_lists_writer(writer)
        with ExcelReader(EXCEL_FILE) as reader:
            self.check_lists_reader(reader)
        with ExcelWriter(XLS_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.__write_lists_writer(writer)
        with ExcelReader(XLS_FILE) as reader:
            self.check_lists_reader(reader)
        os.remove(EXCEL_FILE)
        os.remove(XLS_FILE)

    def test_builders(self) -> None:
        with open_writer(EXCEL_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.__write_lists_writer(writer)
        with ExcelReader(EXCEL_FILE) as reader:
            self.check_lists_reader(reader)
        self.check_lists_excel(excel2list(EXCEL_FILE))
        os.remove(EXCEL_FILE)
        with open_writer(XLS_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.assertEqual(len(writer), 0)
            self.__write_lists_writer(writer)
            self.assertEqual(len(writer), 8)
        with ExcelReader(XLS_FILE) as reader:
            self.check_dicts_reader(reader)
        self.check_dicts_excel(excel2dict(XLS_FILE))
        os.remove(XLS_FILE)
        with open_writer(DATA_FILE, fieldnames=['a', 'b', 'c']) as writer:
            self.__write_lists_writer(writer)
        with CsvReader(DATA_FILE) as reader:
            self.check_objects_reader(reader)
        self.check_objects_csv(csv2objects(DATA_FILE))
        os.remove(DATA_FILE)
        list2csv(COMPRESSED_FILE, lists, ['a', 'b', 'c'])
        self.assertListEqual(lists, list_to_int(csv2list(COMPRESSED_FILE)))
        dict2csv(COMPRESSED_FILE, dicts, ['a', 'b', 'c'])
        r = csv2dict(COMPRESSED_FILE)
        self.assertEqual(len(r), 2)
        self.assertDictEqual(r[0], {'a': '10', 'b': '11', 'c': '12'})
        self.assertDictEqual(r[1], {'a': '13', 'b': '14', 'c': '15'})
        objects2csv(COMPRESSED_FILE, objects, ['a', 'b', 'c'])
        with open_reader(COMPRESSED_FILE) as reader:
            obj = next(reader)
            self.assertEqual(obj.c, '18')
            obj = next(reader)
            self.assertEqual(obj.b, '20')
            obj = next(reader)
            self.assertEqual(obj.a, '22')
        with open_reader(COMPRESSED_FILE, mode=ReadMode.DICT) as reader:
            d = next(reader)
            self.assertEqual(d['c'], '18')
            d = next(reader)
            self.assertEqual(d['b'], '20')
            d = next(reader)
            self.assertEqual(d['a'], '22')
        with open_reader(COMPRESSED_FILE, mode=ReadMode.LIST) as reader:
            lst = next(reader)
            self.assertEqual(lst[2], '18')
            lst = next(reader)
            self.assertEqual(lst[1], '20')
            lst = next(reader)
            self.assertEqual(lst[0], '22')
        os.remove(COMPRESSED_FILE)

    def test_more_builders(self) -> None:
        save(EXCEL_FILE, objects)
        with open_reader(EXCEL_FILE) as reader:
            obj = next(reader)
            self.assertEqual(obj.c, 18)
            obj = next(reader)
            self.assertEqual(obj.b, 20)
            obj = next(reader)
            self.assertEqual(obj.a, 22)
        objs = load(EXCEL_FILE)
        self.assertEqual(objs[0].c, 18)
        self.assertEqual(objs[1].b, 20)
        self.assertEqual(objs[2].a, 22)
        dicts = load(EXCEL_FILE, mode=ReadMode.DICT)
        self.assertEqual(dicts[0]['c'], 18)
        self.assertEqual(dicts[1]['b'], 20)
        self.assertEqual(dicts[2]['a'], 22)
        os.remove(EXCEL_FILE)

    def test_sheets(self) -> None:
        with ExcelReader('Example.xls', sheet=0) as reader:
            self.check_clients_sheet(reader)
            self.assertEqual(len(reader), 2)
        with ExcelReader('Example.xls', sheet=1) as reader:
            self.check_suppliers_sheet(reader)
            self.assertEqual(len(reader), 3)
        with ExcelReader('Example.xls', sheet='Clients') as reader:
            self.check_clients_sheet(reader)
            self.assertEqual(len(reader), 2)
        with ExcelReader('Example.xls', sheet='Suppliers') as reader:
            self.check_suppliers_sheet(reader)
            self.assertEqual(len(reader), 3)
        with ExcelReader('Example.xlsx', sheet=0) as reader:
            self.check_clients_sheet(reader)
            self.assertEqual(len(reader), 2)
        with ExcelReader('Example.xlsx', sheet=1) as reader:
            self.check_suppliers_sheet(reader)
            self.assertEqual(len(reader), 3)
        with ExcelReader('Example.xlsx', sheet='Clients') as reader:
            self.check_clients_sheet(reader)
            self.assertEqual(len(reader), 2)
        with ExcelReader('Example.xlsx', sheet='Suppliers') as reader:
            self.check_suppliers_sheet(reader)
            self.assertEqual(len(reader), 3)

    def check_clients_sheet(self, reader: DataReader) -> None:
        row = next(reader)
        self.assertEqual(row.Name, 'John')
        self.assertEqual(row.Surname, 'Smith')
        self.assertEqual(row.Email, 'johnsmith@example.com')
        self.assertEqual(row.Phone, 72123423)
        row = next(reader)
        self.assertEqual(row.Name, 'Maria')
        self.assertEqual(row.Surname, 'Ortega')
        self.assertEqual(row.Email, 'mariaortega@example.com')
        self.assertEqual(row.Phone, 72112234)

    def check_suppliers_sheet(self, reader: DataReader) -> None:
        row = next(reader)
        self.assertEqual(row.Name, 'Bill')
        self.assertEqual(row.Surname, 'Gates')
        self.assertEqual(row.Company, 'Microsoft')
        self.assertEqual(row.Email, 'billgates@microsoft.com')
        self.assertEqual(row.Phone, 787877878)
        self.assertEqual(row.Charge, 'Adviser')
        row = next(reader)
        self.assertEqual(row.Name, 'Jeff')
        self.assertEqual(row.Surname, 'Bezos')
        self.assertEqual(row.Company, 'Amazon')
        self.assertEqual(row.Email, 'jeffbezos@amazon.com')
        self.assertEqual(row.Phone, 799998789)
        self.assertEqual(row.Charge, 'CEO')
        row = next(reader)
        self.assertEqual(row.Name, 'Elon')
        self.assertEqual(row.Surname, 'Musk')
        self.assertEqual(row.Company, 'Tesla')
        self.assertEqual(row.Email, 'elonmask@tesla.com')
        self.assertEqual(row.Phone, 740023028)
        self.assertEqual(row.Charge, 'Engineering')
        with self.assertRaises(StopIteration):
            next(reader)

    def test_strems(self) -> None:
        with open('data.csv', 'wt') as file:
            writer = CsvWriter(file, ['a', 'b', 'c'])
            self.assertEqual(len(writer), 0)
            writer.write_lists(lists)
            self.assertEqual(len(writer), 3)
            writer.write_dicts(dicts)
            self.assertEqual(len(writer), 5)
            writer.write_objects(objects)
            self.assertEqual(len(writer), 8)
        with open('data.csv', 'rt') as file:
            with self.assertRaisesRegex(DataSourceError, 'The length of the data source cannot be computed if it is '
                                                       'defined as a file stream instead of a file path.'):
                len(CsvReader(file))

        with open(DATA_FILE, 'at') as file:
            with self.assertRaisesRegex(ValueError, r'The reader is in mode Mode.WRITE but the file stream is in not '
                                                    r'in write mode \("at"\).'):
                CsvWriter(file, ['a', 'b', 'c'])
        with open_file(DATA_FILE, Mode.WRITE) as file:
            with self.assertRaisesRegex(ValueError, r'The reader is in mode Mode.APPEND but the file stream is in not '
                                                    r'in append mode \("wt"\).'):
                CsvWriter(file, ['a', 'b', 'c'], Mode.APPEND)
        with open_file(DATA_FILE, Mode.APPEND) as file:
            with self.assertRaisesRegex(DataSourceError,
                                        'The length of the data source cannot be computed if it is defined as a file '
                                        'stream, instead of a file path and this writer is opened in APPEND mode.'):
                len(CsvWriter(file, ['a', 'b', 'c'], Mode.APPEND))
        os.remove(DATA_FILE)

    def test_convert(self) -> None:
        write_registers(open_writer(COMPRESSED_FILE, fieldnames=['a', 'b', 'c']))
        convert(COMPRESSED_FILE, XLS_FILE)
        with open_reader(COMPRESSED_FILE, ReadMode.DICT) as reader1:
            with open_reader(XLS_FILE, ReadMode.DICT) as reader2:
                for dict1 in reader1:
                    dict2 = next(reader2)
                    self.assertDictEqual(dict1, dict2)
                self.assertEqual(len(reader1), len(reader2))
        os.remove(COMPRESSED_FILE)

    def test_excel_append(self) -> None:
        with ExcelWriter(XLS_FILE, fieldnames=['a', 'b', 'c']) as writer:
            writer.write_dicts(dicts)
            self.assertEqual(len(writer), 2)
        with ExcelWriter(XLS_FILE, mode=Mode.APPEND) as writer:
            writer.write_lists(lists)
            writer.write_objects(objects)
            self.assertEqual(len(writer), 8)
        with ExcelReader(XLS_FILE) as reader:
            self.assertDictEqual(reader.read_row(), {'a': 10.0, 'b': 11.0, 'c': 12.0})
            self.assertDictEqual(reader.read_row(), {'a': 13.0, 'b': 14.0, 'c': 15.0})
            self.assertListEqual(reader.read_list(), [1, 2, 3])
            self.assertListEqual(reader.read_list(), [4, 5, 6])
            self.assertListEqual(reader.read_list(), [7, 8, 9])
            self.assertListEqual(reader.read_list(), [16, 17, 18])
            self.assertListEqual(reader.read_list(), [19, 20, 21])
            self.assertListEqual(reader.read_list(), [22, 23, 24])
            self.assertEqual(len(reader), 8)
        os.remove(XLS_FILE)
        with ExcelWriter(EXCEL_FILE, fieldnames=['a', 'b', 'c']) as writer:
            writer.write_dicts(dicts)
            self.assertEqual(len(writer), 2)
        with ExcelWriter(EXCEL_FILE, mode=Mode.APPEND) as writer:
            writer.write_lists(lists)
            writer.write_objects(objects)
            self.assertEqual(len(writer), 8)
        with ExcelReader(EXCEL_FILE) as reader:
            self.assertDictEqual(reader.read_row(), {'a': 10.0, 'b': 11.0, 'c': 12.0})
            self.assertDictEqual(reader.read_row(), {'a': 13.0, 'b': 14.0, 'c': 15.0})
            self.assertListEqual(reader.read_list(), [1, 2, 3])
            self.assertListEqual(reader.read_list(), [4, 5, 6])
            self.assertListEqual(reader.read_list(), [7, 8, 9])
            self.assertListEqual(reader.read_list(), [16, 17, 18])
            self.assertListEqual(reader.read_list(), [19, 20, 21])
            self.assertListEqual(reader.read_list(), [22, 23, 24])
            self.assertEqual(len(reader), 8)
        os.remove(EXCEL_FILE)

    def test_odd_actions(self):
        # Checking writing a list is sorter than the field names
        with open_writer(COMPRESSED_FILE, fieldnames=['a', 'b', 'c']) as writer:
            writer.write_list([18324])
        lists = load_lists(COMPRESSED_FILE)
        self.assertEqual(len(lists), 1)
        self.assertListEqual(lists[0], ['18324', '', ''])
        with open_writer(DATA_FILE, fieldnames=['a', 'b', 'c']) as writer:
            writer.write_list([18324])
        lists = load_lists(DATA_FILE)
        self.assertEqual(len(lists), 1)
        self.assertListEqual(lists[0], ['18324', '', ''])
        with open_writer(EXCEL_FILE, fieldnames=['a', 'b', 'c']) as writer:
            writer.write_list([18324])
        lists = load_lists(EXCEL_FILE)
        self.assertEqual(len(lists), 1)
        self.assertListEqual(lists[0], [18324, None, None])
        with open_writer(XLS_FILE, fieldnames=['a', 'b', 'c']) as writer:
            writer.write_list([18324])
        lists = load_lists(XLS_FILE)
        self.assertEqual(len(lists), 1)
        self.assertListEqual(lists[0], [18324, '', ''])
        os.remove(DATA_FILE)
        os.remove(COMPRESSED_FILE)
        os.remove(EXCEL_FILE)
        os.remove(XLS_FILE)

    def test_csv_types(self) -> None:
        with CsvWriter(DATA_FILE, fieldnames=['a', 'b', 'c', 'd']) as writer:
            writer.write(['One', 2, 3.0, True])
        with CsvReader(DATA_FILE, types=[str, int, float, bool]) as reader:
            self.assertListEqual(reader.read_list(), ['One', 2, 3.0, True])
        with CsvReader(DATA_FILE, types={'a': str, 'b': int, 'c': float, 'd': bool}) as reader:
            self.assertListEqual(reader.read_list(), ['One', 2, 3.0, True])
        with CsvReader(DATA_FILE, types=[str, int, float]) as reader:
            self.assertListEqual(reader.read_list(), ['One', 2, 3.0, 'True'])
        l = csv2list(DATA_FILE, types=[str, int, float])
        self.assertListEqual(l[0], ['One', 2, 3.0, 'True'])
        d = csv2dict(DATA_FILE, types=[str, int, float])
        self.assertDictEqual(d[0], {'a': 'One', 'b': 2, 'c': 3.0, 'd': 'True'})
        o = csv2objects(DATA_FILE, types=[str, int, float])
        self.assertEqual(o[0].c, 3.0)
        os.remove(DATA_FILE)

    def test_sheet_names(self) -> None:
        self.assertListEqual(sheets('Example.xls'), ['Clients', 'Suppliers'])
        self.assertListEqual(sheets('Example.xlsx'), ['Clients', 'Suppliers'])

    def test_errors(self) -> None:
        with CsvWriter(DATA_FILE, fieldnames=['a', 'b', 'c', 'd']) as writer:
            writer.write(['One', 2, 3.0, True])
        with CsvReader(DATA_FILE, types=[int, int, float]) as reader:
            with self.assertRaisesRegex(ValueError, r'invalid literal for int\(\) with base 10: \'One\''):
                self.assertListEqual(reader.read_list(), ['One', 2, 3.0, 'True'])
        os.remove(DATA_FILE)

    def test_without_filenames(self) -> None:
        for files in [['object.xlsx', 'dicts.xlsx', 'lists.xlsx'],
                      ['object.xls', 'dicts.xls', 'lists.xls']]:
            with removable_files(*files) as (f1, f2, f3):
                save_objs(f1, employees)
                self.assertListEqual(excel2dict(f1), employees_dict)
                self.assertListEqual(load_dicts(f1), employees_dict)
                self.assertListEqual([Employee(d['name'], d['surname']) for d in employees_dict], load_objs(f1))
                self.assertListEqual(load_lists(f1), [[d['full_name'], d['name'], d['surname']] for d in employees_dict])
                save_dicts(f2, employees_dict)
                self.assertListEqual(load_dicts(f2), employees_dict)
                self.assertListEqual([Employee(d['name'], d['surname']) for d in employees_dict], load_objs(f2))
                self.assertListEqual(load_lists(f2),
                                     [[d['name'], d['surname'], d['full_name']] for d in employees_dict])
                self.assertListEqual(excel2dict(f2), employees_dict)
                save_lists(f3, employees_list, fieldnames=['name', 'surname', 'full_name'])
                self.assertListEqual(excel2dict(f3), employees_dict)
                self.assertListEqual(load_dicts(f3), employees_dict)
                self.assertListEqual([Employee(d['name'], d['surname']) for d in employees_dict], load_objs(f3))
                self.assertListEqual(load_lists(f3), [[d['name'], d['surname'], d['full_name']] for d in employees_dict])

        for files in [['object.csv', 'dicts.csv', 'lists.csv'],
                      ['object.csv.gz', 'dicts.csv.gz', 'lists.csv.gz']]:
            with removable_files(*files) as (f1, f2, f3):
                save_objs(f1, employees)
                self.assertListEqual(csv2dict(f1), employees_dict)
                self.assertListEqual(load_dicts(f1), employees_dict)
                self.assertListEqual([Employee(d['name'], d['surname']) for d in employees_dict], load_objs(f1))
                self.assertListEqual(load_lists(f1), [[d['full_name'], d['name'], d['surname']] for d in employees_dict])
                save_dicts(f2, employees_dict)
                self.assertListEqual(csv2dict(f2), employees_dict)
                self.assertListEqual([Employee(d['name'], d['surname']) for d in employees_dict], load_objs(f2))
                self.assertListEqual(load_lists(f2),
                                     [[d['name'], d['surname'], d['full_name']] for d in employees_dict])
                self.assertListEqual(csv2dict(f2), employees_dict)
                save_lists(f3, employees_list, fieldnames=['name', 'surname', 'full_name'])
                self.assertListEqual(csv2dict(f3), employees_dict)
                self.assertListEqual(load_dicts(f3), employees_dict)
                self.assertListEqual([Employee(d['name'], d['surname']) for d in employees_dict], load_objs(f3))
                self.assertListEqual(load_lists(f3), [[d['name'], d['surname'], d['full_name']] for d in employees_dict])

    def test_equals(self) -> None:
        with removable_files('test1.xlsx', 'test2.xlsx', 'test1.xls',
                             'test1.csv', 'test1.csv.gz') as (f1, f2, f3, f4, f5):
            save_objs(f1, employees)
            save_objs(f2, employees)
            self.assertTrue(equals(f1, f2))
            save_objs(f2, objects)
            self.assertFalse(equals(f1, f2))
            save_objs(f3, employees)
            self.assertTrue(equals(f1, f3))
            save_objs(f3, objects)
            self.assertFalse(equals(f1, f3))
            save_objs(f4, employees)
            self.assertTrue(equals(f1, f4))
            save_objs(f4, objects)
            self.assertFalse(equals(f1, f4))
            save_objs(f5, employees)
            self.assertTrue(equals(f1, f5))
            save_objs(f5, objects)
            self.assertFalse(equals(f1, f5))
        # objects2excel('test_without_filenames.xlsx', objects)
        # os.remove('test_without_filenames.xlsx')


if __name__ == '__main__':
    unittest.main()
