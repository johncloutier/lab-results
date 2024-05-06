'''
Created on May 1, 2024

@author: jmhz
'''


import dateutil.parser as parser
import re

class Results(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.data = []
        
    def cleanDateTime(self, lab):
        date = parser.parse(lab.time)
        lab.time = date.strftime("%m/%d/%Y")
    
    def setNumericalValue(self, lab):
        #fudge de minimis values
        if "<" in lab.value:
            lab.numvalue = 0
        
        #calc percentage
        if "%" in lab.value:
            percent = re.sub('[^0-9.]','', lab.value)
            lab.numvalue = str(float(percent) / 100)
        
        #scrub units
        lab.numvalue = re.sub('[^0-9.x()]','', lab.value)
        
        #convert sci notation
        split = re.split("x10\((\d+)\)", lab.numvalue)
        if  len(split) == 3:
            lab.numvalue = str(float(split[0]) * 10 ** float(split[1]))
        
        
        
    def addRecord(self, lab):
        Results.cleanDateTime(self, lab)
        Results.setNumericalValue(self, lab)
        newrecord = True
        
        for ls in self.data:
            if ls.name == lab.name:
                for existinglab in ls.results:
                    if existinglab.time == lab.time and existinglab.value == lab.value:
                        return #Duplicate result
                ls.results.append(lab)
                newrecord = False
        if newrecord:
            ls = LabSet()
            ls.name = lab.name
            ls.results.append(lab)
            self.data.append(ls)



class LabSet(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.name = ""
        self.results = []
        
class Lab(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.name = ""
        self.value = ""
        self.numvalue = ""
        self.time = ""
        self.ref = ""