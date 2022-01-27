import jsons
from askdata.smartquery import *

if __name__ == '__main__':
    # TEST SmartQuery Object
    field1 = Field(column='{{measure.A}}', aggregation="MAX", dataset='{{dataset.A}}', entityType="P_MEASURE", alias="max_measure")
    field2 = Field(column='{{dimension.A}}', dataset='{{dataset.B}}', entityType="P_DIMENSION")
    field3 = Field(column='{{timeDimension.A}}', dataset='{{dataset.C}}', entityType="P_TIMEDIM", aggregation="year")
    from1 = From('{{dataset.A}}')
    from2 = From('{{dataset.B}}')
    from3 = From('{{dataset.C}}')
    field4 = Field(column="{{unknownDateDimension.A}}")
    condition1 = Condition(field4, "FROM", direction="NEXT", steps="{{number.A}}", interval="{{timeDimension.B}}")
    condition2 = Condition(field1, "LOE", ["{{number.B}}"])
    condition3 = Condition(field2, "IN", ["{{entity.A}}"])
    condition4 = Condition(field4, "RANGE", value=["{{timePeriodStart.A}}", "{{timePeriodEnd.A}}"])
    sorting1 = Sorting("{{measure.A}}", SQLSorting.DESC)
    component = ChartComponent(type='chart', queryId="0", chartType='LINE')
    query1 = Query(fields=[field1, field2, field3], datasets=[from1, from2, from3], where=[condition1, condition2, condition3, condition4],
                   orderBy=[sorting1], limit=10)
    smartquery = SmartQuery(queries=[query1], components=[component])
    dump = jsons.dumps(smartquery)
    print(dump)
    smartquery = jsons.loads(dump, SmartQuery)
    print(jsons.dumps(smartquery))
    print(smartquery)
    print(smartquery.queries[0].to_sql())
    # print("ORIGINAL JSON: ", dump)
    # compressed_json = SmartQuery.compress(dump)
    # print("COMPRESSED JSON: ", compressed_json)
    # decompressed_json = SmartQuery.decompress(compressed_json)
    # print("DECOMPRESSED JSON: ", decompressed_json)
    # print(str(dump) == decompressed_json)

    # TEST SPELL OUT
    # smartquerty spellout
    sq = SmartQuery(queries=[Query(
        fields=[Field(column="ADDRESS", alias="Address", internalDataType="STRING", sourceDataType="CLOB"),
                Field(column="RENOVATION_DATE", alias="renovation_date", internalDataType="DATE", sourceDataType="TIME")],
        orderBy=[Sorting(field="ADDRESS", order=SQLSorting.DESC),
                 Sorting(field="RENOVATION_DATE", order=SQLSorting.DESC)],
        limit=8,
        offset=0
    )])
    print(sq.spell_out())
