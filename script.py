#!/usr/bin/env python3.9
import mysql.connector

cnx = mysql.connector.connect(user='nikolai', password='jWK8VKfs77PkAe4Pz4ehFEybwubfPJ5M',
                              host='db-ny7-02',
                              database='performance_schema')

cursor = cnx.cursor()

query = (
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

cursor.execute(query)

for (table_name, FETCH_LATENCY, INSERT_LATENCY, UPDATE_LATENCY, DELETE_LATENCY, COUNT_STAR, WAIT_LATENCY) in cursor:
    print(f"table_io,table_name={table_name} FETCH_LATENCY={FETCH_LATENCY},INSERT_LATENCY={INSERT_LATENCY},UPDATE_LATENCY={UPDATE_LATENCY},DELETE_LATENCY={DELETE_LATENCY},COUNT_STAR={COUNT_STAR},WAIT_LATENCY={WAIT_LATENCY}")

cnx.database = 'mysql'

query_replica = "SHOW SLAVE STATUS"
cursor.execute(query_replica)

for row in cursor:
    columns = cursor.column_names
    replication_data = dict(zip(columns, row))

    print(f"replication,host=db-ny7-02 Master_Log_File=\"{replication_data['Master_Log_File']}\",Read_Master_Log_Pos={replication_data['Read_Master_Log_Pos']},Relay_Master_Log_File=\"{replication_data['Relay_Master_Log_File']}\",Exec_Master_Log_Pos={replication_data['Exec_Master_Log_Pos']},Seconds_Behind_Master={replication_data['Seconds_Behind_Master']}")


cursor.close()
cnx.close()

