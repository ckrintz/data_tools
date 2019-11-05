from __future__ import generators  
import json, os, sys, argparse, psycopg2, uuid
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import urllib2, time
#from numpy import *

#import the db interface in the DB directory in parent dir 
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'DB'))
import dbiface

DEBUG = False

###########################
def main():
    parser = argparse.ArgumentParser(description='Delete table tname in db, then recreate it and upload 2 col data in a file to a table called tname in db')
    parser.add_argument('host',action='store',help='DB host IP')
    parser.add_argument('db',action='store',help='DB name')
    parser.add_argument('user',action='store',help='postgres username')
    parser.add_argument('pwd',action='store',help='postgres usernames password')
    parser.add_argument('tname',action='store',default=None,help='tablename to upload into in db -- WARNING, tname will be deleted first')
    parser.add_argument('fname',action='store',default=None,help='filename to upload')
    parser.add_argument('--gt',action='store_true',default=False,help='set of file is ground truth (dt,temp) else (dt,meas)')

    args = parser.parse_args()
    
    #setup the DB
    db = dbiface.DBobj(args.db,args.pwd,args.host,args.user)
    if DEBUG:
        #test that its working
        sql = 'SELECT version()' #db level query
        cur = db.execute_sql(sql) #db level query
        ver = cur.fetchone()
        print ver

    tname = args.tname
    fname = args.fname
    if not os.path.isfile(fname):
        print('Error: dbinfo file {} does not exist!'.format(dbinfo))
        sys.exit(1)

    if args.gt:
        retn = db.create_table('temp',tname) #table type template, table name; returns T/F
    else:
        retn = db.create_table('meas',tname) #table type template, table name; returns T/F

    cur = db.get_cursor()
    with open(fname,"r") as f:
        for line in f:
            eles = line.strip().split(' ')
            assert len(eles) == 2
            epoch = round(float(eles[0]),2)
            key = datetime.fromtimestamp(epoch)
            val = float(eles[1])
            if args.gt:
                cur.execute("INSERT INTO {0} (dt,temp) VALUES (%s, %s)".format(tname), [key,val])
            else:
                cur.execute("INSERT INTO {0} (dt,meas) VALUES (%s, %s)".format(tname), [key,val])

    #clean things up
    cur.close()
    db.commit()
    db.closeConnection()
######################################
if __name__ == "__main__":
    main()
