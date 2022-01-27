import csv
import os

def createCSV(fileName):
    if os.path.exists(fileName)==False:
        with open(fileName, "w", newline="") as f:
            return True
    else:
        return False

def readFromCSV(fileName):
    listOfRows = []
    with open(fileName, "r", newline="") as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            listOfRows.append(list(row))
        return listOfRows

def readFromCSVWithoutHeader(fileName):
    listOfRows = []
    with open(fileName, "r", newline="") as f:
        csv_reader = csv.reader(f, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print('this is the header: ' + str(row))
                line_count += 1
            else:
                listOfRows.append(list(row))
        return listOfRows

def readFromCSVSelection(fileName,rowN,columnN):
    def printCol(data,columnN):
        for i in range(len(data)):
            data[i] = data[i][0:columnN]
        return data
    listOfRows = []
    with open(fileName, "r", newline="") as f:
        csv_reader = csv.reader(f, delimiter=',')
        line_count = 0
        for row in csv_reader:
            listOfRows.append(list(row))
            line_count += 1
            if line_count == rowN:
                return printCol(listOfRows,columnN)
        return printCol(listOfRows,columnN)

def writeToCSV(fileName,data):
    with open(fileName, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def appendToCSV(fileName,data):
    with open(fileName, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def delCSV(fileName):
    if os.path.exists(fileName)==False:
        return False
    else:
        os.remove(fileName)

def printFromCSV(fileName):
    data = readFromCSV(fileName)
    print(data)
