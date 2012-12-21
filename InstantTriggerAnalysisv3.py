#!/usr/bin/env python

import numpy
#from scipy.fftpack import fft as scipy_fft
#from scipy.fftpack import fftfreq 

from numpy.fft import fft as scipy_fft
from numpy.fft import fftfreq

import matplotlib.pyplot as plt
from optparse import OptionParser
import matplotlib.gridspec as gridspec
import itertools



def FFT(data, Timestep):  #Fs is sample rate
    n = len(data)
    #freq = k/T #two sides frequency range
    #freq = freq[range(n/2)] #1 side frequency range
    
    freq = fftfreq(data.size, d=Timestep)
    freq = freq[range(n/2)]
    #freq = (numpy.arange(0,n/2)) * (Fs / n)
    
    print "Length of X-Axis: "+str(len(freq))
    Y = scipy_fft(data) /n #fft and normalize
    Y = Y[range(n/2)]
    print "Length of Y-Vals "+str(len(Y))
    
    return freq, abs(Y)


    
def PlotandFFT(data, wfi_info):
    
    VGain = wfi_info[0]
    Ts = wfi_info[2]
    Fs = 1.0/Ts #sample rate
    #do FFT
    bFreq, bY = FFT(data, Ts)
    
        
    
    #Plotting stuff - plot 1
    #ax = plt.subplot2grid((2,2),(0, 0))
    plt.title('Data and FFT of Signal')
    ax1 = plt.subplot2grid((4,3), (0,0), colspan=3)
    ax2 = plt.subplot2grid((4,3), (1,0), colspan=3)
    
    
    #data
    scaled_data = data*VGain*1000.0
    ax1.plot(scaled_data,'g-')
    ax1.set_xlabel('Sample (S.Time = 8e-7s)')
    ax1.set_ylabel('Amplitude (mV)')
    ##### Data INFO
    data_info = "Sampling Frequency: "+str(Fs/1000000)+" MHz \nNumber of Samples: "+str(wfi_info[4])
    data_min = min(scaled_data)
    ax1.text(1000, data_min*0.9, data_info, fontdict=None)
    
    #Low vs High cutoff
    plotrange = 10000
    plotrange_cutoff = 600
    ##########
    
    #All
    #ax2.semilogy(bY,'g-')
    ax2.plot(bFreq/1000.0, bY,'g-')
    ax2.locator_params(axis = 'x',nbins=50)
    ax2.set_xlabel('Frequency (kHz)')
    #plt.show()
    #plt.clf()
    
    
    
    ########Plot 2########
    ax3 = plt.subplot2grid((4,3), (2,0), colspan=3)
    ax4 = plt.subplot2grid((4,3), (3,0), colspan=3)
    #Low
    ax3.semilogy(bFreq[0:plotrange_cutoff]/1000, bY[0:plotrange_cutoff],'b-')
    ax3.locator_params(axis = 'x',nbins=50)
    ax3.set_xlabel('Frequency (kHz)')
    ax3.set_ylabel('Count')
    #high
    ax4.semilogy(bFreq[plotrange_cutoff:plotrange]/1000, bY[plotrange_cutoff:plotrange],'b-')
    ax4.locator_params(axis = 'x',nbins=50)
    ax4.set_xlabel('Frequency (kHz)')
    #ax4.set_ylabel('Count')
    
    plt.show()
    

def debugprint(*args):
    final = ""
    for i in args:
        final += str(i)
    print final
        
        
def getWFIinfo(filename):
    NumBytes = 0.0
    VerticalGain = 0.0
    VerticalOffset = 0.0
    HorizontalInterval = 0.0
    HorizontalOffset = 0.0
    NumBytePerPoint = 0.0
    
    FileIterator = itertools.islice(file.readlines(open(filename)), None)
    
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
    
    SampleSize = NumBytes / NumBytePerPoint
    
    return VerticalGain, VerticalOffset, HorizontalInterval, HorizontalOffset, SampleSize
    
def PlotDataAndFFT(filename):
    wfi_info = getWFIinfo(filename+".wfi")
    data = numpy.fromfile(filename+".wf",dtype='int16')
    PlotandFFT(data, wfi_info)


    


if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-f", "--filename", dest="filename", help="Data Filename (omit the wf)", metavar="FNAME")
    parser.add_option("-d", "--dirname", dest="dirname", help="Data directory", metavar="DNAME")
    (options, args) = parser.parse_args()
    file_path = str(options.dirname)+"/"+str(options.filename)
    PlotDataAndFFT(file_path)
    #PlotTestandFFT()
    #Manager("192.168.1.190", 1, 10.0, options.run_number)
