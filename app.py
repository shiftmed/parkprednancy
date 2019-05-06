#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Created on: 19 june 2017												#
# Internal app used to adjust parkings' pricing policies				# 
# and get some useful data from it.			 							#
# @author: Mehdi SHAHID @ <Telecom Nancy>		 						#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ## # # # #


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 			IMPORTS					#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from flask import Flask, flash, redirect, render_template, send_from_directory, request, jsonify, Markup, url_for
from werkzeug import secure_filename
import locale
locale.setlocale(locale.LC_TIME,'fr_FR')

import io
try:
	to_unicode = unicode
except NameError:
	to_unicode = str

import multiprocessing
from multiprocessing.pool import Pool
from contextlib import closing

import unicodedata
import time
import shutil
import os
import errno
import jinja2
import urllib2
import json
import sqlite3



from compute import *
from config import *
from models import *
from data import *




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 		TESTING AREA	  	  													#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# drop_table("march")
# create_table("wip")

# drop_table("january")
# create_table("january")
# getOptimalPricingPolicy("octobre", 2, 'gare_thiers')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 		CONFIGURATION  	  												#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask(__name__)
# MARK: change secret key to something really super secret once deployed lol :-)
app.secret_key = "super secret key"



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 		BASIC ROUTING	  	  											#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@app.route('/')
def index():
	return redirect(url_for('simulation'))

@app.route('/simulation')
def simulation():
	return render_template('simulation_wip.html', title = 'Simulation', dataTransactions = fillDataPicker(), dataPricing = p_fillDataPicker())

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html', title = 'API', dataTransactions = fillDataPicker(), dataPricing = p_fillDataPicker())

@app.route('/results', methods = ['GET', 'POST'])
def results():
	if request.method == 'POST':

		error = False
		# Geting the tableName from the first user input 
		select = request.form.get('selectTable')
  		tableName = str(select)
  		selectPricing = request.form.get('selectPricing')
  		fileName = str(selectPricing)
  		fileName = fileName.replace(' ', '')
  		
  		if select == None:
  			flash(u"Merci de sélectionner un mois dans le menu déroulant.","error")
  			error = True
  		if selectPricing == None:
  			flash(u"Merci de sélectionner une grille tarifaire dans le menu déroulant.","error")
  			error = True
  		# Geting the  parkingName  from the second user input 
		
		
		if (error == False):
			f = open('data/'+fileName+'.json')	
			print '					no errors detected. Launching the simulation.'	

	  		start = time.time()
	  		parkingName = fileName


	  		# anomalies_tableName = tableName.lstrip('0123456789.-')

			anomalies_tableName = tableName.replace(' ', '')
	  		
			# anomalies_tableName = anomalies_tableName.split('.')[0]
			anomalies = findAnomalies(anomalies_tableName)
			# if '.xls' in anomalies_tableName:
			# 	anomalies_tableName = anomalies_tableName.replace('.xls', '')
			# if '.xlsx' in f.filename:
			# 	anomalies_tableName = anomalies_tableName.replace('.xlsx', '')
  			
	  		with closing(Pool(processes=5)) as pool:
				a = pool.apply_async(getEstimatedSales, (tableName, parkingName))
				b = pool.apply_async(getOriginalSales, (tableName, parkingName))
				c = pool.apply_async(getOptimalSales, (tableName, parkingName))
				d = pool.apply_async(getEachCarPricing, (tableName, parkingName))
				
				
				pool.close()
				pool.join()

				car_id, estimatedSales, errorSales = a.get()
				realSales = b.get()
				sales, values = c.get()
				eachCarPricing = d.get()

    				pool.terminate()	

	  		
	  		r_duration = time.time() - start
			# return render_template('results.html', title='Resultats', estimatedSales = estimatedSales, errorSales = errorSales, sales = sales, realSales = realSales, values=values, labels=labels, tableName = tableName, parkingName = parkingName, r_duration = r_duration)
			# VERSION 2, WIP:
			return render_template('results_wip.html', title='Resultats', estimatedSales = estimatedSales, errorSales = errorSales, sales = sales, realSales = realSales, values=values, labels=car_id, tableName = tableName, parkingName = parkingName, r_duration = r_duration, eachCarPricing = eachCarPricing, anomalies = anomalies)
	if request.method == 'GET':
		return render_template('results_wip.html', title='Resultats')
		# return simulation()

	return simulation()

@app.route('/xlsx', methods = ['GET', 'POST'])
def upload_xlsx():
	if request.method == 'POST':
		type = 0
		f = request.files['file']
		# print 'lolilol'
		fileName = f.filename
		
		if f.filename == "":
			flash(u"Merci d'insérer un fichier avant de lancer la simulation.")
			return dashboard()
		
		
		
		fileName = fileName.lstrip('0123456789.- ')
		fileName = fileName.replace(' ', '_')
		f.save('data/'+secure_filename(fileName))
		filename_without_ext = fileName.split('.')[0]
		
		if '.xls' in f.filename:
			filename_without_ext = filename_without_ext.replace('.xls', '')
			type = 0
		if '.xlsx' in f.filename:
			filename_without_ext = filename_without_ext.replace('.xlsx', '')
			type = 1
		
		drop_table(filename_without_ext)
		print 'creating the table...'
		create_table(filename_without_ext)
		print 'uploading the data...'
		uploadData(filename_without_ext, type)
		# I'm not removing the files so that the user can detect anomalies 
		# silentremove('data/'+filename_without_ext+'.xls')
		# silentremove('data/'+filename_without_ext+'.xlsx')
		print 'table created and data uploaded. Heading to simulation page.'
		return simulation()

@app.route('/delete_xlsx', methods = ['GET', 'POST'])
def delete_xlsx():
	if request.method == 'POST':
		if request.form['deleteTable'] != 'empty':
			tableName = request.form['deleteTable']
			dataToDelete = []
			if tableName == 'everything':
				for data in fillDataPicker():
					dataToDelete += [dataToDelete for dataToDelete in data if dataToDelete != 'debug' and dataToDelete != 'sqlite_sequence']
				for table in dataToDelete:
					drop_table(table)
			else:
				drop_table(tableName)

		return dashboard()		
	if request.method == 'GET':
		return dashboard()		
@app.route('/delete_json', methods = ['GET', 'POST'])
def delete_json():
	if request.method == 'POST':
		if request.form['deleteParking'] != 'empty':
			tableName = request.form['deleteParking']
			dataToDelete = []
			if tableName == 'everything':
				for data in p_fillDataPicker():
					dataToDelete += [dataToDelete for dataToDelete in data if dataToDelete != 'debug' and dataToDelete != 'sqlite_sequence']
				for table in dataToDelete:
					p_drop_table(table)
					silentremove('data/'+table+'.json')
			else:
				p_drop_table(tableName)
				silentremove('data/'+tableName+'.json')
		return dashboard()		
	if request.method == 'GET':
		return dashboard()			

@app.route('/pricing')
def json_page():
	return render_template('json.html', title=u'Création de grille tarifaire')

@app.route('/json', methods = ['GET', 'POST'])
def create_json():
	error = False
	form = request.form
	if form['parkingName'] == '':
		error = True
		flash(u"Merci d'entrer un nom de parking avant de générer le fichier.","error")
	for elt in form:
		if ',' in form[elt]:
			error = True
			flash(u"Merci de remplacer les virgules par des points dans vos tarifs.","error")


	if request.method == 'POST':
		now 	= datetime.datetime.now()
		d_now 	= now.strftime('%Y-%m-%d %H:%M:%S')
		parkingName = form['parkingName']
		print form['sundayPricing']
		# print parkingName
		parkingName = slugify(parkingName)
		# print parkingName
		if error == False:
			replace_json_value(form)
			p_drop_table(parkingName)
			p_create_table(parkingName)
			p_uploadData(parkingName, d_now)
			return json_page()
		else:
			return json_page()

	if request.method == 'GET':
		return json_page()



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 		API ROUTING	  	  												#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



# MARK: because of some weird issue, I had to split the routing in two because it couldnt handle
# GET and POST requests given the entry parameter... To be fixed, I guess?
@app.route('/api/transactions/<tableName>/', methods=['GET'])
def transactions(tableName):
	all_transactions = get_all_transactions(tableName)
	return json.dumps(all_transactions)

@app.route('/api/transactions/<tableName>', methods=['POST'])
def collection(tableName):
	data = request.form
	result = add_transaction(data['tableName'],data['arrival'], data['departure'], data['price'])
	return jsonify(result)

@app.route('/api/transactions/<tableName>/<transaction_id>', methods=['GET', 'PUT', 'DELETE'])
def resource(tableName, transaction_id):
	if request.method == 'GET':
    		transaction = get_single_transaction(tableName, transaction_id)
    		return json.dumps(transaction)
    	elif request.method == 'PUT':
    		data = request.form
    		result = edit_transaction(tableName, transaction_id, data['arrival'], data['departure'], data['price'])      
    		return jsonify(result)
    	elif request.method == 'DELETE':
    		result = delete_transaction(tableName, transaction_id)
    		return jsonify(result)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 		HELPER FUNCTIONS  	  											#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def silentremove(filename):
    try:
        os.remove(filename)
        print 'Successfully removed the uploaded file ' +str(filename) +'.'
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value

def replace_json_value(form):
	shutil.copy2('data/template2.json', 'data/'+form['parkingName']+'.json')
	if (form['sundayPricing'] == 'no'):
		days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
	else:
		days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

	print '						Special price on Sunday: ' +str(form['sundayPricing'])
	print 'replacing the values inside the template...'
	with open('data/'+form['parkingName']+'.json') as data_file:
		data = json.load(data_file)
		data.keys()[0] 							= form['parkingName'].strip('\"')
		data[data.keys()[0]]['2h4h'] 					= form['price2h4h'].strip('\"')
		data[data.keys()[0]]['4h12h'] 					= form['price4h12h'].strip('\"')
		data[data.keys()[0]]['freeMinutes'] 				= form['freeMinutes'].strip('\"')
		data[data.keys()[0]]['initialPrice'] 				= form['initialPrice'].strip('\"')
		data[data.keys()[0]]['Over24h'] 					= form['Over24h'].strip('\"')
		data[data.keys()[0]]['sundayPricing'] 				= form['sundayPricing'].strip('\"')
		for day in days:			
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["00:45:00"]        = str(float(form["1h"])/2)
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["01:00:00"]        = form["1h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["02:00:00"]        = form["2h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["03:00:00"]        = form["3h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["04:00:00"]        = form["4h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["05:00:00"]        = form["5h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["06:00:00"]        = form["6h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["07:00:00"]        = form["7h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["08:00:00"]        = form["8h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["09:00:00"]        = form["9h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["10:00:00"]        = form["10h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["11:00:00"]        = form["11h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["12:00:00"]        = form["12h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["13:00:00"]        = form["13h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["14:00:00"]        = form["14h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["15:00:00"]        = form["15h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["16:00:00"]        = form["16h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["17:00:00"]        = form["17h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["18:00:00"]        = form["18h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["19:00:00"]        = form["19h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["20:00:00"]        = form["20h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["21:00:00"]        = form["21h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["22:00:00"]        = form["22h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["23:00:00"]        = form["23h"]
			data[data.keys()[0]]["Infos"][day]["Tarifs"]["24:00:00"]        = form["24h"]

			hours = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
			for k in range(1,len(hours)-1):
				price_at_hour								= data[data.keys()[0]]["Infos"][day]["Tarifs"][str(hours[k])+':00:00'] 
				price_at_next_hour							= data[data.keys()[0]]["Infos"][day]["Tarifs"][str(hours[k+1])+':00:00'] 
				data[data.keys()[0]]["Infos"][day]["Tarifs"][str(hours[k])+':15:00']        	= str(float(float(price_at_hour) + 1*(float(price_at_next_hour) - float(price_at_hour))/4))
				data[data.keys()[0]]["Infos"][day]["Tarifs"][str(hours[k])+':30:00']        	= str(float(float(price_at_hour) + 2*(float(price_at_next_hour) - float(price_at_hour))/4))
				data[data.keys()[0]]["Infos"][day]["Tarifs"][str(hours[k])+':45:00']        	= str(float(float(price_at_hour) + 3*(float(price_at_next_hour) - float(price_at_hour))/4))
			price_at_hour								= data[data.keys()[0]]["Infos"][day]["Tarifs"]['23:00:00'] 
			price_at_next_hour							= data[data.keys()[0]]["Infos"][day]["Tarifs"]['24:00:00'] 		
			data[data.keys()[0]]["Infos"][day]["Tarifs"]['23:15:00']        	= str(float(float(price_at_hour) + 1*(float(price_at_next_hour) - float(price_at_hour))/4))
			data[data.keys()[0]]["Infos"][day]["Tarifs"]['23:30:00']        	= str(float(float(price_at_hour) + 2*(float(price_at_next_hour) - float(price_at_hour))/4))
			data[data.keys()[0]]["Infos"][day]["Tarifs"]['23:45:00']        	= str(float(float(price_at_hour) + 3*(float(price_at_next_hour) - float(price_at_hour))/4))
	parkingName = slugify(form['parkingName'])

	with io.open('data/'+str(parkingName)+'.json', 'w', encoding='utf8') as outfile:
		str_ = json.dumps(data,
		indent=4, sort_keys=True,
		separators=(',', ': '), ensure_ascii=False)
		outfile.write(str_)
	print '...file created and placed inside the data folder.'

def startLoading():
	# print 'trying to load the loader '
	loadingMarkUp = Markup(
					'<div id="wait_overlay" class="progress" >'
					'<div class="indeterminate"></div>'
					'</div>'
	                       		)
	flash(loadingMarkUp, 'loader')

def stopLoading():
	loadingMarkUp = Markup(
					' '
	                       		)
	flash(loadingMarkUp, 'loader')

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def add_transaction(tableName, arrival, departure, price):
	try:
		with sqlite3.connect('transactions.db') as connection:
			c = connection.cursor()
			q = 'INSERT INTO {0} (arrival, departure, price) values ({1},{2},{3})'
			connection.execute(q.format(tableName,arrival,departure,price))
			result = {'status': 1, 'message': 'Transaction successfully entered.'}
	except:
		result = {'status': 0, 'message': 'Error, transaction could not be entered.'}
	return result

def get_all_transactions(tableName):
	with sqlite3.connect('transactions.db') as connection:
		c = connection.cursor()
		q = 'SELECT * FROM {0} ORDER BY id asc'
		c.execute(q.format(tableName))
		# c.execute("SELECT * FROM march ORDER BY id desc")
		all_transactions = c.fetchall()
		return all_transactions    	

def get_single_transaction(tableName, transaction_id):
	with sqlite3.connect('transactions.db') as connection:
		c = connection.cursor()
		q = 'SELECT * FROM {0} WHERE id = {1}'
		c.execute(q.format(tableName,transaction_id))
		transaction = c.fetchone()
		return transaction

def edit_transaction(tableName, transaction_id, arrival, departure, price):
	try:
		with sqlite3.connect('transactions.db') as connection:
			q = 'UPDATE {0} SET arrival = {1}, departure = {2}, price = {3} WHERE id = {4}'
			connection.execute(q.format(tableName,arrival,departure,price,transaction_id))
			# connection.execute('UPDATE ? SET arrival = ?, departure = ?, price = ? WHERE id = ?;', (tableName, arrival, departure, price, transaction_id))
			result = {'status': 1, 'message': 'Transaction edited successfully.'}
	except:
		result = {'status': 0, 'message': 'Error, transaction could not be edited.'}
	return result

def py_edit_transaction(tableName,transaction_id,arrival,departure,price):
	opener = urllib2.build_opener(urllib2.HTTPHandler)
	# change url if deployed and put some authentification requirements
	serv =  'http://localhost:5000/api/transactions/'+tableName+'/'+str(transaction_id)
	data = "arrival='"+arrival+"'&departure='"+departure+"'&price="+str(price)
	request = urllib2.Request(serv, data)
	request.get_method = lambda: 'PUT'
	url = opener.open(request)

def delete_transaction(tableName, transaction_id):
	try:
		with sqlite3.connect('transactions.db') as connection:
			q = 'DELETE FROM {0} WHERE id = {1};'
			connection.execute(q.format(tableName, transaction_id))
			result = {'status': 1, 'message': 'Transaction deleted successfully.'}
			
	except:
		result = {'status': 0, 'message': 'Error, transaction could not be deleted.'}
	return result

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 		RUN SETTINGS	  	  				#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__=='__main__':
	app.run(host=HOST, port=PORT, debug=DEBUG)



