#!/bin/python
# -*- coding: utf-8 -*-

############################
# SparkSqlDumpLoader class #
############################
# Class for loading SQL dump files as Spark dataframes
class SparkSqlDumpLoader:

    spark = None
    sc = None
    dbType = None

    dbTypes = {
        "mysql": {
            "schemaStart": "CREATE TABLE",
            "schemaEnd": "ENGINE=",
            "schemaBadTerms": ["CREATE", "KEY", "ENGINE"],
            "schemaTypesMapping": [
                ["integer", "IntegerType"],
                ["int", "IntegerType"],
                ["date", "TimestampType"],
                ["varchar", "StringType"]
            ],
            "dataStart": "INSERT INTO"
        }
    }

    # Constructor
    def __init__(self, spark):
        self.spark = spark
        self.sc = self.spark.sparkContext

    # Load a SQL dump file into a Spark dataframe
    def load(self, sqlDump, dbType="mysql", delimiter=',',
                      setColNames=True, setColTypes=True,
                      inferSchema=False, mergeSchema=False, repartition=32):
        def cleanLine(line):
            line = line.strip()
            line = line[line.find('(')+1: -1]
            if (line.endswith(';')): line = line[0: -1]
            if (line.endswith(')')): line = line[0: -1]
            return line
        def splitRows(line):
            rows = line.split("),(")
            return rows
        def cleanRow(row):
            colDelimiter = ','
            cols = row.split(colDelimiter)
            for i, col in enumerate(cols):
                scol = col.strip()
                if (scol.startswith("'") and scol.endswith("'")): cols[i] = scol[1:-2]
                elif (scol.startswith('"') and scol.endswith('"')): cols[i] = scol[1:-2]
            row = colDelimiter.join(cols)
            return row
        schema = self.getUniqueSchema(sqlDump=sqlDump, dbType=dbType)
        df = None
        if (schema != None):
            dataStart = self._getDataStart(dbType)
            rdd = self.sc.textFile(sqlDump).repartition(repartition)\
                         .filter(lambda line: dataStart in line[0: 20].replace(' ', ''))\
                         .map(lambda line: cleanLine(line))\
                         .flatMap(lambda line: splitRows(line))\
                         .map(lambda row: cleanRow(row))
            if (not rdd.isEmpty()):
                if (inferSchema): inferSchema = "true"
                else: inferSchema = "false"
                if (mergeSchema): mergeSchema = "true"
                else: mergeSchema = "false"
                df = self.spark.read\
                               .option("header", "false")\
                               .option("delimiter", delimiter)\
                               .option("inferSchema", inferSchema)\
                               .option("mergeSchema", mergeSchema)\
                               .csv(rdd)
                # Rename the columns
                if (setColNames):
                    for i, col in enumerate(df.columns): df = df.withColumnRenamed(col, schema[i][0])
                # Cast the columns
                if (setColTypes):
                    from pyspark.sql import types as T
                    for i, col in enumerate(df.columns):
                        cast = "df.withColumn(col, df[col].cast(T." + schema[i][1] + "()))"
                        df = eval(cast)
        return df

    # Get the schema from the SQL dump file
    def getUniqueSchema(self, sqlDump, dbType="mysql"):
        def isKeyExistInList(lines, key):
            for line in lines:
                if (key in line.replace(' ', '')): return True
            return False
        def getStartEnd(lines, schemaStart, schemaEnd):
            start = -1 ; end = -1
            for i, line in enumerate(lines):
                if (schemaStart in line.replace(' ', '')): start = i
                if (schemaEnd in line.replace(' ', '')): end = i
            if (end < start):
                start = -1 ; end = -1
            return start, end
        def containsBadTerm(line, badTerms):
            itContains = False
            for badTerm in badTerms:
                if (line.strip().lower().startswith(badTerm.lower())):
                    itContains = True
                    break
            return itContains
        schema = None
        if (self.dbTypes.get(dbType) != None):
            if (self.findNumberOfSchemas(sqlDump=sqlDump, dbType=dbType) == 1):
                schemaStart = self._getSchemaStart(dbType)
                schemaEnd = self._getSchemaEnd(dbType)
                cpt = 2
                lines = self.sc.textFile(sqlDump).take(cpt)
                while(not isKeyExistInList(lines, schemaEnd)):
                    cpt += 10
                    lines = self.sc.textFile(sqlDump).take(cpt)
                start, end = getStartEnd(lines, schemaStart, schemaEnd)
                lines = lines[start: end+1]
                schema = []
                schemaBadTerms = self.dbTypes.get(dbType).get("schemaBadTerms")
                for line in lines:
                    if (containsBadTerm(line, schemaBadTerms)): pass
                    else:
                        line = line.replace('`', '').replace('(', ' ').strip().split(' ', 2)
                        line[1] = line[1].lower()
                        for typeMapping in self.dbTypes.get(dbType).get("schemaTypesMapping"):
                            if (line[1] == typeMapping[0]):
                                line[1] = line[1].replace(typeMapping[0], typeMapping[1])
                                break
                        schema.append(line[0: 2])
        else:
            raise(Exception("Database type '" + dbType + "' doesn't exists !"))
        return schema

    # Find the number of schemas from the SQL dump file (necessary for "CREATE TABLE")
    def findNumberOfSchemas(self, sqlDump, dbType="mysql"):
        nbrSchemas = 0
        if (self.dbTypes.get(dbType) != None):
            def beginsWith(line, key):
                itBegins = False
                if (len(line) > 3*len(key)): line = line[0: 3*len(key)]
                line = line.replace('`', '').replace('(', ' ').replace(')', ' ').replace(' ', '').lower()
                key = key.replace('`', '').replace('(', ' ').replace(')', ' ').replace(' ', '').lower()
                if (line.startswith(key)): itBegins = True
                return itBegins
            schemaStart = self._getSchemaStart(dbType)
            schemaEnd = self._getSchemaEnd(dbType)
            countCreate = self.sc.textFile(sqlDump).filter(lambda line: beginsWith(line, schemaStart)).count()
            countEngine = self.sc.textFile(sqlDump).filter(lambda line: beginsWith(line, schemaEnd)).count()
            if (countCreate > 0):
                if (countCreate == countEngine): nbrSchemas = countCreate
                else: nbrSchemas = -1
        else:
            raise(Exception("Database type '" + dbType + "' doesn't exists !"))
        return nbrSchemas

    # =========================================
    # =            Private methods            =
    # =========================================

    # Get the position where the schema starts into the SQL dump file
    def _getSchemaStart(self, dbType="mysql"):
        schemaStart = self.dbTypes.get(dbType).get("schemaStart").replace(' ', '')
        return schemaStart

    # Get the position where the schema ends into the SQL dump file
    def _getSchemaEnd(self, dbType="mysql"):
        schemaEnd = self.dbTypes.get(dbType).get("schemaEnd").replace(' ', '')
        return schemaEnd

    # Get the position where the data starts into the SQL dump file
    def _getDataStart(self, dbType="mysql"):
        dataStart = self.dbTypes.get(dbType).get("dataStart").replace(' ', '')
        return dataStart
