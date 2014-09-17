#!/bin/bash

# \author Bruno Combal, IOC-UNESCO
# \date September 2013
# \brief split an input file along the time axis
# syntax: nc_slice_time.sh inputfile.nc outfilePath outfileRootName

EXITCODE_NARG=1
EXITCODE_NRF=100
EXITCODE_NRD=101
NARG=3
if [ $# -ne $NARG ]; then
    echo "Wrong number of arguments, expecting $NARG arguments, read $# arguments."
    echo "Usage: nc_slice_time.sh inputfile.nc outfilePath outfileRootName"
    exit ${EXITCODE_WNARG}
fi

binDir=/application/regrid_thetao/bin/
inFile=$1
outPath=$2
outRootName=$3
step=4

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
    outfile=${outPath}/${outRootName}_${thisTime}_${nextTime}.nc
    ncks -o ${outfile} -d time,${thisTime},${nextTime} ${inFile}
done

