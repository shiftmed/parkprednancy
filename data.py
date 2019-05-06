import xlrd
import sqlite3
import time
import math
import datetime
import re
import sys
from flask import jsonify
import json
from pathlib import Path
# the functions which names are preceeded by 'p' are the xls equivalents for the json handling,
# the names should be enough to understand what each function does.

def drop_table(tableName):
    with sqlite3.connect('transactions.db') as connection:
        print tableName
        c = connection.cursor()
        q = """ drop table if exists %s """ % (tableName)
        c.execute(q)
        # q = 'DROP TABLE IF EXISTS ' +tableName + ";'"
        # c.execute(q)
        print "Dropped the table: '"+str(tableName)+"'."
    connection.close()  
    return True


def create_table(tableName):
    with sqlite3.connect('transactions.db') as connection:
        c = connection.cursor()
        q = 'CREATE TABLE {0} (id           INTEGER PRIMARY KEY             AUTOINCREMENT, arrival  Date                NOT NULL, departure     Date                NOT NULL, price         INTEGER)'   
        c.execute(q.format(tableName))
        print "Created the table: '"+tableName+"'."
    connection.close()
    return True

# FOR THE HTML DISPLAY INSIDE THE SELECT DIV in /simulation
def fillDataPicker():
	data = []
	with sqlite3.connect('transactions.db') as connection:
		c = connection.cursor()
		c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
		data = c.fetchall()  
		# data[0] is a config table used by sqlite3
		# print data[1] 
		return data
def p_fillDataPicker():
	data = []
	with sqlite3.connect('pricings.db') as connection:
		c = connection.cursor()
		c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
		data = c.fetchall()  
		# data[0] is a config table used by sqlite3
		# print data[1] 
		return data

def minimalist_xldate_as_datetime(xldate, datemode):
    # datemode: 0 for 1900-based, 1 for 1904-based
	return (datetime.datetime(1899, 12, 30)+ datetime.timedelta(days=xldate + 1462 * datemode))

def getDataSize(tableName):
	connection = sqlite3.connect('transactions.db')
	cursor = connection.cursor()
	rowsQuery = "SELECT Count() FROM %s" % tableName
	cursor.execute(rowsQuery)
	count = cursor.fetchone()[0]
	return count

def p_getDataSize(tableName):
	connection = sqlite3.connect('pricings.db')
	cursor = connection.cursor()
	rowsQuery = "SELECT Count() FROM %s" % tableName
	cursor.execute(rowsQuery)
	count = cursor.fetchone()[0]
	return count

def uploadData(tableName, type):
	# if (tableExists(tableName)) pour la version console
	connection = sqlite3.connect('transactions.db')
	c = connection.cursor()

	q = """INSERT INTO {0} (arrival, departure, price) VALUES (?, ?, ?)"""
	with sqlite3.connect('transactions.db') as connection:
		if type == 0:
			book = xlrd.open_workbook("./data/"+tableName+".xls")
		else:
			book = xlrd.open_workbook("./data/"+tableName+".xlsx")
		# sheet = book.sheet_by_name("source")
		c = connection.cursor()
		
		sheets = book.sheet_names()
		# sheet = book.sheet_by_name("Feuille1")
		for i in range (0,len(sheets)-1):
			sheet = book.sheet_by_name(sheets[i])
			for r in range(15,sheet.nrows-1):
				# get raw data from excel
				dates_excel           	= sheet.cell(r,4).value
				# print dates_excel
				
				arrival_excel		= dates_excel.split('-')[0]
				departure_excel	= dates_excel.split('-')[1]
				price                   		= sheet.cell(r,12).value
				
				arrival_dt 		= datetime.datetime.strptime(arrival_excel,"%m/%d/%Y  %H:%M ")
				departure_dt 		= datetime.datetime.strptime(departure_excel ," %m/%d/%Y %H:%M")

				arrival_time            	= arrival_dt.strftime('%Y-%m-%d %H:%M:%S')
				departure_time		= departure_dt.strftime('%Y-%m-%d %H:%M:%S')

				values = (arrival_time, departure_time, price)
				c.execute(q.format(tableName),values)	
	print "Excel data has been sucessfully uploaded to the database." 

def p_uploadData(tableName, date):
	# if (tableExists(tableName)) pour la version console
	connection = sqlite3.connect('pricings.db')
	c = connection.cursor()
	file_path = "./data/"+str(tableName)+".json"

	q = """INSERT INTO {0} (creation_date, file) VALUES (?, ?)"""
	with sqlite3.connect('pricings.db') as connection:
		print 'in the with'
		c = connection.cursor()
		values = (date, file_path)
		print values
		c.execute(q.format(tableName),values)	
	print "Pricing data has been sucessfully uploaded to the database." 

def tableExists(tableName):
	connection = sqlite3.connect('transactions.db')
	cursor = connection.cursor()

	if cursor.execute("""SELECT * FROM sqlite_master WHERE name ='{0}' and type='table';""".format(tableName)):
		connection.close()
		return True

	return False

def p_tableExists(tableName):
	print tableName
	connection = sqlite3.connect('pricings.db')
	cursor = connection.cursor()
	cursor.execute("""
	    SELECT name 
	    FROM sqlite_master 
	    WHERE type='table' AND name=?;
	""", (tableName, ))

	exists = bool(cursor.fetchone())
	print exists
	return exists

def p_create_table(tableName):
	with sqlite3.connect('pricings.db') as connection:
		c = connection.cursor()
		q = 'CREATE TABLE IF NOT EXISTS {0} (id 	INTEGER PRIMARY KEY	 AUTOINCREMENT, creation_date 		DATE 		NOT NULL, file 	 TEXT NOT NULL)'
		c.execute(q.format(tableName))
		print 'Created the table: ' + str(tableName) +'.'
	connection.close()
	return True

def p_drop_table(tableName):
	with sqlite3.connect('pricings.db') as connection:
		c = connection.cursor()
		c.execute("DROP TABLE IF EXISTS {0}".format(tableName))
		# q = 'DROP TABLE IF EXISTS ' +tableName + ";'"
		# c.execute(q)
		print "Dropped the table: '"+str(tableName)+"'."
	connection.close()	
	return True

# DEPRECATED FUNCTION
def oldParsing():
	book = xlrd.open_workbook("./data/wip.xlsx")
	sheet = book.sheet_by_name("Feuille3")
	for r in range(3, sheet.nrows):
		# get raw data from excel
		arrival_excel           = sheet.cell(r,1).value
		departure_excel         = sheet.cell(r,3).value
		price                   = sheet.cell(r,4).value
		# convert raw data to SQL Date format
		arrival_dt              = minimalist_xldate_as_datetime(arrival_excel, 1)
		arrival_time            = arrival_dt.strftime('%Y-%m-%d %H:%M:%S')
		departure_dt            = minimalist_xldate_as_datetime(departure_excel, 1)
		departure_time          = departure_dt.strftime('%Y-%m-%d %H:%M:%S')        
		# print '%s %s %s' % (arrival_time, departure_time, price)      
		values = (arrival_time, departure_time, price)
		c.execute(q.format(tableName),values)

def findAnomalies(tableName):
	print 'finding the anomalies withing the file '+tableName+'...'
	connection = sqlite3.connect('transactions.db')
	c = connection.cursor()
	anomalies = []
	q = """SELECT id FROM {0} WHERE (price <= ?)"""
	with sqlite3.connect('transactions.db') as connection:
		type_0 = Path("./data/"+tableName+".xls")
		type_1 = Path("./data/"+tableName+".xlsx")
		if type_0.is_file():
			book = xlrd.open_workbook("./data/"+tableName+".xls")
		else:
			book = xlrd.open_workbook("./data/"+tableName+".xlsx")
		# sheet = book.sheet_by_name("source")
		
		c = connection.cursor()
		
		sheets = book.sheet_names()
		# sheet = book.sheet_by_name("Feuille1")
		anomalies_count 	= 0
		for i in range (0,len(sheets)-1):
			sheet = book.sheet_by_name(sheets[i])
			for r in range(15,sheet.nrows-1):
				# get raw data from excel
				dates_excel           	= sheet.cell(r,4).value
				# print dates_excel
				
				arrival_excel		= dates_excel.split('-')[0]
				departure_excel	= dates_excel.split('-')[1]
				price                   	= sheet.cell(r,12).value
				
				arrival_dt 		= datetime.datetime.strptime(arrival_excel,"%m/%d/%Y  %H:%M ")
				departure_dt 		= datetime.datetime.strptime(departure_excel ," %m/%d/%Y %H:%M")

				arrival_time            	= arrival_dt.strftime('%Y-%m-%d %H:%M:%S')
				departure_time		= departure_dt.strftime('%Y-%m-%d %H:%M:%S')

				duration		= departure_dt - arrival_dt
				if (duration.days == 1):
					duration_dt 		= datetime.datetime.strptime(str(duration),"%d day, %H:%M:%S")
					duration_time 		= duration_dt.strftime('%d %H:%M:%S')

				elif (duration.days > 1):
					duration_dt 		= datetime.datetime.strptime(str(duration),"%d days, %H:%M:%S")
					duration_time 		= duration_dt.strftime('%d  %H:%M:%S')
				else:
					duration_dt 		= datetime.datetime.strptime(str(duration),"%H:%M:%S")
					duration_time 		= duration_dt.strftime('%d  %H:%M:%S')

				# if the car stayed more than one hour and one quarter hour (pricing policy)
				if (duration > datetime.timedelta(hours=1, minutes=15)):
					print datetime.timedelta(hours=1, minutes=15)
					#  and it paid less than 1.60 euros, then this is an anomaly
					#  18/08: swapped it to 2.30 euros to match the quarter pricing policy
					if (price < 2.30):
						# print '							STAYED: ' + str(duration )
						# print '							PAYED: ' +str(price)
						# print ''
						anomalies_count = anomalies_count + 1
						str_duration = str(duration)

						if ('day' in str_duration):
							str_duration = str_duration.replace('day', 'jour')
						if ('days' in str_duration):
							str_duration = str_duration.replace('days', 'jours')
						nb_hours = duration.days*24 + duration_dt.hour
						anomalies.append([i+1,r+1, str_duration, price, nb_hours])

		print anomalies_count
				# values = (arrival_time, departure_time, price)
				# c.execute(q.format(tableName),values)	
	# print anomalies 
	# print anomalies_count
	# print len(sheets)
	#  sorting the multidimensionnal list
	sorted_anomalies = sorted(anomalies, key=lambda x: x[4], reverse=True)
	print sorted_anomalies
	#  SHEET, LINE, DURATION, PRICE, NBHOURS
	return sorted_anomalies

# # # # # # # # # # # # # # # # # # # # # # # # #
#    TESTING ZONE			    				#
# # # # # # # # # # # # # # # # # # # # # # # # #

# findAnomalies("mars_2017")
# uploadData("march")
# getDataSize("april")

# uploadData('wip')
# RUN ONCE
# check SELECT * FROM tableName before running lol

