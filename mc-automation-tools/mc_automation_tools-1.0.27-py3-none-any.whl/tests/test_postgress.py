"""Unittest for postgress client adapter"""
import os
import json
from datetime import datetime as dt
# dt = str(datetime.now(timezone.utc))

from mc_automation_tools import postgres
user = os.environ['PG_USER']
password = os.environ['PG_PASS']
host = os.environ['PG_HOST']
db_name = os.environ['PG_DB_NAME']
table_name = 'test_full'

entity_sample = {"geo_json": {
    "type": "Polygon",
    "coordinates": [
        [
            [35.201037526130676, 31.769924871200327],
            [35.20086854696274, 31.769892946554663],
            [35.201058983802795, 31.76914499456106],
            [35.20123064517975, 31.769181480164423],
            [35.201037526130676, 31.769924871200327]
        ]
    ]
}}
geo_json = json.dumps(entity_sample['geo_json'])
entity_sample = json.dumps(entity_sample)
uuid = "'acf8c600-423f-402c-815a-f986c34352ec'"

# geo_json = entity_sample["geo_json"]
# geo_json= entity_sample
command = f'INSERT INTO "v_buildings"("entity_id","layer_id","name","type",dateCreation,updateCreation,"polygon","json_object")' \
          f"VALUES({uuid},'416','building_1','building','{str(dt.now())}','{str(dt.now())}',ST_GeomFromGeoJSON('{geo_json}'),'{entity_sample}')"
def test_connection():
    """This test check connection to db"""
    client = postgres.PGClass(host, db_name, user, password)
    commands = ["CREATE TABLE v_buildings "
                "(entity_id UUID PRIMARY KEY,"
                "layer_id VARCHAR(255) NOT NULL,"
                "name VARCHAR(255),"
                "type VARCHAR(255),"
                "dateCreation TIMESTAMP NOT NULL,"
                "updateCreation TIMESTAMP NOT NULL,"
                "polygon geometry,"
                "json_object JSON NOT NULL)",
                "CREATE INDEX geo_coordinate_idx ON v_buildings USING GIST(polygon)"]

    client.command_execute(commands)


# command = f'INSERT INTO "v_buildings"("entity_id","name","type","dateCreation","updateCreation","polygon",json_object' \
#           f'VALUES("{uuid}","416","building_1","building",{dt},{dt},{entity_sample["geo_json"]},{json.dumps(entity_sample)} )'
def test_insert(command):
    client = postgres.PGClass(host, db_name, user, password)
    client.command_execute([command])
# test_connection()
# test_insert(command)
# ST_GeomFromGeoJSON()
def test_get_column(table_name, column_name):
    client = postgres.PGClass(host, db_name, user, password)
    res = client.get_column_by_name(table_name, column_name)
    return res
geo_json_test = {'type': 'Polygon', 'coordinates': [[[-76.904982, 38.894971], [-76.904858, 38.895051], [-76.904982, 38.894971]]]}

def test_update_column(uuid):
    client = postgres.PGClass(host, db_name, user, password)
    client.update_value_by_pk('entity_id', uuid, 'v_buildings', 'polygon', json.dumps(geo_json_test))

def test_polygon_convertor(uuid):
    client = postgres.PGClass(host, db_name, user, password)
    res = client.polygon_to_geojson('polygon','v_buildings', 'entity_id', uuid)
    return res

def test_delete_row(uuid):
    client = postgres.PGClass(host, db_name, user, password)
    client.delete_row_by_id('v_buildings', 'entity_id', uuid)

def test_drop_table(table_name):
    client = postgres.PGClass(host, db_name, user, password)
    client.drop_table(table_name)

def test_truncate_table(table_name):
    client = postgres.PGClass(host, db_name, user, password)
    client.truncate_table(table_name)

res = test_get_column('v_buildings', 'entity_id')

def test_multi_get(table_name):
    client = postgres.PGClass(host, db_name, user, password)
    args = ["000075a3-d5ba-463a-953c-d40d700cac0b", "0001a442-f24e-45e6-9c9f-2059d918a8de", "0000dc0d-3ef6-4451-ba9d-a64ca04a7fe6", "0003624e-b970-44db-aced-12ae2c05f793"]
    res = client.get_by_n_argument(table_name, 'entity_id', args,'json_object')
    return res
# test_update_column(res[0])
# uuid = res[0]
# res = test_get_column('v_buildings', 'polygon')
# res = test_polygon_convertor(uuid)
#
# print(res)
# test_delete_row(uuid)
# test_drop_table('v_buildings')
# test_truncate_table('v_buildings')

def test_multi_row():
    # v= [('00000543-1b1f-4890-b7f3-f8de46b4ced2', "{'g':1}"),('000105f4-cf53-4ad4-b633-b580e17513e6',"{'g':1}"),('0003a8b9-61bd-491c-bd12-897e77fd3208',"{'g':1}")]
    v= [('00000543-1b1f-4890-b7f3-f8de46b4ced2', json.dumps({'g':1})),('000105f4-cf53-4ad4-b633-b580e17513e6',json.dumps({'g':1})),('0003a8b9-61bd-491c-bd12-897e77fd3208',json.dumps({'g':1}))]
    client = postgres.PGClass(host, db_name, user, password)
    client.update_multi_with_multi('v_buildings','entity_id','json_object',v,'uuid','json')


res = test_multi_get('v_buildings')
# for r in res:
#     print('\n',r,'\n')


# test_multi_row()
