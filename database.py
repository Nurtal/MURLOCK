"""
This file contain function
for the management of MURLOCK
Database
"""


import sqlite3






def createDatabase(name):

	"""
	Create A database for MURLOCK data, i.e:
	
	-> Title of the web page
	-> Sub title of the web page
	-> code in the web page
	-> url of the web page	

	"""
	conn = sqlite3.connect(name)
	cursor = conn.cursor()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS gnolledge(
     		id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     		title TEXT,
     		subtitle TEXT,
     		code TEXT,
		url TEXT
		)
	""")
	conn.commit()
	conn.close()

	return 0


def insertInto(database, title, subtitle, code, url):

	"""
	Insert data into database,
	default table : gnolledge
	"""

	conn = sqlite3.connect(database)
	cursor = conn.cursor()
	cursor.execute("""
	INSERT INTO gnolledge(title, subtitle, code, url) VALUES(?, ?, ?, ?)""", (title, subtitle, code, url))
	conn.commit()
	conn.close()

	return 0

def getDatafromDatabase(database):
	
	"""
	fetch all data from the database
	default table : gnolledge
	"""
	conn = sqlite3.connect(database)
	cursor = conn.cursor()
	
	cursor.execute("""SELECT title, subtitle, code, url FROM gnolledge""")
	result = cursor.fetchall()
	conn.close()

	return result



"""
TEST SPACE
"""

#database = "DATA/database/testDb.db"
#createDatabase("DATA/database/testDb.db")
#insertInto("DATA/database/testDb.db", "myTitle of the death", "really good title", "print hello world", "google.com")
#print getDatafromDatabase(database)



#title = "my title"
#subtitle = "Grmblbmblb"
#code = "print hello world"
#url = "google.com"
#
#name = "DATA/database/testDb.db"
#
#conn = sqlite3.connect(name)
#cursor = conn.cursor()
#cursor.execute("""
#	CREATE TABLE IF NOT EXISTS gnolledge(
#	id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
#	title TEXT,
#	subtitle TEXT,
#	code TEXT,
#	url TEXT
#	)
#""")
#
#conn.commit()
#
#cursor = conn.cursor()
#cursor.execute("""
#INSERT INTO gnolledge(title, subtitle, code, url) VALUES(?, ?, ?, ?)""", (title, subtitle, code, url))
#
#cursor.execute("""SELECT title, subtitle, code, url FROM gnolledge""")
#user1 = cursor.fetchall()
#print(user1)
#
#conn.close()

