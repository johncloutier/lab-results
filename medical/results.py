'''
Created on May 1, 2024

@author: John Cloutier
'''


import dateutil.parser as parser
import re
import pandas as pd
import numpy as np
from scipy import stats

class Results(object):
    '''
    Class with various functions to store and normalize records
    '''
    def __init__(self):
        self.data = []
        
    def cleanDateTime(self, lab):
        date = parser.parse(lab.time)
        lab.time = date.strftime("%m/%d/%Y")
                
    def setNumericalValue(self, lab):
        
        # Look for negative results
        if "neg" in lab.value.lower() or "non" in lab.value.lower() \
        or "not" in lab.value.lower() or "tnp" in lab.value.lower() \
        or "no growth" in lab.value.lower():
            lab.numvalue = "-1"
            return
        
        # Look for positive results
        if "pos" in lab.value.lower() or "present" in lab.value.lower() \
        or "normal" == lab.value.lower() or "adequate" in lab.value.lower()\
        or "critical high" in lab.value.lower():
            lab.numvalue = "1"
            return
        
        # Look for human-readable results
        if "pos" in lab.value.lower():
            lab.numvalue = "1"
            return
        
        # Fudge de minimis values
        if "<" in lab.value  or "na" in lab.value.lower():
            lab.numvalue = "0"
            return
        
        # Scrub percentage
        if "/100" in lab.value:
            lab.numvalue = re.sub('(\\s+)?/100(.+)?','', lab.value)
            return 
        
        # Look for sci notation
        split = re.split("[A-Za-z\\s]*x10\\((\d)\\)", lab.value)
        if  len(split) == 3:
            lab.numvalue = split[0]
            return
        split = re.split("[^0-9.]10\\^(\\d+)", lab.value)
        if  len(split) == 3:
            lab.numvalue = split[0]
            return
        
        # Scrub units
        lab.numvalue = re.sub('[^0-9.]','', lab.value)
    
    def printDataFrame(self, results):    
        records = 0
        for labset in results.data:
            dates = []
            numvalues = []
            values = []
            for lab in labset.results:   
                dates.append(lab.time)
                numvalues.append(lab.numvalue)
                values.append(lab.value)
                records += 1
            df = pd.DataFrame({'Dates': dates, labset.name: numvalues, "origvalues": values})
            df['Dates'] = pd.to_datetime(df['Dates'])
            df = df.sort_values('Dates', ascending=True)
            print(df)
        print("total records in df: " + str(records))    
            
    def scrubOutliers(self, results):
        for labset in results.data:
            numeric = False
            for lab in labset.results:
                if lab.numvalue not in ['-1', '0', '-1']:
                    numeric = True
            
            badlabs = []
            if numeric:
                for lab in labset.results:
                    if lab.numvalue in ['-1', '0', '-1']:
                        badlabs.append(lab)
                for badlab in badlabs:
                    labset.results.remove(badlab)
       
    # Add a particular result to the Results collection
    def addRecord(self, lab):
        #Clean up timestamps and numerical values
        Results.cleanDateTime(self, lab)
        Results.setNumericalValue(self, lab)
        
        # Check for zero value
        if lab.numvalue == "":
            if False:
                print("-----Dropped Record-----")
                print("name: " + lab.name)
                print("numvalue: " + lab.numvalue)
                print("value: " + lab.value)
                print("time: " + lab.time)
            return # useless result
        
        # Check duplicate exists
        newrecord = True
        
        for ls in self.data:
            if ls.name == lab.name:
                for existinglab in ls.results:
                    if existinglab.time == lab.time and existinglab.numvalue == lab.numvalue:
                        return #Duplicate result
                ls.results.append(lab)
                newrecord = False
        if newrecord:
            ls = LabSet()
            ls.name = lab.name
            ls.results.append(lab)
            self.data.append(ls)
            
            if ls.ref == "":
                ls.ref = lab.ref



class LabSet(object):
    '''
    Object to hold a particular lab and a collection of values
    '''
    def __init__(self):
        self.name = ""
        self.ref = ""
        self.results = []
        
class Lab(object):
    '''
    Object to hold one lab result
    '''
    def __init__(self):
        self.name = ""
        self.value = ""
        self.numvalue = ""
        self.time = ""
        self.ref = ""