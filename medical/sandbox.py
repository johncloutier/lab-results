'''
Created on Apr 28, 2024

@author: John Cloutier
'''

from xml.dom import minidom
from xml.etree.ElementTree import ElementTree as et

if __name__ == '__sandbox__':
    pass


# Get components from file
def getComponents(record_file):
    dom = minidom.parse(record_file)
    body = dom.getElementsByTagName("structuredBody")[0]
    return body.getElementsByTagName("component")

# Print labs the old way
def printLabs(record_file):
    
    for component in getComponents(record_file):
        
        # Check if we're in the lab section
        if component.getElementsByTagName("title").length > 0:
            this_title = component.getElementsByTagName("title")[0].firstChild.nodeValue
            title = this_title
            
        if "Results" not in title:
            continue
        
        names = component.getElementsByTagName("text")
        values = component.getElementsByTagName("value")
        times = component.getElementsByTagName("effectiveTime")
        refs = component.getElementsByTagName("observationRange")
        
        if len(names) > 0 or len(values) > 0:
            print("-----Record:-----")
            for n in names:
                if n.firstChild.nodeValue is not None:
                    print("name:",n.firstChild.nodeValue)
            
            for v in values:
                if len(v.childNodes) != 0:
                    print("values:",v.firstChild.nodeValue)
                    
            for t in times:
                if t.getAttribute("value") is not None:
                    print("timestamp:",t.getAttribute("value"))
                    
            for r in refs:
                if r.firstChild.nodeValue is not None:
                    print("ref range:",r.getElementsByTagName("text")[0].firstChild.nodeValue)  
            
            global records 
            records += 1              

            #value = content.text[:content.text.find(' <')-1]
            #time = content.text[content.text.find('/<(')-1:content.text.find(') <')-1]