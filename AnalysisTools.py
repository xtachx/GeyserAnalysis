#!/usr/bin/env python

#This file provides the analysis tools for
#Geyser's Acoustic Data. PVar, FVar etc definitions
#taken from Elog, here:
#https://picassoweb.lps.umontreal.ca/elog/Physics/48

#Numpy is python's number cruncing library. For math ops
#like cumsum etc. Scipy is scientific library
import numpy, scipy

class AcousticsAnalysis():
    
    #Dont know if init needs anything yet, lets see
    
    def __init__(self):
        pass
    
    #This class calculates PVar of the data
    #PVar definition is in:
    #https://picassoweb.lps.umontreal.ca/elog/Physics+Paper+2011/11
    #Taken from M.C. Piro's definition of PVar in Matlab code
    
    def calculatePVar(self, data, start_sample=13000, end_sample=20000):
        '''
        Calculates PVar -> Energy of the Waveform
        Needs:
        
        start_sample -> Where does the waveform begin
        Geyser Default: 13000
        
        end_sample -> where does the waveform end
        Geyser Default: 20000
        '''
        
        #Reshape the data to the working region, so we have
        #Less memory overhead
        WorkingRegion = data[start_sample:end_sample]
        NumberOfSamples = end_sample - start_sample 
        
        #Find the power of the signal
        sqr_power = numpy.power(WorkingRegion,2)
        
        #Find the cumulative sum of the data
        DataCumulativeSum = numpy.cumsum(sqr_power)
        
        #Find the max of the cumulative sum.
        #instead of max(DataCumulativeSum) we use
        #DataCumulativeSum[:-1] to take the last variable
        #This saves an extra calculation.
        MaxCumulativeSum = DataCumulativeSum[-1:]
        
        #Define a "baseline" int he cumulative sum to subtract from
        CumSumBaseline = (xrange(0,NumberOfSamples))*MaxCumulativeSum/NumberOfSamples
        
        #subtract the baseline from cumulative sum
        CumSumSansBaseline = abs(DataCumulativeSum - CumSumBaseline)
        
        #Integrate the CumSumSansBaseline
        IntegralDifference = sum(CumSumSansBaseline)
        
        #PVar value is given by log(IntegralDifference)
        return numpy.log(IntegralDifference)
    
    #This function calculates the max amplitude of the signal
    def calculateMaxAmp(self, data, start_sample=13000, end_sample=20000):
        '''
        Calculates Max Amplitude 
        Needs:
        
        start_sample -> Where does the waveform begin
        Geyser Default: 13000
        
        end_sample -> where does the waveform end
        Geyser Default: 20000
        '''
        WorkingRegion = data[start_sample:end_sample]
        
        return max(abs(WorkingRegion))
    
    #this function applies high pass and low pass filters
    def ApplyFiltersWall(self, data, lowFreq, highFreq, SampleFreq=1250000.0):
        '''Applies FFT software filters.
        In -> Data, lowFreq, highFreq
        Out-> filteredSignal
        
        Warning: Appling a blank wall filter is the same as
        convolving with sinc function!!
        THIS PRODUCES RINGING!!
        '''
        #Perform FFT
        fftsigs=numpy.fft.fft(data)
        fftfreqs = numpy.fft.fftfreq(len(data),1.0/SampleFreq)
        
        
        #Apply blank wall filter by cutting off the unwanted frequencies
        if lowFreq is not None:
            lowfreq_pos =  [i for i,x in enumerate(fftfreqs) if lowFreq-10<=x<=lowFreq+10]
            for i in range(lowfreq_pos[0]):
                    fftsigs[i]=0
            #for i in range(len(fftsigs)):
            #    if abs(fftfreqs[i])<=lowFreq:
            #        fftsigs[i]=0
                    
        if highFreq is not None:
            for i in range(len(fftsigs)):
                if fftfreqs[i]>=highFreq:
                    fftsigs[i]=0
        #Regenerate Signal
        return scipy.ifft(fftsigs, n=len(fftsigs)/2)
    
    def ApplyFiltersFIR(self, data, lowFreq, highFreq, SampleFreq=1250000):
        '''
        FIR filter is the Finite Impulse Response
        high speed filter based on FFT using Kaiser Window.
        To change window, use the window ="" param
        Recommended: Kaiser, Blackman-Harris, Gaussian, Hamming and Hanning.
        '''
        import scipy.signal as signal
        
        #Construct the filter
        #HighPass
        if lowFreq is not None:
            SignalFilter=signal.firwin(151, lowFreq ,pass_zero=False,nyq=SampleFreq/2)
        #lowpass
        if highFreq is not None:
            SignalFilter=signal.firwin(151, highFreq ,pass_zero=True,nyq=SampleFreq/2)
        
        #Apply the filter
        filtered_data = signal.lfilter(SignalFilter,1.0,data)
        #done
        return filtered_data
        
        