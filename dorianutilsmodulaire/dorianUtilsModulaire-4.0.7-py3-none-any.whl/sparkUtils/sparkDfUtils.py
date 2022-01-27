#!/bin/python
# -*- coding: utf-8 -*-

######################
# SparkDfUtils class #
######################
# Spark Dataframe utility
class SparkDfUtils:

    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    from pyspark.sql import Row
    from pyspark.sql.window import Window as W
    from pyspark import StorageLevel
    import json
    from . import sparkSqlDumpLoader

    sc = None
    spark = None
    fu = None # FileUtil (for HDFS and local FS)
    sfu = None # SparkFsUtils (for HDFS and local FS)
    ssql = None

    # Constructor
    def __init__(self, spark):
        self.spark = spark
        self.sc = self.spark.sparkContext
        FileUtil = self.sc._gateway.jvm.org.apache.hadoop.fs.FileUtil
        fu = FileUtil()
        self.fu = fu
        self.sfu = SparkFsUtils(self.sc)

    '''
    Show a dataframe or a dataset

    #########
    # USAGE #
    #########
    - Shows the ten first rows of the Spark dataframe or dataset:
    show(df)
    show(df, 10)
    show(df, count=10)

    - Shows a random sample which represents 15% of a Spark dataframe:
    show(df, percent=0.15)
    ''';
    # Show a Spark dataframe in graphic mode
    def show(self, df, count=None, percent=None, maxColumns=0, index=True):
        if (df == None): return
        import pandas
        from IPython.display import display, HTML
        pandas.set_option('display.encoding', 'UTF-8')
        # Pandas dataframe
        dfp = None
        # maxColumns param
        if (maxColumns >= 0):
            if (maxColumns == 0): maxColumns = len(df.columns)
            pandas.set_option('display.max_columns', maxColumns)
        # max colwidth
        import sys
        if (sys.version_info[0]>=3 and sys.version_info[1]>=8):
            pandas.set_option('max_colwidth', None)
        else:
            pandas.set_option('max_colwidth', -1)
        # count param
        if (count == None and percent == None): count = 10 # Default count
        if (count != None):
            count = int(count)
            if (count == 0): count = df.count()
            pandas.set_option('display.max_rows', count)
            dfp = pandas.DataFrame(df.head(count), columns=df.columns)
            if (index): display(dfp)
            else: display(HTML(dfp.to_html(index=False)))
        # percent param
        elif (percent != None):
            percent = float(percent)
            if (percent >=0.0 and percent <= 1.0):
                import datetime
                now = datetime.datetime.now()
                seed = long(now.strftime("%H%M%S"))
                dfs = df.sample(False, percent, seed)
                count = df.count()
                pandas.set_option('display.max_rows', count)
                dfp = dfs.toPandas()
                if (index): display(dfp)
                else: display(HTML(dfp.to_html(index=False)))

    # Show the first line(s) of a raw file whatever its size
    def showFile(self, file, nbrOfLines=10):
        rdd = self.sc.textFile(file)
        lines = rdd.take(nbrOfLines)
        for line in lines: print(line)

    # Check if a file is empty
    def isFileEmpty(self, file):
        rdd = self.sc.textFile(file)
        isEmpty = rdd.isEmpty()
        rdd.unpersist()
        return isEmpty

    # Check if a Spark dataframe is empty
    def isEmpty(self, df, byCounting=False):
        '''
        Useful function which checks if a dataframe is empty or not.

        - Warning:
        In certain cases the fact of using isEmpty() or take(1) can put the code in an infinite wait...
        Also isEmpty() can return True if there is partition, but no data...
        So the solution is to use the df.count(), and using cache() just before also improves performances.

        - Usage 1 (by checking the first row with take(1), but the code can be in an infinite wait):
        df, empty = isEmpty(df)
        print("Empty=" + str(empty))

        - Usage 2 (by counting rows):
        df = df.cache()
        df, empty, count = isEmpty(df, byCounting=True)
        print("Empty=" + str(empty) + " Count=" + str(count))
        '''
        empty = True
        count = 0
        # Counting
        if (byCounting):
            count = 0
            if (df != None): count = df.count()
            if (count > 0): empty = False
        # Taking the first row and throwing an exception if no row
        else:
            row = None
            try:
                if (df != None): row = df.rdd.take(1) # Normally throws an exception if no row
            except BaseException as err:
                row = None
            if (row != None and len(row) > 0): empty = False
        if (byCounting): return df, empty, count
        return df, empty

    # Replace key-value pairs into a Spark dataframe, by specifying some columns (or all columns if None)
    def replace(self, df, kvPairs=None, columns=None):
        '''
        Complete RegExp replace function
        - Usage example:
        df = replace(df, kvPairs={"^ND$": ''}, df.columns)
        df = replace(df, kvPairs={'': None}, df.columns)
        '''
        if (columns == None): columns = df.columns
        if (kvPairs != None):
            for column in columns:
                for key, value in kvPairs.items():
                    if (key == ""):
                        df = df.withColumn(column, self.F.when(self.F.col(column) == "", value).otherwise(self.F.col(column)))
                    elif (key == None and value != None):
                        df = df.withColumn(column, self.F.when(self.F.col(column).isNull(), value).otherwise(self.F.col(column)))
                    elif (key != None and value == None):
                        df = df.withColumn(column, self.F.regexp_replace(column, key, ""))
                        df = df.withColumn(column, self.F.when(self.F.col(column) == "", None).otherwise(self.F.col(column)))
                    elif (key != None and value != None):
                        df = df.withColumn(column, self.F.regexp_replace(column, key, value))
        return df

    # Replace by Null a list of values into a Spark dataframe, by specifying some columns (or all columns if None)
    def replaceByNull(self, df, values=[''], columns=None):
        if (columns == None): columns = df.columns
        if (values != None):
            for column in columns:
                for value in values:
                    df = df.withColumn(column, self.F.when(self.F.col(column) == value, None).otherwise(self.F.col(column)))
        return df

    # Replace Null by a value into a Spark dataframe, by specifying some columns (or all columns if None)
    def replaceNullBy(self, df, value, columns=None):
        if (columns == None): columns = df.columns
        if (value != None):
            for column in columns:
                df = df.withColumn(column, self.F.when(self.F.col(column).isNull(), value).otherwise(self.F.col(column)))
        return df

    # Replace not Null by Null into a Spark dataframe, by specifying some columns (or all columns if None)
    def replaceNotNullByNull(self, df, columns=None):
        if (columns == None): columns = df.columns
        for column in columns:
            df = df.withColumn(column, self.F.when(self.F.col(column).isNotNull(), None).otherwise(self.F.col(column)))
        return df

    # Replace not Null by a value into a Spark dataframe, by specifying some columns (or all columns if None)
    def replaceNotNullBy(self, df, value, columns=None):
        if (columns == None): columns = df.columns
        if (value != None):
            for column in columns:
                df = df.withColumn(column, self.F.when(self.F.col(column).isNotNull(), value).otherwise(self.F.col(column)))
        return df

    # Cast a single column into a Spark dataframe
    def castColumn(self, df, columnName, columnType):
        sparkClassType = self._getSparkClassType(columnType)
        cmd = "df.withColumn(columnName, df[columnName].cast(self.T." + sparkClassType + "()))"
        df = eval(cmd)
        return df

    # Cast several columns with the same type into a Spark dataframe
    def castColumns(self, df, columnNames, columnType):
        for columnName in columnNames:
            df = self.castColumn(df=df, columnName=columnName, columnType=columnType)
        return df

    # Prepare an array column to be parsed as an array of numbers (Array<Integer>, Array<Long>, Array<Float>, Array<Doubles>).
    def prepareArrayColumnForNumbers(self, df, columnName):
        '''
        Prepare an array column to be parsed as an array of numbers (Array<Integer>, Array<Long>, Array<Float>, Array<Doubles>).
        In order to drop the bad characters this function pre-cast the column as a String type,
        so after don't forget to explicitly cast your column with the Array<?> type of your choice.

        - Input example:
        ID 	VALUE
        1 	345,null,,None,nothing
        2 	346,ND,ND,null
        3 	[347,,ND,null] <= This value will need the function prepareArrayColumnForNumbers()

        - Output example:
        ID 	VALUE
        1 	[345, None, None, None, None]
        2 	[346, None, None, None]
        3 	[347, None, None, None] <= Good result

        - Output example if you don't use this function:
        ID 	VALUE
        1 	[345, None, None, None, None]
        2 	[346, None, None, None]
        3 	[None, None, None, None] <= Bad result
        '''
        def dropBadCharacters(string):
            if (string != None):
                badChars = ['[', ']', ' ', "'", '"', "ND"] # [, ] and spaces are mandatory (note that space characters are ignored in Spark V3.0)
                for charsToDrop in badChars: string = string.replace(charsToDrop, '')
            return string
        udf_dropBadCharacters = self.F.udf(dropBadCharacters, self.T.StringType())
        df = df.withColumn(columnName, df[columnName].cast("string"))
        df = df.withColumn(columnName, udf_dropBadCharacters(df[columnName]))
        return df

    # Cast a single column to an Array<type> into a Spark dataframe
    def castColumnToArray(self, df, columnName, subType='string', delimiter=',', prepareForNumbers=False):
        '''
        Cast a column as an Array<?> type, where ? is the subtype.

        - Params:
        df: The Spark Dataframe.
        columnName: The column name to cast.
        subType: The subtype.
        delimiter: The delimiter used into the array values (default is ',').
        prepareForNumbers: See the help of the function prepareArrayColumnForNumbers().

        - Return:
        The Spark Dataframe with the column casted as an Array.
        '''
        if (prepareForNumbers == True): df = self.prepareArrayColumnForNumbers(df=df, columnName=columnName)
        try:
            df = df.withColumn(columnName, self.F.split(self.F.col(columnName), delimiter).cast("array<" + subType + ">"))
        except BaseException as err:
            serr = str(err)
            if ("cannot resolve" in serr and "split" in serr):
                df = df.withColumn(columnName, self.F.col(columnName).cast("array<" + subType + ">"))
            else: raise(err)
        return df

    # Cast several columns to an Array<type> into a Spark dataframe
    def castColumnsToArray(self, df, columnNames, subType='string', delimiter=',', prepareForNumbers=False):
        for columnName in columnNames:
            df = self.castColumnToArray(df=df, columnName=columnName, subType=subType, delimiter=delimiter, prepareForNumbers=prepareForNumbers)
        return df

    # Get the type of a column into a Spark dataframe
    def getColumnType(self, df, columnName):
        columnType = None
        schema = self.getSchema(df)
        for kvpair in schema:
            if (kvpair[0] == columnName):
                columnType = kvpair[1]
        return columnType

    # Rename a column into a Spark dataframe
    def renameColumn(self, df, oldName, newName):
        df = df.withColumnRenamed(oldName, newName)
        return df

    # Rename several columns into a Spark dataframe
    def renameAllColumns(self,
                      df,
                      dropAccents=False,
                      upperCase=False,
                      lowerCase=False,
                      stdReplaces=[['.', '_']],
                      reReplaces=None,
                      reReplacesFirst=False):
        '''
        Rename several columns in once
        reReplaces = [
            ["^telephone$", "PHONE", True],
            ["^cellular$", "MOBILE", True]
        ]
        df = renameAllColumns(df, upperCase=True, stdReplaces=[['.', '_']], reReplaces=reReplaces)
        '''
        newColumns = []
        for currentName in df.columns:
            newName = currentName.strip()
            if (dropAccents): newName = self._removeAccents(newName, dropReplacementCharater=False)
            if (upperCase): newName = newName.upper()
            if (lowerCase): newName = newName.lower()
            newName = self.strReplace(newName, stdRules=stdReplaces, reRules=reReplaces, reRulesFirst=reReplacesFirst)
            newColumns.append(newName)
        newStrColumns = "'" + "', '".join(newColumns) + "'"
        cmd = "df.toDF(" + newStrColumns + ")"
        df = eval(cmd)
        return df

    # Copy a column to a new one into a Spark dataframe
    def copyColumn(self, df, sourceColumnName, targetColumnName):
        df = df.withColumn(targetColumnName, df[sourceColumnName])
        return df

    # Create a column with a constant value into a Spark dataframe
    def createColumnWithValue(self, df, columnName, columnType=None, value=None):
        if (columnType != None):
            df = df.withColumn(columnName, self.F.lit(value).cast(columnType))
        else:
            df = df.withColumn(columnName, self.F.lit(value))
        return df

    # Create a column into a Spark dataframe by calling a rule from an object class (e.g: business rules)
    def createColumnWithRule(self, df, columnName, columnType, ruleClass, ruleName, columns=None):
        '''
        Create a column into a Spark dataframe by calling a rule from a Python class (e.g: business rules)

        - Note:
        If you plan to outsource your code into a Python file, don't forget to add your file into the Spark PATH like this:
        sc.addPyFile(APPLICATION_HOME + "/lib/BusinessRules_V1_0.py")

        - Usage example:
        # Creating a source dataframe
        columns = ["NAME", "AGE", "ADDRESS"]
        content = [
            ("Martin", 30, "Paris"),
            ("Dupont", 21, "Bordeaux")
        ]
        df = sc.parallelize(content).toDF(columns)
        df.show()
        +------+---+--------+
        |  NAME|AGE| ADDRESS|
        +------+---+--------+
        |Martin| 30|   Paris|
        |Dupont| 21|Bordeaux|
        +------+---+--------+

        # Implementing a business rule
        class CustomerRisk:
            churns = None
            def churn(self, columns=None):
                dic = eval(self.churns)
                if (columns["AGE"] <= 25 and dic["CHURN_FOR_YOUNGS"] > 75): churn = 75
                else: churn = dic["CHURN_FOR_OLDS"]
                return churn

        # Creating a new column by executing the business rule
        sdu = SparkDfUtils(spark)
        cr = CustomerRisk()
        cr.churns = "{'CHURN_FOR_YOUNGS':80, 'CHURN_FOR_OLDS':50}"
        df = sdu.createColumnWithRule(df,
                                      columnName="CHURN(%)", columnType="integer",
                                      ruleClass=cr, ruleName="churn",
                                      columns=["NAME", "AGE", "ADDRESS"])
        df.show()
        +------+---+--------+--------+
        |  NAME|AGE| ADDRESS|CHURN(%)|
        +------+---+--------+--------+
        |Martin| 30|   Paris|      50|
        |Dupont| 21|Bordeaux|      75|
        +------+---+--------+--------+
        '''
        # Spark type (e.g: "string", "array<string>", etc.)
        if (columnType != None):
            columnType = columnType.strip()
            if ("array" in columnType):
                sparkClassType = columnType.replace("array", "ArrayType")
            elif ("ArrayType" in columnType):
                sparkClassType = columnType
            else:
                sparkClassType = self._getSparkClassType(columnType)
        else: sparkClassType = "StringType"
        if (sparkClassType.startswith("ArrayType<") and sparkClassType.endswith('>')):
            subType = sparkClassType[1+sparkClassType.find('<'): sparkClassType.find('>')]
            subType = self._getSparkClassType(subType)
            sparkClassType = "self.T.ArrayType(self.T." + subType + "(), True)"
        else:
            sparkClassType = "self.T." + sparkClassType + "()"
        # UDF call
        aUdf = eval("self.F.udf(ruleClass." + ruleName + ", " + sparkClassType + ")")
        if (columns != None):
            # See https://stackoverflow.com/questions/36584812/pyspark-row-wise-function-composition
            structColumns = self.F.struct([df[column] for column in columns])
            df = df.withColumn(columnName, aUdf(structColumns))
        else:
            df = df.withColumn(columnName, aUdf(self.F.lit(None)))
        # Return the dataframe
        return df

    def createColumnWithMilliseconds(self, df, millisecondsColumn, timestampColumn):
        F = self.F
        timestampColumnStr = timestampColumn + "_STR123456789"
        df = df.withColumn(timestampColumnStr, F.col((timestampColumn)))
        df = self.castColumn(df, timestampColumnStr, "string")

        df = df.withColumn(timestampColumnStr, F.regexp_replace( # E.g: "2020-12-01 23:11:58" -> "2020-12-01 23:11:58.000"
            F.col(timestampColumnStr),
            "^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})$",
            "$1-$2-$3 $4:$5:$6.000"
            )
        )

        df = df.withColumn(timestampColumnStr, F.regexp_replace( # E.g: "2020-12-01 23:11:58.4" -> "2020-12-01 23:11:58.400"
            F.col(timestampColumnStr),
            "^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{1})$",
            "$1-$2-$3 $4:$5:$6.$700"
            )
        )

        df = df.withColumn(timestampColumnStr, F.regexp_replace( # E.g: "2020-12-01 23:11:58.45" -> "2020-12-01 23:11:58.450"
            F.col(timestampColumnStr),
            "^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{2})$",
            "$1-$2-$3 $4:$5:$6.$70"
            )
        )

        df = df.withColumn(millisecondsColumn, F.substring_index(timestampColumnStr, '.', -1))
        df = self.castColumn(df, millisecondsColumn, "integer")
        df = self.dropColumn(df, timestampColumnStr)

        return df

    # Drop a column into a Spark dataframe
    def dropColumn(self, df, columnName):
        df = df.drop(columnName)
        return df

    # Drop several columns into a Spark dataframe
    def dropColumns(self, df, columns):
        for columnName in columns: df = df.drop(columnName)
        return df

    # Drop duplicate(s) into a Spark dataframe
    def dropDuplicates(self, df, columns):
        df = df.dropDuplicates(columns)
        return df

    # Count duplicate(s) into a Spark dataframe
    def getDuplicatesCount(self, df, columns):
        dfDuplicates = df.groupBy(columns).count().filter('count > 1')
        return dfDuplicates

    # Sort a Spark dataframe by specifying a set of columns
    def sort(self, df, sortedColumnNames=None, ascending=True):
        if (sortedColumnNames != None): df = df.sort(sortedColumnNames, ascending=ascending)
        return df

    # See: https://databricks.com/blog/2015/07/15/introducing-window-functions-in-spark-sql.html
    # Add consecutive index into a Spark dataframe (Advice: Sort your data before)
    def addConsecutiveIndex(self, df, indexColumnName):
        from pyspark.sql.window import Window
        monotonicColumnName = indexColumnName + "_monotonic"
        df = df.withColumn(monotonicColumnName, self.F.monotonically_increasing_id())
        w = Window.orderBy(monotonicColumnName)
        df = df.withColumn(indexColumnName, self.F.row_number().over(w))
        df = df.drop(monotonicColumnName)
        return df

    # Create a column into a Spark dataframe by converting a Spark timestamp to an Excel timestamp
    def convertTimestampToExcelDate(self, df, sourceColumn, targetColumn=None):
        # https://gist.github.com/peter216/6361201
        def epoch2excel(epoch, tz=None):
            from datetime import datetime, timezone
            if tz is None:
                tz = timezone.utc
            dtepoch = datetime.fromtimestamp(epoch, tz)
            temp = datetime(1899, 12, 30, tzinfo=timezone.utc)
            delta = dtepoch - temp
            return float(delta.days) + (float(delta.seconds) / 86400)
        udf_epoch2excel = self.F.udf(epoch2excel, self.T.DoubleType())
        if (targetColumn == None): targetColumn = sourceColumn
        df = df.withColumn(targetColumn, udf_epoch2excel(df[sourceColumn]))
        return df

    # Create a column into a Spark dataframe by converting an Excel timestamp to a Spark timestamp
    def convertExcelDateToTimestamp(self, df, sourceColumn, targetColumn=None):
        # https://gist.github.com/peter216/6361201
        def excel2epoch(exceldate, tz=None): # Return a timestamp in seconds
            from datetime import datetime, timedelta, timezone
            if tz is None:
                tz = timezone.utc
            temp = datetime(1899, 12, 30, tzinfo=tz)
            exceldate = float(exceldate)
            days = int(exceldate)
            seconds = (exceldate - days) * 86400
            date = temp + timedelta(days=days, seconds=seconds)
            epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
            return (date - epoch).total_seconds()
        udf_excel2epoch = self.F.udf(excel2epoch, self.T.DoubleType())
        if (targetColumn == None): targetColumn = sourceColumn
        df = df.withColumn(targetColumn, self.F.to_timestamp(udf_excel2epoch(df[sourceColumn])))
        return df

    # Get distinct values from a Spark dataframe by specifying a column
    def getDistinctValues(self, obj, columnName, where=None, forceStringType=True):
        df = self._getDfFromObject(obj)
        if (where != None): df2 = df.where(where)
        else: df2 = df
        values = df2.select(columnName).distinct().collect()
        for i, value in enumerate(values):
                value = value.asDict().get(columnName)
                if (forceStringType): value = str(value)
                values[i] = value
        return values

    # Get the column's value of a dataframe's first row
    def getFirst(self, df, columnName):
        '''
        Get the column's value of a dataframe's first row
        '''
        f = df.first().asDict().get(columnName)
        return f

    # Return the first Spark row
    def getFirstRow(self, df):
        row = df.first()
        return row

    # Get the first Spark row as array
    def getFirstRowAsArray(self, df):
        row = self.getFirstRow(df)
        array = self.convertRowsAsArrays(row)
        return array

    # Return the Spark rows
    def getRows(self, df):
        rows = df.collect()
        return rows

    # Get Spark rows as arrays
    def getRowsAsArrays(self, df):
        rows = self.getRows(df)
        arrays = self.convertRowsAsArrays(rows)
        return arrays

    # Convert Saprk rows as arrays containing values
    def convertRowsAsArrays(self, rows, columns=None):
        rowsValues = []
        if (columns == None): columns = rows[0].asDict().keys()
        for row in rows:
            rowValues = []
            for col in columns:
                value = row[col]
                rowValues.append(value)
            rowsValues.append(rowValues)
        return rowsValues

    # Get an aggregated dataframe by specifying a column name, asColumn, groupBy, a where clause and an aggregate function
    def getAggregate(self, df, columnName, asColumnName=None, groupByColumns=None, agg='max', where=None):
        '''
        Get an aggregated dataframe by specifying a column name, asColumn, groupBy, a where clause and an aggregate function
        '''
        if (agg == "mean"): agg = "avg"
        if (where != None): df = df.where(where)
        cmd = "df"
        if (groupByColumns != None): cmd += ".groupBy(" + str(groupByColumns) + ")"
        cmd += ".agg(self.F." + agg + "(\"" + columnName + "\")"
        if (asColumnName != None): cmd += ".alias(\"" + asColumnName + "\")"
        cmd += ")"
        df_result = eval(cmd)
        return df_result

    # Get aggregation from a Spark dataframe by specifying a column
    def getAggregatedValue(self, obj, columnName, agg='max', where=None):
        # From table
        if (type(obj) is str):
            tableName = str(obj)
            query = "SELECT " + agg + "(" + columnName + ") AS RESULT FROM " + tableName
            if (where != None): query += " WHERE " + where
            df = self.spark.sql(query)
            ret = None
            dictionary = df.first().asDict()
            for key in dictionary:
                ret = dictionary.get(key) # key can have sometimes the value "RESULT", or "EXPR_0"
                break
        # From dataframe
        else:
            if (where != None): df = obj.where(where)
            else: df = obj
            from pyspark.sql import functions as F
            agg = agg.strip().lower()
            if (agg == "mean"): agg = "avg"
            cmd = "df.agg(F." + agg + "(\"" + columnName + "\")).first().asDict().get(\"" + agg + "(" + columnName + ")\")"
            ret = eval(cmd)
        return ret

    # Drop rows into a Spark dataframe which exist from another Spark dataframe (by joining primary keys)
    def dropExistingRowsFromOtherDf(self, df, dfKey, otherDf, otherDfKey):
        '''
        from pyspark.sql import types as T

        schema1 = T.StructType([T.StructField("id", T.StringType()), T.StructField("value", T.StringType())])
        schema2 = T.StructType([T.StructField("id", T.StringType()), T.StructField("value", T.StringType()), T.StructField("value2", T.StringType())])

        data1 = [["1", "A1"], ["2", "A2"], ["3", "A3"], ["4", "A4"]]
        data2 = [["3", "A3", "B3"], ["4", "A4", "B4"], ["5", "A5", "B5"], ["6", "A6", "B6"]]

        df1 = spark.createDataFrame(data1, schema=schema1)
        df2 = spark.createDataFrame(data2, schema=schema2)

        df1.show()
        +---+-----+
        | id|value|
        +---+-----+
        |  1|   A1|
        |  2|   A2|
        |  3|   A3|
        |  4|   A4|
        +---+-----+

        df2.show()
        +---+-----+------+
        | id|value|value2|
        +---+-----+------+
        |  3|   A3|    B3|
        |  4|   A4|    B4|
        |  5|   A5|    B5|
        |  6|   A6|    B6|
        +---+-----+------+

        df3 = dropExistingRowsFromOtherDf(df1, "id", df2, "id")
        df3.show()
        +---+-----+
        | id|value|
        +---+-----+
        |  1|   A1|
        |  2|   A2|
        +---+-----+
        '''
        df_result = eval("df.join(otherDf, df[dfKey]==otherDf[otherDfKey], how='left_anti')")
        return df_result

    # Load Parquet data source as a Spark dataframe
    def loadParquet(self, inputDir, inferSchema=False, mergeSchema=False, partitions=None, dropDuplicates=None):
        '''
        # Load a dataset at once, with parquet|avro format and with|without partitions

        - Example 1 (simple):
        inputDir = "/home/foo/myData"
        df = load(inputDir=inputDir, inferSchema=False, mergeSchema=True, inputFormat="parquet")

        - Example 2 (one combination of partitions):
        inputDir = "/home/foo/myData"
        partitions = "EVT_YEAR=2020/EVT_MONTH=4/EVT_DAY=15/EVT_HOUR={17,19}"
        df = load(inputDir=inputDir, inferSchema=False, mergeSchema=True, inputFormat="parquet", partitions=partitions)

        - Example 3 (several combinations of partitions):
        inputDir = "/home/foo/myData"
        partitions = [
            "EVT_YEAR=2020/EVT_MONTH=4/EVT_DAY=15/EVT_HOUR={17,19}",
            "EVT_YEAR=2020/EVT_MONTH=4/EVT_DAY={16,17}/EVT_HOUR=20"
        ]
        df = load(inputDir=inputDir, inferSchema=False, mergeSchema=True, inputFormat="parquet", partitions=partitions)

        # Test concerning the 'mergeSchema' option

        tableHeader1 = ["YEAR", "ID", "NAME", "TYPE"]
        tableContent1 = [
            ("2017", "0", "name0", "type0"),
            ("2018", "1", "name1", "type1"),
            ("2018", "2", "name2", "type2"),
            ("2018", "3", "name3", "type3")
        ]
        tableDf1 = sc.parallelize(tableContent1).toDF(tableHeader1)
        tableDf1.write.partitionBy("YEAR").mode("append").parquet("./myData")

        tableHeader2 = ["YEAR", "ID", "DESCRIPTION", "TYPE", "NAME"]
        tableContent2 = [
            ("2019", "4", "desc4", "type4", "name4"),
            ("2019", "5", "desc5", "type5", "name5"),
            ("2019", "6", "desc6", "type6", "name6"),
            ("2018", "3", None,    "type3", "name3")
        ]
        tableDf2 = sc.parallelize(tableContent2).toDF(tableHeader2)
        tableDf2.write.partitionBy("YEAR").mode("append").parquet("./myData")

        tableDf = spark.read.option("mergeSchema", "true").parquet("./myData")
        tableDf = tableDf.dropDuplicates(subset=['ID'])

        tableDf.show()

        +---+-----+-----+-----------+----+
        | ID| NAME| TYPE|DESCRIPTION|YEAR|
        +---+-----+-----+-----------+----+
        |  3|name3|type3|       null|2018|
        |  0|name0|type0|       null|2017|
        |  5|name5|type5|      desc5|2019|
        |  6|name6|type6|      desc6|2019|
        |  1|name1|type1|       null|2018|
        |  4|name4|type4|      desc4|2019|
        |  2|name2|type2|       null|2018|
        +---+-----+-----+-----------+----+
        '''
        df = self._load(inputDir=inputDir, inferSchema=inferSchema, mergeSchema=mergeSchema, inputFormat="parquet", partitions=partitions)
        if (dropDuplicates != None): df = self.dropDuplicates(df, dropDuplicates)
        return df

    # Load Avro data source as a Spark dataset or dataframe
    def loadAvro(self, inputDir, inferSchema=False, mergeSchema=True, partitions=None):
        df = self._load(inputDir=inputDir, inferSchema=inferSchema, mergeSchema=mergeSchema, inputFormat="avro", partitions=partitions)
        return df

    # Load Json data source as a Spark dataset
    def loadJson(self, obj, inferSchema=False, isFile=True, transform=True):
        '''
        - Usage example 1:
        df = loadJson(aFile)

        - Usage example 2:
        > loadJson(obj, inferSchema=False|True, isFile=False) can takes 3 types:
          DICT   => obj = {"name": "Yin", "address": {"city": "Columbus", "state": "Ohio"}}
          LIST   => obj = [{"name": "Yin", "address": {"city": "Columbus", "state": "Ohio"}}]
          STRING => obj = "{"name": "Yin", "address": {"city": "Columbus", "state": "Ohio"}}" E.g:  json.loads()
        df = loadJson(obj, inferSchema=True, isFile=False)
        df.show()
        > Output dataframe:
        #+----------------+----+
        #|         address|name|
        #+----------------+----+
        #|[Columbus, Ohio]| Yin|
        #+----------------+----+
        '''
        def transformJson(obj):
            # Cleaning the text
            obj = obj.strip()
            if (obj.startswith("[")): obj = obj[1:].strip()
            if (obj.endswith("]")): obj = obj[:-1].strip()
            obj = obj.replace("}, {", "}\n{")
            return obj
        if (not isFile):
            if (type(obj) == dict or type(obj) == list): obj = self.json.dumps(obj)
            if (transform): obj = transformJson(obj)
            obj = obj.split('\n')
            obj = self.sc.parallelize(obj)
        if (inferSchema): inferSchema = "true"
        else: inferSchema = "false"
        ds = self.spark.read.option("inferSchema", inferSchema).json(obj)
        return ds

    # Load a Json string as a Spark dataset
    def loadJsonString(self, json, inferSchema=False, preTransform=True, stdReplaces=None, reReplaces=None, reReplacesFirst=False):
        def preTransformJson(jss):
            jss = jss.strip()
            if (jss.startswith("[")): jss = jss[1:].strip()
            if (jss.endswith("]")): jss = jss[:-1].strip()
            jss = jss.replace('\n', '')
            jss = self.strReplace(jss, reRules=[["},\s+{", "}\n{"]], reRulesFirst=True)
            return jss
        jss = json
        if (type(jss) == dict or type(jss) == list): jss = self.json.dumps(jss)
        if (preTransform): jss = preTransformJson(jss)
        jss = self.strReplace(jss, stdRules=stdReplaces, reRules=reReplaces, reRulesFirst=reReplacesFirst)
        jss = jss.split('\n')
        jss = self.sc.parallelize(jss)
        if (inferSchema): inferSchema = "true"
        else: inferSchema = "false"
        ds = self.spark.read.option("inferSchema", inferSchema).json(jss)
        return ds

    '''
    Load a simple CSV file
    ''';
    # Load a well formed CSV data source as a Spark dataframe
    def loadSimpleCsv(self, file, header=True, delimiter=';', inferSchema=True):
        if (inferSchema): inferSchema = "true"
        else: inferSchema = "false"
        if (header): header = "true"
        else: header = "false"
        try:
            df = self.spark.read.load(format="csv", path=file, header=header, sep=delimiter, inferSchema=inferSchema)
        except BaseException as err:
            df = None
            print("- ERROR: Problem to load the CSV file '" + file + "'")
            print("  " + str(err))
            print("  header='" + header + "', delimiter='" + delimiter + "', inferSchema='" + inferSchema + "'")
        return df

    '''
    Load a CSV file to be cleaned, add columns for lineage
    Remove blank lines and lines with wrong number of columns, drop quotes
    ''';
    # Load a dirty or well formed CSV data source as a Spark dataframe
    def loadCsv(self, file, header=True, delimiter=None, inferSchema=True,
                      trimColumns=True, dropAccents=False, replaces=None,
                      colDateTime=None, colFileName=None, colFileSize=None, colNbrRows=None):
        from SparkFormatDelimited_V1_1 import SparkFormatDelimited
        sfd = SparkFormatDelimited(self.spark)
        sfd.isHeader = header
        sfd.columnDelimiter = delimiter
        sfd.columnsTrim = trimColumns
        sfd.columnsDropQuotes = True
        sfd.stripAccents = dropAccents
        sfd.replaceAll = replaces
        sfd.inferSchema = inferSchema
        sfd.excludeBlankLines = True
        sfd.excludeLinesLikeHeader = True
        sfd.excludeLinesWithWrongNumberOfColumns = True
        sfd.sourceDateTimeColumn = colDateTime
        sfd.sourceFileNameColumn = colFileName
        sfd.sourceSizeColumn = colFileSize
        sfd.sourceNbrRowsColumn = colNbrRows
        sfd.fileToDf(file)
        return sfd.df

    '''
    Load an EXCEL file to be cleaned, add columns for lineage
    Remove blank lines and lines with wrong number of columns, drop quotes
    ''';
    # Load an Excel data source as a Spark dataframe
    def loadExcel(self, file, sheetName='sheet1', header=True, tmpDelimiter='|', inferSchema=True,
                        trimColumns=True, dropAccents=False, replaces=None,
                        colDateTime=None, colFileName=None, colFileSize=None, colNbrRows=None, quoteAll=True):
        from SparkFormatDelimited_V1_1 import SparkFormatDelimited
        try:
            sfd = SparkFormatDelimited(self.spark)
            sfd.isHeader = header
            sfd.columnsTrim = trimColumns
            sfd.columnsDropQuotes = True
            sfd.stripAccents = dropAccents
            sfd.replaceAll = replaces
            sfd.inferSchema = inferSchema
            sfd.excludeBlankLines = True
            sfd.excludeLinesLikeHeader = True
            sfd.excludeLinesWithWrongNumberOfColumns = True
            sfd.sourceDateTimeColumn = colDateTime
            sfd.sourceFileNameColumn = colFileName
            sfd.sourceSizeColumn = colFileSize
            sfd.sourceNbrRowsColumn = colNbrRows
            sfd.localExcelToDf(localExcelPath=file, sheetName=sheetName, columnDelimiter=tmpDelimiter,
                               removeTempCsvFile=True, selectedColumns=None, encoding=None, quoteAll=quoteAll)
        except BaseException as err:
            serr = str(err)
            if ("need" in serr and "escape" in serr):
                print("ERROR: It seems that the value tmpDelimiter='" + tmpDelimiter + "' is already present as a data !")
                print("       Please modify this temporary delimiter or use instead the option quoteAll=True.")
            raise err
        return sfd.df

    '''
    Connection to a MongoDb database

    - Steps to generate secure files from a pem file:
    See:
    https://www.ibm.com/support/knowledgecenter/SSB23S_1.1.0.15/gtpd5/tmdbssljava.html
    https://spark.apache.org/docs/latest/security.html

    - Example of directory with certificates:
    ssl
    ├── 01-import-cacertificate-into-truststore.sh
    ├── 02-create-pkcs12-file.sh
    ├── 03-import-pkcs12-file-into-keystore.sh
    ├── cacerts
    │   ├── ima-cert-rootandsubca.pem
    │   ├── ima-cert-selfsigned.pem
    │   ├── MongoClientCert.pem
    │   └── MongoClientKey.pem
    ├── keystore
    ├── p12
    ├── README
    └── truststore
        └── MongoStore.ts

    0) How a retrieve a self signed pem certificate from a mongodb server
    $ echo -n | openssl s_client -connect {server}:{port} | openssl x509 -outform PEM > selfsigned_certificate.pem

    1) Import CaCertificate into truststore
    $ ${JAVA_HOME}/bin/keytool -import \
      -file ./cacerts/MongoClientCert.pem \
      -alias mongoClient \
      -keystore ./truststore/MongoStore.ts \
      -storepass StorePass

    2) Create Pkcs12 file
    $ openssl pkcs12 -export \
      -in ./cacerts/MongoClientCert.pem \
      -inkey ./cacerts/MongoClientKey.pem \
      -out ./p12/MongoClientKeyCert.p12 \
      -name mongoClient

    3) Import Pkcs12 file into keystore
    $ {$JAVA_HOME}/bin/keytool -importkeystore \
    -srckeystore ./p12/MongoClientKeyCert.p12 \
    -destkeystore ./keystore/MongoClientKeyCert.jks \
    -srcstoretype pkcs12 \
    -alias mongoClient \
    -destkeypass StorePass
    ''';
    # Load a MongoDb data source as a Spark dataset
    def loadMongoDb(self, userLogin,
                    userPassword,
                    server='127.0.0.1',
                    port=27017,
                    database=None,
                    table=None,
                    trustoreFile=None,
                    trustorePassword=None):
        ds = None
        if (database != None and table != None):
            url = "mongodb://{userLogin}:{userPassword}@{server}:{port}/{database}.{table}"
            if (userLogin != None and userPassword != None):
                url = url.replace("{userLogin}", userLogin)
                url = url.replace("{userPassword}", userPassword)
            else: url = url.replace("{userLogin}:{userPassword}@", '')
            url = url.replace("{server}", server)
            url = url.replace("{port}", str(port))
            url = url.replace("{database}", database)
            url = url.replace("{table}", table)
            if (trustoreFile != None and trustorePassword != None):
                url += "?ssl=true"
                # Retrieve the java System singleton and set trustore variables
                System = self.sc._gateway.jvm.java.lang.System
                System.setProperty("javax.net.ssl.trustStore", trustoreFile)
                System.setProperty("javax.net.ssl.trustStorePassword", trustorePassword)
            ds = self.spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri", url).load()
        return ds

    def loadSqlQuery(self, query, driver, url, user, password):
        df = self.spark.read.format("jdbc").options(driver=driver, url=url, user=user, password=password, query=query).load()
        return df

    def loadSqlTable(self, table, driver, url, user, password):
        df = self.spark.read.format("jdbc").options(driver=driver, url=url, user=user, password=password, dbtable=table).load()
        return df

    # Load a SQL dump file as a Spark dataset
    def loadSqlDump(self, sqlDump, dbType='mysql', delimiter=',',
                          setColNames=True, setColTypes=True,
                          inferSchema=False, mergeSchema=False, repartition=32):
        if (self.ssql == None): self.ssql = self. SparkSqlDumpLoader(self.spark)
        df = self.ssql.load(sqlDump, dbType, delimiter, setColNames, setColTypes, inferSchema, mergeSchema, repartition)
        return df

    # Load a XML file from a local FileSystem into a Spark dataset (requires 'xmltodict' dependency)
    def loadXml(self, inputFile, outputFile=None, inferSchema=False, returnTuple=False):
        '''
        Load a XML file from a local FileSystem into a Spark dataset (requires 'xmltodict' dependency)

        - Usages:
        ds = loadXml(inputFile="./myFile.xml", inferSchema=True)

        ds, outputFile = loadXml(inputFile="./myFile.xml", inferSchema=True, returnTuple=True)
        ... operations on ds ...
        os.remove(outputFile)

        ds = loadXml(inputFile="./myFile.xml", outputFile="./myFile.json", inferSchema=True)
        ... operations on ds ...
        os.remove("./myFile.json")
        '''
        if (inputFile == None): return None
        import datetime, os, xmltodict
        if (outputFile == None):
            currentDt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
            outputFile = '/tmp/' + os.path.basename(inputFile) + '.' + currentDt + '.json'
        with open(inputFile) as inputXml:
            with open(outputFile, 'w') as outputXml:
                self.json.dump(xmltodict.parse(inputXml.read()), outputXml)
        ds = self.loadJson(outputFile, inferSchema=inferSchema)
        if (returnTuple): return ds, outputFile
        return ds

    # Create a SQL table from a Spark dataframe
    def createTableFromDf(self, df, baseName, tableName, cacheTable=False):
        if (baseName != None): table = baseName + '.' + tableName
        else: table = tableName
        tmpTable = "tmp_" + table.replace('.', '_')
        df.createOrReplaceTempView(tmpTable)
        self.spark.sql("UNCACHE TABLE IF EXISTS " + table)
        self.spark.sql("DROP TABLE IF EXISTS " + table)
        self.spark.sql("CREATE TABLE " + table + " AS SELECT * FROM " + tmpTable)
        if (cacheTable == True): self.spark.sql("CACHE TABLE " + table)
        self.spark.sql("DROP TABLE IF EXISTS " + tmpTable)

    # Insert a Spark dataframe into a SQL table
    def insertDfIntoTable(self, df, baseName, tableName, cacheTable=False):
        if (baseName != None): table = baseName + '.' + tableName
        else: table = tableName
        tmpTable = "tmp_" + table.replace('.', '_')
        df.createOrReplaceTempView(tmpTable)
        self.spark.sql("INSERT INTO TABLE " + table + " SELECT * FROM " + tmpTable)
        if (cacheTable == True): self.spark.sql("CACHE TABLE " + table)
        self.spark.sql("DROP TABLE IF EXISTS " + tmpTable)

    # Save a Spark dataframe a Parquet format
    def saveAsParquet(self, df, filePath, compression=True, overwrite=True, partitionNames=None, nbrPartitions=None):
        if (overwrite == True): mode = "overwrite"
        else: mode = "append"
        if (nbrPartitions != None): df = self._arrangePartitions(df, nbrPartitions)
        if (compression == True): compression = "snappy"
        else: compression = "none"
        if (partitionNames != None):
            df.write.partitionBy(partitionNames).option("compression", compression).mode(mode).save(filePath, format="parquet")
        else:
            df.write.option("compression", compression).mode(mode).save(filePath, format="parquet")

    # Save a Spark dataframe as CSV format
    def saveAsCsv(self, df, filePath, delimiter=';', header=True, quoteAll=False, overwrite=True, nbrPartitions=None):
        if (header == True): isHeader = "true"
        else: isHeader = "false"
        if (quoteAll == True): isQuoteAll = "true"
        else: isQuoteAll = "false"
        if (overwrite == True): mode = "overwrite"
        else: mode = "append"
        if (nbrPartitions != None): df = self._arrangePartitions(df, nbrPartitions)
        df.write.option("delimiter", delimiter).option("header", isHeader).option("quoteAll", isQuoteAll).mode(mode).save(filePath, format="csv")

    # Save a Spark dataframe as Excel format
    def saveAsExcel(self, df, filePath, sheetName='Sheet1'):
        dfp = df.toPandas()
        dfp.to_excel(filePath, sheet_name=sheetName, index=False)

    # Flush as Parquet (save then reload the data to/from Parquet)
    def flushAsParquet(self, df, path, nbrPartitions=None, partitionNames=None, compression=False, inferSchema=False, mergeSchema=False):
        self.saveAsParquet(df, path, compression=compression, overwrite=True, partitionNames=partitionNames, nbrPartitions=nbrPartitions)
        df = self.loadParquet(inputDir=path, inferSchema=inferSchema, mergeSchema=mergeSchema)
        return df

    # Create a Spark dataframe from scratch
    def createDataFrame(self, schema, data=None):
        '''
        Create a DataFrame from scratch

        - Example 1:
        df = createDataFrame(
            schema=[["AGE", "integer"], ["NAME", "string"]],
            data=[[35, "JON"], [29, "BETTY"]]
        )

        df.printSchema()
        root
         |-- AGE: integer (nullable = true)
         |-- NAME: string (nullable = true)

        df.show()
        +---+-----+
        |AGE| NAME|
        +---+-----+
        | 35|  JON|
        | 29|BETTY|
        +---+-----+

        - Example 2 (create an empty DataFrame):
        df = createDataFrame(
            schema=[["AGE", "integer"], ["NAME", "string"]]
        )

        df.printSchema()
        root
         |-- AGE: integer (nullable = true)
         |-- NAME: string (nullable = true)

        df.show()
        +---+-----+
        |AGE| NAME|
        +---+-----+
        +---+-----+
        '''
        def getSparkType(strType):
            strType = strType.strip().lower()
            if (strType == "int"): strType = "integer"
            if (strType == "bigint"): strType = "long"
            strType = strType[0].upper() + strType[1:] + "Type"
            return strType
        strSchema = "self.T.StructType(["
        for i, field in enumerate(schema):
            if (i > 0): strSchema += ", "
            strSchema += "self.T.StructField(\"" + field[0] + "\", self.T." + getSparkType(field[1]) + "())"
        strSchema += "])"
        schema = eval(strSchema)
        if (data == None): data = self.sc.emptyRDD()
        df = self.spark.createDataFrame(data, schema=schema)
        return df

    # Append one or several rows into a Spark dataframe
    def append(self, df, data):
        '''
        Append new rows into a DataFrame

        - Example:
        df = append(df, data=[[54, "PETER"], [38, "SABRINA"]])

        df.printSchema()
        root
         |-- AGE: integer (nullable = true)
         |-- NAME: string (nullable = true)

        df.show()
        +---+-------+
        |AGE|   NAME|
        +---+-------+
        | 35|    JON|
        | 29|  BETTY|
        | 54|  PETER|
        | 38|SABRINA|
        +---+-------+
        '''
        dfl = self.spark.createDataFrame(data, schema=df.schema)
        df = df.union(dfl)
        return df

    # Delete the contents of a directory, not the directory itself (works with HDFS and local FS)
    def delDirectoryContent(self, dir):
        self.sfu.fullyDeleteContents(dir)

    # Delete a path and all its contents (works with HDFS and local FS)
    def delDirectory(self, dir):
        self.sfu.fullyDelete(dir)

    # Move a path (works with HDFS and local FS)
    def movePath(self, src, dest):
        self.sfu.move(src, dest)

    # Get the size of a file (works with HDFS and local FS)
    def getFileSize(self, filePath):
        self.sfu.getSize(filePath)

    # Get the list of files from a parent directory (works with HDFS and local FS)
    def getFiles(self, parentPath, recursive=False, startsWith=None, contains=None, endsWith=None):
        self.sfu.scan(parentPath, recursive)
        paths = self.sfu.listPaths
        if (startsWith != None or contains != None or endsWith != None):
            paths = self.sfu.filterPaths(paths, startsWith, contains, endsWith)
        strPaths = self.sfu.getFiles(paths)
        if (strPaths != None and len(strPaths)==0): strPaths = None
        if (strPaths != None):
            for i, aPath in enumerate(strPaths):
                if (aPath.startswith("file:")): strPaths[i] = aPath[5:]
        return strPaths

    # Get directories from a parent directory (works with HDFS and local FS)
    def getDirectories(self, parentPath, recursive=False, startsWith=None, contains=None, endsWith=None):
        self.sfu.scan(parentPath, recursive)
        paths = self.sfu.listPaths
        if (startsWith != None or contains != None or endsWith != None):
            paths = self.sfu.filterPaths(paths, startsWith, contains, endsWith)
        strPaths = self.sfu.getDirectories(paths)
        if (strPaths != None and len(strPaths)==0): strPaths = None
        if (strPaths != None):
            for i, aPath in enumerate(strPaths):
                if (aPath.startswith("file:")): strPaths[i] = aPath[5:]
        return strPaths

    # Cache a Spark dataframe only in memory
    def cacheMemoryOnly(self, df):
        df = df.persist(self.StorageLevel.MEMORY_ONLY)
        return df

    # Cache a Spark dataframe only in disk
    def cacheDiskOnly(self, df):
        df = df.persist(self.StorageLevel.DISK_ONLY)
        return df

    # Cache a Spark dataframe both in memory and disk
    def cacheMemoryAndDisk(self, df):
        df = df.persist(self.StorageLevel.MEMORY_AND_DISK)
        return df

    # Uncache (or unpersist) a Spark dataframe
    def uncache(self, df):
        df.unpersist()
        return None

    '''
    Get the whole Spark config
    ''';
    # Get the Spark configuration
    def getSparkConf(self):
        allConf = self.sc.getConf().getAll()
        return allConf

    '''
    Flatten a data to a dataframe
    # See https://gist.github.com/nguyenvulebinh/794c296b1133feb80e46e812ef50f7fc
    Example:
        df = flatten(ds)
        df = renameAllColumns(df, upperCase=True, stdReplaces=[['VALUE_', '']])
    ''';
    # Flatten a Spark dataset (an embedded structure) into a Spark dataframe (a tabular structure)
    def flatten(self, df, separator='_', flattenArray=False):
        df = self._flatten(df, separator)
        if (flattenArray):
            (df, have_array) = self._flattenArray(df)
            if have_array:
                return self.flatten(df, separator, True)
            else:
                return df
        return df

    # Get the schema of a Spark dataframe (as a list)
    def getSchema(self, df):
        return self.getSchemaAsList(df)
    def getSchemaAsList(self, df):
        import pyspark
        def helper(schem, prefix=[]):
            for item in schem.fields:
                if isinstance(item.dataType, pyspark.sql.types.StructType):
                    helper(item.dataType, prefix + [item.name])
                else:
                    columns.append(prefix + [item.name] + [item.dataType])
        columns = []
        helper(df.schema)
        return columns

    def getSchemaAsJson(self, df):
        schema = df.schema
        jsonSchema = schema.json()
        return jsonSchema

    def getSchemaAsDict(self, df):
        import json
        jsonSchema = self.getSchemaAsJson(df)
        dictSchema = json.loads(jsonSchema)
        return dictSchema

    # Get the schema of a Spark dataframe (as a tree)
    def getSchemaTree(self, df, lightened=False):
        return self.getSchemaAsTree(df, lightened)
    def getSchemaAsTree(self, df, lightened=False):
        schema = str(df._jdf.schema().treeString())
        if (lightened):
            schema = schema.replace("root\n", '').split('\n')
            stdRules = [[" (nullable = true)", ''], [" (nullable = false)", ''], [" (containsNull = true)", ''], [" (containsNull = false)", '']]
            for i, branch in enumerate(schema):
                for rule in stdRules: branch = branch.replace(rule[0], rule[1])
                if (branch.startswith(" |-- ")): branch = branch[5:]
                if (branch.startswith(" |   ")): branch = branch[5:]
                schema[i] = branch
            schema = '\n'.join(schema)
        return schema

    # Convert a Spark dataframe to a Pandas dataframe
    def sparkToPandas(self, df):
        dfp = df.toPandas()
        return dfp

    # Convert a Pandas dataframe to a Spark dataframe
    def pandasToSpark(self, df, forceStringType=True):
        if (forceStringType): df = df.astype(str)
        dfs = self.spark.createDataFrame(df)
        return dfs

    # Get the number of partitions from a Spark dataframe
    def getNumberOfPartitions(self, df):
        n = df.rdd.getNumPartitions()
        return n

    # Arrange the partitions number of a Spark dataframe (uses either coalesce or repartition)
    def arrangePartitions(self, df, nbrPartitions):
        df = self._arrangePartitions(df, nbrPartitions)
        return df

    # Organize the columns of a dataframe
    def organizeColumns(self, df, columns, atStart=False, atEnd=False):
        '''
        - Example 1:
        df = organizeColumns(df, columns=["NAME", "ADDRESS"])               => Filter only the two columns "NAME" and "ADDRESS"
        df = organizeColumns(df, columns=["NAME", "ADDRESS"], atStart=True) => Put at the beginning the two columns "NAME" and "ADDRESS"
        df = organizeColumns(df, columns=["NAME", "ADDRESS"], atEnd=True)   => Put at the end the two columns "NAME" and "ADDRESS"
        '''
        if (atStart or atEnd):
            rest = set(df.columns) - set(columns)
            diff = [col for col in df.columns if col not in columns]
            if (atEnd): columns = diff + list(columns)
            if (atStart): columns = list(columns) + diff
        df = df[columns]
        return df

    '''
    strReplace() is a useful function for replacements (standard way and/or with regular expressions).

    - Example:
    # Regular expression rules
    # arg1 is what to replace, arg2 is the replacement value, arg3=True means IgnoreCase (default=False)
    reRules = [
        ["^telephone$", "Phone", True],
        ["^cellular$", "Mobile", True],
        ["^unknown$", "", True],
        ["^yes$", "true", True],
        ["^no$", "false", True],
        ["a phone$", "the best PHONE", True]
    ]
    # Standard rules
    # arg1 is what to replace, arg2 is the replacement value
    stdRules = [
        ["Smith", "SMITH"]
    ]
    print(strReplace(string="TelephonE", reRules=reRules))
    print(strReplace(string="No", reRules=reRules))
    print(strReplace(string="YES", reRules=reRules))
    print(strReplace(string="I'm Mr Smith and I need a phone", stdRules=stdRules, reRules=reRules, reRulesFirst=True))

    - Output:
    Phone
    false
    true
    I'm Mr SMITH and I need the best PHONE
    ''';
    # Useful method in order to make standard and regularExpression replaces into strings
    def strReplace(self, string, stdRules=None, reRules=None, reRulesFirst=False):
        # Standard replacements
        def stdReplace(string, stdRules=None):
            if (string != None and stdRules != None):
                for rule in stdRules:
                    string = string.replace(rule[0], rule[1])
            return string
        # Replacements with regular expressions
        def regReplace(string, reRules=None):
            # Compiling regular expression rules
            def compileReRules(reRules):
                import re
                cRules = []
                for rule in reRules:
                    expression = rule[0]
                    if (len(rule) > 2 and rule[2] == True): cRules.append(re.compile(expression, re.IGNORECASE))
                    else: cRules.append(re.compile(expression))
                if (len(cRules) == 0): cRules = None
                return cRules
            if (string != None and reRules != None):
                cRules = compileReRules(reRules)
                for i, cRule in enumerate(cRules):
                    value = reRules[i][1]
                    string = cRule.sub(value, string)
            return string
        # Call replacements with regular expressions first
        if (reRulesFirst):
            string = regReplace(string, reRules)
            string = stdReplace(string, stdRules)
        # Call standard replacements first
        else:
            string = stdReplace(string, stdRules)
            string = regReplace(string, reRules)
        # Return the modified string
        return string

    # ===================
    # = PRIVATE METHODS =
    # ===================

    # Load Parquet and Avro formats into a Spark dataframe
    def _load(self, inputDir, inferSchema=False, mergeSchema=True, inputFormat='parquet', partitions=None):
        # Prepare the arguments
        inputDir = inputDir.strip()
        if (inputDir.endswith('/')): inputDir = inputDir[:-1].strip()
        if (inputFormat == None): inputFormat = "parquet"
        inputFormat = inputFormat.strip().lower()
        # Prepare the partitions sub-directories
        dirPartitions = []
        if (partitions != None):
            if (type(partitions) == list):
                for i, partition in enumerate(partitions):
                    partition = partition.strip().replace(' ', '')
                    if (partition.startswith('/')): partition = partition[1:].strip()
                    if (partition.endswith('/')): partition = partition[:-1].strip()
                    dirPartition = inputDir + '/' + partition
                    dirPartitions.append(dirPartition)
            else:
                dirPartitions.append(inputDir + '/' + str(partitions))
        # Adapt types
        if (inferSchema == True): inferSchema = "true"
        else: inferSchema = "false"
        if (mergeSchema == True): mergeSchema = "true"
        else: mergeSchema = "false"
        # Load with partitions (notion of basePath)
        if (partitions != None):
            if (inputFormat == "parquet"):
                ds = self.spark.read.option("basePath", inputDir).option("inferSchema", inferSchema).option("mergeSchema", mergeSchema).parquet(*dirPartitions)
            elif (inputFormat == "avro"):
                ds = self.spark.read.option("basePath", inputDir).option("inferSchema", inferSchema).option("mergeSchema", mergeSchema).avro(*dirPartitions)
        # Load without partitions
        else:
            if (inputFormat == "parquet"):
                ds = self.spark.read.option("inferSchema", inferSchema).option("mergeSchema", mergeSchema).parquet(inputDir)
            elif (inputFormat == "avro"):
                ds = self.spark.read.option("inferSchema", inferSchema).option("mergeSchema", mergeSchema).avro(inputDir)
        # Return the Spark result
        return ds

    # Return a df from a table name, or the df itself
    def _getDfFromObject(self, obj):
        if (type(obj) is str):
            objectName = str(obj)
            df = self.spark.sql("SELECT * FROM " + objectName)
        else: df = obj
        return df

    # Convert a simple type to a Spark type (e.g: "string" to "StringType")
    def _getSparkClassType(self, shortType):
        defaultSparkClassType = "StringType"
        typesMapping = {
            "bigint"    : "LongType",
            "binary"    : "BinaryType",
            "boolean"   : "BooleanType",
            "byte"      : "ByteType",
            "date"      : "DateType",
            "decimal"   : "DecimalType",
            "double"    : "DoubleType",
            "float"     : "FloatType",
            "int"       : "IntegerType",
            "integer"   : "IntegerType",
            "long"      : "LongType",
            "numeric"   : "NumericType",
            "string"    : defaultSparkClassType,
            "timestamp" : "TimestampType"
        }
        sparkClassType = None
        try:
            sparkClassType = typesMapping[shortType]
        except:
            sparkClassType = defaultSparkClassType
        return sparkClassType

    # Arrange the partitions number of a Spark dataframe (uses either coalesce or repartition)
    def _arrangePartitions(self, df, nbrPartitions):
        n = df.rdd.getNumPartitions()
        if (n > nbrPartitions): df = df.coalesce(nbrPartitions)
        elif (n < nbrPartitions) : df = df.repartition(nbrPartitions)
        # if (n == nbrPartitions): df = df
        return df

    # Flatten a Spark dataset to a tabular structure (dataframe)
    def _flatten(self, df, separator='_'):
        import cytoolz.curried as tz
        aliased_columns = []
        for col_spec in self.getSchema(df):
            col_spec = col_spec[:-1]
            c = tz.get_in(col_spec, df)
            if len(col_spec) == 1:
                aliased_columns.append(c)
            else:
                aliased_columns.append(c.alias(separator.join(col_spec)))
        return df.select(aliased_columns)

    # Flatten array columns into a Spark dataframe
    def _flattenArray(self, df):
        import cytoolz.curried as tz
        from pyspark.sql.functions import explode
        have_array = False
        aliased_columns = []
        i=0
        for column, t_column in df.dtypes:
            if t_column.startswith('array<') and i == 0:
                have_array = True
                c = explode(df[column]).alias(column)
                i = i+ 1
            else:
                c = tz.get_in([column], df)
            aliased_columns.append(c)
        return (df.select(aliased_columns), have_array)

    # Remove accents from a text
    def _removeAccents(self, text, dropReplacementCharater=False):
        isStr = False
        isUnicode = False
        if isinstance(text, str):
            isStr = True
        elif isinstance(text, unicode):
            isUnicode = True
        # --------------------
        # | STR type (UTF-8) |
        # --------------------
        if (isStr):
            # à, â, ä, À, Â, Ä
            text = text.replace('à', 'a')
            text = text.replace('â', 'a')
            text = text.replace('ä', 'a')
            text = text.replace('À', 'a')
            text = text.replace('Â,', 'a')
            text = text.replace('Ä', 'a')
            text = text.replace('\xc3\xa0', 'a')
            text = text.replace('\xc3\xa2', 'a')
            text = text.replace('\xc3\xa4', 'a')
            text = text.replace('\xc3\x80', 'A')
            text = text.replace('\xc3\x82', 'A')
            text = text.replace('\xc3\x84', 'A')
            # é, è, ê, ë, É, È, Ê, Ë
            text = text.replace('é', 'e')
            text = text.replace('è', 'e')
            text = text.replace('ê', 'e')
            text = text.replace('ë', 'e')
            text = text.replace('É', 'e')
            text = text.replace('È', 'e')
            text = text.replace('Ê', 'e')
            text = text.replace('Ë', 'e')
            text = text.replace('\xc3\xa9', 'e')
            text = text.replace('\xc3\xa8', 'e')
            text = text.replace('\xc3\xaa', 'e')
            text = text.replace('\xc3\xab', 'e')
            text = text.replace('\xc3\x89', 'E')
            text = text.replace('\xc3\x88', 'E')
            text = text.replace('\xc3\x8a', 'E')
            text = text.replace('\xc3\x8b', 'E')
            # î, ï, Î, Ï
            text = text.replace('î', 'i')
            text = text.replace('ï', 'i')
            text = text.replace('Î', 'i')
            text = text.replace('Ï', 'i')
            text = text.replace('\xc3\xae', 'i')
            text = text.replace('\xc3\xaf', 'i')
            text = text.replace('\xc3\xae', 'I')
            text = text.replace('\xc3\xaf', 'I')
            # ô, ö, Ô, Ö
            text = text.replace('ô', 'o')
            text = text.replace('ö', 'o')
            text = text.replace('Ô', 'o')
            text = text.replace('Ö', 'o')
            text = text.replace('\xc3\xb4', 'o')
            text = text.replace('\xc3\xb6', 'o')
            text = text.replace('\xc3\x94', 'O')
            text = text.replace('\xc3\x96', 'O')
            # ù, û, ü, Ù, Û, Ü
            text = text.replace('ù', 'u')
            text = text.replace('û', 'u')
            text = text.replace('ü', 'u')
            text = text.replace('Ù', 'u')
            text = text.replace('Û', 'u')
            text = text.replace('Ü', 'u')
            text = text.replace('\xc3\xb9', 'u')
            text = text.replace('\xc3\xbb', 'u')
            text = text.replace('\xc3\xbc', 'u')
            text = text.replace('\xc3\x99', 'U')
            text = text.replace('\xc3\x9b', 'U')
            text = text.replace('\xc3\x9c', 'U')
        # ----------------
        # | UNICODE type |
        # ----------------
        if (isUnicode):
            # à, â, ä, À, Â, Ä
            text = text.replace(u'\xe0', 'a')
            text = text.replace(u'\xe2', 'a')
            text = text.replace(u'\xe4', 'a')
            text = text.replace(u'\xc0', 'A')
            text = text.replace(u'\xc2', 'A')
            text = text.replace(u'\xc4', 'A')
            # é, è, ê, ë, É, È, Ê, Ë
            text = text.replace(u'\xe9', 'e')
            text = text.replace(u'\xe8', 'e')
            text = text.replace(u'\xea', 'e')
            text = text.replace(u'\xeb', 'e')
            text = text.replace(u'\xc9', 'E')
            text = text.replace(u'\xc8', 'E')
            text = text.replace(u'\xca', 'E')
            text = text.replace(u'\xcb', 'E')
            # î, ï, Î, Ï
            text = text.replace(u'\xee', 'i')
            text = text.replace(u'\xef', 'i')
            text = text.replace(u'\xce', 'I')
            text = text.replace(u'\xcf', 'I')
            # ô, ö, Ô, Ö
            text = text.replace(u'\xf4', "o")
            text = text.replace(u'\xf6', "o")
            text = text.replace(u'\xd4', "o")
            text = text.replace(u'\xd6', "o")
            # ù, û, ü, Ù, Û, Ü
            text = text.replace(u'\xf9', "u")
            text = text.replace(u'\xfb', "u")
            text = text.replace(u'\xfc', "u")
            text = text.replace(u'\xd9', "U")
            text = text.replace(u'\xdb', "U")
            text = text.replace(u'\xdc', "U")
            # '
            #text = text.replace(u'\x92', "'")
            # œ
            #text = text.replace(u'\x9c', "'")
            #text = text.replace('\\x89', "‰")
            # Replacement character
            if (dropReplacementCharater == True): text = text.replace(u'\fffd', "")
        return text

######################
# SparkFsUtils class #
######################
# Spark FileSystem utility (works with HDFS and local FS)
class SparkFsUtils:

    sc = None
    serviceUri = None
    fs = None
    fu = None
    listPaths = None

    # Constructor
    def __init__(self, sparkContext, serviceUri=None):
        self.sc = sparkContext
        self.serviceUri = serviceUri
        self.fs = self._getFileSystem(serviceUri)
        self.fu = self._getFileUtil()

    # ============
    # = Examples =
    # ============
    # - FS or HDFS (for HDFS it will access to the files from '/etc/hadoop/conf'):
    # listPaths = getFsOrHdfsPaths(sc, "None, "/data/mydata")

    # - HDFS only (by specifying the NameNode):
    # listPaths = getFsOrHdfsPaths(sc, "hdfs://10.8.18.3:8020", "/data/mydata")
    # - FS only (by forcing the parent path with the "file:" prefixe):
    # listPaths = getFsOrHdfsPaths(sc, None, "file:/home/datalab/data/mydata")
    # - PRINT by filtering:
    # for aPath in listPaths:
    #     if (aPath.isFile()): print("FILE: " + str(aPath.getPath()))
    #     if (aPath.isDir()): print("DIR: " + str(aPath.getPath()))
    # Scan a file system from a parent directory (works with HDFS and local FS)
    def scan(self, parentPath, recursive=False):
        self._scan(parentPath, recursive)
        return

    # Get all scanned paths objects (works with HDFS and local FS)
    def getAll(self):
        return self.listPaths

    # Get all scanned paths (works with HDFS and local FS)
    def getPaths(self):
        listPaths = None
        if (self.listPaths != None):
            listPaths = []
            for aPath in self.listPaths:
                listPaths.append(str(aPath.getPath()))
        return listPaths

    # Get all scanned files (works with HDFS and local FS)
    def getFiles(self, paths=None):
        if (paths == None): paths = self.listPaths
        listFiles = None
        if (paths != None):
            listFiles = []
            for aPath in paths:
                if (aPath.isFile()): listFiles.append(str(aPath.getPath()))
        return listFiles

    # Get all scanned directories (works with HDFS and local FS)
    def getDirectories(self, paths=None):
        if (paths == None): paths = self.listPaths
        listDirs = None
        if (paths != None):
            listDirs = []
            for aPath in paths:
                if (aPath.isDir()): listDirs.append(str(aPath.getPath()))
        return listDirs

    # Get filtered paths (works with HDFS and local FS)
    def getFilteredPaths(self, startsWith, contains, endsWith):
        return self.convertPathsToStr(self.filterPaths(self.listPaths, startsWith, contains, endsWith))
        '''
        listStrPaths = None
        if (self.listPaths != None):
            listStrPaths = []
            for aPath in self.listPaths:
                strPath = str(aPath.getPath()).strip()
                isOk = True
                if (isOk):
                    if (not(startsWith==None) and not strPath.startswith(startsWith)): isOk = False
                if (isOk):
                    if (not(endsWith==None) and not strPath.endswith(endsWith)): isOk = False
                if (isOk):
                    if (not(contains==None) and not (contains in strPath)): isOk = False
                if (isOk): listStrPaths.append(strPath)
            if (len(listStrPaths) == 0): listStrPaths = None
        return listStrPaths
        '''

    # Filter paths (works with HDFS and local FS)
    def filterPaths(self, paths, startsWith, contains, endsWith):
        filteredPaths = None
        if (paths != None):
            filteredPaths = []
            for aPath in paths:
                strPath = str(aPath.getPath()).strip()
                if (strPath.startswith("file:")): strPath = strPath[5:]
                isOk = True
                if (isOk):
                    if (not(startsWith==None) and not strPath.startswith(startsWith)): isOk = False
                if (isOk):
                    if (not(endsWith==None) and not strPath.endswith(endsWith)): isOk = False
                if (isOk):
                    if (not(contains==None) and not (contains in strPath)): isOk = False
                if (isOk): filteredPaths.append(aPath)
            if (len(filteredPaths) == 0): filteredPaths = None
        return filteredPaths

    def convertPathsToStr(self, paths):
        convertedPaths = None
        if (paths != None):
            convertedPaths = []
            for aPath in paths:
                strPath = str(aPath.getPath()).strip()
                convertedPaths.append(strPath)
            if (len(convertedPaths) == 0): convertedPaths = None
        return convertedPaths

    # Print the list of all scanned paths (works with HDFS and local FS)
    def printAll(self):
        for aPath in self.listPaths:
            if (aPath.isFile()): print("FILE: " + str(aPath.getPath()))
            if (aPath.isDir()): print("DIRECTOY: " + str(aPath.getPath()))

    # Rename a path by a new one (works with HDFS and local FS)
    def rename(self, src, dest):
        Path = self.sc._gateway.jvm.org.apache.hadoop.fs.Path
        srcPath = Path(src)
        destPath = Path(dest)
        self.fs.rename(srcPath, destPath)

    # Move a path to a new one (works with HDFS and local FS)
    def move(self, src, dest):
        File = self.sc._gateway.jvm.java.io.File
        srcFile = File(src)
        destFile = File(dest)
        self.fu.replaceFile(srcFile, destFile)

    # Delete a directory and all its contents (works with HDFS and local FS)
    def fullyDelete(self, aPath):
        File = self.sc._gateway.jvm.java.io.File
        aFile = File(aPath)
        self.fu.fullyDelete(aFile)

    # Delete the contents of a directory, not the directory itself (works with HDFS and local FS)
    def fullyDeleteContents(self, aPath):
        File = self.sc._gateway.jvm.java.io.File
        aFile = File(aPath)
        self.fu.fullyDeleteContents(aFile)

    # ========
    # = Copy =
    # ========
    #def copy(self, ...):
    #    # Use FileUtil
    #    # See https://stackoverflow.com/questions/5507804/moving-files-in-hadoop-using-the-java-api

    # =========================================
    # = Delete a path (a file or a directory) =
    # =========================================
    # Mark a path to be deleted when FileSystem API is closed
    # When the JVM shuts down, all FileSystem objects will be closed automatically
    # Then, the marked path will be deleted as a result of closing the FileSystem
    # The path has to exist in the file system
    #def deleteOnExit(self, aPath):
    #    self.fs.deleteOnExit(aPath)

    # No more filesystem operations are needed
    # Will release any held locks
    # Close a filesystem (no more filesystem operations are needed, will release any held locks)
    def close(self):
        self.fs.close(aPath)

    # Close all cached filesystems
    # Be sure those filesystems are not used anymore
    # Close all filesystems (close all cached filesystems, be sure those filesystems are not used anymore)
    def closeAll(self):
        self.fs.closeAll(aPath)

    # Split a file path into (parentPath, baseName, fileName, fileExt)
    def splitFilePath(self, strFilePath):
        import os
        parentPath = os.path.dirname(strFilePath)
        baseName = os.path.basename(strFilePath)
        fileName, fileExt = os.path.splitext(strFilePath)
        fileName = os.path.basename(fileName)
        if (fileExt.strip() == ""): fileExt = None
        if (fileExt != None and fileExt.startswith(".")): fileExt = fileExt[1:]
        return parentPath, baseName, fileName, fileExt

    # Return a file's size (works with HDFS and local FS)
    def getSize(self, strFilePath):
        Path = self.sc._gateway.jvm.org.apache.hadoop.fs.Path
        filePath = Path(strFilePath)
        size = self.fs.getContentSummary(filePath).getLength()
        return size

    # Return a file's size taken in the whole cluster (works with HDFS)
    def getSizeInCluster(self, strFilePath):
        Path = self.sc._gateway.jvm.org.apache.hadoop.fs.Path
        filePath = Path(strFilePath)
        sizeInCluster = self.fs.getContentSummary(filePath).getSpaceConsumed()
        return sizeInCluster

    #########################
    # == PRIVATE FUNCTIONS ==
    #########################

    # Get the type of filesystem (works with HDFS and local FS)
    def _getFileSystem(self, serviceUri=None):
        FileSystem = self.sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
        Configuration = self.sc._gateway.jvm.org.apache.hadoop.conf.Configuration
        URI = self.sc._gateway.jvm.java.net.URI
        if (serviceUri == None):
            fs = FileSystem.get(Configuration())
        else:
            fs = FileSystem.get(URI(serviceUri), Configuration())
        return fs

    # Return a FileUtil instance (works with HDFS and local FS)
    def _getFileUtil(self):
        FileUtil = self.sc._gateway.jvm.org.apache.hadoop.fs.FileUtil
        fu = FileUtil()
        return fu

    # Scan files (works with HDFS and local FS)
    def _scan(self, parentPath, recursive=False):
        self.listPaths = self._scanFsOrHdfsPaths(parentPath, [], recursive)
        if (self.listPaths == []): self.listPaths = None

    # Return the local filesystem or hdfs paths (works with HDFS and local FS)
    def _getFsOrHdfsPaths(self, parentPath):
        #URI = self.sc._gateway.jvm.java.net.URI
        #Path = self.sc._gateway.jvm.org.apache.hadoop.fs.Path
        #FileSystem = self.sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
        #Configuration = self.sc._gateway.jvm.org.apache.hadoop.conf.Configuration
        Path = self.sc._gateway.jvm.org.apache.hadoop.fs.Path
        listPaths = self.fs.listStatus(Path(parentPath))
        return listPaths

    # Scan paths (works with HDFS and local FS)
    def _scanFsOrHdfsPaths(self, parentPath, globalListPaths, recursive=False):
        parentPath = parentPath.strip()
        if (parentPath.endswith("*")): parentPath = parentPath[0:-1]
        if (parentPath.endswith("/")): parentPath = parentPath[0:-1]
        continueLoop = True
        while continueLoop:
            listPaths = self._getFsOrHdfsPaths(parentPath)
            if (listPaths != None and listPaths != []):
                globalListPaths.extend(listPaths)
                if (recursive == True):
                    listDirs = []
                    for aPath in listPaths:
                        if (aPath.isDir()):
                            listDirs.append(str(aPath.getPath()))
                    if (listDirs != []):
                        for aDir in listDirs:
                            self._scanFsOrHdfsPaths(aDir, globalListPaths, recursive)
                            continueLoop = False
                    else: continueLoop = False
                else: continueLoop = False
            else: continueLoop = False
        return globalListPaths
