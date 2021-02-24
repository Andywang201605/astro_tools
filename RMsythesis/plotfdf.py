#!/usr/bin/env python
import numpy as np
import sys
import matplotlib.pyplot as plt

# Perform RM-synthesis on Stokes Q and U data
#
# dataQ, dataU and freqs - contains the Q/U data at each frequency (in Hz) measured.
# startPhi, dPhi - the starting RM (rad/m^2) and the step size (rad/m^2)
def getFDF(dataQ, dataU, freqs, startPhi, stopPhi, dPhi, dType='float32'):
    # Calculate the RM sampling
    phiArr = np.arange(startPhi, stopPhi, dPhi)

    # Calculate the frequency and lambda sampling
    lamSqArr = np.power(2.99792458e8 / np.array(freqs), 2.0)

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

def plotFDFAll(phi, FDFclean, title):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plot, = ax1.plot(phi, np.abs(FDFclean), marker='+', color="black")
    ax1.set_title("%s - clean" %(title))
    ax1.set_xlabel("phi (rad m$^{-2}$)")
    ax1.set_ylabel("Flux (Jy beam$^{-1}$ RMSF$^{-1}$)")
    ax1.set_xlim(phi[0], phi[-1])
    plt.show()
    plt.close()


def findpeaks(freqs, fdf, phi, rmsf, rmsfphi, nsigma):
    # Create the Gaussian filter for reconstruction
    c = 299792458.0 # Speed of light
    lam2 = (c / freqs) ** 2.0
    lam02 = np.mean(lam2)
    minl2 = np.min(lam2)
    maxl2 = np.max(lam2)
    width = (2.0 * np.sqrt(3.0)) / (maxl2 - minl2)

    Gauss = np.exp((-rmsfphi ** 2.0) / (2.0 * ((width / 2.355) ** 2.0)))
    components = np.zeros((len(phi)), np.float32)
    peaks = []
    phis = []
    std = 0.0
    rmsflen = int((len(rmsf) - 1) / 2)
    fdflen = len(phi) + rmsflen
    while True:
        std = np.std(np.abs(fdf))
        peak1 = np.max(np.abs(fdf))
        pos1 = np.argmax(np.abs(fdf))
        val1 = phi[pos1]
        if peak1 < nsigma * std :
        	break
        fdf -= rmsf[rmsflen - pos1:fdflen - pos1] * fdf[pos1]
        peaks.append(peak1)
        phis.append(val1)
        components[pos1] += peak1
    fdf += np.convolve(components, Gauss, mode='valid')
    return phis, peaks, std

def main():
    # Expects input file in the format:
    # freq(MHz),I(Jy),Q(Jy),U(Jy),V(Jy)
    csvfile = sys.argv[1]
    startPhi = -1000.0
    dPhi     = 0.1
    stopPhi = -startPhi+dPhi

    freqs = []
    i = []
    q = []
    u = []
    v = []
    for line in open("%s" %(csvfile)):
        if len(line) < 2:
            continue
        if line[0] == "#":
            continue
        data = line.split(",")
        freqs.append(float(data[0]) * 1.0e6)
        i.append(float(data[1]))
        q.append(float(data[2]))
        u.append(float(data[3]))
        v.append(float(data[4]))

    # Work out the channel width
    df = []
    for f in range(1, len(freqs)):
        df.append(freqs[f] - freqs[f-1])
    chanBW = np.min(np.array(df))
    C = 299792458           # Speed of light
    fmin = np.min(freqs)
    fmax = np.max(freqs)
    bw = fmax - fmin

    dlambda2 = np.power(C / fmin, 2) - np.power(C / (fmin + chanBW), 2)
    Dlambda2 = np.power(C / fmin, 2) - np.power(C / (fmin + bw), 2)
    phimax = np.sqrt(3) / dlambda2
    dphi = 2.0 * np.sqrt(3) / Dlambda2
    phiR = dphi / 5.0
    Nphi = 2 * phimax / phiR
    print("Frequency range: %7.3f MHz - %7.3f MHz" %(fmin / 1.0e6, (fmin + bw) / 1.0e6))
    print("Bandwidth: %7.3f MHz" %(bw / 1.0e6))
    print("Channel width: %.1f KHz" %(chanBW / 1.0e3))
    print("dlambda2: %7.3f" %(dlambda2))
    print("Dlambda2: %7.3f" %(Dlambda2))
    print("phimax: %7.3f" %(phimax))
    print("dphi: %7.3f" %(dphi))
    print("phiR: %7.3f" %(phiR))
    print("Nphi: %7.3f" %(Nphi))
    fwhm = dphi

    # Determine the FDF using the q, u and ferquency values read from the file.
    dirty, phi = getFDF(q, u, freqs, startPhi, stopPhi, dPhi)
    FDFqu, phi = getFDF(q, u, freqs, startPhi, stopPhi, dPhi)
    plotFDFAll(phi, np.array(FDFqu), csvfile)
    rstartPhi = startPhi * 2
    rstopPhi = stopPhi * 2 - dPhi
    RMSF, rmsfphi = getFDF(np.ones((len(q))), np.zeros((len(q))), freqs, rstartPhi, rstopPhi, dPhi)

    phis, peaks, sigma = findpeaks(np.array(freqs), FDFqu, phi, RMSF, rmsfphi, 6.0)
    snr = peaks / sigma
    phierr = fwhm / (2 * snr)
    print (phis, phierr, peaks, sigma)
    imean = np.mean(np.array(i))
    print("S = %.3f" %(imean))
    if len(peaks) > 0:
    	print("p = %.3f%%" %(100.0 * peaks[0] / imean))
    # Plot the RMSF
    plotFDFAll(phi, np.array(FDFqu), csvfile)

if __name__ == '__main__':
  main()
