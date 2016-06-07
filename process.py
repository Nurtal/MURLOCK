"""
This file contain
a few process for the 
Murlock Project,

currently focus on data aquisition
"""


import trashlib



"""
Get Data from StackOverflow
"""

print "*-----------------------------------*"
print "|      Scanning StackOverFLow       |"
print "*-----------------------------------*"
trashlib.customScanStackOverFlow()


"""          OBSOLETE 

print "*-----------------------------------*"
print "|   Looking for \"best\" Langage    |"
print "*-----------------------------------*"
dataFile = open("DATA/CustomScan.csv", "r")
max_count = 0
langage = ""
for line in dataFile:
	lineWithoutBackN = line.replace("\n", "")
	lineInArray = lineWithoutBackN.split(",")
	
	if int(lineInArray[1]) > max_count:
		max_count = int(lineInArray[1])
		langage = lineInArray[0]
		
dataFile.close()
print "=> " +langage + "["+str(max_count)+"]"
print "*-----------------------------------*"
print "|     Retrieving relevent url       |"
print "*-----------------------------------*"
#trashlib.retrieveUrlfromStackOverFlowfor(langage)
print "*-----------------------------------*"
print "|      Scraping relevent url        |"
print "*-----------------------------------*"
urlFile = open("DATA/selectedUrl.log", "r")
for line in urlFile:
	url = line.replace("\n", "")
	code = trashlib.collectCodeFromSOF(url)
	title = trashlib.collectTitleFromSOF(url)
	print title


urlFile.close()
"""




