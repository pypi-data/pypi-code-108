from redbeard_cli import snowflake_utils


def install_handle_new_datasets_procedure(sf_connection):
    """
    Installs handler for new_datasets
    :param sf_connection:
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_DATASETS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT " + 
                                    " id AS request_id, " + 
                                    " request_data:clean_room_id AS clean_room_id, " +
                                    " request_data:source_db AS source_db, " + 
                                    " request_data:view_name AS view_name, " +
                                    " request_data:view_sql AS view_sql, " + 
                                    " request_data:available_values_sql AS available_values_sql " + 
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_DATASET', 'PENDING']
            });

            var rs = stmt.execute();    
            var newDatasetParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var sourceDB = rs.getColumnValue(3);
                var viewName = rs.getColumnValue(4);
                var viewSql = rs.getColumnValue(5);
                var availableValuesSql = rs.getColumnValue(6);
                newDatasetParams.push({
                    'rID': requestID, 
                    'crID': cleanRoomID, 
                    'sourceDB': sourceDB, 
                    'vn': viewName, 
                    'vs': viewSql,
                    'avs': availableValuesSql
                })
            }

            for (var i = 0; i < newDatasetParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_DATASET(:1, :2, :3, :4, :5, :6)',
                    binds: [
                        newDatasetParams[i]['rID'], 
                        newDatasetParams[i]['crID'],
                        newDatasetParams[i]['sourceDB'], 
                        newDatasetParams[i]['vn'], 
                        newDatasetParams[i]['vs'],
                        newDatasetParams[i]['avs']
                    ]
                });        
                stmt.execute();
            }        
            result = "SUCCESS";
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, "", Object.keys(this)[0]
                ]
            });        
            var res = stmt.execute();
        }
        return result;
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_create_new_dataset_procedure(sf_connection):
    """
    Handles new data set command
    :param sf_connection:
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_DATASET
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, SOURCE_DB VARCHAR, VIEW_NAME VARCHAR, VIEW_SQL VARCHAR, AVAILABLE_VALUES_SQL VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            
            var habuShareDb = "HABU_CR_" + sf_clean_room_id + "_HABU_SHARE"
            var partnerShareDb = "HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"

            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE " + habuShareDb
            })
            
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE " + partnerShareDb
            })
            
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE HABU_DATA_CONNECTIONS  TO SHARE " + habuShareDb
            })

            snowflake.execute({sqlText: VIEW_SQL});
            
            if (AVAILABLE_VALUES_SQL !== "NONE") {
                snowflake.execute({sqlText: AVAILABLE_VALUES_SQL});
            
                snowflake.execute({
                    sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_AVAILABLE_VALUES TO SHARE " + habuShareDb
                });
            }
            
            var policySql = "CREATE OR REPLACE ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_POLICY AS (query_clean_room_id VARCHAR) " + 
            "RETURNS BOOLEAN -> " + 
            "CASE " + 
            " WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN') THEN TRUE " + 
            " WHEN EXISTS (SELECT 1 FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ALLOWED_STATEMENTS WHERE " + 
            " account_id = CURRENT_ACCOUNT() AND statement_hash = SHA2(CURRENT_STATEMENT()) " + 
            " AND clean_room_id = QUERY_CLEAN_ROOM_ID) " + 
            " THEN TRUE END;";

            var policyStmt = snowflake.createStatement({sqlText: policySql});
            policyStmt.execute();

            snowflake.execute({
                sqlText: "ALTER VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + " ADD ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_POLICY ON (clean_room_id)"
            });
            

            snowflake.execute({
                sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + " TO SHARE " + partnerShareDb
            });
	    
            snowflake.execute({
                sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                binds: ['COMPLETE', REQUEST_ID]
            })

            result = "SUCCESS";
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, REQUEST_ID, Object.keys(this)[0]
                ]
            });        
            var res = stmt.execute();
        }
        return result;
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)
