from redbeard_cli import snowflake_utils
from redbeard_cli.commands.init.new_clean_room import (
    install_new_clean_room_stored_procedure,
    install_handle_new_clean_rooms_procedure
)
from redbeard_cli.commands.init.new_dataset import (
    install_handle_new_datasets_procedure,
    install_create_new_dataset_procedure
)
from redbeard_cli.commands.init.question_runs import (
    install_handle_new_question_runs_controller_procedure,
    install_add_new_question_run_procedure
)
from redbeard_cli.commands.init.questions import (
    install_handle_question_run_data_share_procedure,
    install_question_run_data_share_procedure
)


def install_clean_room_objects(sf_connection, organization_id: str, customer_account_id: str, share_restrictions: bool):

    install_habu_error_handler_procedure(sf_connection)
    install_habu_log_handler_procedure(sf_connection)
    install_habu_controller_procedure(sf_connection)

    install_handle_new_clean_rooms_procedure(sf_connection)
    install_new_clean_room_stored_procedure(sf_connection, share_restrictions)

    install_create_new_dataset_procedure(sf_connection)
    install_handle_new_datasets_procedure(sf_connection)

    install_handle_question_run_data_share_procedure(sf_connection)
    install_question_run_data_share_procedure(sf_connection, share_restrictions)

    install_handle_new_question_runs_controller_procedure(sf_connection)
    install_add_new_question_run_procedure(sf_connection)

    # at this point, we have accepted the share for the organization database from the habu account
    # habu_org_xxx_db contains a table called clean_room_requests that is shared with the customer
    # we are now going to setup a stream for the clean_room_requests table so that we can setup
    # the machinery for db-rpc
    setup_stream_sql = """CREATE OR REPLACE STREAM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS_STREAM
    ON TABLE HABU_ORG_%s_SHARE_DB.CLEAN_ROOM.CLEAN_ROOM_REQUESTS
    APPEND_ONLY=TRUE
    COMMENT = 'HABU_%s'""" % (organization_id, customer_account_id)
    snowflake_utils.run_query(sf_connection, setup_stream_sql)

    # stream has been setup, now create a task that listens to the stream and triggers the
    # PROCESS_ORG_REQUEST stored procedure to process pending clean room requests
    task_sql = """CREATE OR REPLACE TASK HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS_TASK
    SCHEDULE = '1 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS_STREAM') 
    AS CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.PROCESS_ORG_REQUEST();"""
    snowflake_utils.run_query(sf_connection, task_sql)

    # tasks are created in 'suspend' mode and need to 'resumed' explictly
    snowflake_utils.run_query(
        sf_connection,
        "ALTER TASK HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS_TASK RESUME;"
    )


def install_habu_error_handler_procedure(sf_connection):
    """
    Install stored procedure that will add error to the error table.

    :param sf_connection: the Snowflake connection object used to communicate with Snowflake
    :return:
    """
    er_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ERROR
    (ERROR_CODE DOUBLE, ERROR_STATE STRING, ERROR_MESSAGE STRING, ERROR_STACK_TRACE STRING, 
    REQUEST_ID VARCHAR, PROC_NAME VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        snowflake.execute({
              sqlText: `INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_ERRORS
               (CODE, STATE, MESSAGE, REQUEST_ID, PROC_NAME, STACK_TRACE, CREATED_AT)
               VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP())`
              ,binds: [ERROR_CODE, ERROR_STATE, ERROR_MESSAGE, REQUEST_ID, PROC_NAME, ERROR_STACK_TRACE]
              });

        return "SUCCESS";
    $$;"""
    snowflake_utils.run_query(sf_connection, er_sql)

def install_habu_log_handler_procedure(sf_connection):
    """
    Install stored procedure that will add error to the error table.

    :param sf_connection: the Snowflake connection object used to communicate with Snowflake
    :return:
    """
    er_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.SP_LOGGER
    (LOG_MESSAGE VARCHAR, REQUEST_ID VARCHAR, PROC_NAME VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        snowflake.execute({
              sqlText: `INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_LOGS
               (LOG_MESSAGE, REQUEST_ID, PROC_NAME, CREATED_AT)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP())`
              ,binds: [LOG_MESSAGE, REQUEST_ID, PROC_NAME]
              });

        return "SUCCESS";
    $$;"""
    snowflake_utils.run_query(sf_connection, er_sql)


def install_habu_controller_procedure(sf_connection):
    """
    Install stored procedure that will be called when a new clean room request is generated
    via the Habu application. The Controller procedure calls individual stored procedures
    to handle various types of clean room requests.  For example, HANDLE_NEW_CLEAN_ROOMS is
    called to process NEW_CLEAN_ROOM requests.

    :param sf_connection: the Snowflake connection object used to communicate with Snowflake
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.PROCESS_ORG_REQUEST()
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            // copy all new requests from stream into a local table to reset the stream
            var sqlCommand = "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS (ID, REQUEST_TYPE, REQUEST_DATA, CREATED_AT, UPDATED_AT, REQUEST_STATUS) (SELECT ID, REQUEST_TYPE, REQUEST_DATA, CREATED_AT, UPDATED_AT, REQUEST_STATUS FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS_STREAM)";
            snowflake.execute({sqlText: sqlCommand});
            
            var stmt = snowflake.createStatement({sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_CLEAN_ROOMS();'})
            stmt.execute();
            
            var stmt = snowflake.createStatement({sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_DATASETS();'})
            stmt.execute();
                        
            var stmt = snowflake.createStatement({sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_QUESTION_RUN_DATA_SHARE();'})
            stmt.execute();
    
            var stmt = snowflake.createStatement({sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_QUESTION_RUNS();'})
            stmt.execute();
    
    
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
