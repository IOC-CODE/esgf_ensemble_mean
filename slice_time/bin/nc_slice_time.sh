#!/bin/bash

# \author Bruno Combal, IOC-UNESCO
# \date September 2013
# \brief split an input file along the time axis
# syntax: nc_slice_time.sh inputfile.nc outfilePath outfileRootName

# this version has different numbering strategy if the slice has 1 date or several dates

# source the ciop functions (e.g. ciop-log)
source ${ciop_job_include}

set -x
SUCCESS=0
EXITCODE_WNARG=1
EXITCODE_NRF=100
EXITCODE_NRD=101
EXITCODE_WGETDATE=200
NARG=3

function cleanExit(){
    local retval=$?
    local msg=""
    case "$retval" in
	$SUCCESS) msg="Processing successfully completed" ;;
	$EXITCODE_WNARG) msg="Wrong number of arguments; Exit." ;;
	$EXITCODE_NRF) msg="Wrong input file parameter; Exit." ;;
	$EXITCODE_NRD) msg="Directory not found; Exit." ;;
	$EXITCODE_WGETDATE) msg="function nc_getDate failed; Exit.";;
	*) msg="Unknown error. Exit." ;;
	esac
	[ "$retval" != "0" ] && ciop-log "ERROR" "Error $retval - ${msg}, processing aborted" || ciop-log "INFO" "$msg"
	exit $retval
}
trap cleanExit EXIT

if [ $# -ne $NARG ]; then
    echo "Wrong number of arguments, expecting $NARG arguments, read $# arguments."
    echo "Usage: nc_slice_time.sh inputfile.nc outfilePath outfileRootName"
    exit ${EXITCODE_WNARG}
fi

#binDir=`dirname $0` #/application/regrid_thetao/bin/
binDir=${0%/*} # faster than dirname, same properties
inFile=$1
outPath=$2
outRootName=$3
step=1

if [ ! -f ${inFile} ]; then
    echo "Parameter ${inFile} is not a regular file."
    exit ${EXITCODE_NRF}
fi
if [ ! -d ${outPath} ]; then
    echo "Parameter ${outPath} is not a regular directory."
    exit ${EXITCODE_NRD}
fi
 
ntime=$(${binDir}/nc_info.py -v time_bnds ${inFile} | cut -d ';' -f 2 | cut -d ',' -f 1 | tr -d '(' | tr -d '[:blank:]')
startTime=($(seq 0 ${step} $((ntime-1))))
endTime=($(seq $((step-1)) ${step} $((ntime-1))))

for ((ii=0; ii<${#startTime[@]}; ii+=1))
do
    thisTime=${startTime[$ii]}
    nextTime=${endTime[$ii]}

    if [ $thisTime -eq $nextTime ]; then
	thisDate=$(${binDir}/nc_getDate.py -v 'thetao' -d ${ii} ${inFile})	
	[ $? -ne 0 ] && exit $EXITCODE_WGETDATE
	thisDate=`echo ${thisDate} | awk -F '-' '{print 100*$1 + $2}'`
	outfile=${outPath}/${outRootName}_${inFile##*/}_${thisDate}.nc    
    else
	outfile=${outPath}/${outRootName}_${inFile##*/}_${thisTime}_${nextTime}.nc
    fi
    ncks -o ${outfile} -d time,${thisTime},${nextTime} ${inFile}
done
