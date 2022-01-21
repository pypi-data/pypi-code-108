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
    # query semplice
    sq = '{"queries":[{"id":"q0","fields":[{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY SEMPLICE------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query con cond semplice
    sq = '{"queries":[{"id":"q0","fields":[{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[{"field":{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false},"operator":"GOE","type":"NUMERIC","expression":false,"negate":false,"value":["4000"],"conditions":null}],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY 1COND------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query con 2 cond in AND
    sq = '{"queries":[{"id":"q0","fields":[{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[{"field":{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false},"operator":"GOE","type":"NUMERIC","expression":false,"negate":false,"value":["4000"],"conditions":null},{"field":{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false},"operator":"LOE","type":"NUMERIC","expression":false,"negate":false,"value":["10000"],"conditions":null}],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY 2COND------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query con OR
    sq = '{"queries":[{"id":"q0","fields":[{"column":"TOPICS","alias":"Topics","aggregation":null,"dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"STRING","expression":false},{"column":"PUBLISHED","alias":"PUBLISHED","aggregation":"YEAR","dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"DATE","expression":false}],"datasets":[{"dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8"}],"relationships":null,"where":[{"field":null,"operator":"OR","type":null,"expression":false,"negate":false,"value":null,"conditions":[{"field":{"column":"PUBLISHED","alias":"PUBLISHED","aggregation":"YEAR","dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"DATE","expression":false},"operator":"RANGE","type":"DATE","expression":false,"negate":false,"value":["2020-01-01 00:00:00","2020-12-31 23:59:59"],"conditions":null},{"field":{"column":"PUBLISHED","alias":"PUBLISHED","aggregation":"YEAR","dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"DATE","expression":false},"operator":"RANGE","type":"DATE","expression":false,"negate":false,"value":["2021-01-01 00:00:00","2021-12-31 23:59:59"],"conditions":null}]}],"orderBy":[{"field":"PUBLISHED","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY COND OR------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query con 3 cond, AND + OR
    sq = '{"queries":[{"id":"q0","fields":[{"column":"TOPICS","alias":"Topics","aggregation":null,"dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"STRING","expression":false},{"column":"PUBLISHED","alias":"PUBLISHED","aggregation":"YEAR","dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"DATE","expression":false}],"datasets":[{"dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8"}],"relationships":null,"where":[{"field":null,"operator":"AND","type":null,"expression":false,"negate":false,"value":null,"conditions":[{"field":{"column":"TOPICS","alias":"Topics","aggregation":null,"dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"STRING","expression":false},"operator":"IN","type":"STRING","expression":false,"negate":false,"value":["Other"],"conditions":null},{"field":null,"operator":"OR","type":null,"expression":false,"negate":false,"value":null,"conditions":[{"field":{"column":"PUBLISHED","alias":"PUBLISHED","aggregation":"YEAR","dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"DATE","expression":false},"operator":"RANGE","type":"DATE","expression":false,"negate":false,"value":["2020-01-01 00:00:00","2020-12-31 23:59:59"],"conditions":null},{"field":{"column":"PUBLISHED","alias":"PUBLISHED","aggregation":"YEAR","dataset":"94037f2f-38eb-4b5c-968e-f0a22e0d1169-DATA_TABLE-69e01670-46b7-4904-8373-29f26686efb8","internalDataType":"DATE","expression":false},"operator":"RANGE","type":"DATE","expression":false,"negate":false,"value":["2021-01-01 00:00:00","2021-12-31 23:59:59"],"conditions":null}]}]}],"orderBy":[{"field":"PUBLISHED","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY 3COND AND+OR------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query sorting
    sq = '{"queries":[{"id":"q0","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"DENOMINAZIONE_REGIONE","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY SORTING------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query limit
    sq = '{"queries":[{"id":"q0","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":5,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY LIMIT------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query top
    sq = '{"queries":[{"id":"q0","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":3,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY TOP------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query worst
    sq = '{"queries":[{"id":"q0","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"TOTALE_CASI","order":"ASC"}],"limit":3,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY WORST------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query comparison
    sq = '{"queries":[{"id":"q0","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[{"field":{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},"operator":"IN","type":"STRING","expression":false,"negate":false,"value":["Campania"],"conditions":null}],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true},{"id":"q1","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"DECEDUTI","alias":"Deceduti","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[{"field":{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},"operator":"IN","type":"STRING","expression":false,"negate":false,"value":["Lazio"],"conditions":null}],"orderBy":[{"field":"DECEDUTI","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY COMPARISON------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query trend semplice
    sq = '{"queries":[{"id":"q0","fields":[{"column":"NUOVI_POSITIVI","alias":"Nuovi positivi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"NUOVI_POSITIVI","order":"DESC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY TREND------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")

    # query nested trend
    sq = '{"queries":[{"id":"q0","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[],"orderBy":[{"field":"TOTALE_CASI","order":"DESC"}],"limit":2,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true},{"id":"q1","fields":[{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},{"column":"TOTALE_CASI","alias":"Totale casi","aggregation":"SUM","dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"NUMERIC","expression":false},{"column":"DATA","alias":"DATA","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"DATE","expression":false}],"datasets":[{"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7"}],"relationships":null,"where":[{"field":{"column":"DENOMINAZIONE_REGIONE","alias":"Denominazione regione","aggregation":null,"dataset":"f2c705dd-f63f-475b-95a9-c1ad20f33716-MYSQL-34b83631-1108-41c3-870f-cee0636c58c7","internalDataType":"STRING","expression":false},"operator":"IN","type":"STRING","expression":false,"negate":false,"value":["rs0.DENOMINAZIONE_REGIONE"],"conditions":null}],"orderBy":[{"field":"DATA","order":"ASC"}],"limit":50,"offset":null,"joinedSmartQuery":null,"pivot":null,"pivotableFields":null,"join":null,"valid":true}]}'
    sq_json = jsons.loads(sq, SmartQuery)
    print("------QUERY NESTED TREND------")
    print(sq_json)
    print(sq_json.spell_out())
    print("--------------------------")
