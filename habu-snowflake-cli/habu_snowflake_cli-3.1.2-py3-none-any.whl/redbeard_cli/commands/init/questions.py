from redbeard_cli import snowflake_utils


def install_handle_question_run_data_share_procedure(sf_connection):
    """
    Installs the handler for question run data share
    :param sf_connection:
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_QUESTION_RUN_DATA_SHARE() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id,  " + 
            " request_data:compute_account_id AS compute_account_id, " +
            " request_data:statement_hash AS statement_hash " + 
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";
            
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['QUESTION_DATA_SHARE', 'PENDING']
            });

            var rs = stmt.execute();    
            var questionDataShareParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var computeAccountId = rs.getColumnValue(3);
                var statementHash = rs.getColumnValue(4);
                
                questionDataShareParams.push({
                    'requestID': requestID,
                    'cleanRoomID': cleanRoomID, 
                    'computeAccountId': computeAccountId,
                    'statementHash': statementHash 
                })
            }
            
            for (var i = 0; i < questionDataShareParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.QUESTION_RUN_DATA_SHARE(:1, :2, :3, :4)',
                    binds: [
                        questionDataShareParams[i]['requestID'], 
                        questionDataShareParams[i]['cleanRoomID'],
                        questionDataShareParams[i]['computeAccountId'],
                        questionDataShareParams[i]['statementHash']
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

def install_question_run_data_share_procedure(sf_connection, share_restrictions: bool):
    """
    Installs question run data share procedure
    :param sf_connection:
    :param share_restrictions:
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.QUESTION_RUN_DATA_SHARE
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, COMPUTE_ACCOUNT_ID VARCHAR, STATEMENT_HASH VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            var partnerShareDb = "HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"

            snowflake.execute({
                sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) VALUES (:1, :2, :3)",
                binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH]
            })
            
            snowflake.execute({
                sqlText: "ALTER SHARE " + partnerShareDb + " ADD ACCOUNTS = :1 SHARE_RESTRICTIONS=%s",
                binds: [COMPUTE_ACCOUNT_ID]
            });
            
            snowflake.execute({
                sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                binds: ['COMPLETE', REQUEST_ID]
            });
                     
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
    $$;""" % share_restrictions
    snowflake_utils.run_query(sf_connection, sp_sql)
