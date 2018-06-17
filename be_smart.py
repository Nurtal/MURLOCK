##
## Try to find a smart solution to the compensation problem
## by smart i mean "pseudo linear" solution, without invoking
## big monsters like CNN
##




def select_compensation_matrix():
	"""
	Find the good compensation files
	and store them in the data folder,
	by good I mean with an equivalent
	uncompensated file

	Start small
	"""

	## importation
	import glob
	import shutil

	## get files list
	uncompensated_matrix_files = glob.glob("data/matrix/uncompensated/*.txt")
	compensated_matrix_files = glob.glob("/home/elrohir/COMPENSATION/*.txt")

	output_directory = "data/matrix/compensated/"
	found_cmpt = 0

	for compensated_matrix in compensated_matrix_files:

		clear_to_copy = False

		## parse compensated matrix file name
		compensated_matrix_name = compensated_matrix.split("/")
		compensated_matrix_name_in_array = compensated_matrix_name[-1].split("_")
		compensated_matrix_panel = compensated_matrix_name_in_array[1]
		compensated_matrix_center = compensated_matrix_name_in_array[2]
		compensated_matrix_ID = compensated_matrix_name_in_array[3]
		compensated_matrix_ID = compensated_matrix_ID.split(".")
		compensated_matrix_ID = compensated_matrix_ID[0]

		for uncompensated_matrix in uncompensated_matrix_files:

			## parse uncompensated matrix file name
			uncompensated_matrix_name = uncompensated_matrix.split("/")
			uncompensated_matrix_name_in_array = uncompensated_matrix_name[-1].split("_")
			uncompensated_matrix_panel = uncompensated_matrix_name_in_array[1]
			uncompensated_matrix_center = uncompensated_matrix_name_in_array[2]
			uncompensated_matrix_ID = uncompensated_matrix_name_in_array[3]		

			## test the files, get the "goods one"
			if(uncompensated_matrix_center == compensated_matrix_center and uncompensated_matrix_panel == compensated_matrix_panel and uncompensated_matrix_ID == compensated_matrix_ID):
				clear_to_copy = True

		if(clear_to_copy):
			shutil.copy(compensated_matrix, output_directory+str(compensated_matrix_name[-1]))
			found_cmpt += 1

	print "[*] Retrieve "+str((float(found_cmpt)/float(len(uncompensated_matrix_files))*100)) +"%"




def compute_delta_matrix(matrix_1, matrix_2, output_matrix):
	"""
	compute and write a new matrix from matrix 1 and 2
	which is the "delta matrix", represent the variation
	at each position

	write the result in an output file given ny the
	output_matrix parameters

	matrix_1 correspond to the uncompensated matrix
	matrix_2 correspond to the compensated matrix
	"""


	## deal with the uncompensated matrix
	matrix_1_data = open(matrix_1, "r")
	matrix_1_value = []
	
	cmpt = 0
	for line in matrix_1_data:
		if(cmpt != 0):
			vector = []
			line = line.rstrip()
			line_in_array = line.split(",")
			index = 0
			for scalar in line_in_array:
				if(index != 0):
					vector.append(scalar)
				index += 1
			matrix_1_value.append(vector)
		cmpt += 1
	matrix_1_data.close()

	## deal with the compensated matrix
	matrix_2_data = open(matrix_2, "r")
	matrix_2_value = []
	cmpt = 0
	for line in matrix_2_data:
		line = line.rstrip()
		if(cmpt != 0):
			vector = []
			line_in_array = line.split("\t")
			
			index = 0
			for scalar in line_in_array:
				if(index >= 2):
					vector.append(float(scalar)/100.0)
				index += 1
			matrix_2_value.append(vector)
		cmpt += 1
	matrix_2_data.close()


	## compute the delta matrix
	delta_matrix = []
	pos_y = 0
	for vector in matrix_1_value:
		delta_vector = []
		pos_x = 0
		for scalar in vector:
			compensated_scalar = matrix_2_value[pos_y][pos_x] 
			delta_scalar = float(compensated_scalar) - float(scalar)
			delta_vector.append(delta_scalar)
			pos_x += 1

		delta_matrix.append(delta_vector)
		pos_y += 1


	## write the delta matrix in a csv file
	delta_matrix_file = open(output_matrix, "w")
	cmpt = 0
	for vector in delta_matrix:
		line_to_write = ""
		for scalar in vector:
			line_to_write += str(scalar)+","
		line_to_write = line_to_write[:-1]
		if(cmpt < len(delta_matrix)):
			delta_matrix_file.write(line_to_write+"\n")
		else:
			delta_matrix_file.write(line_to_write)
		cmpt +=1
	delta_matrix_file.close()





def generate_all_delta_matrix():
	"""
	Generate all delta matrix from matrix
	found in the data folder
	"""

	## importation
	import glob

	## get files list
	uncompensated_matrix_files = glob.glob("data/matrix/uncompensated/*.txt")
	compensated_matrix_files = glob.glob("data/matrix/compensated/*.txt")

	output_directory = "data/matrix/delta/"
	found_cmpt = 0

	for compensated_matrix in compensated_matrix_files:

		## parse compensated matrix file name
		compensated_matrix_name = compensated_matrix.split("/")
		compensated_matrix_name_in_array = compensated_matrix_name[-1].split("_")
		compensated_matrix_panel = compensated_matrix_name_in_array[1]
		compensated_matrix_center = compensated_matrix_name_in_array[2]
		compensated_matrix_ID = compensated_matrix_name_in_array[3]
		compensated_matrix_ID = compensated_matrix_ID.split(".")
		compensated_matrix_ID = compensated_matrix_ID[0]

		for uncompensated_matrix in uncompensated_matrix_files:

			## parse uncompensated matrix file name
			uncompensated_matrix_name = uncompensated_matrix.split("/")
			uncompensated_matrix_name_in_array = uncompensated_matrix_name[-1].split("_")
			uncompensated_matrix_panel = uncompensated_matrix_name_in_array[1]
			uncompensated_matrix_center = uncompensated_matrix_name_in_array[2]
			uncompensated_matrix_ID = uncompensated_matrix_name_in_array[3]		

			## test the files, get the "goods one"
			if(uncompensated_matrix_center == compensated_matrix_center and uncompensated_matrix_panel == compensated_matrix_panel and uncompensated_matrix_ID == compensated_matrix_ID):

				delta_matrix = output_directory+str(compensated_matrix_name[-1])
				delta_matrix = delta_matrix.split(".")
				delta_matrix = str(delta_matrix[0])+"_delta."+str(delta_matrix[1])

				compute_delta_matrix(uncompensated_matrix, compensated_matrix, delta_matrix)







def get_untouched_position():
	"""
	
	Loop over the delta matrix file and find the
	position that are left untouched by the compensation
	(i.e delta = 0)
	
	display the grid in the console

	return list of position

	"""

	## importation
	import glob


	## init display matrix
	display_matrix = []
	untouched_char = "#"
	touched_char = "-"
	for x in xrange(0,8):
		display_matrix.append([])
		for y in xrange(0,8):
			display_matrix[x].append(untouched_char)


	## loop over all delta matrix
	delta_matrix_files = glob.glob("data/matrix/delta/*.txt")
	for delta_matrix in delta_matrix_files:

		current_delta_matrix = []
		data_file = open(delta_matrix, "r")
		
		pos_y = 0
		for line in data_file:
			line = line.rstrip()
			line_in_array = line.split(",")
			pos_x = 0
			for scalar in line_in_array:
				if(float(scalar) != 0.0):
					display_matrix[pos_y][pos_x] = touched_char
				pos_x += 1
			pos_y += 1
		data_file.close()
		

		## Display grid
		untouched_position = []
		pos_y = 0
		for vector in display_matrix:
			line_to_display = ""
			pos_x = 0
			for scalar in vector:
				line_to_display += " " + str(scalar)+" "
				if(scalar == untouched_char):
					untouched_position.append((pos_y,pos_x))
				pos_x += 1

			print line_to_display
			pos_y += 1

		print "="*23


		## return untouched position
		return untouched_position




def draw_variance_matrix(data_folder):
	"""
	Get the distribution of delta values for each slot of 
	the compensation matrix from all delta matrix, then compute
	variance of each distribution and plot an heatmap to highlight
	the spot with high variance
	"""

	## importation
	import glob
	import numpy
	import matplotlib
	import matplotlib.pyplot as plt


	## init distribution matrix
	position_to_distribution = {}
	for x in xrange(0,8):
		for y in xrange(0,8):			
			key = str(y)+"_"+str(x)
			position_to_distribution[key] = []


	## init variance matrix
	variance_matrix = []
	variance = "NA"
	for x in xrange(0,8):
		variance_matrix.append([])
		for y in xrange(0,8):
			variance_matrix[x].append(variance)


	## loop over all delta matrix
	delta_matrix_files = glob.glob(data_folder+"/*.txt")
	for delta_matrix in delta_matrix_files:

		data_file = open(delta_matrix, "r")
		pos_y = 0
		for line in data_file:

			line = line.rstrip()
			line_in_array = line.split(",")
			pos_x = 0
			
			for scalar in line_in_array:

				key = str(pos_y)+"_"+str(pos_x)
				position_to_distribution[key].append(float(scalar))
				pos_x += 1

			pos_y += 1
		data_file.close()

	## compute variance matrix
	for y in xrange(0,8):
		for x in xrange(0,8):
			key = str(x)+"_"+str(y)
			distribution = position_to_distribution[key]
			variance = numpy.var(distribution)
			variance_matrix[y][x] = variance


	## plot heatmap

	## get the label
	x_label = ["FITC.A","PE.A","PC5.5.A","PC7.A","APC.A","APC.AF750.A","PB.A","KO.A"]
	y_label = x_label

	## get the grid
	grid_to_display = numpy.asarray(variance_matrix)

	## plot the stuff
	fig, ax = plt.subplots()
	im = ax.imshow(grid_to_display)

	# We want to show all ticks...
	ax.set_xticks(numpy.arange(len(x_label)))
	ax.set_yticks(numpy.arange(len(y_label)))
	# ... and label them with the respective list entries
	ax.set_xticklabels(x_label)
	ax.set_yticklabels(y_label)

	# Add colorbar, make sure to specify tick locations to match desired ticklabels
	cbar = fig.colorbar(im, ticks=[numpy.amin(grid_to_display), numpy.amax(grid_to_display)])
	cbar.ax.set_yticklabels([numpy.amin(grid_to_display), numpy.amax(grid_to_display)])  # vertically oriented colorbar


	# Rotate the tick labels and set their alignment.
	plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
	         rotation_mode="anchor")

	ax.set_title("Matrix compensation variance")
	fig.tight_layout()
	plt.show()




def perform_linear_regression(channel_a, channel_b):
	"""
	
	Perform linear regression on specific slot for
	the compensation matrix

		=> not the best solution, uncompensated matrix are identical

	"""

	## impotation
	import glob
	import matplotlib.pyplot as plt
	import numpy as np
	from sklearn import datasets, linear_model
	from sklearn.metrics import mean_squared_error, r2_score


	channel_list = ["FITC.A","PE.A","PC5.5.A","PC7.A","APC.A","APC.AF750.A","PB.A","KO.A"]

	## check the target slot
	target_x = "NA"
	target_y = "NA"

	index = 0
	for channel in channel_list:
		if(channel_a == channel):
			target_y = index
		if(channel_b == channel):
			target_x = index
		index += 1

	## get uncompensated coordinates
	uncompensated_vector = []
	uncompensated_files = glob.glob("data/matrix/uncompensated/*.txt")
	for uncompensated_matrix in uncompensated_files:
		cmpt = 0
		pos_y = 0
		data_file = open(uncompensated_matrix, "r")
		for line in data_file:
			if(cmpt != 0):
				line = line.rstrip()
				line_in_array = line.split(",")
				pos_x = 0
				index = 0
				for elt in line_in_array:
					if(index > 0):
						if(pos_x == target_x and pos_y == target_y):
							uncompensated_vector.append(elt)
						pos_x += 1
					index += 1
				pos_y += 1	

			cmpt += 1
		data_file.close()

	## get compensated coordinates
	compensated_vector = []
	compensated_files = glob.glob("data/matrix/compensated/*.txt")
	for compensated_matrix in compensated_files:
		cmpt = 0
		pos_y = 0
		data_file = open(compensated_matrix, "r")
		for line in data_file:
			if(cmpt != 0):
				line = line.rstrip()
				line_in_array = line.split("\t")
				pos_x = 0
				index = 0
				for elt in line_in_array:
					if(index > 1):
						if(pos_x == target_x and pos_y == target_y):
							compensated_vector.append(float(elt)/100.0)
						pos_x += 1
					index += 1
				pos_y += 1	

			cmpt += 1
		data_file.close()

	## Perform linear regression

	## split data into training an testing
	X_train = uncompensated_vector[:-50]
	X_test = uncompensated_vector[-50:]
		
	X_train_formated = []
	for scalar in X_train:
		X_train_formated.append([float(scalar)])
	X_test_formated = []
	for scalar in X_test:
		X_test_formated.append([float(scalar)])

	Y_train = compensated_vector[:-50]
	Y_test = compensated_vector[-50:]

	# Create linear regression object
	regr = linear_model.LinearRegression()

	# Train the model using the training sets
	regr.fit(X_train_formated, Y_train)

	# Make predictions using the testing set
	Y_pred = regr.predict(X_test_formated)

	# The coefficients
	print "Coefficients: " +str(regr.coef_)
	# The mean squared error
	print("Mean squared error: %.2f"
      % mean_squared_error(Y_test, Y_pred))
	# Explained variance score: 1 is perfect prediction
	print('Variance score: %.2f' % r2_score(Y_test, Y_pred))


	"""
	# Plot outputs
	plt.scatter(X_test_formated, Y_test,  color='black')
	plt.plot(X_test_formated, Y_pred, color='blue', linewidth=3)

	plt.xticks(())
	plt.yticks(())

	plt.show()
	"""





def get_custum_coeff(channel_a, channel_b):
	"""
	get custum score from the delta matrix	
	"""

	## impotation
	import glob
	import numpy


	channel_list = ["FITC.A","PE.A","PC5.5.A","PC7.A","APC.A","APC.AF750.A","PB.A","KO.A"]

	## check the target slot
	target_x = "NA"
	target_y = "NA"

	index = 0
	for channel in channel_list:
		if(channel_a == channel):
			target_x = index
		if(channel_b == channel):
			target_y = index
		index += 1

	## get uncompensated coordinates
	delta_vector = []
	delta_files = glob.glob("data/matrix/delta/*.txt")
	for delta_matrix in delta_files:
		
		pos_y = 0
		data_file = open(delta_matrix, "r")
		for line in data_file:
			line = line.rstrip()
			line_in_array = line.split(",")
			pos_x = 0
			for elt in line_in_array:
				if(pos_x == target_x and pos_y == target_y):
					delta_vector.append(float(elt))
				pos_x += 1
			pos_y += 1	

		data_file.close()

	## Youhou ...
	score = numpy.mean(delta_vector)

	return score




def create_correction_values():
	"""
	Create custom correction values for all
	slot in compensation matrix

	return a dictionnary
	"""

	channel_to_correction = {}
	channel_list = ["FITC.A","PE.A","PC5.5.A","PC7.A","APC.A","APC.AF750.A","PB.A","KO.A"]

	for channel_a in channel_list:
		for channel_b in channel_list:

			key = str(channel_a)+"_"+str(channel_b)
			channel_to_correction[key] = get_custum_coeff(channel_a, channel_b)

	return channel_to_correction



def create_compensated_matrix(uncompensated_matrix_file, correction_values):
	"""
	
	Apply correction stored in correction_values to the uncompensated 
	matrix and write the results in a new predicted matrix file

	=> Might be a problem there

	"""

	## Init parameters
	channel_list = ["FITC.A","PE.A","PC5.5.A","PC7.A","APC.A","APC.AF750.A","PB.A","KO.A"]
	output_folder = "data/matrix/predicted"
	predicted_matrix_name = uncompensated_matrix_file.split("/")
	predicted_matrix_name = predicted_matrix_name[-1].replace("uncompensated", "predicted")
	predicted_matrix = []
	for x in xrange(0,8):
		predicted_vector = []
		for y in xrange(0,8):
			predicted_vector.append("NA")
		predicted_matrix.append(predicted_vector)

	## Parse original matrix
	input_data = open(uncompensated_matrix_file, "r")
	cmpt = 0
	pos_y = 0
	for line in input_data:
		if(cmpt > 0):
			line = line.rstrip()
			line_in_array = line.split(',')
			index = 0
			pos_x = 0 
			for scalar in line_in_array:
				if(index > 0):
					key = str(channel_list[pos_x]+"_"+channel_list[pos_y])
					predicted_value = float(scalar) + float(correction_values[key])
					predicted_matrix[pos_x][pos_y] = predicted_value
					pos_x += 1
				index += 1
			pos_y += 1
		cmpt += 1
	input_data.close()

	## Write predicted matrix
	predicted_matrix_data = open(output_folder+"/"+predicted_matrix_name, "w")
	header_line = "Autofl.\t\t"
	for channel in channel_list:
		header_line += channel+"\t"
	header_line = header_line[:-1]
	predicted_matrix_data.write(header_line+"\n")
	cmpt = 0	
	for vector in predicted_matrix:
		vector_in_line = "0\t"+channel_list[cmpt]+"\t"
		for scalar in vector:
			vector_in_line += str(float(scalar)*100.0)+"\t"
		vector_in_line = vector_in_line[:-1]
		if(cmpt < len(predicted_matrix)):
			predicted_matrix_data.write(vector_in_line+"\n")
		else:
			predicted_matrix_data.write(vector_in_line)
		cmpt += 1
	predicted_matrix_data.close()





def create_all_prediction():
	"""
	Create a prediction matrix for
	each uncompensated matrix found in the
	uncompsated fodler
	"""

	## importation
	import glob

	## get correction values
	correction_structure = create_correction_values()

	## Generate all the predictes matrix
	for uncompensated_matrix_file in glob.glob("data/matrix/uncompensated/*.txt"):
		create_compensated_matrix(uncompensated_matrix_file, correction_structure)






def create_delta_prediction_matrix(compensated_matrix, predicted_matrix, output_matrix):
	"""
	IN PROGRESS
	
	Scavange from compute orginal delta matrix

	"""

	## deal with the compensated matrix
	matrix_1_data = open(compensated_matrix, "r")
	matrix_1_value = []
	
	cmpt = 0
	for line in matrix_1_data:
		if(cmpt != 0):
			vector = []
			line = line.rstrip()
			line_in_array = line.split("\t")
			index = 0
			for scalar in line_in_array:
				if(index >= 2):
					vector.append(scalar)
				index += 1
			matrix_1_value.append(vector)
		cmpt += 1
	matrix_1_data.close()


	## deal with the predicted matrix
	matrix_2_data = open(predicted_matrix, "r")
	matrix_2_value = []
	cmpt = 0
	for line in matrix_2_data:
		line = line.rstrip()
		if(cmpt != 0):
			vector = []
			line_in_array = line.split("\t")
			
			index = 0
			for scalar in line_in_array:
				if(index >= 2):
					vector.append(float(scalar))
				index += 1
			matrix_2_value.append(vector)
		cmpt += 1
	matrix_2_data.close()


	## compute the delta matrix
	delta_matrix = []
	pos_y = 0
	for vector in matrix_1_value:
		delta_vector = []
		pos_x = 0
		for scalar in vector:
			compensated_scalar = matrix_2_value[pos_y][pos_x] 
			delta_scalar = float(compensated_scalar) - float(scalar)
			delta_vector.append(delta_scalar)
			pos_x += 1

		delta_matrix.append(delta_vector)
		pos_y += 1


	## write the delta matrix in a csv file
	delta_matrix_file = open(output_matrix, "w")
	cmpt = 0
	for vector in delta_matrix:
		line_to_write = ""
		for scalar in vector:
			line_to_write += str(scalar)+","
		line_to_write = line_to_write[:-1]
		if(cmpt < len(delta_matrix)):
			delta_matrix_file.write(line_to_write+"\n")
		else:
			delta_matrix_file.write(line_to_write)
		cmpt +=1
	delta_matrix_file.close()




def generate_all_delta_predicted_matrix():
	"""
	IN PROGRESS
	"""

	## importation
	import glob

	## get files list
	compensated_matrix_files = glob.glob("data/matrix/compensated/*.txt")
	predicted_matrix_files = glob.glob("data/matrix/predicted/*.txt")

	output_directory = "data/matrix/delta_predicted/"
	found_cmpt = 0

	for predicted_matrix in predicted_matrix_files:

		## parse compensated matrix file name
		predicted_matrix_name = predicted_matrix.split("/")
		predicted_matrix_name_in_array = predicted_matrix_name[-1].split("_")
		predicted_matrix_panel = predicted_matrix_name_in_array[1]
		predicted_matrix_center = predicted_matrix_name_in_array[2]
		predicted_matrix_ID = predicted_matrix_name_in_array[3]
		predicted_matrix_ID = predicted_matrix_ID.split(".")
		predicted_matrix_ID = predicted_matrix_ID[0]

		for compensated_matrix in compensated_matrix_files:

			## parse uncompensated matrix file name
			compensated_matrix_name = compensated_matrix.split("/")
			compensated_matrix_name_in_array = compensated_matrix_name[-1].split("_")
			compensated_matrix_panel = compensated_matrix_name_in_array[1]
			compensated_matrix_center = compensated_matrix_name_in_array[2]
			compensated_matrix_ID = compensated_matrix_name_in_array[3].split(".")
			compensated_matrix_ID = compensated_matrix_ID[0]		


			

			## test the files, get the "goods one"
			if(compensated_matrix_center == predicted_matrix_center and compensated_matrix_panel == predicted_matrix_panel and compensated_matrix_ID == predicted_matrix_ID):

				delta_matrix = output_directory+str(compensated_matrix_name[-1])
				delta_matrix = delta_matrix.split(".")
				delta_matrix = str(delta_matrix[0])+"_delta."+str(delta_matrix[1])

				create_delta_prediction_matrix(compensated_matrix, predicted_matrix, delta_matrix)






def create_data_file_for_linear_regression(data_folder, output_file):
	"""
	IN PROGRESS
	"""

	## importation
	import glob


	## open output file
	output_data = open(output_file, "w")

	## get all data files
	data_files = glob.glob(data_folder+"/*.txt")
	
	## write header
	variable_list = ["FITC.A","PE.A","PC5.5.A","PC7.A","APC.A","APC.AF750.A","PB.A","KO.A"]
	header = ""
	for var in variable_list:
		for var2 in variable_list:
			header += var+"-"+var2+","
	header = header[:-1]
	output_data.write(header+"\n")

	## get data, assume matrix files are compensated matrix file
	cmpt = 0
	for data_file in data_files:
		line_to_write = ""
		cmpt = 0
		data = open(data_file, "r")
		for line in data:
			line = line.rstrip()
			line_in_array = line.split("\t")
			if(cmpt > 0):
				index =0
				for elt in line_in_array:
					if(index > 1):
						line_to_write += str(elt)+","
					index += 1
			cmpt += 1
		data.close()
		line_to_write = line_to_write[:-1]
		if(cmpt < len(data_files)):
			output_data.write(line_to_write+"\n")
		else:
			output_data.write(line_to_write)
		cmpt += 1

	## close output file
	output_data.close()




#create_data_file_for_linear_regression("data/matrix/compensated", "data_reg_test.csv")




def write_report():
	"""
	IN PROGRESS
	"""

	## importation
	import glob

	## parameters
	entry_list = []
	uncompensated_images = glob.glob("output/uncompensated_images/*.png")
	predicted_images = glob.glob("output/predicted_images/*.png")
	report_file_name = "report.html"


	## get list of entry
	for image_file in uncompensated_images:
		image_file_in_array = image_file.split("/")
		image_file_in_array = image_file_in_array[-1].split(".")
		image_file_in_array = image_file_in_array[0].split("_")
		file_panel = image_file_in_array[1]
		file_id = image_file_in_array[2]
		file_center = image_file_in_array[3]
		patient_tag = "Panel_"+str(file_panel)+"_"+str(file_id)+"_"+str(file_center)
		if(patient_tag not in entry_list):
			entry_list.append(patient_tag)


	## Write report
	report_file = open(report_file_name, "w")

	report_file.write("<html>\n")
	report_file.write("<head>\n\t<title>Automatic Compensation</title>\n</head>\n")
	report_file.write("<body>\n")
	report_file.write("\t<h1>Automatic Compensation</h1>\n")

	for tag in entry_list:
		report_file.write("\t<h2>"+str(tag)+"</h2>\n")

	report_file.write("</body>\n")
	report_file.write("</html>")
	report_file.close()



def compensation_tool(fcs_file):
	"""
	
	Compensation tool, V1

	A lot of stuff in progress

	-> fcs_file must be an absolute path

	"""

	## importation
	import os

	## parameters
	EXTRACTMATRIX_SCRIPT = "extractMatrix.R"
	GENERATEIMAGE_SCRIPT = "CreateImageFromFCS.R"
	APPLYCOMPENSATION_SCRIPT = "ApplyCompensation.R"
	
	uncompensated_matrix_file_name = fcs_file.split("/")
	uncompensated_matrix_file_name = uncompensated_matrix_file_name[-1].split("_")

	output_folder = "data/matrix/uncompensated"
	Panel = uncompensated_matrix_file_name[1]
	ID = uncompensated_matrix_file_name[2]
	center = uncompensated_matrix_file_name[3]
	uncompensated_matrix_file_name = output_folder+"/Panel_"+str(Panel)+"_"+str(center)+"_"+str(ID)+"_uncompensated.txt"
	predicted_matrix_file_name = uncompensated_matrix_file_name.replace("uncompensated", "predicted")
	compensated_fcs = fcs_file+"_comp.fcs"
	image_uncomp_folder = "output/uncompensated_images"
	image_predict_folder = "output/predicted_images"

	## compute correction matrix
	print "[Step 1][+] Create correction values" 
	correction_values = create_correction_values()

	## extract compensation from fcs_file
	print "[Step 2][+] Extract compensation matrix"
	os.system("Rscript "+EXTRACTMATRIX_SCRIPT+" "+str(fcs_file))

	## Generate image from fcs file
	print "[Step 3][+] Generate images for uncompensated files"
	os.system("Rscript "+GENERATEIMAGE_SCRIPT+" "+str(fcs_file))
	os.system("mv *.png "+str(image_uncomp_folder+"/"))

	## compute compensated matrix
	print "[Step 4][+] Compute new compensation matrix"
	create_compensated_matrix(uncompensated_matrix_file_name, correction_values)

	## apply compensated matrix
	print "[Step 5][+] Apply new compensation"
	os.system("Rscript "+APPLYCOMPENSATION_SCRIPT+" "+str(fcs_file)+" "+str(predicted_matrix_file_name))

	## generate image from compensated fcs file
	print "[Step 6][+] Generate images for compensated files"
	os.system("Rscript "+GENERATEIMAGE_SCRIPT+" "+str(compensated_fcs))
	os.system("mv *.png "+str(image_predict_folder+"/"))

	## create graphical output
	print "[Step 7][+] Write report"
	write_report()


	print "[Step 8][*] EOF"















## try compensation tool
input_fcs_file = "/home/glorfindel/Spellcraft/SIDEQUEST/compensation/Panel_5_32152231_DRFZ_CANTO2_22JUL2016_22JUL2016.fcs_intra.fcs"
input_fcs_file = "/home/glorfindel/Spellcraft/SIDEQUEST/compensation/Panel_5_42_TEST_blablabla.fcs"
compensation_tool(input_fcs_file)
