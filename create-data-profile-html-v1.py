import os
import pandas
from pandas_profiling import ProfileReport
import cx_Oracle

# cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle2\instantclient-basic-windows.x64-21.7.0.0.0dbru\instantclient_21_7")

html_dir = '<Place your directory name for html>'
if not os.path.exists(html_dir):
    os.makedirs(html_dir)

json_dir = '<Place your directory name for html>'
if not os.path.exists(json_dir):
    os.makedirs(json_dir)

dsn = """
(DESCRIPTION =
      (ADDRESS =
        (COMMUNITY = mtoprod.nrs.bcgov)
        (PROTOCOL = TCP)
        (Host = nrkdb02.bcgov)
        (Port = 1521)
      )
    (CONNECT_DATA =
        (SERVICE_NAME = mtoprod.nrs.bcgov)
        (GLOBAL_NAME = mtoprod.nrs.bcgov)
    )
  )"""

connection = cx_Oracle.connect("<UserName>", "<Password>", dsn)

scope_sql = """
SELECT
    owner,
    table_name
FROM
    all_tables
WHERE
    owner = 'MTA'
AND
    table_name like 'MTA%'
AND    
    tablespace_name = 'MTA_TABLES'
ORDER BY table_name    
"""

cursor = connection.cursor()
cursor.execute(scope_sql)

for row in cursor:
    schema = row[0]
    tablename = row[1]
    print('\033[91m', schema, '>>>', tablename, '\033[0m')

    query = """SELECT * FROM %s.%s""" % (schema, tablename)
    df = pandas.read_sql(query, con=connection)

    if len(df) > 0:
        prf = ProfileReport(df, minimal=True, title=schema + '.' + tablename)
        prf.to_file(os.path.join(html_dir, schema + '.' + tablename + '.html'))
        prf.to_file(os.path.join(json_dir, schema + '.' + tablename + '.json'))

    continue
