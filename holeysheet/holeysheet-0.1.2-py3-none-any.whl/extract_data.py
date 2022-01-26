import yaml

from holeysheet.excel import ExcelParser, PylightExcelReader
from holeysheet.schema import Config


def extract_to_list(schema, file):
    config = Config(**schema)
    parser = ExcelParser(PylightExcelReader(file), config=config)
    data = []
    for row in parser.parse():
        data.append(row)
    return data
