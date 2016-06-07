


'''
A few code lines
for the Murlock Project
'''
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import requests
from lxml import html

import random
import os.path

def sendMailWrapper(fromaddr, toaddr, subject, content, passwd): 
 
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subject
 
	msg.attach(MIMEText(content, 'plain'))
 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, passwd)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	
	return




def collectCodeFromSOF(url):
	"""
	=> Scan a web page looking for html code
	balise.
	=> Return Balise content in a string array
	
	----------------
	Optimize for StackOverFlow (SOF) : IN PROGRESS

	"""

	page = requests.get(url)
	tree = html.fromstring(page.content)
	code = tree.xpath('//code/text()')

	return code


def collectTitleFromSOF(url):
	"""
	Return web page title
	"""

	page = requests.get(url)
	tree = html.fromstring(page.content)
	title = tree.xpath('//title/text()')

	return title



def scanStackOverFlow(userQuery):

	"""
	This function generate random url,
	scan the page subject and compare it to
	the input keywords

	Input should be a string
	Return the url of selected pages

	[TODO]
	=> Use alternative comparison score
	=> work on return value
	"""

	# Search parameters
	keywords = userQuery.split(" ")
	precisionScoreTreshold = 2
	

	# Url Generation
	prefix = "http://stackoverflow.com/questions/"
	for number in range(1, 99999):
		generatedUrl = prefix + str(number) + "/"

		# Get title of the page
		page = requests.get(generatedUrl)
		tree = html.fromstring(page.content)
		title = tree.xpath('//title/text()')
		titleInArray = title[0].split('-')

		# Scan Subject
		if titleInArray[0] != "Page Not Found ":
			mainSubject = titleInArray[0]
			precision = titleInArray[1]
	
			passFirstCollection = 0
			firstSelectionScore = 0
			firstSelectionCount = 0
			mainSubjectSize = 0
			print title[0]
			for mesh in mainSubject.split(" "):
				mainSubjectSize = mainSubjectSize + 1
				for query in keywords:
					if mesh == query:
						firstSelectionCount = firstSelectionCount + 1	
						passFirstCollection = 1
	
			firstSelectionScore = (float(firstSelectionCount) / float(len(keywords)))*float(100)
			#print firstSelectionScore

			if passFirstCollection == 1:
				precisionSize = 0
				precisionScore = 0
				precisionCount = 0	
				for subMesh in precision.split(" "):
					precisionSize = precisionSize + 1
					for query in keywords:
						if subMesh == query:
							precisionCount = precisionCount + 1
							
				precisionScore = (float(precisionCount) / float(len(keywords))) * float(100)
				print "=> Match <="
				print precisionScore				


	return 0





def customScanStackOverFlow():

	"""
	This function generate random url,
	scan the page subject and count the 
	occurence of a few langages

	write results in a file
	"""

	# data
	perl_count = 0
	c_count = 0
	csharp_count = 0
	cplus_count = 0
	java_count = 0
	bash_count = 0
	python_count = 0
	ruby_count = 0
	html_count = 0
	php_count = 0
	sql_count = 0
	javascript_count = 0

	# dataFile
	perlUrl_file = "DATA/perlUrl.data"
	cUrl_file = "DATA/cUrl.data"
	csharpUrl_file = "DATA/csharpUrl.data"
	cplusUrl_file = "DATA/cplusUrl.data"
	javaUrl_file = "DATA/javaUrl.data"
	bashUrl_file = "DATA/bashUrl.data"
	pythonUrl_file = "DATA/pythonUrl.data"
	rubyUrl_file = "DATA/rubyUrl.data"
	htmlUrl_file = "DATA/htmlUrl.data"
	phpUrl_file = "DATA/phpUrl.data"
	sqlUrl_file = "DATA/sqlUrl.data"
	javascriptUrl_file = "DATA/javascriptUrl.data"
	

	# look for existing log file
	startNumber = 1
	if os.path.isfile("DATA/log/customScan.log"):
		logFile = open("DATA/log/customScan.log", "r")
		for line in logFile:
			lineWithoutBackN = line.replace("\n", "")
			lineInArray = lineWithoutBackN.split(",")
			
			if lineInArray[0] == "Current topic":
				startNumber = int(lineInArray[1])
			elif lineInArray[0] == "perl":
				perl_count = int(lineInArray[1])
			elif lineInArray[0] == "c":
				c_count = int(lineInArray[1])
			elif lineInArray[0] == "c++":
				cplus_count = int(lineInArray[1])
			elif lineInArray[0] == "c#":
				csharp_count = int(lineInArray[1])
			elif lineInArray[0] == "Java":
				java_count = int(lineInArray[1])
			elif lineInArray[0] == "Bash":
				bash_count = int(lineInArray[1])
			elif lineInArray[0] == "Python":
				python_count = int(lineInArray[1])
			elif lineInArray[0] == "Ruby":
				ruby_count = int(lineInArray[1])
			elif lineInArray[0] == "Html":
				html_count = int(lineInArray[1])
			elif lineInArray[0] == "Php":
				php_count = int(lineInArray[1])
			elif lineInArray[0] == "SQL":
				sql_count = int(lineInArray[1])
			elif lineInArray[0] == "JavaScript":
				javascript_count = int(lineInArray[1])
				
		logFile.close()
			

	# Look for existing data file
	if not os.path.isfile(perlUrl_file):
		fileToInit = open(perlUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(cUrl_file):
		fileToInit = open(cUrl_file, "w")    
		fileToInit.close()
	if not os.path.isfile(cplusUrl_file):
		fileToInit = open(cplusUrl_file, "w")    
		fileToInit.close()
	if not os.path.isfile(csharpUrl_file):
		fileToInit = open(csharpUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(javaUrl_file):
		fileToInit = open(javaUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(bashUrl_file):
		fileToInit = open(bashUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(pythonUrl_file):
		fileToInit = open(pythonUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(rubyUrl_file):
		fileToInit = open(rubyUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(htmlUrl_file):
		fileToInit = open(htmlUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(phpUrl_file):
		fileToInit = open(phpUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(sqlUrl_file):
		fileToInit = open(sqlUrl_file, "w")
		fileToInit.close()
	if not os.path.isfile(javascriptUrl_file):
		fileToInit = open(javascriptUrl_file, "w")
		fileToInit.close()	

	# Url Generation
	prefix = "http://stackoverflow.com/questions/"
	for number in range(startNumber, 200):
		generatedUrl = prefix + str(number) + "/"
		
		# Get title of the page
		page = requests.get(generatedUrl)
		tree = html.fromstring(page.content)
		title = tree.xpath('//title/text()')
		titleInArray = title[0].split('-')

		# Write data in log file
		logFile = open("DATA/log/customScan.log", "w")
		logFile.write("Current topic,"+str(number)+"\n")
		logFile.write("perl," +str(perl_count) +"\n")
		logFile.write("c," +str(c_count) +"\n")
		logFile.write("c++," +str(cplus_count) +"\n")
		logFile.write("c#," +str(csharp_count) +"\n")
		logFile.write("Java," +str(java_count) +"\n")
		logFile.write("Bash," +str(bash_count) +"\n")
		logFile.write("Python,"+str(python_count) +"\n")
		logFile.write("Ruby,"+str(ruby_count) +"\n")
		logFile.write("Html,"+str(html_count) +"\n")
		logFile.write("Php,"+str(php_count) +"\n")
		logFile.write("SQL,"+str(sql_count) +"\n")
		logFile.write("JavaScript,"+str(javascript_count) +"\n")
		logFile.close()
		
		# Scan Subject
		if titleInArray[0] != "Page Not Found ":
			mainSubject = titleInArray[0]
			precision = titleInArray[1]

			print "["+str(number)+"] "+title[0]

			for mesh in mainSubject.split(" "):
				if mesh.lower() == "perl":
					perl_count = perl_count + 1
					fileToAdd = open(perlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "c":
					c_count = c_count + 1
					fileToAdd = open(cUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "c#":
					csharp_count = csharp_count + 1
					fileToAdd = open(csharpUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "c++":
					cplus_count = cplus_count + 1
					fileToAdd = open(cplusUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "java":
					java_cout = java_count + 1
					fileToAdd = open(javaUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "bash":
					bash_count = bash_count + 1
					fileToAdd = open(bashUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "python":
					python_count = python_count + 1
					fileToAdd = open(pythonUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "ruby":
					ruby_count = ruby_count + 1
					fileToAdd = open(rubyUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "html":
					html_count = html_count + 1
					fileToAdd = open(htmlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "php":
					php_count = php_count + 1
					fileToAdd = open(phpUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "sql":
					sql_count = sql_count + 1
					fileToAdd = open(sqlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "mysql":
					sql_count = sql_count + 1
					fileToAdd = open(sqlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "javascript":
					javascript_count = javascript_count + 1
					fileToAdd = open(javascriptUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
			
			for mesh in precision.split(" "):
				if mesh.lower() == "perl":                      
					perl_count = perl_count + 1
					fileToAdd = open(perlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "c":                                                       
					c_count = c_count + 1
					fileToAdd = open(cUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "c#":
					csharp_count = csharp_count + 1     
					fileToAdd = open(csharpUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()            
				elif mesh.lower() == "c++":
					cplus_count = cplus_count + 1
					fileToAdd = open(cplusUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "java":            
					java_cout = java_count + 1
					fileToAdd = open(javaUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "bash":            
					bash_count = bash_count + 1
					fileToAdd = open(bashUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "python":
					python_count = python_count + 1
					fileToAdd = open(pythonUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "ruby":
					ruby_count = ruby_count + 1
					fileToAdd = open(rubyUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "html":
					html_count = html_count + 1
					fileToAdd = open(htmlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "php":
					php_count = php_count + 1
					fileToAdd = open(phpUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "sql":
					sql_count = sql_count + 1
					fileToAdd = open(sqlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "mysql":
					sql_count = sql_count + 1
					fileToAdd = open(sqlUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()
				elif mesh.lower() == "javascript":
					javascript_count = javascript_count + 1
					fileToAdd = open(javascriptUrl_file, "a")
					fileToAdd.write(generatedUrl+"\n")
					fileToAdd.close()


	print "perl: " +str(perl_count) +"\n"
	print "c: " +str(c_count) +"\n"
	print "c++: " +str(cplus_count) +"\n"
	print "c#: " +str(csharp_count) +"\n"
	print "Java: " +str(java_count) +"\n"
	print "Bash: " +str(bash_count) +"\n"	
	print "Python: "+str(python_count) +"\n"
	print "Ruby: "+str(ruby_count) +"\n"
	print "Html: "+str(html_count) +"\n"
	print "Php: "+str(php_count) +"\n"
	print "SQL: "+str(sql_count) +"\n"
	print "JavaScript: "+str(javascript_count) +"\n"


	fileLog = open("DATA/CustomScan.csv", "w")
	fileLog.write("perl," +str(perl_count) +"\n")
	fileLog.write("c," +str(c_count) +"\n")
	fileLog.write("c++," +str(cplus_count) +"\n")
	fileLog.write("c#," +str(csharp_count) +"\n")
	fileLog.write("Java," +str(java_count) +"\n")
	fileLog.write("Bash," +str(bash_count) +"\n")
	fileLog.write("Python,"+str(python_count) +"\n")
	fileLog.write("Ruby,"+str(ruby_count) +"\n")
	fileLog.write("Html,"+str(html_count) +"\n")
	fileLog.write("Php,"+str(php_count) +"\n")
	fileLog.write("SQL,"+str(sql_count) +"\n")
	fileLog.write("JavaScript,"+str(javascript_count) +"\n")
	fileLog.close()


	return 0



def retrieveUrlfromStackOverFlowfor(query):
	"""
	Write all url of pages
	conatining query in a file
	"""


	fileLog = open("DATA/selectedUrl.log", "w")

	# Url Generation
	prefix = "http://stackoverflow.com/questions/"
	for number in range(1, 200):
		generatedUrl = prefix + str(number) + "/"

		# Get title of the page
		page = requests.get(generatedUrl)
		tree = html.fromstring(page.content)
		title = tree.xpath('//title/text()')
		titleInArray = title[0].split('-')

		# Scan Subject
		if titleInArray[0] != "Page Not Found ":
			mainSubject = titleInArray[0]
			precision = titleInArray[1]

			for mesh in mainSubject.split(" "):
				if mesh.lower() == query.lower():
					print generatedUrl
					fileLog.write(generatedUrl+"\n")

			for subMesh in precision.split(" "):
				if subMesh.lower() == query.lower():
					print generatedUrl
					fileLog.write(generatedUrl+"\n")
	
	fileLog.close()

	return 0







"""
Test Space
"""

#query = ("perl")
#scanStackOverFlow(query)
#retrieveUrlfromStackOverFlowfor("c#")
#customScanStackOverFlow()


#stuff = collectCodeFromSOF('http://stackoverflow.com/questions/846257/how-can-i-remove-the-last-seven-characters-of-a-hash-value-in-perl')
#print stuff
"""
# Example
page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
tree = html.fromstring(page.content)
#This will create a list of buyers:
buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
prices = tree.xpath('//span[@class="item-price"]/text()')
#print 'Buyers: ', buyers
#print 'Prices: ', prices
"""


#page = requests.get('http://stackoverflow.com/questions/846257/how-can-i-remove-the-last-seven-characters-of-a-hash-value-in-perl')
#tree = html.fromstring(page.content)
#code = tree.xpath('//code/text()')
#print code;






