#!/usr/bin/python

"""
S. Leon @ ALMA

Classes, functions to be used for the array configuration evaluation with CASA

HISTORY:
    2011.11.06:
        - class to create the Casas pads file from a configuration file
        
    2011.11.09:
        - Class to compute statistics on the baselines
        
    2012.03.07L:
        - Class to manipulate the visibilities
        
    2012.05.22:
        - Change name of ArrayStatistics
        - add plotAntPos
        
    2012.11.30:
        - Modification of createCasaConfig from a list of Pads (not a file)
        
    2013.03.22:
        - Modification of createCasaConfig  to read as well from a file
        
        
    2013.04.19:
        - Update Arrayinfo.stats to get the information in the instance.
        
        
    2013.04.20:
        - Put the padPositionfile as a parameter
        
    2013.09.13:
        - fix a CASA problem
 

RUN:

## Create a CASA file
a=ArrayConfigurationCasaFile()
a.createCasaConfig("/home/stephane/alma/ArrayConfig/Cycle1/configurations/cycle1_config.txt")


CASA> :
sys.path.insert(0,'/home/stephane/git/ALMA/ALMA/ArrayConfiguration/')

"""

__version__="0.2.2@2013.09.13"
__author__ ="ALMA: SL"


import numpy as np
import os
import pickle
from math import sqrt
import pylab as pl

home = os.environ['WTO']

class ArrayConfigurationCasaFile:
    """
    Class to create the CASA configuration file matching the Pads and the positions
    """
    
    def __init__(self, padPositionFile = home + "conf/Pads.cfg"):
        
        self.padPositionFile = padPositionFile
        self.pad={}
        self.__readPadPosition__()
        
    def __readPadPosition__(self):
        "Read the position of all the Pads and put them in a Dictionary"
        
        
        padFile=open(self.padPositionFile,"r")
             
        
        dump=padFile.readline()
        while(dump != ""):
            
            if dump[0] !="#":
                padsplt=dump.split()
                self.pad[padsplt[4]]=[padsplt[0],padsplt[1],padsplt[2],padsplt[3]]
        
            dump=padFile.readline()
            
         
        padFile.close()   



    def createCasaConfig(self,configurationFile,listPads = []):
        """
        If listPads is not empty, it will use configurationFile to create the CASA file.
        """
                       
            
        # Creating the array config files
        
        headerCasa="# observatory=ALMA\n"
        headerCasa+="# coordsys=LOC (local tangent plane)\n"
        headerCasa+="# x y z diam pad#\n"
        
            
            
        ## Read the Pads in configurationFile if listPads is empty
        
        if len(listPads) == 0:
            listPads = []
            
            fin = open(configurationFile)
            
            for pad in fin:
                dat = pad.split()
                listPads.append(dat[0])
            
            fin.close

               
        configurationFile +=".cfg"
        f = open(configurationFile,"w")
        f.write(headerCasa) 
        
        
        for pads in listPads:

            line=""
            for s in self.pad[pads]:
                line += s+" "
            line+=pads
            line+="\n"
                
            f.write(line)
        
        print "### %s created."%(configurationFile)   
        f.close()
            


class ArrayInfo:
    """
    Compute the Statistics from a CASA array file.
    max baseline, min baseline, rms, etc...
    
    """
    
    def __init__(self,filename):
        
        self.filename=filename
        self.xPos = []
        self.yPos = []
        self.antName = []
        self.__readFileArray__()
        
    def __readFileArray__(self):
        "Read  the CASA file array and create the self.baseline array"
        
        f=open(self.filename)
        
        dump=f.readline()
        while dump[0] == "#":
            dump=f.readline()
        
        ant=[]    
        xMean = 0.
        yMean = 0.
        while dump != "":
            dataAnt=dump.split()
            if dataAnt[0][0] != '#':
                ant.append([float(dataAnt[0]),float(dataAnt[1])])
                self.xPos.append(float(dataAnt[0]))
                self.yPos.append(float(dataAnt[1]))
                self.antName.append(dataAnt[4])
                xMean += float(dataAnt[0])
                yMean += float(dataAnt[1])
            
            dump=f.readline()
            
        nAnt=len(ant)
        xMean = xMean / nAnt
        yMean = yMean / nAnt
        
        self.xMean = xMean
        self.yMean = yMean
        
        for i in range(nAnt):
            self.xPos[i] -= xMean
            self.yPos[i] -= yMean
        
        nBl=(nAnt*(nAnt-1))/2
        self.baseline=np.zeros(nBl,np.float32)
        
        indexBl=0
            
        for i in range(0,nAnt):
            for j in range(i+1,nAnt):
                blij2=(ant[i][0]-ant[j][0])*(ant[i][0]-ant[j][0])+(ant[i][1]-ant[j][1])*(ant[i][1]-ant[j][1])
                self.baseline[indexBl]=sqrt(blij2)
                indexBl+=1
        
        print "Number of baselines: %d"%(nBl)
       
 
    def stats(self):
        "compute the statistics on self.baseline"
        
        self.minBl=np.amin(self.baseline)
        self.maxBl=np.amax(self.baseline)
        bl2=self.baseline*self.baseline
        self.rms=sqrt(np.average(bl2))
        
        print "Array: %s"%(self.filename)
        print "x Pos. Mean:%f"%(self.xMean)
        print "y Pos. Mean:%f"%(self.yMean)
        print "Min. baseline:%f"%(self.minBl)
        print "Max. baseline:%f"%(self.maxBl)
        print "RMS of the baselines:%f"%(self.rms)
        print "\n"


    def  plotAntPos(self,xmin=-100,xmax=100,ymin=-100.,ymax=100,title='ALMA',xtitle=75.,ytitle=75.,figure=None):
        "plot the positions of the antennas"
        
        fig = pl.figure()

        ax = fig.add_subplot('111')
       
        ax.plot(self.xPos,self.yPos,'ro',markersize = 10.)
        
        index = 0
        for name  in self.antName:
            xx = self.xPos[index]
            yy = self.yPos[index]
            ax.text(xx,yy,name)
            index += 1
            
        
        ax.set_xlabel('X (meter)')
        ax.set_ylabel('Y (meter)')
        
        ax.set_xlim((xmin,xmax))
        ax.set_ylim((ymin,ymax))
 
        ax.text(xtitle,ytitle,title)
        
        # pl.show()
        if figure != None:
            pl.savefig(figure)

        
        
        


            
            
class visibility:
    
    def __init__(self,visname):
        self.visname = visname
        
                        
        
########################Main program####################################
if __name__=="__main__":
    " main program"      
          
        
    ## a=ArrayConfigurationCasaFile()
    ## a.createCasaConfig("/home/stephane/alma/ArrayConfig/Cycle1/configurations/cycle1_config.txt")
    
    
   