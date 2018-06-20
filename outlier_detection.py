

##
## part of AutoComp
## play with MFI
##



def create_outlier_detection_training_datafile(data_folder):
	"""
	IN PROGRESS
	"""


	## importation
	import glob

	## initialise training data file
	training_data = open("MFI_training_data.csv", "w")

	
	


	## loop over the files in the data_folder
	cmpt = 0
	for mfi_file in glob.glob(data_folder+"/*.txt"):

		mfi_file_name = mfi_file.split("/")
		mfi_file_name = mfi_file_name[-1].split("_")
		mfi_data = open(mfi_file, "r")

		mfi_cmpt = 0
		for line in mfi_data:

			## Write header
			if(cmpt == 0 and mfi_cmpt == 0):
				header = "analysable,compensated,"
				line = line.rstrip()
				line = line.replace("\"", "")
				line_in_array = line.split(",")
				line_in_array = line_in_array[1:]
				for elt in line_in_array:
					header += str(elt)+","
				header = header[:-1]

				training_data.write(header+"\n")
			else:

				## TODO
				## determine if the file is an outlier
				analysable = 1

				## determine if the file is compensated
				compensated = "NA"
				if("compensated.txt" == mfi_file_name[-1]):
					compensated = 1
				else:
					compensated = 0

				line_to_write = str(analysable)+","+str(compensated)+","

				line = line.rstrip()
				line_in_array = line.split(",")
				line_in_array = line_in_array[1:]
				for elt in line_in_array:
					line_to_write += str(elt)+","
				line_to_write = line_to_write[:-1]
				training_data.write(line_to_write+"\n")
			mfi_cmpt+= 1

		mfi_data.close()


		cmpt += 1


	## close training data file
	training_data.close()




create_outlier_detection_training_datafile("trash/MFI_test")