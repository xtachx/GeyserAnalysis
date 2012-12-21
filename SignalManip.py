#!/usr/bin/env python

#This file is intended for manipulating signals such as
#generate an avergae of all signals, save this etc etc,
#especially when we need to physically change the signal to
#do our analysis.

#We need the EventPassport
import EventPassport

#AnalysisTools gives uf the tools for analysis
import AnalysisTools

#waveformloader loads waveforms
import WaveformLoader

#pydblite needed for database
from PyDbLite import Base

#matplotlib for plotting
import matplotlib.pyplot as plt

#numpy and scipy for scientific ops
import numpy, scipy

#OS is for checking if certain files exist
import os

#signal Manip class for signal manipulation
class SignalManip:
    
    #usual stuff in init
    def __init__(self):
        self.AnalysisResults = Base('AnalysisResults/AnalysisResults.pdl')
        
        #check if the DB exists. If Yes, open, if not
        #create it:
        if not self.AnalysisResults.exists():
            self.genPDL()
        else:
            self.AnalysisResults.open()
        
        self.PassportOffice = EventPassport.EventPassportOffice()
        self.LoadWaveform = WaveformLoader.LoadWave()
        self.AcousticAnalysis = AnalysisTools.AcousticsAnalysis()
        
        
    #If DB doesnt exist, make it!
    def genPDL(self):
        #Create the PDL file for database
        self.AnalysisResults.create('EventID','PVar', mode = "open")
    
    #Function to generate signal average
    def genSignalAverage(self, EventType = "Neutron"):
        #get all Events of type EventType
        EventList = []
        EventList = self.PassportOffice.CheckPassport_Runtype(EventType)
        
        SignalAvgMem = numpy.zeros((50000))
        
        for Event in EventList:
            #Load Raw data
            raw_data = self.LoadWaveform.LoadData(Event['Path'][:-3])
            SignalAvgMem += raw_data[0]
        
        SignalAvgMem /= len(EventList)
        
        ####Storage#####
        Storage = open("AnalysisResults/signalAvg."+EventType+".binary", "wb")
        SignalAvgMem.tofile(Storage, format="%f")
        Storage.close()
        
        return SignalAvgMem
    
    #function to generate FFT avergae
    def genFFTAverage(self, EventType="Neutron", doWin = False, winStart=10000, winEnd=30000, Fs = 1250000.0):
        #get all Events of type EventType
        EventList = []
        EventList = self.PassportOffice.CheckPassport_Runtype(EventType)
        
        
        
        
        FFTAvgMem = numpy.zeros((50000))
        FFTAvgBins = numpy.fft.fftfreq(len(FFTAvgMem), 1.0/Fs)
        
        
        for Event in EventList:
            #Load Raw data
            raw_data = self.LoadWaveform.LoadData(Event['Path'][:-3])
            
            
             
            
            ####SignalWindow####
            if doWin:
                print "is it"
                TempSigMem = numpy.zeros((50000))
                TempSigMem[winStart:winEnd] = raw_data[0][winStart:winEnd]
                R_data = TempSigMem
            else:
                R_data = raw_data[0]
            
            #
            
            FFTs = numpy.fft.fft(R_data)
            
            #for i in range(5000,6000):
            #pwrspec = abs(numpy.mean(FFTs[5000:6000]))
            #if pwrspec>10:
            #    print pwrspec, Event
            
            
            FFTAvgMem += FFTs
        
        
        
        FFTAvgMem /= len(EventList)
        
        
        
        ####Storage#####
        #FFT#
        Storage = open("AnalysisResults/FFTAvg."+EventType+"win"+str(doWin)+".binary", "wb")
        FFTAvgMem.tofile(Storage, format="%f")
        Storage.close()
        #FFT FREQS#
        Storage = open("AnalysisResults/FFTAvgBins."+EventType+"win"+str(doWin)+".binary", "wb")
        FFTAvgBins.tofile(Storage, format="%f")
        Storage.close()
        
        ####Plotting#####
        
        return FFTAvgMem, FFTAvgBins
    
    #Functions to show the Average values (load from cache)
    def getSignalAverage(self, EventType = "Neutron"):
        
        Storage = "AnalysisResults/signalAvg."+EventType+".binary"
        
        if not os.path.exists(Storage):
            data = self.genSignalAverage(EventType)
        else:
            data = numpy.fromfile(Storage)
            
        
        return data
    
    #function to show average FFT
    def getFFTAverage(self, EventType = "Neutron", doWin = False,):
        
        Storage_FFT = "AnalysisResults/FFTAvg."+EventType+"win"+str(doWin)+".binary"
        Storage_FFTfreq = "AnalysisResults/FFTAvgBins."+EventType+"win"+str(doWin)+".binary"
        
        #Broken. Needs param check and hassles.
        #if os.path.exists(Storage_FFT) and os.path.exists(Storage_FFTfreq) :
        #    data_FFT = numpy.fromfile(Storage_FFT)
        #    data_FFTFreq = numpy.fromfile(Storage_FFTfreq)
        #else:
        #    data_FFT, data_FFTFreq = self.genFFTAverage(EventType, doWin)
        
        
        data_FFT, data_FFTFreq = self.genFFTAverage(EventType, doWin)
        
        return data_FFT, data_FFTFreq
            

if __name__ == "__main__":
    
    Usage = '''Usage: This is meant to be used as a module\n
    and not standalone script. Please use the methods\n
    built in, as a module. '''
    
    print Usage