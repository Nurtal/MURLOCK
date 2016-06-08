"""
This file contains process
for the database organisation
"""

import database
import trashlib


"""
Create database for one langage (to start)
"""

print "/-----------------------------\\"
print "|     DATABASE CREATION       |"
print "\\-----------------------------/"
database.createDatabase("DATA/database/test.db")
print "/-----------------------------\\"
print "|     DATABASE INSERTION      |"
print "\\-----------------------------/"
dataFile = open("DATA/testUrl.data", "r")
for line in dataFile:
	url = line.replace("\n", "")
	code = trashlib.collectCodeFromSOF(url)
	header = trashlib.collectTitleFromSOF(url)
	titleInArray = header[0].split("-")
	title = titleInArray[0]
	subtitle = ""
	if len(titleInArray) > 1:
		subtitle = titleInArray[1]

	codeToInsert = ""
	for bloc in code:
		codeToInsert = codeToInsert + "<Grmbmbl>" + str(bloc) + "</Grmbmbl>"
		

	print "[INSERTION] " +str(url)

	database.insertInto("DATA/database/test.db", title, subtitle, codeToInsert, url)



"""          VALIDATION
print "/-----------------------------\\"
print "|       DATABASE TEST         |"
print "\\-----------------------------/"
result = database.getDatafromDatabase("DATA/database/test.db")
print result
"""















