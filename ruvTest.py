import numpy as np

import sys
import os
from lxml import objectify
import arrayConfigurationTools as ac
import numpy as np
import math


def computeRuv(fileCasa):
    """
    Compute the radial distance in the uv plane
    """

    f = open(fileCasa, 'r')

    xx = []
    yy = []

    for line in f:
        if line[0] != "#":
            dat = line.split()

            xx.append(float(dat[0]))
            yy.append(float(dat[1]))

    f.close()

    nant = len(xx)
    nbl = nant * (nant - 1) / 2
    Ruv = np.zeros(nbl)

    index = 0
    for i in range(nant):
        for j in range(0, i):
            r2 = (xx[i] - xx[j]) * (xx[i] - xx[j]) + (yy[i] - yy[j]) * (
                yy[i] - yy[j])
            Ruv[index] = math.sqrt(r2)
            index += 1

    return (Ruv)


def computeBL(AR, freq):
    """
    compute the BL in meter for a resolution AR (applying a Briggs correction
    """

    BLmax = 61800 / (freq * AR)

    return (BLmax)


# a = ac.ArrayConfigurationCasaFile()
# a.createCasaConfig("examplePads.txt")

# ruv = computeRuv("examplePads.txt.cfg")

# print ruv

