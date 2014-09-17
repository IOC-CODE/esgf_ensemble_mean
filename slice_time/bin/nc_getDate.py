#!/usr/bin/env python
# \author: Bruno Combal, IOC/UNESCO, EC/FP7 GEOWOW
# \date: September 2013
# \brief print actual date for a slice

import cdms2
import sys

# _____________________________
def exitMessage(message='Error. Exit 1', ExitCode=1):
    print message
    sys.exit(ExitCode)

# _____________________________
if __name__=="__main__":

    infile=None #input file: full path
    variable=None # to get info on a particular variable

    ii=1
    while ii < len(sys.argv):
        arg=sys.argv[ii]

        if arg=='-v':
            ii = ii + 1
            variable=sys.argv[ii]

        elif arg=='-d':
            ii=ii+1
            slicePos= int(sys.argv[ii])

        else:
            infile = sys.argv[ii]
        ii = ii+1


    if infile is None:
        exitMessage('Input file {0} not found. Exit(1)'.format(infile),1)

    if variable is None:
        exitMessage('No variable selected. Exit(2).',2)

    # ______________________________
    thisFile=cdms2.open(infile, 'r')


    if not variable in thisFile.listvariables():
        thisFile.close()
        exitMessage('Variable {0} not found. Exit 3'.format(variable),3)
    

    listDate=thisFile[variable].getTime().asComponentTime()[:]
    print listDate[slicePos]
        
    thisFile.close()

    
