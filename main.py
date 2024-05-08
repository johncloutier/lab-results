'''
Created on Apr 24, 2024

@author: John Cloutier
'''

from xml.dom import minidom
from xml.etree.ElementTree import ElementTree as et
import medical.results as res
import plot.plot as plot

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

def getComponent(component):
    '''
    Look for tests that are inclosed in a "component" tag
    '''
    
    # Get lab result name
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
    
    # Search various locations for lab result values
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
    
    # Get the lab result timestamp
    time = component.find("./{*}observation/{*}effectiveTime")
    if time is not None:
        time = time.get("value")
        if time is None:
            return
    else:
        return 
    
    # Get the lab result units
    unit = component.find("./{*}observation/{*}code/{*}value")
    if unit is not None:
        unit = unit.get("unit")
        if unit not in value:
            value = value + " " + unit
    else:
        unit = ""
    
    # Get lab result reference range
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
    
    # Set properties and add lab result to Results
    lab = res.Lab()
    lab.name = name
    lab.value = value
    lab.time = time
    lab.ref = ref
    global results
    results.addRecord(lab)
    
    global records
    records += 1

def getComponents(root):
    '''
    Sift through document to find all "component" tags that follow a "section" 
    with "Results" in its name
    '''
    components = root.findall(".//{*}component")
    title = ""
    for component in components:
        # Check if we're in the lab section
        this_title = component.find("./{*}section/{*}title")
        if this_title is not None:
            title = this_title.text
            
        if "Results" not in title:
            continue
        
        # Some results have a whole "component" node others are jammed into
        # HTML tables within component nodes
        getComponent(component) 
        getGenTables(component)
        getTOLTables(component)

def getTOLTable(table):
    '''
    Extract results from HTML tables within the XML; TOL flavor
    '''
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

    # Set properties and add lab result to Results
    lab = res.Lab()
    lab.name = name
    lab.value = value + (unit if unit else "")
    lab.time = time
    lab.ref = ref
    global results
    results.addRecord(lab)
    
    global records
    records += 1

# Find all HTML tables; TOL flavor
def getTOLTables(root):
    tables = root.findall(".//{*}table")
    for table in tables:
        getTOLTable(table) 

def getGenTable(table):
    '''
    Extract results from HTML table within the XML; Genesis flavor
    '''
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
                    # Set properties and add lab result to Results
                    lab = res.Lab()
                    lab.name = name
                    lab.value = value
                    lab.time = time.replace('(','').replace(')', '')
                    lab.ref = ref
                    global results
                    results.addRecord(lab)
                    
                    global records
                    records += 1

# Find all HTML tables; Genesis flavor
def getGenTables(root):
    tables = root.findall(".//{*}tbody")
    for table in tables:
        getGenTable(table) 

# Print results from Result structure
def printResults(results):
    uniquerecords = 0
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
            uniquerecords += 1
        print(numvalues)
        print(values)
        print(times)
        
    print("number of unique records: " + str(uniquerecords)) 
        
# Main
results = res.Results()
records = 0

# Print TOL Records
#printCategories('TOL_records.xml')
root = et(file='tol_records.xml').getroot()
getComponents(root)


# Print Genesis Records
#printCategories('genesis_records.xml')
root = et(file='genesis_records.xml').getroot()
getComponents(root)

res.Results.scrubOutliers(res, results)
#res.Results.printDataFrame(res, results)
#printResults(results)
#plot.plotLabSet(results.data[0])
plot.plotResults(results)

print("number of records: " + str(records))
print('done.')