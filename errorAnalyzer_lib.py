"""
function for
Error analysis

"""

import subprocess
from shutil import copyfile


def identifyLangage(script):
	"""
	determine langage used base
	on the extension
	"""
	langage = "undefined"
	scriptNameInArray = script.split(".")
	extension = scriptNameInArray[-1]
	
	if(extension == "pl"):
		langage = "perl"
	elif(extension == "py"):
		langage = "python"
	elif(extension == "sh"):
		langage = "bash"
	else:
		langage == "not recognised"

	return langage



def getErrors(script):
	"""
	Get the stderr of script
	"""
	p = subprocess.Popen(['./'+script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	return err



def getFirstNonEmptyCharInArray(array):
	firstNonEmptyCharacter = ""
	for charac in array:
		if(charac != " " and charac != "\t"):
			firstNonEmptyCharacter = charac
			break
	return firstNonEmptyCharacter



def scanForSimpleError(script):
	"""
	scan script for simple
	errors
	"""
	langage = identifyLangage(script)
	line_number = 0
	logFile_name = "scan.log"

	# Scanning File
	logFile = open(logFile_name, 'w')
	scriptFile = open(script, 'r')
	for line in scriptFile:
		line_number +=1
		lineWithoutBackN = line.replace("\n", "")
		lineInArray = lineWithoutBackN.split(" ")
		lastWord = lineInArray[-1]
		lastWordInArray = list(lastWord)
		lineInCharacterArray = list(lineWithoutBackN)

		#########################
		# looking for a shebang #
		# => for perl		#
		# => for bash		#
		#########################
		if(langage == "perl" and line_number == 1 and lineInArray[0] != "#!/usr/bin/perl"):
			logFile.write("[WARNING]: SET line "+str(line_number)+" TO #!/usr/bin/perl\n")
		if(langage == "bash" and line_number == 1 and line != "#!/bin/bash"):
			logFile.write("[WARNING]: SET line "+str(line_number)+" TO #!/bin/bash\n")

		#########################
		# Check for semi-column	#
		# => for perl		#
		#########################
		if(len(lastWordInArray) > 0):
			if(langage == "perl" and line_number != 1 and lastWordInArray[-1] != ";"):
				if(lastWordInArray != "}"):
					firstNonEmptyCharacter = getFirstNonEmptyCharInArray(lineInCharacterArray)
					if(firstNonEmptyCharacter != "#"):
						logFile.write("[ERROR]: ADD \";\" to line "+str(line_number)+"\n")

		#################################
		# Check variable declaration	#
		# => for perl			#
		#################################
		if(getFirstNonEmptyCharInArray(lineInCharacterArray) != "#" ):
			word_number = 0
			for word in lineInArray:
				if(word == "my"):
					variable = lineInArray[word_number+1]
					variableInArray = list(variable)
					if(variableInArray[0] != "$" and variableInArray[0] != "@"):
						if "list" in variable:
							logFile.write("[ERROR]: ADD \"@\" to "+variable+", line "+str(line_number)+"\n")
						else:
							logFile.write("[ERROR]: ADD \"$\" to "+variable+", line "+str(line_number)+"\n")
				

			
					

	scriptFile.close()
	logFile.close()




def fixSimpleError(scan_log, script):
	"""
	fixe script using log of the
	scan function

	Is working but need several pass
	for multiple errors on same line

	TODO:
	=> Implement log file (list of performed corrections)
	"""

	# save original script
	# create model file
	scriptInArray = script.split(".")
	dst = scriptInArray[0]+"_save."+scriptInArray[1]
	model = scriptInArray[0]+"_model."+scriptInArray[1]
	copyfile(script, dst)
	copyfile(script, model)


	# open log file
	fileLog = open(scan_log, "r")
	for line in fileLog:
		if "[ERROR]:" in line:
			
			lineWithoutBackN = line.replace("\n", "")
			lineInArray = lineWithoutBackN.split(" ")
			
			lineToChange = int(lineInArray[-1])
			
			fileModel = open(model, "r")
			fileToWrite = open(script, "w")			

			line_number = 1
			for lineModel in fileModel:
				if(line_number != lineToChange):
					fileToWrite.write(lineModel)
				else:
					if(lineInArray[2] == "\";\""):
						lineModelWithoutBackN = lineModel.replace("\n", "")	
						fileToWrite.write(lineModelWithoutBackN+";\n")
					elif(lineInArray[2] == "\"$\""):
						correctedWord = "$"+lineInArray[4]
						correctedWord = correctedWord.replace(",", "")
					
						lineModelInArray = lineModel.split(" ")
						wordToChange = lineInArray[4].replace(",", "")	

						word_number = 0
						correctedLine = ""

					
						for word in lineModelInArray:
							if(wordToChange not in word):
								correctedLine = correctedLine + " " + word
							else:
								correctedLine = correctedLine + " " +correctedWord

						if(correctedLine[0] == " "):
							correctedLine = correctedLine[1:]
							
						fileToWrite.write(correctedLine+"\n")

				line_number += 1
			

			fileToWrite.close()
			fileModel.close()
			copyfile(script, model)
	
	fileLog.close()
	
	






def IdentifySimpleError(langage, errorLog):
	"""
	Identify
	simple errors

	[UNFINISHED]
	"""
	
	if(langage == "perl"):
		errorLogInArray = errorLog.split(" ")
		if(errorLogInArray[0] == "syntax" and errorLogInArray[1] == "error"):
			if (errorLogInArray[4] == "line"):
				errorLineInArray = errorLogInArray[5].split(",")
				errorLine = int(errorLineInArray[0])-1
				print "ADD \";\" at the end of line "+str(errorLine)+" IF \";\" is missing\n"
			




"""
TEST SPACE
"""
scanForSimpleError("test.pl")
fixSimpleError("scan.log", "test.pl")
