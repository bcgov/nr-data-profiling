# Data profiling for on-prem Oracle and PostgreSQL datatabases

## Basic Requirements:

Python 

For database connection:
* oracledb>=1.3.1 (replacing Cx_Oracle)
* psycopg2>=2.9.6
* SQLAlchemy>=2.0.18

For data profiling: 
* ydata-profiling>=4.3.1 (replacing pandas-profiling)
* pandas>1.1, <2.1, !=1.4.0
* numpy>=1.16.0,<1.24


## Changes from v1 to v2:
* new function for PostgreSQL database connections
* data type handling for dates and timestamps 
* using SQLAlchemy wrapping to fix multimethod.DispatchError
* all parameters go in .env
* removing unwanted html


## Next steps: 
* publish .html files on Teams 
* file structure based on Ministry 
* add function for OpenShift database connections 