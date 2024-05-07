'''
Created on May 1, 2024

@author: John Cloutier
'''


import dateutil.parser as parser
import re
from decimal import Decimal

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
        or "not" in lab.value.lower() or "tnp" in lab.value.lower() :
            lab.numvalue = "-1"
            return
        
        # Look for positive results
        if "pos" in lab.value.lower() or "present" in lab.value.lower() \
        or "normal" in lab.value.lower() or "adequate" in lab.value.lower():
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
        
        # Calc percentage
        if "%" in lab.value:
            percent = re.sub('[^0-9.]','', lab.value)
            lab.numvalue = str(round(float(percent) / 100, 8))
            return
        if "/100" in lab.value:
            percent = re.sub('(\\s+)?/100(.+)?','', lab.value)
            lab.numvalue = str(round(float(percent) / 100, 8))
            return 
        
        # Convert sci notation
        split = re.split("[A-Za-z\\s]+?x10\\((\\d+)\\)", lab.value)
        if  len(split) == 3:
            lab.numvalue = str(round(float(split[0]) * 10 ** float(split[1]), 8))
            return
        split = re.split("x10\\((\\d+)\\)", lab.value)
        if  len(split) == 3:
            lab.numvalue = str(round(float(split[0]) * 10 ** float(split[1]), 8))
            return
        
        # Scrub units
        lab.numvalue = re.sub('[^0-9.]','', lab.value)
        
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



class LabSet(object):
    '''
    Object to hold a particular lab and a collection of values
    '''
    def __init__(self):
        self.name = ""
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