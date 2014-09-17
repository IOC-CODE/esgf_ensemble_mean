#!/bin/bash

indir=$1 #/home/bcombal/ensembleOutput/results
outdir=$2 #/home/bcombal/ensembleOutput/colored
mkdir -p $outdir
tmpdir=$outdir/tmp
mkdir -p $tmpdir
colorMap=/application/get_esgf/NCV_jet_rgb.txt

for ifile in $indir/*.nc
do
    echo "Processing file "$ifile
    nbands=$(gdalinfo $ifile | grep mean_mean_thetao | grep DESC | sed 's/.*=\[//' | sed 's/x.*//')

    thisFile=${ifile##*/}
    for ilevel in $(seq 1 $nbands)
    do
	tmpfile=${tmpdir}/${thisFile%.nc}_${RANDOM}.tif
	outfile=$outdir/${thisFile%.nc}_lvl_${ilevel}.tif
    # convert to gtiff
	gdal_translate -of gtiff -co "compress=lzw" -b $ilevel -scale 273 313 1 255 NETCDF:$indir/$thisFile:mean_mean_thetao $tmpfile
    # apply color scheme
	gdaldem color-relief ${tmpfile} $colorMap $outfile
	rm -f $tmpfile
    done
done


# --- end of script ---
