#!/usr/bin/env python

#This file containes functions to clean signals by
#corroborating them wih other forms of data
#such as pressure or the camera for the piezo and vice
#versa

#Glob is for parsing files in a folder
import glob

#datetime is for date and time ops
from datetime import datetime, timedelta

#PressureVeto is for the timing of bubles from pressure rise
import PressureVeto


class CleanData:
    #What do we need in init?
    #Remember, variables in init need GC
    #and or manipulation methods!
    def __init__(self):
        #space for triggers from the present run being investigated
        self.ThisRunTriggers = []
        #Minimum time separation between events
        self.meanTimeBetweenTriggers = timedelta(seconds=10)
        
        
    #This function filters the list of events, which passes
    #the time cut. 
    def MakeAcousticEventList(self, Path, RunNumberAcoustic):
        '''
        Takes in a folder and applies a time cut
        between the triggers, and returns a list of triggers
        separated by a threshold of time, so we know
        that these are distinct events.
        
        In: Folder
        Out: List of time filtered triggers, timings.
        
        Note: Even after the time cut, some electronic noise will
        pass the trigger. Sometimes these are people closing doors
        or people working, someone walking by
        or simply vibrations in the room or amplifier noise/spikes.
        
        These can be filtered with a pressure veto cut, worked out in
        CleanData.MatchEvent_PressurePiezo(Path, RunNumberAcoustic, RunNumberPressure)
        '''
        #get a list of Acoustic triggers in the given folder
        allfiles = glob.glob(Path+"*.wf")
        #Make sure the memory is clean before we write.
        self.ThisRunTriggers = []
        ValidTriggers = []
        
        #make a list of paths and the timings of each trigger belonging
        #to the Acoustic Run Number
        for file in allfiles:
            #print file[len(Path)+32:len(Path)+35]
            if file[len(Path)+32:len(Path)+35]==RunNumberAcoustic:
                self.ThisRunTriggers.append([file, datetime.strptime(file[len(Path)+8:len(Path)+27], '%Y.%m.%d_%H.%M.%S')])
        #Sort the list of triggers by datetime
        self.ThisRunTriggers.sort(key = lambda r: r[1])
        
        #Start the Time cut here
        
        prevtrig_time = self.ThisRunTriggers[0][1]
        #For each trigger, check if the time difference crosses the threshold.
        #If not, KEEP first one, DISCARD rest.
        for triggers in self.ThisRunTriggers[1:]:
            if triggers[1]>=prevtrig_time+self.meanTimeBetweenTriggers:
                ValidTriggers.append(triggers)
            prevtrig_time = triggers[1]
        
        #Return the time filtered triggers
        return ValidTriggers
        
        
    
    #This is the pressure veto cut for acoustic events from the geyser
    def MatchEvent_PressurePiezo(self, Path, RunNumberAcoustic, RunNumberPressure):
        '''
        Pressure Veto cut
        In: Event list based on pressure spike and acoustic data
        Out: Coincidences between the two
        '''
        #Get the acoustic event list
        ValidTriggers = self.MakeAcousticEventList(Path, RunNumberAcoustic)
        
        #get the event list by pressure
        PVeto = PressureVeto.PressureVeto(RunNumberPressure)
        PressureBubbles = PVeto.findBubbleTimings()

        #print PressureBubbles
        #Assign space for the filtered data
        CleanData = []
        #For each bubble in the pressure veto, search for a maching bubble in the acoustic
        #signals, by time. If a match is found, store it in this list
        for Bubble in PressureBubbles:
            Timing = Bubble[1]
            #search
            x = [Event for Event in ValidTriggers if Event[1]-timedelta(seconds=2)<=Timing<=Event[1]+timedelta(seconds=2)]
            #if something is found....
            if not len(x)==0:
                x[0].append(Bubble[0])
                x[0].append(Bubble[2])
                CleanData.append(x[0])
            #clear memory
            x = []
        #return the vetoed events
        return CleanData
        
