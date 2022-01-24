from redbeard_cli import snowflake_utils

# Recording these commands over here but they are not executed by our customers
# These are executed bu Habu in the Habu Snowflake account to share the ID Graph database and tables
# with our customers


def init(sf_connection):
    """
    Initialize the Habu ID Graph share objects.
    Create the share and add the corresponding schema and tables to the ID Graph Share

    :param sf_connection: the Snowflake connection to use (this is a connection to the Habu Snowflake account)
    :return:
    """
    snowflake_utils.run_query(sf_connection, "CREATE OR REPLACE SHARE HABU_ID_GRAPH_SHARE;")
    snowflake_utils.run_query(
        sf_connection,
        "GRANT USAGE ON DATABASE :1 TO SHARE HABU_ID_GRAPH_SHARE;",
        ["HABU_ORG_66663BAF74724EB4AC7FB336A11E8B9A"]
    )
    snowflake_utils.run_query(
        sf_connection,
        "GRANT USAGE ON SCHEMA :1.PUBLIC TO SHARE HABU_ID_GRAPH_SHARE;",
        ["HABU_ORG_66663BAF74724EB4AC7FB336A11E8B9A"]
    )
    snowflake_utils.run_query(
        sf_connection,
        "GRANT SELECT ON TABLE :1.PUBLIC.MAID_ID_GRAPH TO SHARE HABU_ID_GRAPH_SHARE;",
        ["HABU_ORG_66663BAF74724EB4AC7FB336A11E8B9A"]
    )
    snowflake_utils.run_query(
        sf_connection,
        "GRANT SELECT ON TABLE :1.PUBLIC.EMAIL_ID_GRAPH TO SHARE HABU_ID_GRAPH_SHARE;",
        ["HABU_ORG_66663BAF74724EB4AC7FB336A11E8B9A"]
    )


def share_id_graph_with_account(sf_connection, customer_account_id: str):
    """
    Add the specified customer account to the Habu ID Graph Share.

    :param sf_connection: the Snowflake connection to use (this is a connection to the Habu Snowflake account)
    :param customer_account_id: the Snowflake Account ID of the customer
    :return:
    """
    snowflake_utils.run_query(
        sf_connection,
        "ALTER SHARE HABU_ID_GRAPH_SHARE ADD ACCOUNTS = :1;",
        [customer_account_id.upper()]
    )

