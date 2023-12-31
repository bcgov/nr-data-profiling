import os
import re
import dotenv
import pandas
import ydata_profiling 
import datetime
import oracledb
import psycopg2
import sqlalchemy 
from sqlalchemy.orm import sessionmaker

def load_configuration():
    dotenv.load_dotenv()
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    service_name = os.getenv('DATABASE')
    dbms = os.getenv('DBMS')
    owner = os.getenv('OWNER')

    return username, password, host, port, service_name, dbms, owner

def connect_to_postgres(username, password, host, port, service_name):
        try:
            url = f"postgresql://{username}:{password}@{host}:{port}/{service_name}"
            engine = sqlalchemy.create_engine(url)
             
            # connection_string = f"host={host} port={port} dbname={service_name} user={username} password={password}"
            # con = psycopg2.connect(connection_string)
            # cursor = con.cursor()
            # return con, cursor

            return engine
            
        except (psycopg2.Error, Exception) as e:
            print("Error connecting to PostgreSQL:", e)
            return None, None

def connect_to_oracle(username, password, host, port, service_name):
    
        try:

            dsn = oracledb.makedsn(host=host, port=port, service_name=service_name)
            url = f"oracle+oracledb://{username}:{password}@{dsn}"
            engine = sqlalchemy.create_engine(url)
    
            # con = oracledb.connect(user=username, password=password, dsn=dsn)
            # cursor = con.cursor()
            # return con, cursor

            return engine

        except (oracledb.Error, Exception) as e:
            print("Error connecting to Oracle:", e)
            return None, None
        
def run_database_query(engine, scope_sql):

    Session = sessionmaker(bind=engine)
    
    cursor = Session()
    
    result = cursor.execute(sqlalchemy.text(scope_sql))

    for row in result:

        print(row)

        schema = row[0]
        tablename = row[1]

        query = """SELECT * FROM %s.%s""" % (schema, tablename)
        df = pandas.read_sql(sql=query, con=engine)
        
        df = df.applymap(lambda x: pandas.Timestamp(x) if isinstance(x, datetime.datetime) else x)

        if len(df) > 0:
            prf = ydata_profiling.ProfileReport(df, minimal=True, title=schema + '.' + tablename)
            prf.to_file(os.path.join(html_dir, schema + '.' + tablename + '.html'))
            # prf.to_file(os.path.join(json_dir, schema + '.' + tablename + '.json'))

        continue

def remove_line_from_html(html_dir, html_to_remove):
    for current_file in os.listdir(html_dir):
        if current_file.endswith('.html'):
            file_path = os.path.join(html_dir, current_file)

            with open(file_path, 'r') as file:
                lines = file.readlines()

            with open(file_path, 'w') as file:
                for line in lines:
                    if not re.search(html_to_remove, line):
                        file.write(line)
     
def main():
    try:
        username, password, host, port, service_name, dbms, owner = load_configuration()

        if dbms == 'Oracle':
            scope_sql = f"SELECT owner, table_name FROM all_tables WHERE owner = '{owner}' AND table_name like '{owner}%' AND tablespace_name = '{owner}_TABLES' ORDER BY table_name"
            engine = connect_to_oracle(username, password, host, port, service_name)
            run_database_query(engine, scope_sql)
            remove_line_from_html(html_dir, html_to_remove)
                
        elif dbms == 'PostgreSQL':
            scope_sql = f"SELECT schemaname, tablename FROM pg_tables WHERE schemaname = '{owner}'"
            engine = connect_to_postgres(username, password, host, port, service_name)
            run_database_query(engine, scope_sql)
            remove_line_from_html(html_dir, html_to_remove)
                
        else:
            print("Unsupported DBMS:", dbms)

    except Exception as e:
        print("Other error:", str(e))

html_dir = '\\objectstore.nrs.bcgov\da_data_analysis\DataProfile\html'
if not os.path.exists(html_dir):
    os.makedirs(html_dir)

json_dir = '\\objectstore.nrs.bcgov\da_data_analysis\DataProfile\json'
if not os.path.exists(json_dir):
    os.makedirs(json_dir)

html_to_remove = r'<p class="text-muted text-center">Report generated by <a href="https://ydata.ai/\?utm_source=opensource&utm_medium=pandasprofiling&utm_campaign=report">YData</a>'

main()