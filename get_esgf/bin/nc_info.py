#!/usr/bin/env python

# to run the script with the correct version of uvcdat:
#  source /usr/local/uvcdat/1.4.0/bin/setup_runtime.sh

import cdms2
from cdms2 import MV2
import numpy
import sys
import os
from os import path
import re
import string

# _________________________________
def usage():
    text='SYNOPSIS:\n\tnc_info.py -time infile'
    text = text+'\t-time: indicate to report for time axis related information.'
    return text
# _________________________________
def exitMessage(msg, exitCode='1'):
    print msg
    print
    print usage()
    sys.exit(exitCode)

# _________________________________
# more info query option can be added in future versions
def doGetInfo(infile, timeQuery):
    
    thisFile = cdms2.open(infile)

    timeAxis = thisFile['time']
    timeAxisCT = thisFile['time'].asComponentTime()
    dateTimeStart=timeAxisCT[0]
    dateTimeEnd=timeAxisCT[-1]
    # output: time component and year month day extracted
    print 'dateTimeStart: ',timeAxisCT[0]
    print 'yearStart:', dateTimeStart.year
    print 'monthStart:',dateTimeStart.month
    print 'dayStart:',dateTimeStart.day

    print 'dateTimeEnd: ',timeAxisCT[-1]
    print 'yearEnd:', dateTimeEnd.year
    print 'monthEnd: ',dateTimeEnd.month
    print 'dayEnd: ',dateTimeEnd.day

    thisFile.close()
    print 'exiting'
# _________________________________
if __name__=="__main__":

    infile=None #input file
    infoFlag=False
    timeQuery=False

    ii = 1
    while ii < len(sys.argv):
        arg = sys.argv[ii].lower()

        if arg == '-time':
            infoFlag=True
            timeQuery=True
        else:
            infile = sys.argv[ii]
        ii = ii + 1

    if infile is None:
        exitMessage('Missing an input file. Exit(1).', 1)

    if not os.path.exists(infile):
        exitMessage('Input file does not exist. Exit(2).',2)

    if infoFlag==False:
        exitMessage('Please define a parameter to search for. Exit(3).',3)

    doGetInfo(infile, timeQuery)

