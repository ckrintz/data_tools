'''
    Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license
    USAGE: python dbiface.py 169.231.XXX.YYY table_name postgres_user_name password
'''
import psycopg2, sys, argparse
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from random import randint

DEBUG=False

TABLE_TYPE_MAP = { #these are different schemas (column types) for database tables
    'meas':""" (dt timestamp PRIMARY KEY, 
        meas real
    )
    """,
    'temp':""" (dt timestamp PRIMARY KEY, 
        temp real 
    )
    """,
    'cimis':""" (dt timestamp PRIMARY KEY, 
        temp real, 
        hum real, 
        vappres real,
        dewpt real,
        solrad real,
        netrad real,
        eto real,
        a_eto real,
        a_etr real,
        precip real,
        windres real,
        winddir real,
        windspd real,
        soil real 
    )
    """,
    'pred':""" (dt timestamp PRIMARY KEY, 
        gtmeas real,
        estdt timestamp,
        estmeas real,
        pred real
    )
    """,
    'simple':""" (dt timestamp PRIMARY KEY, 
        meas real
    )
    """,
    'simple2':""" (dt timestamp PRIMARY KEY, 
        meas real,
        meas2 real
    )
    """
}

class DBobj(object):
    '''A postgresql instance object
    Attributes:
        conn: A database connection
    '''

    #constructor of a DBobj object
    def __init__(self, dbname, pwd, host='localhost',user='postgres'):
        args = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbname,user,host,pwd)
        try:
            self.args = args
            self.conn = psycopg2.connect(args)
        except Exception as e:
            print(e)
            print('Problem connecting to DB')
            sys.exit(1)

    #reset the connection
    def reset(self):
        try:
            self.conn = psycopg2.connect(self.args)
        except Exception as e:
            print(e)
            print('Problem connecting to DB in reset')
            sys.exit(1)
    
    #return the cursor
    def get_cursor(self,svrcursor=None):
        if svrcursor:
            return self.conn.cursor(svrcursor)
        return self.conn.cursor()

    #commit the changes to the db
    def commit(self):
        if self.conn:
            self.conn.commit()

    #see if table exists, return True else False
    def table_exists(self,tablename): 
        curs = self.conn.cursor()
        curs.execute("select exists(select * from information_schema.tables where table_name=%s)", (tablename,))
        val = curs.fetchone()[0]
        return val

    #create a table
    def create_table(self,typename,tablename):
        curs = self.conn.cursor()
        typestring = TABLE_TYPE_MAP[typename]
        if typestring is None:
            print('Error: unable to create table {0}, no types in typemap: {1}'.format(tablename,TABLE_TYPE_MAP))
            return False
        try:
            curs.execute("DROP TABLE IF EXISTS {0}".format(tablename))
            curs.execute("CREATE TABLE {0} {1}".format(tablename,typestring))
        except Exception as e:
            print(e)
            print('Error: unable to create table {0}, in exceptional case. Type: \n{1}'.format(tablename,typestring))
            return False
        self.conn.commit()
        return True

    #delete a table
    def rm_table(self,tablename):
        curs = self.conn.cursor()
        try:
            curs.execute("DROP TABLE {0}".format(tablename))
        except:
            pass
        self.conn.commit()


    #invoke an SQL query on the db
    def execute_sql(self,sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            print('execute_sql: SQL problem:\n\t{0}'.format(sql))
            sys.exit(1)
        return cur

    #close the DB connection
    def closeConnection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Test a connection to a remote postgres DB')
    parser.add_argument('host',action='store',help='DB host IP')
    parser.add_argument('db',action='store',help='DB name')
    parser.add_argument('user',action='store',help='postgres username')
    parser.add_argument('pwd',action='store',help='postgres usernames password')
    parser.add_argument('--removetable',action='store_true',default=False,help='delete the table we create')
    args = parser.parse_args()
    
    #tests
    db = DBobj(args.db,args.pwd,args.host,args.user)
    sql = 'SELECT version()'
    cur = db.execute_sql(sql)
    ver = cur.fetchone()
    print(ver)

    #generate some random data
    val1 = randint(0,100)
    val2 = randint(0,100)

    tname = 'testtable'
    exists = db.table_exists(tname)
    print("Does table already exist? {}".format(exists))

    try:
        #create table with name tname and schema simple2 (above in TABLE_TYPE_MAP)
        if not exists:
            retn = db.create_table('simple2',tname) #table schema name (from TABLE_TYPE_MAP entry above), table name; returns T/F
        #get a cursor (row pointer) for table
        cur = db.get_cursor()

        #https://pynative.com/python-postgresql-insert-update-delete-table-data-to-perform-crud-operations/
        #executes an SQL command, names in first set of parens much match TABLE_TYPE_MAP for schema name
        #%s's in second set of parens must have same count as first parens
        dtval = datetime.now()
        record = (dtval,val1,val2) #tuple
        #insert record in DB
        cur.execute("INSERT INTO {0} (dt,meas,meas2) VALUES (%s, %s, %s)".format(tname), record)
    
        #generate some more random data
        val1 = randint(0,100)
        val2 = randint(0,100)
        record = (dtval,val1,val2) #tuple
        #insert record in DB, if the primary key is already in the database do nothing (same dtval so do nothing)
        cur.execute("INSERT INTO {0} (dt,meas,meas2) VALUES (%s, %s, %s) ON CONFLICT (dt) DO NOTHING".format(tname), record)
        #change dt and retry
        dtval = datetime.now()
        record = (dtval,val1,val2) #tuple
        #insert record in DB, if the primary key is already in the database do nothing (new dtval so add it)
        cur.execute("INSERT INTO {0} (dt,meas,meas2) VALUES (%s, %s, %s) ON CONFLICT (dt) DO NOTHING".format(tname), record)
 
        #turn off the cursor (row pointer) and persist/flush the table to disk
        cur.close()
        db.commit()
    
        #get a cursor (row pointer) for table with name tname
        cur = db.get_cursor(tname)
        #get all of the data from the table and iterate over it to print it all
        cur.execute("SELECT * from {}".format(tname))
        rows = cur.fetchall()
        for row in rows:
            print(row)
    
        #test if table delete works
        if args.removetable:
            print("removing the table {}".format(tname))
            db.rm_table(tname) 
            db.commit()

    except Exception as e: 
        print("Exception in DB tests {}".format(e))

    #always remember to close the connection before you exit
    db.closeConnection()

if __name__ == '__main__':
    main()
