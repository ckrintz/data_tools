from __future__ import generators  
import json, os, sys, argparse, psycopg2, uuid
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import urllib2, time
from numpy import *

#import the db interface in the DB directory in parent dir 
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'DB'))
import dbiface

DEBUG = False

###########################
def main():
    parser = argparse.ArgumentParser(description='Process a file with first column time stamp (epoch), rewrite the file as is and then add an additional column which is a datetime in double quotes equivalent for the timestamp column')
    parser.add_argument('fname',action='store',default=None,help='filename to process')
    args = parser.parse_args()
    
    fname = args.fname
    if not os.path.isfile(fname):
        print('Error: input file {} does not exist!'.format(fname))
        sys.exit(1)
    tmpfname = '{}.timestring'.format(fname)

    with open(fname,"r") as f, open (tmpfname,"w") as fout:
        for line in f:
            line = line.strip()
            eles = line.split(' ')
            dt = datetime.fromtimestamp(double(eles[0])) #will thrown an exception if not a timestamp
            newline = '{} "{}"\n'.format(line,dt)
            fout.write(newline)

        fout.flush()

    #replace the file: don't need this here, keep both
    #shutil.move(tmpfname, fname)


######################################
if __name__ == "__main__":
    main()
