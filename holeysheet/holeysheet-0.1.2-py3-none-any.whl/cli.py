import yaml

from holeysheet.excel import ExcelParser, PylightExcelReader
from holeysheet.schema import Config

if __name__ == "__main__":
    with open("config.yaml") as f:
        config = Config(**yaml.load(f, Loader=yaml.FullLoader))
        parser = ExcelParser(PylightExcelReader("MTC 2020 .xlsx"), config=config)
        for row in parser.parse():
            print(row)
