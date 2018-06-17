


def transpose_matrix_file(matrix_file):
	"""
	IN PROGRESS
	"""

	# importation
	import numpy
	import shutil

	## parameters
	channel_list = ["channel1","channel2","channel3","channel4","channel5","channel6","channel7","channel8"]
	output_file_name = matrix_file.split("/")
	output_file_name = output_file_name[-1].split(".")
	output_file_name = output_file_name[0]+"_transposed."+output_file_name[1]

	## init grid
	matrix_grid = []
	scalar = "NA"
	for x in xrange(0,8):
		grid_vector = []
		for x in xrange(0,8):
			grid_vector.append(scalar)
		matrix_grid.append(grid_vector)

	## Parse data
	matrix_data = open(matrix_file, "r")
	cmpt = 0
	pos_y = 0
	header = ""
	prefix = ""
	for line in matrix_data:
		if(cmpt > 0):
			line = line.rstrip()
			line_in_array = line.split("\t")
			index = 0
			pos_x = 0
			prefix = line_in_array[0]
			for scalar in line_in_array:
				if(index > 1):
					matrix_grid[pos_y][pos_x] = float(scalar)
					pos_x += 1

				index += 1
			pos_y += 1
		else:
			header = line
		cmpt += 1
	matrix_data.close()

	## transpose matrix
	matrix_grid = numpy.asarray(matrix_grid)
	matrix_grid = matrix_grid.transpose()

	## write new matrix file
	transposed_matrix = open(output_file_name, "w")
	transposed_matrix.write(header)
	cmpt = 0
	for vector in matrix_grid:
		line_to_write = str(prefix)+"\t"+channel_list[cmpt]+"\t"
		for scalar in vector:
			line_to_write += str(scalar)+"\t"
		line_to_write = line_to_write[:-1]
		if(cmpt == 7):
			transposed_matrix.write(line_to_write)
		else:
			transposed_matrix.write(line_to_write+"\n")

		cmpt += 1
	transposed_matrix.close()

	## replace old matrix file transpose matrix file
	shutil.copy(output_file_name, matrix_file)

transpose_matrix_file("test_matrix.csv")