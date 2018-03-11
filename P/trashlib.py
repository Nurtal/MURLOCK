"""
Grand Bazar
"""
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from Bio import Entrez
from Bio.Entrez import efetch, read
import nltk
import re
import pprint
import glob
import os
import operator
import collections

import numpy as np

from word2number import w2n

from bioservices import *

import mygene


Entrez.email = 'murlock.raspberypi@gmail.com'


def fetch_abstract(pmid):
	"""
	Retrun abstract of a given
	article using pmid

	=> Return None when pmid can't be return
	(can happen when article is in chinese)
	"""
	handle = efetch(db='pubmed', id=pmid, retmode='xml', )
	xml_data = read(handle)
	xml_data = xml_data['PubmedArticle'][0]
	
	try:
		article = xml_data['MedlineCitation']['Article']
		abstract = article['Abstract']['AbstractText'][0]
		return abstract
	except IndexError:
		return None
	except KeyError:
		return None


def fetch_article(pmid):
	"""
	Test function
	"""
	handle = efetch(db='pubmed', id=pmid, retmode='xml', )
	xml_data = read(handle)[0]

	try:
		article = xml_data['MedlineCitation']['Article']
		abstract = article['Abstract']['AbstractText'][0]
		return article

	except IndexError:
		return None


def get_ListOfArticles(term, max_count):
	"""
	return the list of pmid article conatining
	the term.
	"""
	h = Entrez.esearch(db='pubmed', retmax=max_count, term=term)
	result = Entrez.read(h)
	listOfArticles = result["IdList"]


	return listOfArticles;



def get_ListOfCommunPathway(elt1, elt2):

	"""
	-> elt1 and elt2 are KEGG id
	return the list of commun pathway between elt1 and elt2
	-> Use bioservices
	-> Internet connection needed
	-> Use KEGG database
	-> "hsa" correspond to human in KEGG database
	"""

	k = KEGG(verbose=False)

	list_OfCommunPathway = []
	list_pathways_elt1 = k.get_pathway_by_gene(str(elt1), "hsa")
	list_pathways_elt2 = k.get_pathway_by_gene(str(elt2), "hsa")

	for pathway_elt1 in list_pathways_elt1.keys():
		for pathway_elt2 in list_pathways_elt2.keys():
			if(str(pathway_elt1) == str(pathway_elt2)):
				list_OfCommunPathway.append(str(pathway_elt1))

	return list_OfCommunPathway



def get_ListOfDirectInteraction(elta, eltb):
	"""
	-> Scan interaction DataBase and return the list of direct interaction
	between elta and eltb.
	-> For now elta and eltb have to be uniprot ID
	-> For now only scan mint DB
	"""

	list_interactions = []
	s = PSICQUIC(verbose=False)
	data = s.query("mint", str(elta)+" AND species:9606")

	for interaction in data:
		line1 = interaction[0]
		line2 = interaction[1]
		line1InArray = line1.split(":")
		line2InArray = line2.split(":")
		uniprotId_elt1 = line1InArray[1]
		uniprotId_elt2 = line2InArray[1]
		if(str(uniprotId_elt1) == str(elta) and str(uniprotId_elt2) == str(eltb)):
			list_interactions.append(interaction)


	return list_interactions



def get_interactors(interaction):
	"""
	return the list of elements in interaction
	-> always 2 elements
	-> work for mint db
	"""

	list_ofInteractors = []

	line1 = interaction[0]
	line2 = interaction[1]
	line1InArray = line1.split(":")
	line2InArray = line2.split(":")
	if(len(line1InArray) > 1):
		uniprotId_elt1 = line1InArray[1]
		list_ofInteractors.append(str(uniprotId_elt1))
	else:
		uniprotId_elt1 = "CAN'T PARSE DATA"
		list_ofInteractors.append(str(uniprotId_elt1))
	if(len(line2InArray) > 1):
		uniprotId_elt2 = line2InArray[1]
		list_ofInteractors.append(str(uniprotId_elt2))
	else:
		uniprotId_elt2 = "CAN'T PARSE DATA"
		list_ofInteractors.append(str(uniprotId_elt2))

	return list_ofInteractors



def get_CuratedInteraction(elementToCheck):
	"""
	return the list of curated interaction (i.e doublons are removed)
	including elementToCheck.

	-> work for mint db
	-> id are uniprotId
	"""
	#list_elementsToCheck.append(str(elementToCheck))
	s = PSICQUIC(verbose=False)
	data = s.query("mint", str(elementToCheck)+" AND species:9606")

	listOfInterctorsInGraph = []
	listOfCuratedInteraction = []

	for db in data:
		machin = get_interactors(db)
		interactionType = get_InteractionType(db)
		if(str(machin[0]) == str(elementToCheck) and str(machin[1]) not in listOfInterctorsInGraph):
			interaction = str(machin[0])+"\t"+str(interactionType)+"\t"+str(machin[1])
			listOfCuratedInteraction.append(interaction)
			listOfInterctorsInGraph.append(machin[1])
		elif(str(machin[1]) == str(elementToCheck) and str(machin[0]) not in listOfInterctorsInGraph):
			interaction = str(machin[1])+"\t"+str(interactionType)+"\t"+str(machin[0])
			listOfCuratedInteraction.append(interaction)
			listOfInterctorsInGraph.append(machin[0])

	return listOfCuratedInteraction




def draw_InteractionGraph(element, fileName):
	"""
	Write all interactions including element and interactions
	including each element assiocated with the first element
	and so on ... in a .sif file (fileName).

	-> Work with mint database
	-> use grep -v "sapiens" to deal with unwanted output
	return nothing
	"""

	list_elementsToCheck = []
	list_elementChecked = []
	list_elementsToCheck.append(element)

	for element in list_elementsToCheck:
		if(element not in list_elementChecked):
			machin = get_CuratedInteraction(str(element))
		
			list_elementsToCheck.remove(str(element))
			list_elementChecked.append(str(element))

			for interaction in machin:
				interactionInArray = interaction.split("\t")

				grapheFile = open(fileName, "a")
				grapheFile.write(interaction+"\n")
				grapheFile.close()

				print interaction
				if(interactionInArray[2] not in list_elementsToCheck):
					list_elementsToCheck.append(interactionInArray[2])
		else:
			print "->"+str(element) + "already Ckeck"



def get_InteractionType(interaction):
	"""
	return the type of interaction
	-> work on mint db
	"""

	typeOfInteraction =  interaction[11]
	typeOfInteractionInArray = typeOfInteraction.split("(")
	interactionName = typeOfInteractionInArray[1]
	interactionName = interactionName[:-1]
	return interactionName



def convert_SifFileToGDFfile(fileName):
	"""
	[IN PROGRESS]

	-> Try on small files 

	"""

	#check extension
	fileNameInArray = fileName.split(".")
	if(len(fileNameInArray) < 1):
		print "Can't parse format for conversion\n"
	elif(fileNameInArray[1] != "sif"):
		print "Wrong format for input file, .sif expected ("+fileNameInArray[1]+" found)"
	else:
		inputFilename = fileNameInArray[0]

	#Initialise node tmp file
	tmpFile_node = open("nodes_buildGDF.tmp", "a")
	tmpFile_node.write("nodedef>name VARCHAR\n")
	tmpFile_node.close()

	#Initialise edge tmp file
	tmpFile_edge = open("edges_buildGDF.tmp", "a")
	tmpFile_edge.write("edgedef>node1 VARCHAR,node2 VARCHAR\n")
	tmpFile_edge.close()

	listOfNodes = []
	sifFile = open(fileName, "r")
	for line in sifFile:
		lineInArray = line.split("\t")
		node1 = lineInArray[0]
		node2 = lineInArray[2]
		if(node1 not in listOfNodes):
			tmpFile_node = open("nodes_buildGDF.tmp", "a")
			tmpFile_node.write(str(node1)+"\n")
			tmpFile_node.close()
			listOfNodes.append(node1)
		
		tmpFile_edge = open("edges_buildGDF.tmp", "a")
		tmpFile_edge.write(str(node1)+","+str(node2))
		tmpFile_edge.close()

	# Write GDF file
	outputFile = open(str(inputFilename)+".gdf", "a")
	tmpFile_node = open("nodes_buildGDF.tmp", "r")
	for line in tmpFile_node:
		outputFile.write(line)
	tmpFile_node.close()
	tmpFile_edge = open("edges_buildGDF.tmp", "r")
	for line in tmpFile_edge:
		outputFile.write(line)
	tmpFile_edge.close()
	outputFile.close()

	# delete tmp file
	os.remove("nodes_buildGDF.tmp")
	os.remove("edges_buildGDF.tmp")


def save_abstract(abstract, save_file):
	##
	## -> Save the abstract in a text file
	## convert the abstract to unicode.
	##

	## preprocess abstract
	#abstract_preprocess = unicode(abstract)
	abstract_preprocess = abstract.encode('utf8')

	## save abstract in file
	output = open(save_file, "w")
	output.write(abstract_preprocess)
	output.close()

def get_cohorte_size(abstract_file):
	##
	## IN PROGRESS
	##
	## -> Try to retrieve the number of patients/case
	## in the dataset presented in the abstract
	## 
	## TODO : add more regex for size detection
	## TODO : add to bibotlite.py
	##

	## useful_data_structure


	## read abstract
	abstract = open(abstract_file, "r")

	cohorte_size = -1
	for line in abstract:


		## try to catch a written number before the apparition 
		## of the term in catch list
		catch_terms = ["patients", "cases", "observations", "subjects"]
		line_in_array = line.split(" ")
		cmpt_in_line = 0
		for elt in line_in_array:	
			if(elt in catch_terms):
				try:
					fetched_cohorte_size = w2n.word_to_num(line_in_array[cmpt_in_line-1])
					if(fetched_cohorte_size > cohorte_size):
						cohorte_size = fetched_cohorte_size
						nothing_retrieved = False
				except:
					nothing_retrieved = True

				if(nothing_retrieved):
					try:
						fetched_cohorte_size = w2n.word_to_num(line_in_array[cmpt_in_line-2])
						if(fetched_cohorte_size > cohorte_size):
							cohorte_size = fetched_cohorte_size
							nothing_retrieved = False
					except:
						nothing_retrieved = True

				if(nothing_retrieved):
					try:
						fetched_cohorte_size = w2n.word_to_num(line_in_array[cmpt_in_line-3])
						if(fetched_cohorte_size > cohorte_size):
							cohorte_size = fetched_cohorte_size
							nothing_retrieved = False
					except:
						nothing_retrieved = True
			cmpt_in_line += 1



		## Try to catch a number before the apparition of the 
		## term in catch terms list. keep the biggest number
		## found in the abstract.
		catch_terms = ["patients", "cases", "observations", "subjects"]
		for item in catch_terms:
			m = re.findall(r"([0-9]+[\.|,]?[0-9]+) "+str(item), line)		
			if(m is not None):
				for match in m:
					match = match.replace(",", "")
					try:
						fetched_cohorte_size = int(match)
						if(fetched_cohorte_size > cohorte_size):
							cohorte_size = fetched_cohorte_size
					except:
						## do nothing
						tardis = 1


		## Try to catch a number after the apparition of the 
		## term "n = ". keep the biggest number found in the
		## abstract.
		m = re.findall(r"n = ([0-9]+[\.|,]?[0-9]+)", line)		
		if(m is not None):
			for match in m:
				match = match.replace(",", "")
				try:
					fetched_cohorte_size = int(match)
					if(fetched_cohorte_size > cohorte_size):
						cohorte_size = fetched_cohorte_size
				except:
					## do nothing
					tardis = 1

		## Try to catch a number in a classic expression
		m = re.findall(r"[I,i]n total, ([0-9]+[\.|,]?[0-9]+) subjects", line)
		if(m is not None):
			for match in m:
				match = match.replace(",", "")
				try:
					fetched_cohorte_size = int(match)
					if(fetched_cohorte_size > cohorte_size):
						cohorte_size = fetched_cohorte_size
				except:
					## do nothing
					tardis = 1

		"""
		## Try to catch a number in a classic expression
		m = re.findall(r"([0-9]+[\.|,]?[0-9]+)", line)
		if(m is not None):
			for match in m:
				match = match.replace(",", "")
				try:
					fetched_cohorte_size = int(match)
					if(fetched_cohorte_size > cohorte_size):
						cohorte_size = fetched_cohorte_size
				except:
					## do nothing
					tardis = 1
		"""


	## close abstract
	abstract.close()

	## check if the cohorte_size variable
	## is still set to -1, set it to NA if
	## True
	if(cohorte_size == -1):
		cohorte_size = "NA"

	## return the detected size of the cohorte
	return cohorte_size





def get_date_from_meta_save(meta_file):
	##
	## Get the date of an article using the
	## meta data file created on local device,
	## no connection needed to NCBI server
	##
	## -> return the year of publication
	##
	## TODO : add to bibotlite.py
	##

	## Retrieve the year of publication
	## from the meta data file.
	year = "NA"
	meta_data = open(meta_file, "r")
	for line in meta_data:
		
		line = line.replace("\n", "")
		if(line[0] == ">"):

			line_in_array = line.split(";")
			if(line_in_array[0] == ">Date"):
				date_in_array = line_in_array[1].split("/")
				year = date_in_array[2]

	meta_data.close()

	## return only the year of publication
	return year




def plot_pulbications_years(meta_data_folder):
	##
	## Retrieve the year of publications of all
	## articles from the meta_data_folder and
	## plot the histogramm of publications over
	## the years
	##
	## TODO : add to bibotlite.py
	##

	## create the structure
	year_to_count = {}
	for meta_file in glob.glob(meta_data_folder+"/*.csv"):
		year = get_date_from_meta_save(meta_file)
		
		if(int(year) < 2018):

			if(year not in year_to_count.keys()):
				year_to_count[year] = 1
			else:
				year_to_count[year] += 1

	## plot graphe
	plt.bar(year_to_count.keys(), year_to_count.values(), 1, color='b')
	plt.show()




def plot_word_evolution(item_list, run_folder):
	##
	## -> Plot word frequency evolution over
	## the last decade
	##


	for item in item_list:

		## get year to pmid
		year_to_pmid = {}
		for meta_file in glob.glob(run_folder+"/meta/*.csv"):
			pmid = meta_file.split("/")
			pmid = pmid[-1]
			pmid = pmid.split(".")
			pmid = pmid[0]
			year = get_date_from_meta_save(meta_file)
			if(year not in year_to_pmid.keys()):
				year_to_pmid[year] = []
				year_to_pmid[year].append(pmid)
			else:
				year_to_pmid[year].append(pmid)

		## get apparition count in articles
		year_to_count = {}
		for year in year_to_pmid.keys():
			list_of_pmis_to_check = year_to_pmid[year]
			year_to_count[year] = 0
			for pmid in list_of_pmis_to_check:
				abstract_file = run_folder+"/"+"abstract/"+str(pmid)+"_abstract.txt"
				try:
					abstract_data = open(abstract_file, "r")
					for line in abstract_data:	
						m = re.findall(r"("+str(item)+")", line)		
						if(m is not None):
							if(len(m) > 0):
								year_to_count[year] += 1
					abstract_data.close()
				except:
					## do nothing
					tardis = 1

		## get apparition frequencies
		year_to_frequency = {}
		for year in year_to_pmid.keys():
			frequency = float(year_to_count[year])/float(len(year_to_pmid[year]))
			year_to_frequency[year] = frequency

		## save the figure
		y_vector = []
		x_vector = sorted(year_to_frequency.keys())

		for year in x_vector:
			y_vector.append(year_to_frequency[year])
		fig = plt.figure()
		plt.plot(x_vector, y_vector)
		plt.savefig(str(item)+"_frequency.png")
		#plt.show()
	




def describe_articles_type(run_folder):
	##
	## 
	## Count the number of articles talking about
	## several diseases, return a dictionnary.
	## currently work on:
	##		- SjS
	##		- SLE
	##		- RA
	##

	abstract_to_disease = {}
	abstract_to_disease["SjS"] = 0
	abstract_to_disease["SLE"] = 0
	abstract_to_disease["RA"] = 0 
	abstract_to_disease["Other"] = 0
	abstract_list = glob.glob(str(run_folder)+"/abstract/*.txt")
	for abstract_file in abstract_list:

		talking_about_SjS = False
		talking_about_RA = False
		talking_about_SLE = False

		abstract = open(abstract_file, "r")

		for line in abstract:

			## SjS
			m = re.findall(r"([S,s]j.gren)", line)
			if(len(m)>0):
				talking_about_SjS = True
			m = re.findall(r"(SjS)", line)
			if(len(m)>0):
				talking_about_SjS = True

			## SLE
			m = re.findall(r"([L,l]upus)", line)
			if(len(m)>0):
				talking_about_SLE = True
			m = re.findall(r"(SLE)", line)
			if(len(m)>0):
				talking_about_SLE = True

			## RA
			m = re.findall(r"([A,a])rthrisis", line)
			if(len(m)>0):
				talking_about_RA = True
			m = re.findall(r"(RA)", line)
			if(len(m)>0):
				talking_about_RA = True

		
		if(talking_about_SjS):
			abstract_to_disease["SjS"] += 1
		if(talking_about_SLE):
			abstract_to_disease["SLE"] += 1
		if(talking_about_RA):
			abstract_to_disease["RA"] += 1
		else:
			abstract_to_disease["Other"] += 1

			
		abstract.close()

	

	print abstract_to_disease
		





def get_all_subjects_from_abstract(abstract_folder):
	##
	## The idea is to find all key word from
	## each abstract in a run folder and
	## return a list of key word.
	##
	## Word are selected by the number of apparition in
	## all abstracts, if found in more than 10 % of the articles,
	## the word is selected
	##

	## get list of all abstract files
	abstract_list = glob.glob(abstract_folder+"/*.txt")
	name_list = []
	name_to_count = {}

	treshold = 0.1

	abstract_parsed = 0
	for abstract in abstract_list:
		names_found_in_abstract = []
		abstract_data = open(abstract, "r")
		for line in abstract_data:
			try:
				tokens = nltk.word_tokenize(line.encode('utf8'))
				tagged = nltk.pos_tag(tokens)
				entities = nltk.chunk.ne_chunk(tagged)
				abstract_parsed += 1
			except:
				## Something went wrong
				entities = []

			for item in entities:
				try:
					if(item[1] in ["NN", "NNS", "NNP"]):
						if(item[0] not in names_found_in_abstract):
							names_found_in_abstract.append(item[0])
				except:
					## Somethig went wrong
					choucroute = True

		for name in names_found_in_abstract:
			if(name not in name_to_count.keys()):
				name_to_count[name] = 1
			else:
				name_to_count[name] += 1
		abstract_data.close()

	for name in name_to_count.keys():
		if(float(name_to_count[name]/float(abstract_parsed)) > treshold and name not in name_list):
			name_list.append(name)	

	return name_list



def get_number_of_articles_from_log_file(log_file):
	##
	## Get the total number of articles found
	## by the run by looking to the run's log
	## file.
	##
	## return an int or "NA" if nothing is found. 
	##

	number_of_articles = "NA"
	log_data = open(log_file, "r")
	for line in log_data:
		line = line.replace("\n", "")
		line_in_array = line.split(";")
		if(line_in_array[0] == "Total_number_of_articles"):
			try:
				number_of_articles = int(line_in_array[1])
			except:
				number_of_articles = "NA"

	log_data.close()

	return number_of_articles


def get_number_of_keywords_from_log_file(log_file):
	##
	## Get the total number of keywords used to
	## generate the combination of request by
	## the run.
	##
	## return an int or "NA" if nothing is found. 
	##

	number_of_keywords = "NA"
	log_data = open(log_file, "r")
	cmpt = 0
	for line in log_data:
		line = line.replace("\n", "")
		line_in_array = line.split(";")
		if(cmpt == 0):
			try:
				number_of_keywords = len(line_in_array)
			except:
				number_of_keywords = "NA"
		else:
			break

		cmpt += 1

	log_data.close()

	return number_of_keywords



def get_articles_filter_stat(log_file):
	##
	## Get the count of articles that passed the first
	## filter, the second filter, and both.
	## return a tuple of int
	##

	first_filter_pass_cmpt = 0
	second_filter_pass_cmpt = 0
	pass_both_filter_cmpt = 0

	log_data = open(log_file, "r")
	for line in log_data:
		line = line.replace("\n", "")
		line_in_array = line.split(";")
		if(line[0] == ">"):
			
			filter_1_info = line_in_array[1].split("=")
			if(filter_1_info[1] == "PASSED"):
				first_filter_pass_cmpt += 1

			filter_2_info = line_in_array[2].split("=")
			if(filter_2_info[1] == "PASSED"):
				second_filter_pass_cmpt += 1


			if(filter_1_info[1] == "PASSED" and filter_2_info[1] == "PASSED"):
				pass_both_filter_cmpt += 1


	log_data.close()

	return (first_filter_pass_cmpt, second_filter_pass_cmpt, pass_both_filter_cmpt)



def get_number_of_articles_for_year(run_folder, year):
	##
	## get the number of articles published in a
	## specific year, parse data from meta files
	## in the given run folder
	##

	article_cmpt = 0

	for meta_file in glob.glob(run_folder+"/meta/*.csv"):
		meta_data = open(meta_file, "r")
		for line in meta_data:
			line = line.replace("\n", "")
			line_in_array = line.split(";")
			if(line_in_array[0] == ">Date"):
				date = line_in_array[1]
				date_in_array = date.split("/")
				year_fetched = date_in_array[-1]
				if(int(year_fetched) == year):
					article_cmpt += 1
		meta_data.close()

	return article_cmpt


def get_country_publication_stat(run_folder):
	##
	## Get the publications stats for country.
	## get the list of pmid retrieved from the
	## meta folder and connect to the NCBI to fecth
	## publications informations, parse it to get the
	## country of publication.
	## 
	## return a dictionnary
	##

	## init structure
	country_to_count = {}

	## get list of PMID to process
	meta_file_list = glob.glob(run_folder+"/meta/*.csv")
	for meta_file in meta_file_list:
		meta_file_in_array = meta_file.split("/")
		file_name = meta_file_in_array[-1]
		file_name_in_array = file_name.split(".")
		pmid = file_name_in_array[0]

		## get country publication
		try:
			handle = efetch(db='pubmed', id=pmid, retmode='xml', )
			informations = read(handle)
			stuff = informations[u'PubmedArticle'][0]
			country = stuff[u'MedlineCitation'][u'MedlineJournalInfo'][u'Country']
		except:
			country = "NA"

		## fill dictionnary
		if(country not in country_to_count.keys()):
			country_to_count[country] = 1
		else:
			country_to_count[country] += 1

	return country_to_count





def get_article_domain(abstract):
	##
	## IN PROGRESS
	##
	## Fit an article on a pre existing
	## class based on the content of its abstract
	##
	##
	## Class:
	##
	##	- Diagnostic : predict the diagnostic of a patient
	##
	##	- Therapeutic : test a treatment
	##
	##	- Modelisation : try to understand the disease
	##
	## 	- Unclassified : not sure what we are talking about
	##

	## Control structure
	diagnostic_keywords = ["classification", "Classification", "criteria", "diagnostic", "diagnosis", "prevalence", "epidemiological"]
	therapeutic_keywords = ["therapeutic", "therapy", "treatment", "treatments", "rituximab"]
	modelisation_keywords = ["model", "models", "modelisation", "components", "dynamics", "composition", "pathway", "regulatory", "regulates", "mechanistic", "mechanism", "mechanisms"]

	diagnostic_score = 0
	therapeutic_score = 0
	modelisation_score = 0

	article_theme = "Unclassified"

	## Looking for keyword in the abstract with nltk
	names_found_in_abstract = []
	abstract_data = open(abstract, "r")
	for line in abstract_data:
		try:
			tokens = nltk.word_tokenize(line.encode('utf8'))
			tagged = nltk.pos_tag(tokens)
			entities = nltk.chunk.ne_chunk(tagged)
		except:
			## Something went wrong
			entities = []
		for item in entities:
			try:
				if(item[1] in ["NN", "NNS", "NNP"]):
					if(item[0] not in names_found_in_abstract):
						names_found_in_abstract.append(item[0])
			except:
				## Somethig went wrong
				choucroute = True

	## compute score
	for name in names_found_in_abstract:
		if(name in diagnostic_keywords):
			diagnostic_score += 1
		elif(name in therapeutic_keywords):
			therapeutic_score += 1
		elif(name in modelisation_keywords):
			modelisation_score += 1

	abstract_data.close()
	
	## looking for regular expression
	## split abstract into sentences, look for combination
	## of keywords in each sentences.
	## Get the list of words
	abstract_data = open(abstract, "r")
	text = ""
	for line in abstract_data:
		text +=line
	abstract_data.close()
	sentences = text.split(". ")
	words = text.replace(".", "")
	words = words.replace(",", "")
	words = words.replace(":", "")
	words = words.replace(";", "")
	words = words.split(" ")


	## Looking for co-occurences
	for sentence in sentences:
		
		## modelisation 
		if(("mechanisms" in sentence or "mechanism" in sentence) and ("understood" in sentence or "understand" in sentence)):
			modelisation_score += 1
		if(("summarize" in sentence) and ("mechanism" in sentence or "mechanisms" in sentence or "pathway" in sentence or "pathways" in sentence)):
			modelisation_score += 1
		if(("present" in sentence and "study" in sentence) and "investigated" in sentence):
			modelisation_score += 1
		if("investigated" in sentence and "interactions" in sentence):
			modelisation_score += 1

		## Diagnostic
		if("identification" in sentence and ("phenotype" in sentence or "phenotypes" in sentence or "subphenotype" in sentence or "subphenotypes" in sentence)):
			diagnostic_score += 1
		if("severity" in sentence and "marker" in sentence):
			diagnostic_score += 1
		if("differentiate" in sentence and "patients" in sentence):
			diagnostic_score += 1
		if(("biomarker" in sentence or "biomarkers" in sentence) and ("disease" in sentence or "diseases" in sentence)):
			diagnostic_score += 1

		## Therapeutic
		if("impact" in sentence and "course of disease" in sentence):
			therapeutic_score += 1

	## Checking words
	for word in words:
		if(word in diagnostic_keywords):
			diagnostic_score += 1
		elif(word in therapeutic_keywords):
			therapeutic_score += 1
		elif(word in modelisation_keywords):
			modelisation_score += 1



	## compute score
	scores = {"Diagnostic":diagnostic_score, "Therapeutic":therapeutic_score, "Modelisation":modelisation_score}
	sorted_scores = sorted(scores.items(), key=operator.itemgetter(1))

	if(sorted_scores[-1][1] > 0):
		article_theme = sorted_scores[-1][0]

	return article_theme



def get_count_of_articles_type_for_each_disease():
	##
	## IN PROGRESS
	##

	## Diagnostic
	for file in glob.glob("articles_classification/Diagnostic/*"):

		abstract = open(file, "r")
		abstract_in_line = ""
		for line in abstract:
			abstract_in_line += line
		abstract.close()

		## SjS
		disease_keywords = ["SjS", "sjogren"]




def retrieve_techniques(run_folder, display_details):
	##
	## Retrieve techniques used in articles from parsing the abstracts
	## run_folder is the name of the run_folder
	## display_details is a boolean:
	##    - True: display details
	##    - False: do nothing 
	##
	##
	## Read abstracts in the articles_classification subfolders
	##    - Diagnostic
	##    - Therapeutic
	##    - Modelisation
	##    - Unclassified
	## 
	## Parse each abstract and look for a list of statistical analaysis appraoches:
	##    - t-test
	##    - logistic regression
	##    - cox regression
	##    - multivariate regression
	##    - univariate regression
	##    - linear regression
	##    - Poisson regression
	##    - regression tree
	##    - regression analysis
	##    - clustering
	##    - hierarchical clustering
	##    - decision tree
	##    - random forest
	##    - artificial neural network
	##    - support vector machine
	##    - machine learning
	##    - Wilcoxon test
	##    - PCA
	##    - chi-squared
	##    - multivariate analysis
	##    - univariate analysis
	##    - discriminant analysis
	##    - bioinformatics analysis
	##    - GLM (generalized linear model)
	##    - mixed models
	##    - normalization
	##    - k mean
	##
	## Return a tuple of dictionnary ({category : technique : count}, {year: techniques : count}
	##


	## initiate data structure
	category_to_techniques = {"Diagnostic":{}, "Therapeutic":{}, "Modelisation":{}, "Unclassified":{}}
	date_to_techniques_to_count = {}
	date_to_category_to_techniques_to_count = {}
	## Parse the abstracts
	for category in ["Diagnostic", "Therapeutic", "Modelisation", "Unclassified"]:
		date_to_category_to_techniques_to_count[category] = {}
		for file in glob.glob("articles_classification/"+str(category)+"/*"):

			## get pmid
			pmid = file.split("/")
			pmid = pmid[-1]
			pmid = pmid.split("_")
			pmid = pmid[0]

			## get date
			date = get_date_from_meta_save(str(run_folder)+"/meta/"+str(pmid)+".csv")

			## initialise dict
			if(date not in date_to_techniques_to_count.keys()):
				date_to_techniques_to_count[date] = {}
			if(date not in date_to_category_to_techniques_to_count.keys()):
				date_to_category_to_techniques_to_count[category][date] = {}

			abstract = open(file, "r")
			abstract_in_line = ""
			for line in abstract:
				abstract_in_line += line
			abstract.close()

			abstract_in_array = abstract_in_line.split(" ")

			cmpt = 0
			for word in abstract_in_array:

				## t-test
				if(word == "t-test"):
					if("t-test" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["t-test"] = 1
					else:
						category_to_techniques[str(category)]["t-test"] += 1

					## get information by year
					if("t-test" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["t-test"] = 1
					else:
						date_to_techniques_to_count[date]["t-test"] += 1

					## get information by year and category
					if("t-test" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["t-test"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["t-test"] += 1

				elif(word == "t" and cmpt + 1 < len(abstract_in_array)):
					if(abstract_in_array[cmpt+1] in ["test", "tests"]):
						if("t-test" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["t-test"] = 1
						else:
							category_to_techniques[str(category)]["t-test"] += 1

						## get information by year
						if("t-test" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["t-test"] = 1
						else:
							date_to_techniques_to_count[date]["t-test"] += 1

						## get information by year and category
						if("t-test" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["t-test"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["t-test"] += 1


				## regression
				##    - logistic
				##    - cox
				##    - multivariate
				##    - univariate
				##    - linear
				##    - tree
				##    - Poisson
				if(word in ["regression", "Regression"] and cmpt-1 >= 0):

					## logistic
					if(abstract_in_array[cmpt-1] in ["logistic", "Logistic", "logistical", "Logistical"]):
						if("logistic regression" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["logistic regression"] = 1
						else:
							category_to_techniques[str(category)]["logistic regression"] += 1

						## get information by year
						if("logistic regression" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["logistic regression"] = 1
						else:
							date_to_techniques_to_count[date]["logistic regression"] += 1

						## get information by year and category
						if("logistic regression" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["logistic regression"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["logistic regression"] += 1

					## multivariate
					elif(abstract_in_array[cmpt-1] in ["multivariate", "Multivariate", "multiple", "Multiple"]):
						if("multivariate regression" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["multivariate regression"] = 1
						else:
							category_to_techniques[str(category)]["multivariate regression"] += 1

						## get information by year
						if("multivariate regression" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["multivariate regression"] = 1
						else:
							date_to_techniques_to_count[date]["multivariate regression"] += 1

						## get information by year and category
						if("multivariate regression" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["multivariate regression"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["multivariate regression"] += 1
					
					## univariate
					elif(abstract_in_array[cmpt-1] in ["simple", "Simple", "univariate", "Univariate"]):
						if("univariate regression" not in category_to_techniques[str(category)]):
							category_to_techniques[str(category)]["univariate regression"] = 1
						else:
							category_to_techniques[str(category)]["univariate regression"] += 1

						## get information by year
						if("univariate regression" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["univariate regression"] = 1
						else:
							date_to_techniques_to_count[date]["univariate regression"] += 1

						## get information by year and category
						if("univariate regression" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["univariate regression"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["univariate regression"] += 1
					

					## linear
					elif(abstract_in_array[cmpt-1] in ["Linear", "linear"]):
						if("linear regression" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["linear regression"] = 1
						else:
							category_to_techniques[str(category)]["linear regression"] += 1

						## get information by year
						if("linear regression" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["linear regression"] = 1
						else:
							date_to_techniques_to_count[date]["linear regression"] += 1

						## get information by year and category
						if("linear regression" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["linear regression"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["linear regression"] += 1
					

					## cox
					elif(abstract_in_array[cmpt-1] in ["Cox", "cox", "Cox's", "cox's"]):
						if("Cox regression" not in category_to_techniques["Diagnostic"].keys()):
							category_to_techniques[str(category)]["Cox regression"] = 1
						else:
							category_to_techniques[str(category)]["Cox regression"] += 1

						## get information by year
						if("Cox regression" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["Cox regression"] = 1
						else:
							date_to_techniques_to_count[date]["Cox regression"] += 1

						## get information by year and category
						if("Cox regression" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["Cox regression"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["Cox regression"] += 1

					## proportion hazard regression model
					elif(abstract_in_array[cmpt-1] in ["hazard", "hazards"]):
						if(abstract_in_array[cmpt-2] in ["proportion", "proportional"] and abstract_in_array[cmpt+1] in ["analysis", "model"]):
							if("proportion hazard regression model" not in category_to_techniques[str(category)].keys()):
								category_to_techniques[str(category)]["proportion hazard regression model"] = 1
							else:
								category_to_techniques[str(category)]["proportion hazard regression model"] += 1
					
							## get information by year
							if("proportion hazard regression model" not in date_to_techniques_to_count[date].keys()):
								date_to_techniques_to_count[date]["proportion hazard regression model"] = 1
							else:
								date_to_techniques_to_count[date]["proportion hazard regression model"] += 1

							## get information by year and category
							if("proportion hazard regression model" not in date_to_category_to_techniques_to_count[category][date].keys()):
								date_to_category_to_techniques_to_count[category][date]["proportion hazard regression model"] = 1
							else:
								date_to_category_to_techniques_to_count[category][date]["proportion hazard regression model"] += 1

					## regression tree
					elif(abstract_in_array[cmpt+1] == "tree"):
						if("regression tree" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["regression tree"] = 1
						else:
							category_to_techniques[str(category)]["regression tree"] += 1

						## get information by year
						if("regression tree" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["regression tree"] = 1
						else:
							date_to_techniques_to_count[date]["regression tree"] += 1

						## get information by year and category
						if("regression tree" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["regression tree"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["regression tree"] += 1


					## Poisson regression
					elif(abstract_in_array[cmpt-1] in ["Poisson", "poisson"]):
						if("Poisson regression" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["Poisson regression"] = 1
						else:
							category_to_techniques[str(category)]["Poisson regression"] += 1

						## get information by year
						if("Poisson regression" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["Poisson regression"] = 1
						else:
							date_to_techniques_to_count[date]["Poisson regression"] += 1

						## get information by year and category
						if("Poisson regression" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["Poisson regression"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["Poisson regression"] += 1

					elif(abstract_in_array[cmpt+1] in ["analysis", "test", "tests"]):
						if("regression analysis" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["regression analysis"] = 1
						else:
							category_to_techniques[str(category)]["regression analysis"] += 1

						## get information by year
						if("regression analysis" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["regression analysis"] = 1
						else:
							date_to_techniques_to_count[date]["regression analysis"] += 1

						## get information by year and category
						if("regression analysis" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["regression analysis"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["regression analysis"] += 1

				## Cox's hazard model
				elif(word in ["Cox's", "cox's", "cox", "Cox"] and abstract_in_array[cmpt+1] in ["proportional", "hazards", "hazard", "model", "models"]):
					if("proportion hazard regression model" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["proportion hazard regression model"] = 1
					else:
						category_to_techniques[str(category)]["proportion hazard regression model"] += 1

					## get information by year
					if("proportion hazard regression model" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["proportion hazard regression model"] = 1
					else:
						date_to_techniques_to_count[date]["proportion hazard regression model"] += 1

					## get information by year and category
					if("proportion hazard regression model" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["proportion hazard regression model"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["proportion hazard regression model"] += 1


				## clustering
				elif(word in ["clustering", "Clustering"]):
					if(abstract_in_array[cmpt-1] in ["Hierarchical", "hierarchical"]):
						if("hierarchical clustering" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["hierarchical clustering"] = 1
						else:
							category_to_techniques[str(category)]["hierarchical clustering"] += 1

						## get information by year
						if("hierarchical clustering" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["hierarchical clustering"] = 1
						else:
							date_to_techniques_to_count[date]["hierarchical clustering"] += 1

						## get information by year and category
						if("hierarchical clustering" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["hierarchical clustering"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["hierarchical clustering"] += 1


					else:
						if("clustering" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["clustering"] = 1
						else:
							category_to_techniques[str(category)]["clustering"] += 1

						## get information by year
						if("clustering" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["clustering"] = 1
						else:
							date_to_techniques_to_count[date]["clustering"] += 1

						## get information by year and category
						if("clustering" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["clustering"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["clustering"] += 1

				## tree
				elif(word in ["tree", "Tree"]):
					if(abstract_in_array[cmpt-1] in ["decision", "Decision"]):
						if("decision tree" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["decision tree"] = 1
						else:
							category_to_techniques[str(category)]["decision tree"] += 1

						## get information by year
						if("decision tree" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["decision tree"] = 1
						else:
							date_to_techniques_to_count[date]["decision tree"] += 1

						## get information by year and category
						if("decision tree" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["decision tree"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["decision tree"] += 1

				## random forest
				elif(word in ["forest", "Forest"]):
					if(abstract_in_array[cmpt-1] in ["random", "Random"]):
						if("random forest" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["random forest"] = 1
						else:
							category_to_techniques[str(category)]["random forest"] += 1

						## get information by year
						if("random forest" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["random forest"] = 1
						else:
							date_to_techniques_to_count[date]["random forest"] += 1

						## get information by year and category
						if("random forest" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["random forest"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["random forest"] += 1

				## artificial neural network
				elif(word in ["neural", "Neural"]):
					if(abstract_in_array[cmpt+1] in ["network", "networks"] and (abstract_in_array[cmpt-1] in ["artificial", "Artificial"] or abstract_in_array[cmpt+2] in ["algorithm", "algorithms"])):
						if("artificial neural network" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["artificial neural network"] = 1
						else:
							category_to_techniques[str(category)]["artificial neural network"] += 1

						## get information by year
						if("artificial neural network" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["artificial neural network"] = 1
						else:
							date_to_techniques_to_count[date]["artificial neural network"] += 1

						## get information by year and category
						if("artificial neural network" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["artificial neural network"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["artificial neural network"] += 1

				## machine learning
				## support vector machine
				elif(word in ["machine", "Machine"]):
					if(abstract_in_array[cmpt+1] in ["learning", "Learning"]):
						if("machine learning" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["machine learning"] = 1
						else:
							category_to_techniques[str(category)]["machine learning"] += 1

						## get information by year
						if("machine learning" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["machine learning"] = 1
						else:
							date_to_techniques_to_count[date]["machine learning"] += 1

						## get information by year and category
						if("machine learning" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["machine learning"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["machine learning"] += 1


					elif(abstract_in_array[cmpt-1] == "vector" and abstract_in_array[cmpt-2] in ["support", "Support"]):
						if("support vector machine" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["support vector machine"] = 1
						else:
							category_to_techniques[str(category)]["support vector machine"] += 1

						## get information by year
						if("support vector machine" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["support vector machine"] = 1
						else:
							date_to_techniques_to_count[date]["support vector machine"] += 1

						## get information by year and category
						if("support vector machine" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["support vector machine"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["support vector machine"] += 1


				elif(word in ["machine-learning", "Machine-learning"]):
					if("machine learning" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["machine learning"] = 1
					else:
						category_to_techniques[str(category)]["machine learning"] += 1

					## get information by year
					if("machine learning" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["machine learning"] = 1
					else:
						date_to_techniques_to_count[date]["machine learning"] += 1

					## get information by year and category
					if("machine learning" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["machine learning"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["machine learning"] += 1

				## Wilcoxon test
				elif(word in ["Wilcoxon", "wilcoxon"]):
					if("Wilcoxon test" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["Wilcoxon test"] = 1
					else:
						category_to_techniques[str(category)]["Wilcoxon test"] += 1

					## get information by year
					if("Wilcoxon test" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["Wilcoxon test"] = 1
					else:
						date_to_techniques_to_count[date]["Wilcoxon test"] += 1

					## get information by year and category
					if("Wilcoxon test" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["Wilcoxon test"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["Wilcoxon test"] += 1

				## PCA
				elif(word in ["Principal", "principal"]):
					if(abstract_in_array[cmpt+1] == "component" and abstract_in_array[cmpt+2] == "analysis"):
						if("PCA" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["PCA"] = 1
						else:
							category_to_techniques[str(category)]["PCA"] += 1

						## get information by year
						if("PCA" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["PCA"] = 1
						else:
							date_to_techniques_to_count[date]["PCA"] += 1

						## get information by year and category
						if("PCA" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["PCA"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["PCA"] += 1

				## chi-squared
				elif(word in ["chi-squared", "Chi-squared", "Chi-sqare", "ch-square"]):
					if("chi-squared" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["chi-squared"] = 1
					else:
						category_to_techniques[str(category)]["chi-squared"] += 1

					## get information by year
					if("chi-squared" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["chi-squared"] = 1
					else:
						date_to_techniques_to_count[date]["chi-squared"] += 1

					## get information by year and category
					if("chi-squared" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["chi-squared"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["chi-squared"] += 1

				## Fisher's test
				elif(word in ["Fisher's", "Fisher"]):
					if("Fisher test" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["Fisher test"] = 1
					else:
						category_to_techniques[str(category)]["Fisher test"] += 1

					## get information by year
					if("Fisher test" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["Fisher test"] = 1
					else:
						date_to_techniques_to_count[date]["Fisher test"] += 1

					## get information by year and category
					if("Fisher test" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["Fisher test"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["Fisher test"] += 1


				## analysis
				## - multivariate
				## - univariate
				## - discriminant
				## - bioinformatics
				elif(word in ["analysis", "Analysis"]):

					if(abstract_in_array[cmpt-1] in ["multivariate", "Multivariate"]):
						if("multivariate analysis" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["multivariate analysis"] = 1
						else:
							category_to_techniques[str(category)]["multivariate analysis"] += 1

						## get information by year
						if("multivariate analysis" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["multivariate analysis"] = 1
						else:
							date_to_techniques_to_count[date]["multivariate analysis"] += 1

						## get information by year and category
						if("multivariate analysis" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["multivariate analysis"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["multivariate analysis"] += 1

					elif(abstract_in_array[cmpt-1] in ["univariate", "Univariate"]):
						if("univariate analysis" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["univariate analysis"] = 1
						else:
							category_to_techniques[str(category)]["univariate analysis"] += 1

						## get information by year
						if("univariate analysis" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["univariate analysis"] = 1
						else:
							date_to_techniques_to_count[date]["univariate analysis"] += 1

						## get information by year and category
						if("univariate analysis" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["univariate analysis"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["univariate analysis"] += 1

					elif(abstract_in_array[cmpt-1] in ["discriminant", "Discriminant"]):
						if("discriminant analysis" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["discriminant analysis"] = 1
						else:
							category_to_techniques[str(category)]["discriminant analysis"] += 1

						## get information by year
						if("discriminant analysis" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["discriminant analysis"] = 1
						else:
							date_to_techniques_to_count[date]["discriminant analysis"] += 1

						## get information by year and category
						if("discriminant analysis" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["discriminant analysis"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["discriminant analysis"] += 1

					elif(abstract_in_array[cmpt-1] in ["bioinformatics", "Bioinformatics", "bioinformatic", "Bioinformatic"]):
						if("bioinformatics analysis" not in category_to_techniques[str(category)].keys()):
							category_to_techniques[str(category)]["bioinformatics analysis"] = 1
						else:
							category_to_techniques[str(category)]["bioinformatics analysis"] += 1

						## get information by year
						if("bioinformatics analysis" not in date_to_techniques_to_count[date].keys()):
							date_to_techniques_to_count[date]["bioinformatics analysis"] = 1
						else:
							date_to_techniques_to_count[date]["bioinformatics analysis"] += 1

						## get information by year and category
						if("bioinformatics analysis" not in date_to_category_to_techniques_to_count[category][date].keys()):
							date_to_category_to_techniques_to_count[category][date]["bioinformatics analysis"] = 1
						else:
							date_to_category_to_techniques_to_count[category][date]["bioinformatics analysis"] += 1

				## GLM (generalized linear model)
				elif(word in ["GLM", "(GLM)", "(GLM, ", "GLM)"]):
					if("GLM" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["GLM"] = 1
					else:
						category_to_techniques[str(category)]["GLM"] += 1

					## get information by year
					if("GLM" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["GLM"] = 1
					else:
						date_to_techniques_to_count[date]["GLM"] += 1

					## get information by year and category
					if("GLM" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["GLM"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["GLM"] += 1

				## mixed models
				elif(word in ["models", "model"] and abstract_in_array[cmpt-1] in ["mixed", "Mixed"]):
					if("mixed models" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["mixed models"] = 1
					else:
						category_to_techniques[str(category)]["mixed models"] += 1

					## get information by year
					if("mixed models" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["mixed models"] = 1
					else:
						date_to_techniques_to_count[date]["mixed models"] += 1

					## get information by year and category
					if("mixed models" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["mixed models"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["mixed models"] += 1


				## normalization
				elif(word in ["Normalization", "normalization"]):
					if("normalization" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["normalization"] = 1
					else:
						category_to_techniques[str(category)]["normalization"] += 1

					## get information by year
					if("normalization" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["normalization"] = 1
					else:
						date_to_techniques_to_count[date]["normalization"] += 1

					## get information by year and category
					if("normalization" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["normalization"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["normalization"] += 1

				## k mean
				elif(word in ["kmean", "Kmean", "K-mean", "K-mean-clustering"]):
					if("k mean" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["k mean"] = 1
					else:
						category_to_techniques[str(category)]["k mean"] += 1

					## get information by year
					if("k mean" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["k mean"] = 1
					else:
						date_to_techniques_to_count[date]["k mean"] += 1

					## get information by year and category
					if("k mean" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["k mean"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["k mean"] += 1

				elif(word in ["k", "K"] and abstract_in_array[cmpt+1] in ["mean", "means", "Mean", "Means"]):
					if("k mean" not in category_to_techniques[str(category)].keys()):
						category_to_techniques[str(category)]["k mean"] = 1
					else:
						category_to_techniques[str(category)]["k mean"] += 1

					## get information by year
					if("k mean" not in date_to_techniques_to_count[date].keys()):
						date_to_techniques_to_count[date]["k mean"] = 1
					else:
						date_to_techniques_to_count[date]["k mean"] += 1

					## get information by year and category
					if("k mean" not in date_to_category_to_techniques_to_count[category][date].keys()):
						date_to_category_to_techniques_to_count[category][date]["k mean"] = 1
					else:
						date_to_category_to_techniques_to_count[category][date]["k mean"] += 1

				cmpt += 1

	## Display details of the returned structure
	if(display_details):
		total = 119 + 604 +726 +19
		detected = 0
		for key in category_to_techniques.keys():
			print "=> " +str(key) +" <="
			for tech in category_to_techniques[key].keys():
				print "    -> "+str(tech) +" : " +str(category_to_techniques[key][tech])
				detected += category_to_techniques[key][tech]
		print "=> "+str(detected) +" / " + str(total) +" || [ "+str(float(float(detected)/float(total))*100) +" % ]"


	#print date_to_category_to_techniques_to_count

	for key in date_to_category_to_techniques_to_count.keys():
		print key 
		print date_to_category_to_techniques_to_count[key]

	## return dictionnary
	return (category_to_techniques, date_to_techniques_to_count)



def generate_techniques_figures(category_to_techniques_to_count):
	##
	## Generate 8 figures from techniques count data
	## category_to_techniques_to_count is a dictionnary obtain by the
	## retrieve_techniques() function.
	##
	## save generated figures in images folder.
	##

	## Define category of analysis
	regression_analysis = ["logistic regression", "cox regression", "multivariate regression",
	"univariate regression", "linear regression", "Poisson regression", "regression tree", "regression analysis"]
	machine_learning_analysis = ["random forest", "artificial neural network", "support vector machine", "machine learning",
	"GLM", "mixed models", "k mean", "clustering", "hierarchical clustering", "decision tree"]
	other_analysis = ["t-test", "Wilcoxon test", "PCA", "chi-squared", "multivariate analysis", "univariate analysis", "discriminant analysis",
	"bioinformatic analysis", "normalization"]

	## Detailed histogramm
	Total_number_of_techniques = 0
	total_regression_techniques = 0
	total_machine_learning_techniques = 0
	total_other_techniques = 0
	global_techniques_data = {}
	for category in category_to_techniques_to_count.keys():

		regression_techniques = 0
		machine_learning_techniques = 0
		other_techniques = 0
		number_of_techniques = 0
		for tech in category_to_techniques_to_count[category].keys():
			number_of_techniques += category_to_techniques_to_count[category][tech]
			Total_number_of_techniques += category_to_techniques_to_count[category][tech]

			if(tech not in global_techniques_data.keys()):
				global_techniques_data[tech] = category_to_techniques_to_count[category][tech]
			else:
				global_techniques_data[tech] += category_to_techniques_to_count[category][tech]

			if(tech in regression_analysis):
				regression_techniques += category_to_techniques_to_count[category][tech]
				total_regression_techniques += category_to_techniques_to_count[category][tech]
			elif(tech in machine_learning_analysis):
				machine_learning_techniques += category_to_techniques_to_count[category][tech]
				total_machine_learning_techniques += category_to_techniques_to_count[category][tech]
			elif(tech in other_analysis):
				other_techniques += category_to_techniques_to_count[category][tech]
				total_other_techniques += category_to_techniques_to_count[category][tech]

		techniques_to_count = category_to_techniques_to_count[category]
		for tech in techniques_to_count.keys():
			techniques_to_count[tech] = float(techniques_to_count[tech]) / float(number_of_techniques) *100


		## Detailed Histogram
		plt.bar(techniques_to_count.keys(), techniques_to_count.values(), color='b', align='center', width=0.3)
		plt.xticks(rotation=45)
		plt.savefig("images/techniques_histogram_"+str(category)+".png")
		plt.close()

		## Pie chart
		regression_techniques = float(regression_techniques) / float(number_of_techniques) * 100
		machine_learning_techniques = float(machine_learning_techniques) / float(number_of_techniques) * 100
		other_techniques = float(other_techniques) / float(number_of_techniques) * 100
		x_vector = [regression_techniques, machine_learning_techniques, other_techniques]
		labels = ["regression techniques", "machine learning techniques", "other techniques"]
		plt.pie(x_vector, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
		plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
		plt.savefig("images/techniques_pie_"+str(category)+".png")
		plt.close()

	## Global histogram
	plt.bar(global_techniques_data.keys(), global_techniques_data.values(), color='b', align='center', width=0.3)
	plt.xticks(rotation=45)
	plt.savefig("images/techniques_histogram_global.png")
	plt.close()

	## Global pie chart
	total_regression_techniques = float(total_regression_techniques) / float(Total_number_of_techniques) * 100
	total_machine_learning_techniques = float(total_machine_learning_techniques) / float(Total_number_of_techniques) * 100
	total_other_techniques = float(total_other_techniques) / float(Total_number_of_techniques) * 100
	x_vector = [total_regression_techniques, total_machine_learning_techniques, total_other_techniques]
	labels = ["total regression techniques", "total machine learning techniques", "total other techniques"]
	plt.pie(x_vector, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
	plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	plt.savefig("images/techniques_pie_global.png")
	plt.close()




def get_cohorte_size_for_category():
	##
	## Get the count of patients parsed from abstract for each 
	## each category.
	##
	## return a dictionnary
	##

	## retrieve data
	category_list = ["Diagnostic", "Therapeutic", "Unclassified", "Modelisation"]
	category_to_size = {}
	category_to_size["Retrieved"] = 0
	for category in category_list:
		abstract_list = glob.glob("articles_classification/"+str(category)+"/*")
		category_to_size[category] = 0
		for abstract in abstract_list:
			size = get_cohorte_size(abstract)
			if(size != "NA"):
				category_to_size[category] += size
				category_to_size["Retrieved"] += 1
	

	for key in category_to_size.keys():
		print "[DATA] => "+str(key) +" : " +str(category_to_size[key])

	return category_to_size


def generate_cohorte_size_figures(run_folder):
	##
	## Generate 3 figures about the evolution of 
	## the sizes of cohorte, save the image in
	## the images folder:
	##    - category_sizes_histogram.png
	##    - count_cohorte_size_evolution.png
	##    - median_cohorte_size_evolution.png
	##
	## run_folder is the name of the run_folder, 
	## should contain at least:
	##    - abstract directory
	##    - meta directory
	##
	##

	## Figure 1
	## Histogram with category
	category_to_size = get_cohorte_size_for_category()
	total_number_of_articles = 0
	for value in category_to_size.values():
		total_number_of_articles += value
	for key in category_to_size.keys():
		category_to_size[key] = float(category_to_size[key]) / float(total_number_of_articles) * 100
	plt.bar(category_to_size.keys(), category_to_size.values(), color='b', align='center', width=0.3)
	plt.xticks(rotation=45)
	plt.savefig("images/category_sizes_histogram.png")
	plt.close()

	## Figure 2 and 3
	## Evolution curve
	year_to_pmid = {}
	for meta_file in glob.glob(run_folder+"/meta/*.csv"):
		pmid = meta_file.split("/")
		pmid = pmid[-1]
		pmid = pmid.split(".")
		pmid = pmid[0]
		year = get_date_from_meta_save(meta_file)
		if(year not in year_to_pmid.keys()):
			year_to_pmid[year] = []
			year_to_pmid[year].append(pmid)
		else:
			year_to_pmid[year].append(pmid)

	## -> Global count evolution
	year_to_patient = {}
	for year in year_to_pmid.keys():
		if(int(year) < 2018):
			number_of_patients = 0
			for pmid in year_to_pmid[year]:
				abstract_file = run_folder+"/abstract/"+str(pmid)+"_abstract.txt"
				patients_retrieved = get_cohorte_size(abstract_file)
				if(patients_retrieved != "NA"):
					number_of_patients += int(patients_retrieved)
			year_to_patient[year] = number_of_patients
	ordered_data = collections.OrderedDict(sorted(year_to_patient.items()))
	x = []
	for elt in ordered_data.keys():
		x.append(int(elt))
	y = ordered_data.values()
	m,b = np.polyfit(x, y, 1)
	print "[INFO] => coeff : "+str(m)+" * x + "+str(b)
	fit = np.polyfit(x, y, 1)
	fit_fn = np.poly1d(fit) 
	plt.plot(x, y, 'b-*', label="cohorte sizes")
	plt.plot(x, fit_fn(x), '--k', label="linear regression")
	plt.legend()
	plt.ylim(ymin=0)
	plt.show()
	#plt.plot(ordered_data.keys(), ordered_data.values())
	plt.savefig("images/count_cohorte_size_evolution.png")
	plt.close()

	## -> Median evolution
	year_to_median = {}
	for year in year_to_pmid.keys():
		if(int(year) < 2018):
			cohort_size = []
			for pmid in year_to_pmid[year]:
				abstract_file = run_folder+"/abstract/"+str(pmid)+"_abstract.txt"
				patients_retrieved = get_cohorte_size(abstract_file)
				if(patients_retrieved != "NA"):
					cohort_size.append(patients_retrieved)
			cohorte_median = np.median(cohort_size)
			year_to_median[year] = cohorte_median
	ordered_data = collections.OrderedDict(sorted(year_to_median.items()))
	plt.plot(ordered_data.keys(), ordered_data.values())
	plt.savefig("images/median_cohorte_size_evolution.png")
	plt.close()







def get_techniques_proportions(category_to_techniques_to_count):
	##
	##
	## Generate a dictionnary with proportion data for the
	## differents techniques retrieve in abstracts
	## category_to_techniques_to_count is a dictionnary obtain by the
	## retrieve_techniques() function.
	##
	## return a dictionnary
	##


	## Define category of analysis
	regression_analysis = ["logistic regression", "cox regression", "multivariate regression",
	"univariate regression", "linear regression", "Poisson regression", "regression tree", "regression analysis"]
	machine_learning_analysis = ["random forest", "artificial neural network", "support vector machine", "machine learning",
	"GLM", "mixed models", "k mean", "clustering", "hierarchical clustering", "decision tree"]
	other_analysis = ["t-test", "Wilcoxon test", "PCA", "chi-squared", "multivariate analysis", "univariate analysis", "discriminant analysis",
	"bioinformatic analysis", "normalization"]

	## Detailed histogramm
	Total_number_of_techniques = 0
	total_regression_techniques = 0
	total_machine_learning_techniques = 0
	total_other_techniques = 0
	global_techniques_data = {}
	category_to_proportion = {}
	for category in category_to_techniques_to_count.keys():

		category_to_proportion[category] = {}

		regression_techniques = 0
		machine_learning_techniques = 0
		other_techniques = 0
		number_of_techniques = 0
		for tech in category_to_techniques_to_count[category].keys():
			number_of_techniques += category_to_techniques_to_count[category][tech]
			Total_number_of_techniques += category_to_techniques_to_count[category][tech]

			if(tech not in global_techniques_data.keys()):
				global_techniques_data[tech] = category_to_techniques_to_count[category][tech]
			else:
				global_techniques_data[tech] += category_to_techniques_to_count[category][tech]

			if(tech in regression_analysis):
				regression_techniques += category_to_techniques_to_count[category][tech]
				total_regression_techniques += category_to_techniques_to_count[category][tech]
			elif(tech in machine_learning_analysis):
				machine_learning_techniques += category_to_techniques_to_count[category][tech]
				total_machine_learning_techniques += category_to_techniques_to_count[category][tech]
			elif(tech in other_analysis):
				other_techniques += category_to_techniques_to_count[category][tech]
				total_other_techniques += category_to_techniques_to_count[category][tech]

		techniques_to_count = category_to_techniques_to_count[category]
		for tech in techniques_to_count.keys():
			techniques_to_count[tech] = float(techniques_to_count[tech]) / float(number_of_techniques) *100


		## proportion by category of techniques
		regression_techniques = float(regression_techniques) / float(number_of_techniques) * 100
		machine_learning_techniques = float(machine_learning_techniques) / float(number_of_techniques) * 100
		other_techniques = float(other_techniques) / float(number_of_techniques) * 100
		category_to_proportion[category]["regression"] = regression_techniques
		category_to_proportion[category]["machineLearning"] = machine_learning_techniques
		category_to_proportion[category]["other"] = other_techniques

	## global proportions
	total_regression_techniques = float(total_regression_techniques) / float(Total_number_of_techniques) * 100
	total_machine_learning_techniques = float(total_machine_learning_techniques) / float(Total_number_of_techniques) * 100
	total_other_techniques = float(total_other_techniques) / float(Total_number_of_techniques) * 100	
	category_to_proportion["all"] = {}
	category_to_proportion["all"]["regression"] = regression_techniques
	category_to_proportion["all"]["machineLearning"] = machine_learning_techniques
	category_to_proportion["all"]["other"] = other_techniques

	return category_to_proportion


def generate_tech_evolution_figures(year_to_tech):
	##
	## generate graph evolution of techniques (by count in abstract)
	## over the last decade
	##
	## year_to_tech is a dictionnary return by 
	## the retrieve_techniques functions
	##
	## save figure as images/count_techniques_evolution.png
	##
	##

	## Define category of analysis
	regression_analysis = ["logistic regression", "cox regression", "multivariate regression",
	"univariate regression", "linear regression", "Poisson regression", "regression tree", "regression analysis"]
	machine_learning_analysis = ["random forest", "artificial neural network", "support vector machine", "machine learning",
	"GLM", "mixed models", "k mean", "clustering", "hierarchical clustering", "decision tree"]
	other_analysis = ["t-test", "Wilcoxon test", "PCA", "chi-squared", "multivariate analysis", "univariate analysis", "discriminant analysis",
	"bioinformatic analysis", "normalization"]

	year_to_count = {}

	for year in year_to_tech.keys():
		year_to_count[year] = {}
				
		regression_techniques = 0
		machine_learning_techniques = 0
		other_techniques = 0
		
		for tech in year_to_tech[year].keys():
			
			if(tech in regression_analysis):
				regression_techniques += year_to_tech[year][tech]
			elif(tech in machine_learning_analysis):
				machine_learning_techniques += year_to_tech[year][tech]
			elif(tech in other_analysis):
				other_techniques += year_to_tech[year][tech]

		year_to_count[year]["regression"] = regression_techniques
		year_to_count[year]["machine_learning"] = machine_learning_techniques
		year_to_count[year]["other"] = other_techniques


	## create the figure
	y_vector = []
	for year in year_to_count.keys():
		if(int(year) < 2018):
			y_vector.append(year)
	y_vector = sorted(y_vector)
	r_vector = []
	for year in y_vector:
		r_vector.append(year_to_count[year]["regression"])
	m_vector = []
	for year in y_vector:
		m_vector.append(year_to_count[year]["machine_learning"])
	o_vector = []
	for year in y_vector:
		o_vector.append(year_to_count[year]["other"])

	plt.plot(y_vector, r_vector, 'r--', label="regression")
	plt.plot(y_vector, m_vector, 'b-*', label="machine learning")
	plt.plot(y_vector, o_vector, 'g-^', label="other")
	plt.legend()
	plt.savefig("images/count_techniques_evolution.png")
	plt.close()



def get_cohorte_size_for_year(year, run_folder):
	##
	## Get the cohorte size (total count of patients and
	## median size) for a given year
	##
	## year is an int, the year of interest,
	## run_folder is the run_folder
	##
	## return a tuple (total_count, median)
	##


	total_size = 0
	size_median = 0
	sizes_list = []

	category_list = ["Diagnostic", "Therapeutic", "Unclassified", "Modelisation"]
	for category in category_list:
		abstract_list = glob.glob("articles_classification/"+str(category)+"/*")
		for abstract in abstract_list:
			abstract_in_array = abstract.split("/")
			abstract_in_array = abstract_in_array[-1]
			pmid = abstract_in_array.split("_")
			pmid = pmid[0]
			meta_file = run_folder+"/meta/"+str(pmid)+".csv"
			year_retrieved = get_date_from_meta_save(meta_file)

			if(int(year) == int(year_retrieved)):
				size = get_cohorte_size(abstract)
				if(size != "NA"):
					total_size += int(size)
					sizes_list.append(int(size))

	if(len(sizes_list) > 0):
		size_median = np.median(sizes_list)

	return (total_size, size_median)
"""
TEST SPACE
"""

#run_folder = "SAVE/run_7h:20m:26:1"
#run_folder = "SAVE/run_21h:31m:29:1"
#generate_cohorte_size_figures(run_folder)

#truc, machin = retrieve_techniques(run_folder, False)

run_folder = "SAVE/run_21h:31m:29:1"
#truc = get_cohorte_size_for_year(2008, run_folder)
#machin = get_cohorte_size_for_year(2017, run_folder)
#print truc
#print machin

#generate_tech_evolution_figures(machin)

#get_count_of_articles_type_for_each_disease()

"""
x = [1,2,3,4]
y = [3,8,7,12] 
m,b = np.polyfit(x, y, 1)

fit = np.polyfit(x,y,1)
fit_fn = np.poly1d(fit) 
# fit_fn is now a function which takes in x and returns an estimate for y

plt.plot(x,y, 'yo', x, fit_fn(x), '--k')
plt.xlim(0, 5)
plt.ylim(0, 12)
plt.show()
"""

generate_cohorte_size_figures(run_folder)

"""
print "------[TEST SPACE]------\n"
machin = get_ListOfDirectInteraction("P43403", "P06239")
print "-------------------------------------------------------"
print machin
"""





#plot_pulbications_years("SAVE/run_2/meta")
"""
log_file =  "SAVE/run_14h:1m:25:1/bibotlite.log"
run_folder = "SAVE/run_14h:1m:25:1"
found_cmpt = 0
abstract_list = glob.glob(run_folder+"/abstract/*_abstract.txt")
"""
"""
for abstract in abstract_list:
	data = open(abstract, "r")
	for line in data:
		print line
	data.close()
"""
"""
for abstract_file in abstract_list:
	print "-----------------------"
	size = get_cohorte_size(abstract_file)
	if(size != "NA"):
		found_cmpt += 1
		print "=> Detected : " +str(size)

print "=> "+str(found_cmpt) +" / "+str(len(abstract_list)) +" [" +str(float(float(found_cmpt)/float(len(abstract_list))*100)) +"]"
"""







"""
diagnostic_abstracts = ["abstract/29363510_abstract.txt", ]
therapeutic_abstracts = ["abstract/29359591_abstract.txt", "25672757_abstract.txt"]
modelisation_abstracts = ["abstract/29333443_abstract.txt"]
abstract = "abstract/25573986_abstract.txt"

import shutil

class_to_count = {"Diagnostic":0, "Therapeutic":0, "Modelisation":0, "Unclassified":0}
for abstract in glob.glob("abstract/*_abstract.txt"):
	theme = get_article_domain(abstract)
	class_to_count[theme] += 1
	pmid = abstract.split("/")
	pmid = pmid[-1]
	shutil.copy(abstract, "articles_classification/"+theme+"/"+pmid)

print class_to_count
"""

#get_all_subjects_from_abstract("abstract")

#describe_articles_type("SAVE/run_2")

#item_list = ["neural network", "machine learning", "machine", "classification", "modelisation", "Sjogren", "random forest", "kmean",
#"statistic", "bioinformatic", "big data", "artificial intelligence", "diagnostic", "patients", "learning", "prediction", "cluster", "clusterring",
#"computer", "lupus", "RA", "IA", "sjogren"]
#plot_word_evolution(item_list, "SAVE/run_2")

"""
m = re.search(r"(?P<number>\w+) patients", "There are 257 patients in this study.")
if(m is not None):
	print m.group('number')
"""

"""
pmid_list = []
pmid_file = open("/home/perceval/Workspace/publications/immuno_review/articles/manually_retrieved/MANIFEST.txt", "r")
for line in pmid_file:
	line = line.replace("\n", "")
	pmid_list.append(line)
pmid_file.close()
for pmid in pmid_list:
	try:
		abstract = fetch_abstract(pmid)
		save_abstract(abstract, "abstract_1/abstract/"+str(pmid)+".txt")
	except:
		print "FAILED"
"""

"""
save_path = "SAVE/run_1/abstract/*.txt"
old_path = "abstract_1/abstract/*.txt"
run_2 = "abstract_2/*.txt"
current_run = "abstract/*.txt"
cmpt = 1
for abstract in glob.glob(current_run):
	size = get_cohorte_size(abstract)
	print size
	cmpt += 1
"""


#k = KEGG(verbose=False)
#truc = k.find("hsa", "zap70")
#pathway = k.get_pathway_by_gene("1956", "hsa")
#print pathway
#k.show_pathway("hsa05218", keggid={"1956": "red"})



#draw_InteractionGraph("P43403", "monTest.sif")
#convert_SifFileToGDFfile("monTest.sif")

#abstract = fetch_abstract(27755966)
#print abstract



"""
list_elementsToCheck = []
list_elementChecked = []
list_elementsToCheck.append("P43403")

for element in list_elementsToCheck:
	if(element not in list_elementChecked):
		machin = get_CuratedInteraction(str(element))
		
		list_elementsToCheck.remove(str(element))
		list_elementChecked.append(str(element))

		for interaction in machin:
			interactionInArray = interaction.split("->")
			print interaction
			if(interactionInArray[1] not in list_elementsToCheck):
				list_elementsToCheck.append(interactionInArray[1])
	else:
		print "->"+str(element) + "already Ckeck"
"""



"""
elementToCheck = "ZAP70"
s = PSICQUIC(verbose=False)
#data = s.query("mint", "ZAP70 AND species:9606")
data = s.query("mint", str(elementToCheck)+" AND species:9606")

for db in data:
	machin = get_interactors(db)
	truc = get_InteractionType(db)
	print truc
"""

	

	

"""
	line1 = db[0]
	line2 = db[1]
	line1InArray = line1.split(":")
	line2InArray = line2.split(":")
	uniprotId_elt1 = line1InArray[1]
	uniprotId_elt2 = line2InArray[1]
	print str(uniprotId_elt1)+" || "+str(uniprotId_elt2)
"""






# Retrieve Article
#test = fetch_abstract(27045581)
#print test



## Test get_ListOfArticles function
"""
print "[+] => Testing get_ListOfArticles function"
machin = get_ListOfArticles("HLA", 100)
for pmid in machin:
	try:
		test = fetch_abstract(pmid)
		print "["+str(pmid)+"]\n"
		print test
	except:
		print "[!] Can't read "+str(pmid)
print "[*] => Test Done"
"""


"""
# test data
test = "Rabbits are dangerous. Rabbits are not dangerous"
print test
# import nltk stuff
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Structure Information
sentences = nltk.sent_tokenize(test)
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]

# Chunking
grammar = "NP: {<DT>?<JJ>*<NN>}"
cp = nltk.RegexpParser(grammar)
for sentence in sentences:
	print sentence
	result = cp.parse(sentence)
	result.draw()
"""

## Test mygene module
"""
mg = mygene.MyGeneInfo()
truc = mg.query('NRAS', size=1)
print truc["hits"][0]
"""