from redbeard_cli import snowflake_utils


def install_handle_new_question_runs_controller_procedure(sf_connection):
    """
    Installs the handler for new question runs
    :param sf_connection:
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_QUESTION_RUNS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
        
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, " +
            " request_data:result_table AS result_table, " +
            " request_data:result_table_ddl AS result_table_ddl, " +
            " request_data:accounts AS accounts, " +
            " request_data:compute_account_id AS compute_account_id, " +
            " request_data:statement_hash AS statement_hash, " + 
            " request_data:question_run_query AS question_run_query " +
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";
            
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_QUESTION_RUN', 'PENDING']
            });

            var rs = stmt.execute();    
            var newQuestionRunParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var resultTable = rs.getColumnValue(3);
                var resultTableDDL = rs.getColumnValue(4);
                var accounts = rs.getColumnValue(5);
                var computeAccountId = rs.getColumnValue(6);
                var statementHash = rs.getColumnValue(7);
                var query = rs.getColumnValue(8);
                
                newQuestionRunParams.push({
                    'requestID' : requestID,
                    'cleanRoomID' : cleanRoomID,
                    'resultTable' : resultTable,
                    'resultTableDDL' : resultTableDDL,
                    'accounts' : accounts,
                    'computeAccountId': computeAccountId,
                    'statementHash': statementHash,
                    'query' : query
                })
            }
            
            for (var i = 0; i < newQuestionRunParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_QUESTION_RUN(:1, :2, :3, :4, :5, :6, :7, :8)',
                    binds: [
                        newQuestionRunParams[i]['requestID'], 
                        newQuestionRunParams[i]['cleanRoomID'], 
                        newQuestionRunParams[i]['resultTable'], 
                        newQuestionRunParams[i]['resultTableDDL'], 
                        newQuestionRunParams[i]['accounts'],
                        newQuestionRunParams[i]['computeAccountId'],
                        newQuestionRunParams[i]['statementHash'],
                        newQuestionRunParams[i]['query']
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


def install_add_new_question_run_procedure(sf_connection):
    """
    Install the New question run stored procedure
    :param sf_connection:
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_QUESTION_RUN
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, RESULT_TABLE VARCHAR, RESULT_TABLE_DDL VARCHAR, ACCOUNTS_INPUT VARCHAR, COMPUTE_ACCOUNT_ID VARCHAR, STATEMENT_HASH VARCHAR, QUESTION_RUN_QUERY VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            
            var habuShareDb = "HABU_CR_" + sf_clean_room_id + "_HABU_SHARE"
            
            snowflake.execute({
                sqlText: RESULT_TABLE_DDL 
            });
            
            snowflake.execute({
                sqlText: "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM_RUN_RESULTS." + RESULT_TABLE + " TO SHARE " + habuShareDb
            });
            
            ACCOUNTS = ACCOUNTS_INPUT.split(",");
            
            for (var i = 0; i < ACCOUNTS.length; i++){
                var partnerShare = "HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
                var partnerShareDb = "HABU_CR_" + ACCOUNTS[i] + "_" + sf_clean_room_id + "_PARTNER_SHARE_DB"
                
                 snowflake.execute({
                    sqlText: "CREATE DATABASE IF NOT EXISTS " + partnerShareDb + " FROM SHARE " + ACCOUNTS[i] + "." + partnerShare + " COMMENT = 'HABU_" + ACCOUNTS[i] + "'"
                });
                
                snowflake.execute({
                    sqlText: "GRANT IMPORTED PRIVILEGES ON DATABASE " + partnerShareDb + " TO ROLE ACCOUNTADMIN"
                })
                snowflake.execute({
                    sqlText: "GRANT IMPORTED PRIVILEGES ON DATABASE " + partnerShareDb + " TO ROLE SYSADMIN"
                });
             }
             
            snowflake.execute({
                sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) VALUES (:1, :2, :3)",
                binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH]
            })
             
            snowflake.execute({sqlText: QUESTION_RUN_QUERY})
            
            snowflake.execute({
                sqlText: "DELETE FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS where ACCOUNT_ID = :1 and CLEAN_ROOM_ID = :2 and STATEMENT_HASH = :3",
                binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH]
            })

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
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)
