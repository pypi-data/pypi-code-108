# Helper class for TSV senders and receivers
import csv
from os.path import exists
from os import linesep

class TSV:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        if not exists(file):
            new = open(file, 'w')
            new.close()
        
        with open(file, 'r') as f:
            data = csv.reader(f, delimiter='\t')
            data = [line for line in data]
            self.columnNames = data[0]
            self.rows = data[1:]

            return self
    
    def __exit__(self, type, value, traceback):
        with open(file, 'w') as f:
            f.write('\t'.join(self.columnNames))
            f.write(linesep)
            for row in self.rows:
                f.write('\t'.join(row))
                f.write(linesep)

    def rowDict(row):
        '''Return the given row as a dictionary of columnName => rowColumnValue'''
        dict = {}
        for idx, value in enumerate(row):
            dict[self.columnNames[idx]] = value
        return dict

    def rowWithColumn(columnName, rowColumnValue):
        '''Return the row whose column named columnName has value rowColumnValue according to == comparison'''
        for row in self.rows:
            rowDict = rowDict(row)
            if columnName in rowDict and rowDict[columnName] == rowColumnValue:
                return row

        raise f"No row in {self.file} has {rowColumnValue} in column {columnName}"

    
