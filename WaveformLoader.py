#This module is designed to load wf files and
#wfi files and return waveform data. Please use
#this as a MODULE and not as a standalone file.


#Itertools for efficient iteration
import itertools

#Numpy for some processing and cleaning up the data
import numpy

#This class loads waveforms from parsed file names

class LoadWave():
    
    #init takes nothing
    
    def __init__(self):
        pass
    
    #Function to get raw data
    
    def _getRawData(self, filename):
        #the fileformat is binary
        #2 bytes (int16) is 1 datapoint
        raw_data = numpy.fromfile(filename+".wf",dtype='int16')
        return raw_data
    
    #This function gets scope settings
    #for the trigger we are looking at
    
    def _getScopeSettings(self, filename):
        
        #Number of bytes captured in the waveform
        #This is our sample size. Should be an even number
        #See getRawData for an explanation.
        
        NumBytes = 0.0
        
        #Vertical gain of the Osc. This converts raw
        #data to mV.
        
        VerticalGain = 0.0
        
        #Vertical Offset, for corrections.
        
        VerticalOffset = 0.0
        
        #Horizontal Interval gives the resolution of the scope
        
        HorizontalInterval = 0.0
        
        #Horizontal Interval gives the delay before trigger
        
        HorizontalOffset = 0.0
        
        #How many bytes in the binary file do each point
        #represent. Should be short or uint16 (2 bytes)
        
        NumBytePerPoint = 0.0
        
        #open a file as an iterator with each line being an iteration.
        
        FileIterator = itertools.islice(file.readlines(open(filename+".wfi")), None)
    
        for line in FileIterator:
            if "Number of bytes:" in line:
                NumBytes = float(FileIterator.next())
            if "Vertical gain" in line:
                VerticalGain = float(FileIterator.next())
            if "Vertical offset" in line:
                VerticalOffset = float(FileIterator.next())
            if "Horizontal interval" in line:
                HorizontalInterval = float(FileIterator.next())
            if "Horizontal offset" in line:
                HorizontalOffset = float(FileIterator.next())
            if "Number of bytes per data-point" in line:
                NumBytePerPoint = float(FileIterator.next())
        
        SampleSize = int(NumBytes / NumBytePerPoint)
        
        return VerticalGain, VerticalOffset, HorizontalInterval, HorizontalOffset, SampleSize
    
    #package it all together and return!
    def LoadData(self, filename, badWaveFilter = False):
        
        #Get the data first
        
        data = self._getRawData(filename)
        
        #Now get the info
        
        VerticalGain, VerticalOffset, HorizontalInterval, HorizontalOffset, SampleSize = self._getScopeSettings(filename)
        #process the data
        #First, get the baseline correction
        Baseline = numpy.mean(data[0:10000])
        #apply correct gains and baseline correction
        
        processed_data = 1000.0*VerticalGain*(data-SampleSize*[Baseline])
        #if we have the bad wave filter On
        if badWaveFilter:
            data_mean = numpy.mean(processed_data)
            #if the data is bad, return 0
            if data_mean < 0.5:
                return 0
            else:
                #If the data is good, return it
                return processed_data, HorizontalInterval
        #this else is if the bad wave filter isnt running
        else:
            return processed_data, HorizontalInterval