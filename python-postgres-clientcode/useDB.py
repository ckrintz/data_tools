import requests, json, os, sys, argparse, io, time
from datetime import datetime, date, timedelta
from subprocess import call,Popen,PIPE
import urllib
from numpy import *
from dateutil.relativedelta import relativedelta

#import the db interface in the DB directory in parent dir 
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-postgres'))
import dbiface

DEBUG = False
###########################
def process(db, tname, ts, val,val2):
    '''insert/update the data (ts,val, and maybe val2) in the table called tname in DB db'''
    try:
        cur = db.get_cursor()
        if val2 == -1.0: #schema is dt, meas (named simple)
            cur.execute("INSERT INTO {} (dt,meas) VALUES (%s, %s) ON CONFLICT (dt) DO NOTHING".format(tname), [ts,val])
        else: #schema is dt, meas, meas2 (named simple2)
            cur.execute("INSERT INTO {} (dt,meas,meas2) VALUES (%s, %s, %s) ON CONFLICT (dt) DO NOTHING".format(tname), [ts,val,val2])
        db.commit()
    except Exception as e: 
        print("Exception in process DB record {}".format(e))
        print("Trying to reset connection to DB...")
        try:
            cur.close()
        except:
            cur.close()
            db.reset()
        cur = db.get_cursor()

###########################
def main():
    ''' 
    python3 useDB.py dbIP dbname user pwd
    '''

    parser = argparse.ArgumentParser(description='get data and store it in DB')
    parser.add_argument('dbhost',action='store',help='DB host IP')
    parser.add_argument('db',action='store',help='DB name')
    parser.add_argument('user',action='store',help='postgres username')
    parser.add_argument('pwd',action='store',help='postgres usernames password')
    args = parser.parse_args()

    filenames = [ "test.txt", "test2.txt"]
    datalist = []
    for fname in filenames:
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                #format is linux_epoch measurement
                for line in f:
                    data = line.strip().split(" ") #split on space
                    epoch = data[0]
                    val = data[1]
                    datalist.append((epoch,val)) #pairs
    tname="clienttesttable"
    db = dbiface.DBobj(args.db,args.pwd,args.dbhost,args.user)
    table_type = 'simple'
    lastdt = None
    retn = db.table_exists(tname)
    if not retn:
        retn = db.create_table(table_type,tname)
        if not retn:
            print('Error: Unable to create table {}'.format(tname))
            sys.exit(1)
        print("New Table created with name {}".format(tname))
    else:
        print("Table with name {}, already in database".format(tname))
        #get the last timestamp (dt) in the database and only add data if larger than that
        sql = 'select max(dt) from {}'.format(tname)
        cur = db.get_cursor()
        cur.execute(sql)
        retn = cur.fetchone()[0]
        if retn is not None: #data in the table
            lastdt = retn
            print("loading data from {} forward".format(lastdt))

    #cursor now refers to tname table
    cur = db.get_cursor()
    #process datalists
    count = 0
    for rec in datalist:            
        ts = rec[0]
        val = rec[1]
        val2 = -1
        dt = datetime.fromtimestamp(float(ts))
        if lastdt and dt < lastdt: #don't write again
            continue
        process(db,tname,dt,val,val2)
        if count % 100 == 0:
            print('Processed {} records for table {}'.format(count,tname))
        count += 1

            
######################################
if __name__ == "__main__":
    main()
