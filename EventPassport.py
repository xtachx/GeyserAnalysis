#!/usr/bin/env python

#This class creates a passport for every event we have been able to identify
#the raw data need not be stored in a DB, we can just store enough
#info to reconstruct the raw data


#We are using PyDbLite at the moment I dont know if I should go with
#sqlite3 or MySQL.
from PyDbLite import Base

#datetime and timedelta needed for datetime ops
from datetime import datetime, timedelta

#cleanevents event filtering engine
import CleanEvents

class EventPassportOffice:
    
    #what do we need in init?
    #pressure run ID number
    #acoustic ID number
    #(btw marking those separate is a bad idea on the operators part)
    def __init__(self):
        self.EventPassport = Base('EventPassport/EventPassport.pdl')
        #check if the DB exists. If Yes, open, if not
        #create it:
        if not self.EventPassport.exists():
            self.genPDL()
        else:
            self.EventPassport.open()
        
        self.CleanEvents = CleanEvents.CleanData()
        
        
    
    def genPDL(self):
        #Create the PDL file for database
        self.EventPassport.create('EventID','Temperature','Pressure','Time', 'RunNumber','Path', 'RunType', mode = "open")
        #RunNumber is defined as RunNumberAcoustic
        #Runtype can be neutron or alpha
    
    def genPassport(self, Path, RunNumberAcoustic, RunNumberPressure, RunType_WS):
        FilteredData = self.CleanEvents.MatchEvent_PressurePiezo(Path, str(RunNumberAcoustic), str(RunNumberPressure))
        
        #Get the last EventID
        recs = [ Record['EventID'] for Record in self.EventPassport if Record['RunNumber'] == RunNumberAcoustic]
        if len(recs) == 0:
            EID = str(RunNumberAcoustic)+"0001"
            EID = int(EID)
        else:
            EID = max(recs)+1
        
        #check if we have a duplicate!
        for DataPoint in FilteredData:
            timestamp =  DataPoint[1]
            #Check if we have a dupe/conflict
            x = [Event for Event in self.EventPassport if Event['Time']-timedelta(seconds=2)<=timestamp<=Event['Time']+timedelta(seconds=2)]
            if len(x) == 0:
                self.EventPassport.insert(EventID = EID ,Temperature = DataPoint[3],Pressure = DataPoint[2],Time = DataPoint[1], RunNumber = RunNumberAcoustic, Path = DataPoint[0], RunType = RunType_WS)
                EID += 1
                print("Inserting Entry ...")
            else:
                print "Duplicate entry found at: "+str(DataPoint[1])+" Event ID: "+str(x[0]['EventID'])
        
        self.EventPassport.commit()
        
    def CheckPassport_RunNumber(self, RunNumberQry):
        return self.EventPassport(RunNumber = RunNumberQry)
    def CheckPassport_Temperature(self, HighTemp, LowTemp):
        return self.EventPassport(HighTemp>Temperature>LowTemp)
    def CheckPassport_Time(self, fromTime, toTime):
        recs = [ r for r in self.EventPassport if fromTime < r['Time'] < toTime]
        return recs
    def SizeofPassportDB(self):
        return len(self.EventPassport)
    def CheckPassport_Runtype(self, runtype_WS):
        return self.EventPassport(RunType = runtype_WS)
    def CheckPassport_eventID(self, EventID_WS):
        return self.EventPassport(EventID = EventID_WS)
    def _deleteEvent(self, RecID_WS):
        del self.EventPassport[RecID_WS]
        self.EventPassport.commit()
        


if __name__=='__main__':
    a = EventPassportOffice()
    #a.genPassport('Piezo/triggers.Dec17.alpha/', 204, 204, "Alpha")
    #print a.SizeofPassportDB()
    print len(a.CheckPassport_RunNumber(204))
    #print len(a.CheckPassport_Runtype("Alpha"))
    
    #a._deleteEvent(RecID_WS)
    
    #fromTime = datetime(2012,10,01)
    #toTime = datetime(2012,10,31)
    #OctRuns = a.CheckPassport_Time(fromTime, toTime)
    #for i in OctRuns:
    #    print i['__id__'], i['EventID']
    
    #self.CleanEvents.MatchEvent_PressurePiezo('Piezo/triggers.19Nov/', 190, 190)