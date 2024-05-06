'''
Created on Apr 24, 2024

@author: John Cloutier
'''

from xml.dom import minidom
from xml.etree.ElementTree import ElementTree as et
import medical.Results as Results
import medical.Results as Lab

if __name__ == '__main__':
    pass


# Print high level sections
def printCategories(filename):
    dom = minidom.parse(filename)
    body = dom.getElementsByTagName("structuredBody")[0]

    for component in body.getElementsByTagName("component"):
        title = component.getElementsByTagName("title")
        for t in title:
            print("section:",t.firstChild.nodeValue)

def printComponent(component):
    
    # Get relevant fields
    name = ""
    origname = component.find("./{*}observation/{*}code/{*}originalText")
    textname = component.find("./{*}observation/{*}text")  
    if origname is not None:
        name = origname.text
    else:
        if textname is not None:
            name = textname.text
    if name == "":
        return
    
    obsvalue = component.find("./{*}observation/{*}value")
    codevalue = component.find("./{*}observation/{*}code/{*}value")
    interpvalue = component.find("./{*}observation/{*}interpretationCode/{*}originalText")
    if obsvalue is not None and obsvalue.text is not None and not obsvalue.text.isspace():
        value = obsvalue.text
    else:
        if obsvalue is not None and obsvalue.get("value") is not None:
            value = obsvalue.get("value")
        else:
            if codevalue is not None and not codevalue.get("value").isspace():
                value = codevalue.get("value")
            else:
                if interpvalue is not None and not interpvalue.text.isspace():
                    value = interpvalue.text
                else:
                    return
    
    time = component.find("./{*}observation/{*}effectiveTime")
    if time is not None:
        time = time.get("value")
        if time is None:
            return
    else:
        return 
    
    unit = component.find("./{*}observation/{*}code/{*}value")
    if unit is not None:
        unit = unit.get("unit")
        if unit not in value:
            value = value + " " + unit
    else:
        unit = ""
    
    
    ref = ""
    low = component.find("./{*}observation/{*}referenceRange/{*}observationRange/{*}value/{*}low")
    high = component.find("./{*}observation/{*}referenceRange/{*}observationRange/{*}value/{*}high")
    if low is not None and high is not None:
        low = low.get("value")
        high = high.get("value")
        ref = "(" + low + "-" + high +")"
    else:
        ref = component.find("./{*}observation/{*}referenceRange/{*}observationRange/{*}text")
        if ref is not None:
            ref = ref.text
    
    #print("-----Record:-----")
    #print("name:",name)
    #print("value:",value)
    #print("timestamp:",time)
    #print("ref range:",ref) 
    
    lab = Lab.Lab()
    lab.name = name
    lab.value = value
    lab.time = time
    lab.ref = ref
    global results
    results.addRecord(lab)
    
    global records
    records += 1

def printComponents(root):
    components = root.findall(".//{*}component")
    title = ""
    for component in components:
        # Check if we're in the lab section
        this_title = component.find("./{*}section/{*}title")
        if this_title is not None:
            title = this_title.text
            
        if "Results" not in title:
            continue
        
        printComponent(component) 
        printGenTables(component)
        printTOLTables(component)

def printTOLTable(table):
    
    # Get relevant fields
    lines = table.findall(".//{*}td")
    name = value = unit = time = ref = ""
    
    for line in lines:
        if line.get("ID") is not None:
            if "chemtestname" in line.get("ID"):
                name = line.text

            if "chemvalue" in line.get("ID"):
                value = line.text
            
            if "chemunits" in line.get("ID"):
                unit = line.text

            if "chemcertifieddatetime" in line.get("ID"):
                time = line.text
                
            if "chemreferencerange" in line.get("ID"):
                ref = line.text               

                
    # Check for valid component record
    if name == "" or value == "" or time == "":
        return
    
    #print("-----TOL Table Record:-----")
    #print("name:",name)
    #print("value:",value + (unit if unit else ""))
    #print("timestamp:",time)
    #print("ref range:",ref)
    
    lab = Lab.Lab()
    lab.name = name
    lab.value = value + (unit if unit else "")
    lab.time = time
    lab.ref = ref
    global results
    results.addRecord(lab)
    
    global records
    records += 1

def printTOLTables(root):
    tables = root.findall(".//{*}table")
    for table in tables:
        printTOLTable(table) 

def printGenTable(table):
    
    # Get relevant fields
    rows = table.findall("./{*}tr")
    for row in rows:
        name = value = time = ref = ""
        divs = row.findall("./{*}td")
        for div in divs:
            if div is not None and div.text is not None and not div.text.isspace():
                if '[' in div.text and ']' in div.text:
                    name = div.text[:div.text.find(' [')]
                    ref = div.text[div.text.find(' [')+1:]
                else:   
                    name = div.text
            else:
                content = div.find("./{*}content")
                if content is not None:
                    value = content.text
                    time = content.findall("*")[len(content) - 1].tail
        
                # Check for valid component record
                if name == "" or value == "" or time == "":
                    return
                else:
                    #print("-----Gen Table Record:-----")
                    #print("name:",name)
                    #print("value:",value)
                    #print("timestamp:",time.replace('(','').replace(')', ''))
                    #print("ref range:",ref)

                    
                    lab = Lab.Lab()
                    lab.name = name
                    lab.value = value
                    lab.time = time.replace('(','').replace(')', '')
                    lab.ref = ref
                    global results
                    results.addRecord(lab)
                    
                    global records
                    records += 1


def printGenTables(root):
    tables = root.findall(".//{*}tbody")
    for table in tables:
        printGenTable(table) 

def printResults(results):
    for result in results.data:
        print("======= ResultSet ======")
        print(result.name)
        numvalues = ""
        values = ""
        times = ""
        for lab in result.results:
            numvalues = numvalues + ("," if numvalues else "") + lab.numvalue
            values = values + ("," if values else "") + lab.value
            times = times + ("," if times else "") + lab.time
        print(numvalues)
        print(values)
        print(times)
        
# Main
results = Results.Results()
records = 0

# Print TOL Records
#printCategories('TOL_records.xml')
root = et(file='tol_records.xml').getroot()
printComponents(root)


# Print Genesis Records
#printCategories('genesis_records.xml')
root = et(file='genesis_records.xml').getroot()
printComponents(root)

printResults(results)

print("number of records: " + str(records))
print('done.')