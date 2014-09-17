#!/usr/bin/env python
# \author: Bruno Combal, IOC/UNESCO, EC/FP7 GEOWOW
# \date: July 2013
# to run the script with the correct version of uvcdat:
# source /usr/local/uvcdat/1.2.0/bin/setup_cdat.sh

# version 1: regrid lat/lon, for all t and z
# version 2: add z interpolation, for all t, lat, lon

import cdms2
import numpy
import sys
import os.path

# _____________________________
def exitWM(message='Error. Exit 1', ExitCode=1):
    print message
    sys.exit(ExitCode)

# _____________________________
def makeGrid():
    xstart=0
    xend=360
    xstep=0.5
    ystart=-85
    yend=85
    ystep=0.5

    lon_bnds=[]
    lon=[]
    for ii in numpy.arange(xstart, xend, xstep):
        lon_bnds.append( [ii, ii+xstep] )
        lon.append(ii+0.5*xstep)
    lon_bnds=numpy.array(lon_bnds)
    lon=numpy.array(lon)

    lat_bnds=[]
    lat=[]
    for ii in numpy.arange(ystart, yend, ystep):
        lat_bnds.append([ii, ii+ystep])
        lat.append(ii+0.5*ystep)
    lat_bnds=numpy.array(lat_bnds)
    lat=numpy.array(lat)

    latAxis = cdms2.createAxis(lat, lat_bnds)
    latAxis.designateLatitude(True)
    latAxis.units='degrees_north'
    latAxis.long_name='Latitude'
    latAxis.id='latitude'

    lonAxis = cdms2.createAxis(lon, lon_bnds)
    lonAxis.designateLongitude(True, 360.0)
    lonAxis.units='degrees_east'
    lonAxis.id='longitude'
    lonAxis.long_name='Longitude'

    lvl_bnds=numpy.array([[0,10], [10, 20], [20,30], [30,40], [40,50], [50,60], [60,70], [70,80], [80,90], [90,100], [100, 125], [125, 150], [150,175], [175,200], [200,250],[250,300],[300,400],[400,500], [500,600], [600,700], [700,800]])
    lvl = [ 0.5*(lvls[0] + lvls[1]) for lvls in lvl_bnds ]
#    lvl = numpy.zeros(len(lvl_bnds))
#    for ii in range(len(lvl_bnds)): lvl[ii]=0.5*(lvl_bnds[ii,0]+lvl_bnds[ii,1])
    return((cdms2.createGenericGrid(latAxis, lonAxis, lat_bnds, lon_bnds), latAxis, lonAxis, lat_bnds, lon_bnds, lvl_bnds, lvl))

# _____________________________
# interpolates a series of values
# the output has the size of zNew
def do_zInterp(zProfile, zOrg, zNew, nodata):
    # z profiles have constant size, but final values may be set to nodata (1.e20): they should not be considered
    thisProfile = [zz for zz in zProfile if zz < nodata]
    # the result has the dimensions of zNew
    tmp =  numpy.interp(zNew[0:len(thisProfile)], zOrg[0:len(thisProfile)], thisProfile, right=nodata)
    final = numpy.zeros(len(zNew))+nodata
    final[0:len(final)]=final[:]

    return final
# _____________________________
# interpolates cube t, z, lat, lon along z
# assumes dimensions are t, z, lat, lon
# cubeIn: 4D dataset
# zOrg: the input data z levels
# zNew: the requested zlevels
def do_hyperInterp(cubeIn, zOrg, zNew, nodata):
    thisShape=cubeIn.shape
    
    cubeOut = numpy.zeros( (thisShape[0], len(zNew), thisShape[2], thisShape[3] ) )+nodata

    for itime in range(0, thisShape[0]):
        print itime
        for ilat in range(0, thisShape[2]):
            for ilon in range(0, thisShape[3]):
                if cubeIn[itime, 0, ilat, ilon] < nodata:
                    tmp = do_zInterp( numpy.ravel(cubeIn[itime, :, ilat, ilon]), zOrg, zNew, nodata)
                    cubeOut[itime, :, ilat, ilon] = tmp[:]
                
    return cubeOut
# _____________________________
def do_regrid(infileName, variable, outfileName, netcdfType=4):

    nodata = 1.e20

    if netcdfType==4:
        cdms2.setNetcdfShuffleFlag(1)
        cdms2.setNetcdfDeflateFlag(1)
        cdms2.setNetcdfDeflateLevelFlag(3)
    elif netcdfType==3:
        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevel(0)
    else:
        exitWM('Unknown netcdf type {0}. Exit 2.'.format(netcdfType),2)

    infile = cdms2.open(infileName)
    unitsVar = infile[variable].units
    (referenceGrid, latAxis, lonAxis, latBounds, lonBounds, lvl_bounds, lvl) = makeGrid()
    regridded = infile[variable][:].regrid(referenceGrid)

    outvar = cdms2.createVariable(regridded, typecode='f',
                                  id=variable, fill_value=nodata,
                                  grid=referenceGrid, copyaxes=1,
                                  attributes=dict(long_name='regridded {0}'.format(variable), units=unitsVar))
    #final = do_hyperInterp(regridded, infile[variable].getLevel()[:], lvl, nodata)
    #outvar = cdms2.createVariable(final, typecode='f', id=variable, fill_value=nodata, attributes=dict(long_name='regridded {0}'.format(variable), units=unitsVar) )


    #gridBis = regridded.subSlice(longitude=0).crossSectionRegrid(lvl, latAxis, method="linear")

    #zregrid = tmpvar.crossSectionRegrid(lvl)

    #outvar.setAxisList((latAxis, lonAxis))
    if os.path.exists(outfileName): os.remove(outfileName)
    outfile=cdms2.open(outfileName, 'w')
    outfile.write(outvar)
    outfile.history='Created with '+__file__.encode('utf8')
    outfile.close()
    infile.close()
    
# _____________________________
if __name__=="__main__":

    infile=None #input file: full path
    variable='thetao'
    netcdfType=4
    outfile=None #output file: full path

    # parse input parameters
    # to do: optional grid description

    ii=1
    while ii < len(sys.argv):
        arg=sys.argv[ii]

        if arg=='-o':
            ii=ii+1
            outfile = sys.argv[ii]

        elif arg=='-v':
            ii = ii + 1
            variable=sys.argv[ii]

        else:
            infile = sys.argv[ii]
        ii = ii+1

    # check input parameters
    if infile is None:
        exitWM('Input file is not defined. Exit 3.', 3)

    if outfile is None:
        exitWM('Output file is not defined, use option -o. Exit 4.')

    if not os.path.isfile(infile):
        # infile does not exist or is not a file
        exitWM('Could not find input file {0}. Exit 1.'.format(infile), 1)

    if not os.path.isdir(os.path.dirname(outfile)):
        # outfile directory does not exist or is not a directory
        exitWM('Directory {0} does not exist to store output file {1}'.format(os.path.dirname(outfile), os.path.basename(outfile)))

    do_regrid(infile, variable, outfile, netcdfType)
