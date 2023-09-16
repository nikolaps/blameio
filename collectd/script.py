#!/usr/bin/env python3.9
import os
import mysql.connector
import psycopg2

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

query_io = (
         "SELECT concat(OBJECT_SCHEMA,'.',OBJECT_NAME) as table_name,"
         "SUM_TIMER_FETCH / 1000000000000 as FETCH_LATENCY,"
         "SUM_TIMER_INSERT / 1000000000000 as INSERT_LATENCY,"
         "SUM_TIMER_UPDATE / 1000000000000 as UPDATE_LATENCY,"
         "SUM_TIMER_DELETE / 1000000000000 as DELETE_LATENCY,"
         "COUNT_STAR,"
         "SUM_TIMER_WAIT / 1000000000000 as WAIT_LATENCY "
         "FROM performance_schema.table_io_waits_summary_by_table "
         "WHERE OBJECT_SCHEMA NOT IN ('performance_schema', 'mysql', 'information_schema') "
         "AND SUM_TIMER_WAIT > 0"
         )

query_digest = """
            SELECT processlist_id                  AS id,
                   IFNULL(processlist_user, "")    AS user,
                   IFNULL(processlist_host, "")    AS host,
                   IFNULL(processlist_db, "")      AS db,
                   IFNULL(processlist_command, "") As command,
                   IFNULL(processlist_time, "0")   AS exec_time,
                   IFNULL(processlist_info, "")    AS query,
                   IFNULL(processlist_state, "")   AS state,
                   IFNULL(trx_state, "")           AS trx_state,
                   IFNULL(trx_operation_state, "") AS trx_operation_state,
                   IFNULL(trx_rows_locked, "0")    AS trx_rows_locked,
                   IFNULL(trx_rows_modified, "0")  AS trx_rows_modified
            FROM performance_schema.threads t
                     LEFT JOIN information_schema.innodb_trx tx ON trx_mysql_thread_id = t.processlist_id
            WHERE processlist_id IS NOT NULL
              AND processlist_time IS NOT NULL
              AND processlist_command != 'Daemon'
              AND (processlist_command != 'Sleep' AND processlist_command NOT LIKE 'Binlog Dump%')
              AND (processlist_info IS NOT NULL OR trx_query IS NOT NULL)
               """

query_replica = "SHOW SLAVE STATUS"

# Connect to TimescaleDB
conn = psycopg2.connect(
    dbname='statsdb',
    user='blameio',
    password='RYc7ET6MwdjkmkbkfPJutHfh',
    host='timescaledb',
    port='5432'
)
cur = conn.cursor()

for db_name, db_params in databases.items():
    # Connect to the MySQL database
    cnx = mysql.connector.connect(user=db_params['DB_USER'], password=db_params['DB_PASS'],
                                  host=db_params['DB_HOST'], database=db_params['DB_NAME'])

    # Create a cursor
    cursor = cnx.cursor()

    # Execute the first query
    cursor.execute(query_io)
    for (table_name, FETCH_LATENCY, INSERT_LATENCY, UPDATE_LATENCY, DELETE_LATENCY, COUNT_STAR, WAIT_LATENCY) in cursor:
        cur.execute(
            "INSERT INTO table_io (db, table_name, FETCH_LATENCY, INSERT_LATENCY, UPDATE_LATENCY, DELETE_LATENCY, COUNT_STAR, WAIT_LATENCY) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (db_name, table_name, FETCH_LATENCY, INSERT_LATENCY, UPDATE_LATENCY, DELETE_LATENCY, COUNT_STAR, WAIT_LATENCY)
        )
        conn.commit()

    # Execute the second query
    cursor.execute(query_digest)
    for (id, user, host, db, command, exec_time, query, state, trx_state, trx_operation_state, trx_rows_locked, trx_rows_modified) in cursor:
        cur.execute(
            """
            INSERT INTO digest_stats (
                id, 
                user, 
                host, 
                db, 
                command, 
                exec_time, 
                query, 
                state, 
                trx_state, 
                trx_operation_state, 
                trx_rows_locked, 
                trx_rows_modified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                id, 
                user, 
                host, 
                db, 
                command, 
                exec_time, 
                query, 
                state, 
                trx_state, 
                trx_operation_state, 
                trx_rows_locked, 
                trx_rows_modified
            )
        )
        conn.commit()


    # Check and get replication stats if it's a replica
    if db_name == 'replica':
        cnx.database = 'mysql'
        cursor.execute(query_replica)
        for row in cursor:
            columns = cursor.column_names
            replication_data = dict(zip(columns, row))
            cur.execute(
                "INSERT INTO replication (db, host, Master_Log_File, Read_Master_Log_Pos, Relay_Master_Log_File, Exec_Master_Log_Pos, Seconds_Behind_Master) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (db_name, db_params['DB_HOST'], replication_data['Master_Log_File'], replication_data['Read_Master_Log_Pos'], replication_data['Relay_Master_Log_File'], replication_data['Exec_Master_Log_Pos'], replication_data['Seconds_Behind_Master'])
            )
            conn.commit()

    # Close cursor and connection
    cursor.close()
    cnx.close()

cur.close()
conn.close()
