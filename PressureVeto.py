#!/usr/bin/env python

#This file will calculate the pressure rise from pressure data
#and the time of the rise. IT can then give an accurate estimation of
#when to look for the data

#Datetime and timedelta are needed for time calculations
from datetime import datetime, timedelta
#Import PyDbLite for python database implementation
from PyDbLite import Base
#itertools is for efficient iterators
import itertools

class PressureVeto:
    
    #We need the run number for init. We will use PyDBLite
    #so we need to gen the db first. There will be another
    #function for that. The reason we use this is because
    #of native python compatibility
    
    def __init__(self, RunNumber):
        #property self.RunNumber assigned.
        #This is typecasted to string for manipulation
        self.RunNumber = str(RunNumber)
        #property self.PyDB -> Database for pressures
        self.PyDB = Base('pressures/'+self.RunNumber+'.dbl')
        #check if the DB exists. If Yes, open, if not
        #create it:
        if not self.PyDB.exists():
            self.genPDL()
        else:
            self.PyDB.open()
            
        #Define the time iteration between bubbles minimum threshold
        #Remember, each iteration is 1/10th second!
        #Iter must be integer!
        minSecondsBetweenBubbles = 4
        self.minIterBetweenBubbles = int(minSecondsBetweenBubbles*10)
        
        
        
    #Funtion to generate PyDBLite database
    #I will deliberately not give this MySQL abilities
    #since I dont want my data wiped out by "mistake"
    #The human veto has to be in here somewhere.
    def genPDL(self):
    
        #Create the PDL file for database
        self.PyDB.create('id','temp','pressure','time', mode = "override")
        
        #import CSV for CSV file ops. Import ONLY if needed, so its here.
        import csv
        #filename in CSV file. Assumption -> RunID.csv
        fname_csv = self.RunNumber+".csv"
        PTcsv = csv.reader(open(fname_csv))
        
        #convert CSV to PyDB line by line
        for line in PTcsv:
            self.PyDB.insert(id = int(line[0]),temp=float(line[1]), pressure=float(line[2]), time=datetime.strptime(line[3], "%Y-%m-%d %H:%M:%S"))
        #Commit the database
        self.PyDB.commit()
        #Print a confirmation
        print "Creating PyDB complete."
    
    #this function finds the "peaks" in the pressures.
    #Criterion: Peaks are above 30 PSI
    
    def findBubbleTimings(self):
        '''Finds the bubble timings
        In -> Pressure data
        Out -> Timings (datetime.datetime)
        Assumptions -> Bubble PSI > 30 PSI
        '''
        
        #Select records with pressure > 30.0 PSI
        recs = [r for r in self.PyDB]
        #Make an iterator of this list
        RecIter = itertools.islice(recs, None)
        
        #Declare memory space for:
        #Valid Bubbles
        #Temporary Storage
        #Last Record's ID (to stop Iterator)
        ValidBubbles = []
        _VBubbleAmpTemporaryStorage = []
        RecLastID = recs[-1:][0]['__id__']
        
        #Go record by record:
        for record in RecIter:
            #If pressure > 30:
            if record['pressure'] >= 30.0:
                #Assign the temporary memory with present pressure, time
                _VBubbleAmpTemporaryStorage = [record['pressure'], record['time'], record['temp']]
                #Number of steps to iter so we dont go beyond the last rec
                stepsTillLastRec = RecLastID - record['__id__']
                stepsIter = self.minIterBetweenBubbles if ( stepsTillLastRec > self.minIterBetweenBubbles) else stepsTillLastRec
                #Investigate for next minIterBetweenBubbles for a maxima
                for i in xrange(stepsIter):
                    #Progress iterator by 1
                    record = RecIter.next()
                    #is present iteration > memory stored variable? Yes: Store it, No: Continue
                    _VBubbleAmpTemporaryStorage = [record['pressure'], record['time'], record['temp']] if record['pressure']>=_VBubbleAmpTemporaryStorage else _VBubbleAmpTemporaryStorage
                #The local maxima is found, store it as good data, continue searching
                ValidBubbles.append(_VBubbleAmpTemporaryStorage)
                #clear the temporary space
                _VBubbleAmpTemporaryStorage = []
        
        #Return the time cut!
        return ValidBubbles
    
