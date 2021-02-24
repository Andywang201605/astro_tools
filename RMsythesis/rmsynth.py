#!/usr/bin/env python
import glob
import os
import sys
import numpy as np
import astropy.wcs as wcs
import astropy.io.fits as fits
import astropy.constants as const

# Perform RM-synthesis on Stokes Q and U data
#
# dataQ, dataU and freqs - contains the Q/U data at each frequency (in Hz) measured.
# startPhi, dPhi - the starting RM (rad/m^2) and the step size (rad/m^2)
def getFDF(dataQ, dataU, freqs, startPhi, stopPhi, dPhi, dType='float32'):
    # Calculate the RM sampling
    phiArr = np.arange(startPhi, stopPhi, dPhi)

    # Calculate the frequency and lambda sampling
    lamSqArr = np.power(const.c.value / np.array(freqs), 2.0)

    # Calculate the dimensions of the output RM cube
    nPhi = len(phiArr)

    # Initialise the complex Faraday Dispersion Function (FDF)
    FDF = np.ndarray((nPhi), dtype='complex')

    # Assume uniform weighting
    wtArr = np.ones(len(lamSqArr), dtype=dType)

    K = 1.0 / np.nansum(wtArr)

    # Get the weighted mean of the LambdaSq distribution (B&dB Eqn. 32)
    lam0Sq = K * np.nansum(lamSqArr)

    # Mininize the number of inner-loop operations by calculating the
    # argument of the EXP term in B&dB Eqns. (25) and (36) for the FDF
    a = (-2.0 * 1.0j * phiArr)
    b = (lamSqArr - lam0Sq) 
    arg = np.exp( np.outer(a, b) )

    # Create a weighted complex polarised surface-brightness cube
    # i.e., observed polarised surface brightness, B&dB Eqns. (8) and (14)
    Pobs = (np.array(dataQ) + 1.0j * np.array(dataU))

    # Calculate the Faraday Dispersion Function
    # B&dB Eqns. (25) and (36)
    FDF = K * np.nansum(Pobs * arg, 1)
    return FDF, phiArr

#-----------------------------------------------------------------------------#
# Main control function                                                       #
#-----------------------------------------------------------------------------#
def RMprocess(qlist, ulist, qfreq, nx, ny, startPhi, stopPhi, dPhi):
    diff = []
    for f in range(1, len(qfreq)):
        diff.append(qfreq[f] - qfreq[f-1])
    df = np.median(diff)
    nchan = len(qfreq)
    
    print("Channel separation = %f" %(df))
    print("Frequency range: %f-%f" %(np.min(qfreq), np.max(qfreq)))

    # Allocate space for the data
    peak = np.zeros((ny, nx), dtype=np.float32)
    val = np.zeros((ny, nx), dtype=np.float32)

    # Generate the array of Phi values
    phiArr = np.arange(startPhi, stopPhi, dPhi)

    # Calculate the frequency and lambda sampling from the available frequencies
    lamArr_m = const.c.value / np.array(qfreq)
    lamSqArr_m2 = np.power(lamArr_m, 2.0)
    header = None
    for y in range(ny):
        print("Processing line %d/%d" %(y, ny))
        # Allocate space for the data
        dataQ = np.zeros((nchan, 1, nx), dtype=np.float32)
        dataU = np.zeros((nchan, 1, nx), dtype=np.float32)

        for chan in range(nchan):
            qhdulist = fits.open(qlist[chan], memmap=True)
            if chan == 0:
                header = qhdulist[0].header
            dataQ[chan, 0, :] = qhdulist[0].data[0,0,y,:]
            qhdulist.close()
            uhdulist = fits.open(ulist[chan], memmap=True)
            dataU[chan, 0, :] = uhdulist[0].data[0,0,y,:]
            uhdulist.close()

        # Transpose XYZ into ZXY order (spectrum first)
        # Remember Python ordering of arrays is reversed [zyx]
        # Reorder [zyx] -> [yxz], i.e., [0,1,2] -> [1,2,0]
        dataQ = np.transpose(dataQ, (1,2,0))
        dataU = np.transpose(dataU, (1,2,0))

        # Run the RM-Synthesis routine on the data
        # Currently assume 3-dimensions in do_rmsynth function
        # do_rmsynth returns a complex FDF cube in spectral order [yxz]
        print(" Running RM-Synthesis routine ...")
        FDFcube = do_rmsynth(dataQ, dataU, lamSqArr_m2, phiArr)

        # Transpose the data back into image order [yxz] -> [zyx] ([012] -> [201])
        FDFcube = np.transpose(FDFcube, (2,0,1))

        fdf = np.abs(FDFcube)
        peak[y,:] = np.nanmax(fdf, axis=(0))
        val[y,:] = phiArr[np.nanargmax(fdf, axis=(0))]
        if (y % 100) == 0: # Do a partial write every 100 lines.
            # Write the peak polarised flux derived from the RM cube
            fits.writeto('peak.fits', peak, header, overwrite=True, output_verify='ignore')
            # Write the RM at which the peak polarised flux occurs for each pixel in the RM cube
            fits.writeto('val.fits', val, header, overwrite=True, output_verify='ignore')

    # Write the peak polarised flux derived from the RM cube
    fits.writeto('peak.fits', peak, header, overwrite=True, output_verify='ignore')
    # Write the RM at which the peak polarised flux occurs for each pixel in the RM cube
    fits.writeto('val.fits', val, header, overwrite=True, output_verify='ignore')


#-----------------------------------------------------------------------------#
# Perform RM-synthesis on Stokes Q and U cubes                                #
#-----------------------------------------------------------------------------#
def do_rmsynth(dataQ, dataU, lamSqArr, phiArr, dType='float32'):

    # Parse the weight argument
    wtArr = np.ones(lamSqArr.shape, dtype=dType)

    # Sanity check on Q & U data array sizes
    if not dataQ.shape == dataU.shape:
        sys.exit("do_rmsynth: Stokes Q and U data arrays be the same shape.")

    # Check that the 
    if not dataQ.shape[-1] == lamSqArr.shape[-1]:
        sys.exit("do_rmsynth: The Stokes Q and U arrays must be in spectral order.\n # Stokes = %d, # Lamda = %d." % (dataQ.shape[-1], lamSqArr.shape[-1]))

    # Calculate the dimensions of the output RM cube
    nX = dataQ.shape[1]
    nY = dataQ.shape[0]
    nPhi = phiArr.shape[0]

    # Initialise the complex Faraday Dispersion Function (FDF) cube
    # Remember, python index order is reversed [2,1,0] = [y,x,phy]
    FDFcube = np.ndarray((nY, nX, nPhi), dtype='complex')

    # B&dB equations (24) and (38) give the inverse sum of the weights
    K = 1.0 / np.nansum(wtArr)

    # Get the weighted mean of the LambdaSq distribution (B&dB Eqn. 32)
    lam0Sq = K * np.nansum(lamSqArr)

    # Mininize the number of inner-loop operations by calculating the
    # argument of the EXP term in B&dB Eqns. (25) and (36) for the FDF
    a = (-2.0 * 1.0j * phiArr)
    b = (lamSqArr - lam0Sq) 
    arg = np.exp( np.outer(a, b) )

    # Create a weighted complex polarised surface-brightness cube
    # i.e., observed polarised surface brightness, B&dB Eqns. (8) and (14)
    # Weight-array will broadcast to the spectral dimension
    PobsCube = (dataQ + 1.0j * dataU)

    # Do the synthesis at each pixel of the image
    for k in range(nY):
        for i in range(nX):
            # Calculate the Faraday Dispersion Function
            # B&dB Eqns. (25) and (36)
            FDFcube[k,i,:] = K * np.nansum(PobsCube[k,i,:] * arg, 1)

    return FDFcube

prefix = "pbeam20.1"        # Change this to whatever your "-name" setting was in wsclean
startPhi = -400.0
dPhi     = 0.1
stopPhi = -startPhi+dPhi

qlist = glob.glob("%s-????-Q-image.fits" %(prefix))
qlist.sort()
ulist = glob.glob("%s-????-U-image.fits" %(prefix))
ulist.sort()

if len(qlist) != len(ulist):
    sys.exit("Channel count mismatch")

qfreq = []
nx = 0
ny = 0
for index in range(len(qlist)):
    qheader = fits.getheader(qlist[index], 0)
    uheader = fits.getheader(ulist[index], 0)
    if index == 0:
        nx = int(qheader['NAXIS1'])
        ny = int(qheader['NAXIS2'])
    else:
        if qheader['NAXIS1'] != uheader['NAXIS1']:
            sys.exit('Axis mismatch')
        if qheader['NAXIS2'] != uheader['NAXIS2']:
            sys.exit('Axis mismatch')
        if qheader['NAXIS1'] != nx:
            sys.exit('Axis mismatch')
        if qheader['NAXIS2'] != ny:
            sys.exit('Axis mismatch')
    if qheader["CRVAL3"] != uheader["CRVAL3"]:
        sys.exit("Channel frequency mismatch")
    qfreq.append(float(qheader["CRVAL3"]))

# RM-range to be searched and the step size
RMprocess(qlist, ulist, qfreq, nx, ny, startPhi, stopPhi, dPhi)
