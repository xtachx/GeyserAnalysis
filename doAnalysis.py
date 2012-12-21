#!/usr/bin/env python

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

#numpy for math
import numpy

#Signal manip for signal manipultions
import SignalManip

#This class does the analysis on the dataset based on params given
class doAnalysis:
    
    #What do we need in init now? Ah, the analysis cache DB
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
        
        self.SignalManip = SignalManip.SignalManip()
        
        
    #If DB doesnt exist, make it!
    def genPDL(self):
        #Create the PDL file for database
        self.AnalysisResults.create('EventID','PVar', mode = "open")
    
    #Gen PVAr of the Signals!
    def genPVAR(self):
        
        '''
        Filter Params.
        
        doFilter -> Filter on or OFF
        lowfreq_HP -> Low frequency High Pass
        highFreq_LP -> High Frequency low pass
        
        Set both for a band pass filter.
        
        Filter Types:
        ApplyFiltersWall -> Boxcar window
        ApplyFiltersFIR -> Kaiser Window
        '''
        
        doFilter = True
        lowFreq_HP = 3000
        highFreq_LP = None
        
        
        ####Neutron Data#####
        #get the list of events
        PVar_Neutron_List = []
        EventList = self.PassportOffice.CheckPassport_Runtype("Neutron")
        
        #For every Event
        for Event in EventList:
            
            #Load Raw data
            raw_data = self.LoadWaveform.LoadData(Event['Path'][:-3])
            
            #Apply filter. See the docstring
            #for options
            if doFilter:
                filtered_data = self.AcousticAnalysis.ApplyFiltersWall(raw_data[0], lowFreq=lowFreq_HP, highFreq=highFreq_LP)
            else:
                filtered_data = raw_data[0]
            
            #Calculate PVAR
            PVar = self.AcousticAnalysis.calculatePVar(filtered_data)
            
            #PVAr > 25 were observed for events from the wall from 1 specific run!
            #We dont know what to do with those yet.
            
            #if PVar<20:
            PVar_Neutron_List.append(PVar)
                
        ##########Plotting#########
        hist_bins = numpy.arange(10,13.0,0.1)
        #hist_bins=20
        plt.hist(PVar_Neutron_List, bins=hist_bins, normed=True, facecolor='green', alpha=0.75)
        plt.grid(True)
        plt.xlabel("PVar")
        plt.ylabel("Count")
        plt.title("PVar of Entire Dataset")
        
        
        #### ALPHA DATA ####
        PVar_Alpha_List = []
        EventList = self.PassportOffice.CheckPassport_Runtype("Alpha")
        for Event in EventList:
            #get raw data
            raw_data = self.LoadWaveform.LoadData(Event['Path'][:-3])
            #Apply filter. See the docstring
            #for options
            if doFilter:
                filtered_data = self.AcousticAnalysis.ApplyFiltersWall(raw_data[0], lowFreq=lowFreq_HP, highFreq=highFreq_LP)
            else:
                filtered_data = raw_data[0]
            PVar = self.AcousticAnalysis.calculatePVar(filtered_data)
            PVar_Alpha_List.append(PVar)
        
        ########Plotting#######
        #print PVar_Alpha_List
        plt.hist(PVar_Alpha_List, bins=hist_bins, normed=True, facecolor='red', alpha=0.40)
        
        
        plt.show()
        
    #Functions to show the Average values (load from cache)
    def PlotSignalAverage(self):
        
        #Run 2X to get data for alpha and for neutron
        data_neutron = self.SignalManip.getSignalAverage(EventType = "Neutron")
        data_alpha = self.SignalManip.getSignalAverage(EventType = "Alpha")
        
        ###Plotting###
        plt.plot(data_neutron,'g-')
        plt.plot(data_alpha,'r-')
        plt.xlabel("Timestep")
        plt.ylabel("Signal (mv)")
        plt.grid(True)
        plt.show()
    
    #function to show average FFT
    def PlotFFTAverage(self):
        
        #Run 2X to get data for alpha and for neutron
        FFTs_neutron, FFTfreqs = self.SignalManip.getFFTAverage(EventType = "Neutron", doWin=False)
        FFTs_alpha, FFTfreqs_alpha = self.SignalManip.getFFTAverage(EventType = "Alpha", doWin=False)
        
        #get half length of FFT for plotting
        length = len(FFTs_neutron)
        halflength = length/2
        FFTAvgBins_kHz_HL = FFTfreqs[:halflength]/1000.0
         
        
        #PLOTTING#
        plt.plot(FFTAvgBins_kHz_HL, abs(FFTs_neutron[:halflength]),'g-')
        #plt.plot(abs(FFTs_neutron[:halflength]),'g-')
        plt.plot(FFTAvgBins_kHz_HL, abs(FFTs_alpha[:halflength]),'r-')
        
        plt.xlabel("Frequency")
        plt.ylabel("Count")
        plt.title("Average FFT of all signals")
        plt.grid(True)
        plt.show()
       
    
        
    #################
    ################
    ################
    ###THIS FUNCTION IS MY TEST BED AND HAS NO COMMENTS
    #Nor do I plan on putting some!!
    def _ApplyFilter(self):
        PVar_Neutron_List = []
        EventList = self.PassportOffice.CheckPassport_Runtype("Neutron")
        Loc = EventList[12]['Path'][:-3]
        
        EventList2 = self.PassportOffice.CheckPassport_Runtype("Alpha")
        Loc2 = EventList2[12]['Path'][:-3]
        
        raw_dataNeutron = self.LoadWaveform.LoadData('Piezo/triggers.Nov23/trigger_2012.11.23_12.56.15_run_196_110_85')
        #raw_dataNeutron = self.LoadWaveform.LoadData(Loc)
        raw_dataN = raw_dataNeutron[0]
        
        raw_dataAlpha = self.LoadWaveform.LoadData(Loc2)
        raw_dataA = raw_dataAlpha[0]
        #r_data = numpy.zeros((50000))
        #r_data[13000:20000]=raw_data[13000:20000]
        #r_data=raw_data[0]
        #raw_data=r_data
        SampleTime = raw_dataN[1]
        #print 1.0/SampleTime
        
        
        n = len(raw_dataN)
        #filtered_data = self.AcousticAnalysis.ApplyFiltersWall(raw_data, lowFreq=10000, highFreq=None)
        #print filtered_data
        fftsN = numpy.fft.rfft(raw_dataN)
        fftsN = fftsN[:n/2]
        fftfreqsN = numpy.fft.fftfreq(len(raw_dataN), 1.0/1250000.0)
        fftfreqsN = fftfreqsN[:n/2]
        
        fftsA = numpy.fft.rfft(raw_dataA)
        fftsA = fftsA[:n/2]
        fftfreqsA = numpy.fft.fftfreq(len(raw_dataA), 1.0/1250000.0)
        fftfreqsA = fftfreqsA[:n/2]
        
        
        
        #############PLotting##############
        
        plt.title('Data and FFT of Signal')
        ax1 = plt.subplot2grid((4,3), (0,0), colspan=3)
        ax2 = plt.subplot2grid((4,3), (1,0), colspan=3)
        
        
        #data
        ax1.plot(raw_dataN,'g-')
        ax1.set_xlabel('Sample (S.Time = 8e-7s)')
        ax1.set_ylabel('Amplitude (mV)')
        ##### Data INFO
        
        #Low vs High cutoff
        plotrange = 10000
        plotrange_cutoff = 600
        ##########
        
        #All
        ax2.plot(raw_dataA,'r-')
        #ax2.locator_params(axis = 'x',nbins=50)
        ax2.set_xlabel('Frequency (kHz)')
        ##plt.show()
        ##plt.clf()
        #
        #
        #
        #########Plot 2########
        ax3 = plt.subplot2grid((4,3), (2,0), colspan=3)
        ax4 = plt.subplot2grid((4,3), (3,0), colspan=3)
        ##Low
        ax3.plot(abs(fftN),'g-')
        #ax3.plot(fftfreqsN/1000,abs(fftsN),'g-')
        #ax3.locator_params(axis = 'x',nbins=50)
        #ax3.set_xlabel('Frequency (kHz)')
        #ax3.set_ylabel('Count')
        ##high
        ax4.plot(abs(fftsA),'r-')
        #ax4.plot(fftfreqsA/1000,abs(fftsA),'r-')
        ax4.locator_params(axis = 'x',nbins=50)
        ax4.set_xlabel('Frequency (kHz)')
        ##ax4.set_ylabel('Count')
        
        plt.show()
        
        

if __name__ == "__main__":
    a = doAnalysis()
    #a.PlotFFTAverage()
    #a.PlotSignalAverage()
    #a._ApplyFilter()
    a.genPVAR()