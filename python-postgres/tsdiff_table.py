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
GMTDiffSecs = time.timezone
GMTDiffSecs_DB = 25200 #DB is off/ahead by 3600 secs when tz is used

###########################
def getDataFromDB(cursor,tab,start,end,measFlag):
    if measFlag:
        fld2 = 'temp'
    else:
        fld2 = 'meas'
    sql = """SELECT dt,{} from {} as tab \
        where tab.dt >= '{}' and tab.dt < '{}' \
        order by tab.dt""".format(fld2,tab,start,end)
    cursor.execute(sql)
    return cursor.fetchall()  

###########################
def main():
    parser = argparse.ArgumentParser(description='download data from tname in db with startdate and enddate and write it to standard out')
    parser.add_argument('host',action='store',help='DB host IP')
    parser.add_argument('db',action='store',help='DB name')
    parser.add_argument('user',action='store',help='postgres username')
    parser.add_argument('pwd',action='store',help='postgres usernames password')
    parser.add_argument('tname',action='store',default=None,help='tablename to download data from')
    parser.add_argument('--start',action='store',default='2018-05-10 00:00:00',help='start datetime in this format: YYYY-MM-DD HH:MM:SS in 24hr format; requires that --end be set also')
    parser.add_argument('--end',action='store',default='2018-05-11 00:00:00',help='end datetime in this format: YYYY-MM-DD HH:MM:SS in 24hr format; requires that --start be set also')
    parser.add_argument('--gt',action='store_true',default=False,help='set of file is ground truth (dt,temp) else (dt,meas). (dt,meas) is default')

    args = parser.parse_args()
    startdt = datetime.strptime(args.start,'%Y-%m-%d %H:%M:%S')    
    enddt = datetime.strptime(args.end,'%Y-%m-%d %H:%M:%S')    
    assert enddt > startdt
    #setup the DB
    db = dbiface.DBobj(args.db,args.pwd,args.host,args.user)
    cur = db.get_cursor()
    tname = args.tname
    res = getDataFromDB(cur,tname,startdt,enddt,args.gt)
    last = None
    for ele in res:
        dt = ele[0]
        ts = (dt - datetime(1970,1,1)).total_seconds() + GMTDiffSecs_DB
        val = ele[1]
        if DEBUG:
            print("{}, {}, {}".format(dt,ts,val))
        diff = 0
        if last is not None:
            diff = ts-last
        if diff > 310:
            print("{}, {}, ({}), {}".format(last,ts,dt,diff))
        last = ts

    #clean things up
    cur.close()
    db.closeConnection()

######################################
if __name__ == "__main__":
    main()
