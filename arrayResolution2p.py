#!/usr/bin/python


"""
Script to return the Cycle 2 arrays for a given LAS, Angular Resolution


HISTORY:
    2012.10.11:
        - first shot
        - Cycle 1 setup
        
    2012.11.20:
        - Adding resolution, LAS for different declination
        
    2012.12.27:
        - adding a filter if no configuration is found to multiply by a fudge factor
        
        
    2013.03.04:
        - Adding geometric average for the spatial resolution  and test on twice the spatial resolution
        
    2013.03.05:
        - fixing bugs
        - adding extra information (THB, array)
        
        
    2013.03.11:
        - Removing the condition about AR/2. for the array.
        
        
    2013.03.18:
        - Adding point source option
        - putting the AR/2. if it is not a point source
        
        
    2013.03.20:
        - changing the PS option to LAS = 0
        
    2013.05.02:
        - changing slightly the conditions of acceptance (>= instead of >)
        
    2013.05.03:
        - print version
        - try increasing fudge factor until it gets a solution

    2013.05.10:
        - Add silentRun for P2G (FG)
        
    2013.12.13:
        - Name change for Cycle2 and update of the pickle.
        - Update of the finder (multi-configuration)
        
    2013.12.16:
        - new find_array3 for the multi-configuration
    
    
    2014.01.28:
        - fix the fudge relaxation for the resolution.
        
        
    2014.05.22:
        - New algorithm to deal with minAr, maxAr
        
    2014.05.22:
        - ugly fixConfiguration when OT forces for two configurations
        
    2014.06.02
        - fixing the matchAR
        - relaxing the condition to allow a better AR with a sufficient LAS (0.9)
        
    2014.06.05:
        - adapting the case 7-m+12-m
        
RUN:
Input RES (arcsec) LAS (arcsec) FREQ (GHz) Declination (Degree) Y/N (ACA)
> python arrayResolution2.py 0.2 2.5 640. -53 Y PS

"""

__author__ = "ALMA : SL, AL, FG"
__version__ = "0.7.0@2014.06.05"


import sys, pickle
import math


### ALMA
LATITUDE_ALMA = -23.03
DEG2RAD = math.pi/180.


class arrayRes:

    def __init__(self, arguments):

        self.LAS = [26.1,26.3,18.0,18.0,14.4,9.1,9.1]
        self.LASA = [44.0,44.0,44.0,44.0,14.4,9.1,9.1]
        self.LAST = [390.0,390.0,390.0,390.0,14.4,9.,9.1]
        self.res = [3.73,2.04,1.40,1.11,0.75,0.57,0.41]

        self.frequencyReference = 100.
        self.lasObs = 0.
        self.resObs = 0.
        self.resObsOriginal = 0
        self.freqObs = 0.
        self.pointSource = False
        self.silent = True
        self.nof12m = 1
        self.minAR = [0.,10000.]
        self.maxAR = [0, 0.]

        self.args = arguments

        self.array = {0:"C34-1",1:"C34-2",2:"C34-3",3:"C34-4",4:"C34-5",5:"C34-6",6:"C34-7"}
        self.read_cycle2()



    def set_las(self,las):
        "Set the LAS of the observation"

        self.lasObs = las

    def set_res(self,res):
        "Set the angular resolution of the observation"

        self.resObs = res
        self.resOriginal = res

    def set_frequency(self,freq):
        "Set the frequency of the observation"

        # if ((freq>=64.)&(freq<=116.)): freq = 100.
        # if ((freq>=211.)&(freq<=275.)): freq = 230.
        # if ((freq>=275.)&(freq<=373.)): freq = 345.
        # if ((freq>=602.)&(freq<=720.)): freq = 675.

        self.freqObs = freq


    def set_declination(self,declination):
        "Set the representative declination of the observation"

        self.declination = declination


    def set_aca(self,aca):
        "Set the frequency of the observation"

        self.acaUse = aca


    def set_12m(self,numberof12m):
        "Set the number of 12m array configuration"

        self.nof12m = numberof12m

    def set_pointSource(self, isPS):
        "Set True if point source"

        self.pointSource = isPS

    def read_cycle2(self, directory=None):

        """Read the detailed Resolution, LAS for the Cycle 1 configuration"""

        directory = self.args[0] + 'conf/'
        print directory

        self.data = []

        f = open(directory+'Resolution-C34-1.pickle')
        self.data.append(pickle.load(f))
        f.close()

        f = open(directory+'Resolution-C34-2.pickle')
        self.data.append(pickle.load(f))
        f.close()

        f = open(directory+'Resolution-C34-3.pickle')
        self.data.append(pickle.load(f))
        f.close()

        f = open(directory+'Resolution-C34-4.pickle')
        self.data.append(pickle.load(f))
        f.close()

        f = open(directory+'Resolution-C34-5.pickle')
        self.data.append(pickle.load(f))
        f.close()

        f = open(directory+'Resolution-C34-6.pickle')
        self.data.append(pickle.load(f))
        f.close()

        f = open(directory+'Resolution-C34-7.pickle')
        self.data.append(pickle.load(f))
        f.close()


        ### ACA ####
        f = open(directory+'Resolution-ACA-std.pickle')
        self.aca = pickle.load(f)
        f.close()




    def find_array(self):
        "Find the array with the obs. input"

        TP='N'
        arrayMatch = []
        scalingFrequency = self.frequencyReference / self.freqObs

        if (self.acaUse == 'Y'):
            self.LAS=self.LAST
            if self.lasObs / scalingFrequency > self.LASA[1]:
                TP='Y'

        for arr in self.array :

            if self.silent:
                print  self.LAS[arr] * scalingFrequency, self.res[arr] * scalingFrequency

            if self.LAS[arr] * scalingFrequency >= self.lasObs and self.res[arr] * scalingFrequency <= self.resObs:
                arrayMatch.append(self.array[arr])
            else:
                arrayMatch.append("")
        return arrayMatch,TP



    def find_array2(self,verbose = False):
        "Find the array with the obs. input using the precise resolution, LAS..."

        TP = 'N'
        scalingFrequency = self.frequencyReference / self.freqObs


        nData = len(self.data[0][0])
        decMin = self.data[0][0][0]
        decMax = self.data[0][0][nData-1]
        deltaDec = (decMax-decMin)/nData

        index = int(math.floor(((self.declination-decMin) / deltaDec)))

        # print index

        ### No ACA
        arrayMatch = []

        for arr in self.array :

            lasArr = self.data[arr][3][index]
            resArr = math.sqrt(self.data[arr][1][index] * self.data[arr][2][index])

            lasFreqArr = lasArr * scalingFrequency
            spatialResolutionArr = resArr * scalingFrequency

            res_thb = self.res[arr]*scalingFrequency
            las_thb = self.LAS[arr]*scalingFrequency
            elevation_factor = abs(1./math.sin(DEG2RAD*(90.-LATITUDE_ALMA+self.declination)))

            res_estimated = math.sqrt(res_thb*res_thb*elevation_factor)
            las_estimated = math.sqrt(las_thb*las_thb*elevation_factor)

            if self.silent:
                if(verbose):
                    print("# Array: %s, LAS: %5.2f, RES: %5.2f"%(self.array[arr],lasFreqArr, spatialResolutionArr ))
                    print("#          THB: LAS: %5.2f, RES: %5.2f")%(las_estimated,res_estimated)
                    # print("#")  

            if self.pointSource:
                if lasFreqArr >= self.lasObs and self.resObs >= spatialResolutionArr  :
                    arrayMatch.append(self.array[arr])
                else:
                    arrayMatch.append("")

            else :
                if lasFreqArr >= self.lasObs and self.resObs >= spatialResolutionArr and spatialResolutionArr  >= self.resObs / 2.  :
                    arrayMatch.append(self.array[arr])
                else:
                    arrayMatch.append("")

        ### ACA  used 
        if (self.acaUse == 'Y'):
            arrayMatch = []

            for arr in self.array:
                resArr = math.sqrt(self.data[arr][1][index] * self.data[arr][2][index])
                spatialResolutionArr = resArr*scalingFrequency

                ##

                if self.pointSource:
                    if self.resObs > spatialResolutionArr   and arr < 4:
                        arrayMatch.append(self.array[arr])
                    else:
                        arrayMatch.append("")

                else :
                    if self.resObs >= spatialResolutionArr   and spatialResolutionArr  >= self.resObs / 2. and arr < 4:
                        arrayMatch.append(self.array[arr])
                    else:
                        arrayMatch.append("")


            lasACA = self.aca[3][index]
            if lasACA*scalingFrequency <= self.lasObs:
                TP = 'Y'


        return arrayMatch, TP


    def find_array3(self,verbose = False):
        "Find the array with the obs. input using the precise resolution, LAS.... It takes into account a multi-configuration"

        TP = 'N'
        scalingFrequency = self.frequencyReference / self.freqObs


        nData = len(self.data[0][0])
        decMin = self.data[0][0][0]
        decMax = self.data[0][0][nData-1]
        deltaDec = (decMax-decMin)/nData

        index = int(math.floor(((self.declination-decMin) / deltaDec)))

        # Cycle 2 Match Array

        matchArrayCycle2 = {3:0,4:1,5:2,6:2}

        ###
        arrayMatchRes = []
        arrayMatchLAS = []

        lasFreqArrAll = []
        resFreqArrAll = []



        for arr in self.array :
            arrayMatchRes.append("")
            arrayMatchLAS.append("")

            lasArr = self.data[arr][3][index]
            resArr = math.sqrt(self.data[arr][1][index] * self.data[arr][2][index])

            lasFreqArr = lasArr * scalingFrequency
            spatialResolutionArr = resArr * scalingFrequency

            lasFreqArrAll.append(lasFreqArr)
            resFreqArrAll.append(spatialResolutionArr)

            res_thb = self.res[arr]*scalingFrequency
            las_thb = self.LAS[arr]*scalingFrequency
            elevation_factor = abs(1./ math.sin(DEG2RAD*(90.-LATITUDE_ALMA+self.declination)))

            res_estimated = math.sqrt(res_thb*res_thb*elevation_factor)
            las_estimated = math.sqrt(las_thb*las_thb*elevation_factor)

            if self.silent:
                if(verbose):
                    print("# Array: %s, LAS: %5.2f, RES: %5.2f"%(self.array[arr],lasFreqArr, spatialResolutionArr ))
                    print("#          THB: LAS: %5.2f, RES: %5.2f")%(las_estimated,res_estimated)
                    # print("#")  

        ########################### Comparison #######################

        notFound = True
        notFoundLAS = True

        for arr in self.array :

            lasFreqArr = lasFreqArrAll[arr]
            spatialResolutionArr = resFreqArrAll[arr]


            if self.pointSource:
                if self.resObs >= spatialResolutionArr  :
                    arrayMatchRes[arr] = self.array[arr]
                    notFound = False

            else :


                if  self.resObs >= spatialResolutionArr and spatialResolutionArr  >= self.resObs / 2.  :
                    arrayMatchRes[arr] = self.array[arr]
                    notFound = False

                    if lasFreqArr <= self.lasObs and arr > 2:
                        arrayMatchLAS[matchArrayCycle2[arr]] = self.array[matchArrayCycle2[arr]]

                        if lasFreqArrAll[matchArrayCycle2[arr]] <= self.lasObs and matchArrayCycle2[arr] > 0:
                            for i in range(0,matchArrayCycle2[arr]):
                                if lasFreqArrAll[i] >= self.lasObs :
                                    arrayMatchLAS[i] = self.array[i]
                                    notFoundLAS = False




        ### ACA  used  ###############

        if (self.acaUse == 'Y'):


            arrayMatchRes = []
            arrayMatchLAS = []

            for arr in self.array :
                arrayMatchRes.append("")
                arrayMatchLAS.append("")


            for arr in self.array:
                spatialResolutionArr = resFreqArrAll[arr]

                if  self.resObs >= spatialResolutionArr and spatialResolutionArr  >= self.resObs / 2.  :
                    arrayMatchRes[arr] = self.array[arr]
                    notFound = False

                    if  arr > 2:
                        arrayMatchLAS[matchArrayCycle2[arr]] = self.array[matchArrayCycle2[arr]]


                lasACA = self.aca[3][index]
                if lasACA*scalingFrequency <= self.lasObs:
                    TP = 'Y'


        return [arrayMatchRes,arrayMatchLAS] , TP , notFound, notFoundLAS


    def matchAR(self,resLas):
        "Match the spatial resolution for the number of configurations"


        scalingFrequency = self.frequencyReference / self.freqObs

        nData = len(self.data[0][0])
        decMin = self.data[0][0][0]
        decMax = self.data[0][0][nData-1]
        deltaDec = (decMax-decMin)/nData
        zenith = int(math.floor(((-23.0-decMin) / deltaDec)))

        ## check if the resolution is lower than the most compact one
        ##

        b0_12compact =  self.data[0][1][zenith] * scalingFrequency
        b1_12compact =  self.data[0][2][zenith] * scalingFrequency
        resCompact = math.sqrt(b0_12compact*b1_12compact)

        maxArrayCycle2 = 6
        b0_12ext =  self.data[maxArrayCycle2][1][zenith] * scalingFrequency
        b1_12ext =  self.data[maxArrayCycle2][2][zenith] * scalingFrequency
        resExt = math.sqrt(b0_12ext*b1_12ext)
        ########    

        if self.nof12m == 1:

            self.maxAR[0] = self.resOriginal * 1.1
            self.minAR[0] = self.resOriginal * 0.7

            ## We relax the condition to get at least 0.9 LAS

            for arr in self.array:
                lasArr = self.data[arr][3][zenith] *scalingFrequency
                b0 = self.data[arr][1][zenith] * scalingFrequency
                b1 = self.data[arr][2][zenith] * scalingFrequency
                res = math.sqrt(b0*b1)

                if lasArr > 0.9 * self.lasObs and res < self.minAR[0] :
                    self.minAR[0] = res


            if self.resOriginal > resCompact:
                self.minAR[0] = resCompact * 0.8
                self.maxAR[0] = self.resOriginal

            if self.resOriginal < resExt:
                self.minAR[0] = self.resOriginal
                self.maxAR[0] = resExt * 1.1






        if self.nof12m == 2:

            ## estimate the array 1

            self.minAR[0] = self.resOriginal * 0.7
            self.maxAR[0] = self.resOriginal * 1.1

            minArr = 1000
            maxArr = 0

            for s in resLas:
                for arr in self.array:
                    if s == self.array[arr]:
                        if arr < minArr:
                            minArr = arr
                        if arr > maxArr:
                            maxArr = arr

                        b0 = self.data[arr][1][zenith] * scalingFrequency
                        b1 = self.data[arr][2][zenith] * scalingFrequency
                        res = math.sqrt(b0*b1)

                        if res > self.maxAR[1]:
                            self.maxAR[1] = res
                        if res < self.minAR[1]:
                            self.minAR[1] = res


            if minArr > 0:
                b0 = self.data[minArr-1][1][zenith] * scalingFrequency
                b1 = self.data[minArr-1][2][zenith] * scalingFrequency
                res = math.sqrt(b0*b1) * 0.9
                self.maxAR[1] = res

            if self.maxAR[1] == self.minAR[1]:
                b0 = self.data[maxArr+1][1][zenith] * scalingFrequency
                b1 = self.data[maxArr+1][2][zenith] * scalingFrequency
                res = math.sqrt(b0*b1) * 1.3
                self.minAR[1] = res

            ## check on the highest spatial resolution
            if self.resOriginal < resExt:
                self.minAR[0] = self.resOriginal * 0.7
                self.maxAR[0] = resExt * 1.1







    def fixConfiguration(self,result,nof12m):
        " Fix the configurations"

        lasC = []
        extC = []

        ext = 0
        las = 0

        for s in result[0]:
            if s != '':
                ext += 1
                extC.append(s)

        for s in result[1]:
            if s != '':
                las += 1
                lasC.append(s)


        if nof12m == 2 and las == 0 :

            if extC[-1] == 'C34-7' :
                resN = ['C34-6']

            elif extC[-1] == 'C34-6':
                resN = ['C34-5']

            elif extC[-1] == 'C34-5'  :
                resN = ['C34-4']

            elif extC[-1] == 'C34-4'  :
                resN = ['C34-3']

            elif extC[-1] == 'C34-3'  :
                resN = ['C34-2']

            elif extC[-1] == 'C34-2'  :
                resN = ['C34-1']

            result[1]= resN

        return(result)


        ########################################################################3
    def silentRun(self):
        self.silent = False

    def run(self):
        "Run the matching array"

        TP="N"

        self.set_res(float(self.args[1]))
        self.set_las(float(self.args[2]))
        self.set_frequency(float(self.args[3]))
        self.set_declination(float(-23.0))
        self.set_aca((self.args[4]))
        self.set_12m(int(self.args[5]))

        if self.lasObs == 0.:
            self.set_pointSource(True)


        strOut = "### arrayResolution2p \n"
        strOut += "### Version: %s \n"%(__version__)
        strOut += "### Input \n"
        if self.pointSource:
            strOut += "# Point Source ! \n"
        strOut += "# Spatial Resolution: %s \n"%(self.args[1])
        strOut += "# LAS: %s \n"%(self.args[2])
        strOut += "# Frequency: %s GHz \n"%(self.args[3])
        # strOut += "# Declination: %s \n"%(self.args[4])
        strOut += "# 7-m Array (Y/N): %s \n"%(self.args[4])
        strOut += "# Num. of 12-m Array: %d \n\n"%(self.nof12m)
        strOut += "### Output (target frequency) \n"
        strOut += "### Using CASA simulation with natural weighting (slightly different of THB)"

        if self.silent:
            print(strOut)


        notFound = True
        maxTry = 100
        nTry = 1
        deltaFudgeFactor = 0.05
        fudgeFactor = 1.0

        res , TP , notFound , notFoundLAS = self.find_array3(verbose = True)



        while (notFound and nTry < maxTry and notFoundLAS and self.acaUse == 'N' ):

            nTry += 1
            notFound = False
            fudgeFactor += deltaFudgeFactor
            self.resObs *= fudgeFactor
            self.lasObs /= fudgeFactor
            res , TP , notFound , notFoundLAS = self.find_array3()


        while (notFound and nTry < maxTry ):

            nTry += 1
            notFound = False
            fudgeFactor += deltaFudgeFactor
            self.resObs *= fudgeFactor
            res , TP , notFound , notFoundLAS = self.find_array3()




        if nTry > 1 :
            if self.silent:
                print("# No array configuration found, fudge factor applied (Tol = %3.0f %%)"%((fudgeFactor-1.)*100.))

        if notFound and nTry > 1:
            if self.silent:
                print("# No array configuration found, even with fudge factor, problem ...")


        strOutRes = ""
        strOutLAS = ""
        pcomR = ""
        pcomL = ""

        if self.silent:
            print ""
            print("### Results  - AR - LAS")

        if notFound :
            if self.silent:
                print ",,,,,"
        else:
            for s in res[0]:
                strOutRes += pcomR+s
                pcomR = ","
            strOutRes += ","
            strOutRes += TP

            for s in res[1]:
                strOutLAS += pcomL+s
                pcomL = ","
            strOutLAS += ","
            strOutLAS += TP

            # if self.silent:
            # print strOutLAS
            #  print strOutRes


        resN = self.fixConfiguration(res, self.nof12m)


        self.matchAR(resN[1])


        if self.nof12m == 1:
            print("One Array:")
            print("Min Resolution : %5.2f "%(self.minAR[0]))
            print("Max Resolution : %5.2f "%(self.maxAR[0]))
            return self.minAR[0], self.maxAR[0], 0., 0.

        elif self.nof12m == 2:
            print("Extended Array:")
            print("Min Resolution minAR_e %5.2f "%(self.minAR[0]))
            print("Max Resolution maxAR_e %5.2f "%(self.maxAR[0]))
            print("Compact Array:")
            print("Min Resolution minAR_c %5.2f "%(self.minAR[1]))
            print("Max Resolution maxAR_c %5.2f "%(self.maxAR[1]))
            return self.minAR[0], self.maxAR[0], self.minAR[1], self.maxAR[1]

        #====== Standalone program =========================
if __name__ == "__main__":

    arg = sys.argv

    if len(arg) < 6:
        print "Arguments missing \n"
        print "The correct syntax is:"
        print "python arrayResolution2p.py RES (arcsec) LAS (arcsec) FREQ (GHz) Y/N (ACA) numberofarray \n"
        print "Example:"
        print "python arrayResolution2p.py 0.2 2.0  640.  Y  1   ## if LAS = 0. assumes a point source"

    else:
        a = arrayRes(arg)
        a.run()
