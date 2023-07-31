#!/usr/bin/env python3.9
import os
import mysql.connector

# Define the databases
databases = {
    'master': {
        'DB_HOST': os.getenv('DB_HOST_MASTER'),
        'DB_USER': os.getenv('DB_USER_MASTER'),
        'DB_PASS': os.getenv('DB_PASS_MASTER'),
        'DB_NAME': os.getenv('DB_NAME_MASTER'),
    },
    'replica': {
        'DB_HOST': os.getenv('DB_HOST_REPLICA'),
        'DB_USER': os.getenv('DB_USER_REPLICA'),
        'DB_PASS': os.getenv('DB_PASS_REPLICA'),
        'DB_NAME': os.getenv('DB_NAME_REPLICA'),
    }
}

query_io = ("SELECT concat(OBJECT_SCHEMA,'.',OBJECT_NAME) as table_name,"
         "SUM_TIMER_FETCH / 1000000000000 as FETCH_LATENCY,"
         "SUM_TIMER_INSERT / 1000000000000 as INSERT_LATENCY,"
         "SUM_TIMER_UPDATE / 1000000000000 as UPDATE_LATENCY,"
         "SUM_TIMER_DELETE / 1000000000000 as DELETE_LATENCY,"
         "COUNT_STAR,"
         "SUM_TIMER_WAIT / 1000000000000 as WAIT_LATENCY "
         "FROM performance_schema.table_io_waits_summary_by_table "
         "WHERE OBJECT_SCHEMA NOT IN ('performance_schema', 'mysql', 'information_schema') "
         "AND SUM_TIMER_WAIT > 0")

query_digest = ("SELECT DIGEST, DIGEST_TEXT, COUNT_STAR, SUM_NO_INDEX_USED,"
         "SUM_SELECT_SCAN, SUM_TIMER_WAIT / 1000000000000 as WAIT_LATENCY "
         "FROM performance_schema.events_statements_summary_by_digest")

query_replica = "SHOW SLAVE STATUS"

for db_name, db_params in databases.items():
    # Connect to the database
    cnx = mysql.connector.connect(user=db_params['DB_USER'], password=db_params['DB_PASS'],
                                  host=db_params['DB_HOST'], database=db_params['DB_NAME'])

    # Create a cursor
    cursor = cnx.cursor()

    # Execute the first query
    cursor.execute(query_io)
    for (table_name, FETCH_LATENCY, INSERT_LATENCY, UPDATE_LATENCY, DELETE_LATENCY, COUNT_STAR, WAIT_LATENCY) in cursor:
        print(f"table_io,db={db_name},table_name={table_name} FETCH_LATENCY={FETCH_LATENCY},INSERT_LATENCY={INSERT_LATENCY},UPDATE_LATENCY={UPDATE_LATENCY},DELETE_LATENCY={DELETE_LATENCY},COUNT_STAR={COUNT_STAR},WAIT_LATENCY={WAIT_LATENCY}")

    # Execute the second query
    cursor.execute(query_digest)
    for (DIGEST, DIGEST_TEXT, COUNT_STAR, SUM_NO_INDEX_USED, SUM_SELECT_SCAN, WAIT_LATENCY) in cursor:
        print(f"digest_stats,db={db_name},digest={DIGEST} DIGEST_TEXT=\"{DIGEST_TEXT}\",COUNT_STAR={COUNT_STAR},SUM_NO_INDEX_USED={SUM_NO_INDEX_USED},SUM_SELECT_SCAN={SUM_SELECT_SCAN},WAIT_LATENCY={WAIT_LATENCY}")

    # Check and get replication stats if it's a replica
    if db_name == 'replica':
        cnx.database = 'mysql'
        cursor.execute(query_replica)
        for row in cursor:
            columns = cursor.column_names
            replication_data = dict(zip(columns, row))
            print(f"replication,db={db_name},host={db_params['DB_HOST']} Master_Log_File=\"{replication_data['Master_Log_File']}\",Read_Master_Log_Pos={replication_data['Read_Master_Log_Pos']},Relay_Master_Log_File=\"{replication_data['Relay_Master_Log_File']}\",Exec_Master_Log_Pos={replication_data['Exec_Master_Log_Pos']},Seconds_Behind_Master={replication_data['Seconds_Behind_Master']}")

    # Close cursor and connection
    cursor.close()
    cnx.close()
