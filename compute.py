import sqlite3
import json
import urllib2

import datetime
import calendar
import time
from dateutil import parser
from dateutil.relativedelta import relativedelta
from pprint import pprint

from app import *



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                           	#
#       given a table and a car_id, returns the time      		#
#         the specified car stayed in the parking.         		#
#                                                  				#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def getDuration(tableName, car_id):
	# print 'departure_time: ' +get_single_transaction(tableName, car1)[2]
	r_departure = get_single_transaction(tableName,car_id)[2]                   # parsing the data from json
	d_departure = datetime.datetime.strptime(r_departure,'%Y-%m-%d %H:%M:%S')   # converting to datetime obj

	r_arrival = get_single_transaction(tableName,car_id)[1]
	d_arrival = datetime.datetime.strptime(r_arrival,'%Y-%m-%d %H:%M:%S')
	# print d_departure - d_arrival

	# print (d_departure - d_arrival)
	return d_departure - d_arrival


# Thanks to some guy on reddit if anyone ever reads this :D
def round_minutes(dt, direction, resolution):
	new_minute = (dt.minute // resolution + (1 if direction == 'up' else 0)) * resolution
	return dt + datetime.timedelta(minutes=new_minute - dt.minute)

	for hour, minute, resolution in ((17, 34, 30), (12, 58, 15), (14, 1, 60)):
		dt = datetime.datetime(2014, 8, 31, hour, minute)
	# for direction in 'up', 'down':
	#     print('{} with resolution {} rounded {:4} is {}'.format(dt, resolution, direction,
	#                 round_minutes(dt, direction, resolution)))

def getQuarters(tableName,car_id):
	d_timedelta             = getDuration(tableName, car_id)
	# print 'inside getquarters'
	# print d_timedelta
	d_time_date             = (datetime.datetime.min + d_timedelta).date()
	d_time_time             = (datetime.datetime.min + d_timedelta).time()
	d_time                  = datetime.datetime.combine(d_time_date, d_time_time)   
	d_time_minutes = d_time.minute
	# print str(d_time) + '  > which equals a duration of: ' +str(d_time_days)+ ' days, ' +str(d_time_hours) + ' hours, '+ str(d_time_minutes) + ' minutes and ' + str(d_time_seconds) + ' seconds.'
	# print 'Rounded to the nearest quarter, this gives: ' +str(round_minutes(d_time, 'down', 15))
	# print ''
	# halfs = [0,15,30,45]
	
	next_value = round_minutes(d_time, 'up', 15)
	# if ((d_time_minutes +next_value.minute)/2 <= next_value.minute):
	if (d_time_minutes <= 30):
		# print 'going down'
		direction = 'down'
	else:
		# print 'going up'
		direction = 'up'
	round_with_seconds      = round_minutes(d_time, direction, 15)

	rounded_time            = round_with_seconds.replace(second=0).replace(year=1900)
	# print rounded_time
	# print ''
	# print 'out off getquarters'
	return rounded_time

def getWeekDayArrival(tableName, car_id):

	# print 'The duration is: ' +str(getDuration(tableName, car_id))
	duration = getDuration(tableName,car_id)

	arrival = get_single_transaction(tableName,car_id)[1]
	d_arrival = datetime.datetime.strptime(arrival,'%Y-%m-%d %H:%M:%S')


	day = ''
	if (d_arrival.weekday() == 0):
	# print 'The car '+str(car_id)+' came to the parking on a Monday.'
		day = 'Lundi'
	elif (d_arrival.weekday() == 1):
		day = 'Mardi'

	elif (d_arrival.weekday() == 2):
		day = 'Mercredi'

	elif (d_arrival.weekday() == 3):
		day = 'Jeudi'

	elif (d_arrival.weekday() == 4):
		day = 'Vendredi'

	elif (d_arrival.weekday() == 5):
		day = 'Samedi'

	elif (d_arrival.weekday() == 6):
		day = 'Dimanche'

	return day

def getWeekDayDeparture(tableName, car_id):

	# print 'The duration is: ' +str(getDuration(tableName, car_id))
	duration = getDuration(tableName,car_id)

	departure = get_single_transaction(tableName,car_id)[2]
	d_departure = datetime.datetime.strptime(departure,'%Y-%m-%d %H:%M:%S')

	day = ''
	if (d_departure.weekday() == 0):
	# print 'The car '+str(car_id)+' came to the parking on a Monday.'
		day = 'Lundi'
	elif (d_departure.weekday() == 1):
		day = 'Mardi'

	elif (d_departure.weekday() == 2):
		day = 'Mercredi'

	elif (d_departure.weekday() == 3):
		day = 'Jeudi'

	elif (d_departure.weekday() == 4):
		day = 'Vendredi'

	elif (d_departure.weekday() == 5):
		day = 'Samedi'

	elif (d_departure.weekday() == 6):
		day = 'Dimanche'

	return day

def getCurrentWeekDay(tableName, car_id, duration):
	duration = parser.parse(str(duration))
	day = ''
	if (duration.weekday() == 0):
	# print 'The car '+str(car_id)+' came to the parking on a Monday.'
		day = 'Lundi'
	elif (duration.weekday() == 1):
		day = 'Mardi'

	elif (duration.weekday() == 2):
		day = 'Mercredi'

	elif (duration.weekday() == 3):
		day = 'Jeudi'

	elif (duration.weekday() == 4):
		day = 'Vendredi'

	elif (duration.weekday() == 5):
		day = 'Samedi'

	elif (duration.weekday() == 6):
		day = 'Dimanche'
	return day	

def getNumberOfQuarters(time):
	# print time
	dt = parser.parse(str(time))
	# print dt
	# print 'getNumbersOfQuarters calculated for the input: ' +str(time)
	return dt.minute + dt.hour*60
			
def getNumberOf12Hours(time):
	dt = parser.parse(str(time))
	dt_days = dt.day *24
	dt_hours = dt.time().hour 
	return (dt_days + dt_hours)/12

def getNumberOfHours(time):
	return time.seconds//3600 + (time.seconds//60)%60

def getNumberOf24Hours(time):
	a = getNumberOfHours(time)
	return a / 24

def getNumberOfRemainingHoursFrom12Hours(time):
	dt_12hours = parser.parse(str(datetime.time(12,0,0)))
	dt = parser.parse(str(time))

	res = dt - dt_12hours
	return res

def extractMinutes(td):
    return td.seconds//3600

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                           			#
#       given a table, a car and a parking returns how much 			#
#         			said car owes  										#
#                                                          			 	#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def getEstimatedPricingPolicy(tableName,car_id, parkingName):
	# print getWeekDayArrival(tableName,car_id)
	print 'Calculating the estimated price for the car ' +str(car_id) +'...'
	arrival = get_single_transaction(tableName,car_id)[1]
	d_arrival = datetime.datetime.strptime(arrival,'%Y-%m-%d %H:%M:%S')

	with open('data/old/gare_thiers.json') as data_file:
		data = json.load(data_file)

	# print str(car_id) + getWeekDayArrival(tableName,car_id)
	if (int(d_arrival.hour) <= int(data[data.keys()[0]]["InfosJour"][getWeekDayArrival(tableName,car_id)]["Horaires"]["FinJour"])):
		nightOrDay = 'InfosJour'
	else:
		nightOrDay = 'InfosNuit'

	rounded_duration        = getQuarters(tableName, car_id)
	dur = getDuration(tableName, car_id)
	rounded_duration_time   = rounded_duration.time()

	# if (rounded_duration_time < datetime.time(0,30,0)):
	# 	return car_id, 0

	# Check if the car overstayed so it has to be marked up.
	if (dur.days == 0):
		a = data[data.keys()[0]][nightOrDay][getWeekDayArrival(tableName,car_id)]["Tarifs"][str(rounded_duration_time)]
		return car_id, a
		# print 'OK!'
	else:	
		a = data[data.keys()[0]][nightOrDay][getWeekDayArrival(tableName,car_id)]["Tarifs"][str(rounded_duration_time)]+data[data.keys()[0]][nightOrDay][getWeekDayArrival(tableName,car_id)]["Tarifs"]["00:00:00"]*dur.days
		return car_id, a
				
def tt_getOptimalPricingPolicy(tableName,car_id, parkingName):
	# print getWeekDayArrival(tableName,car_id)
	print 'Calculating the tt_estimated price for the car ' +str(car_id) +'...'
	arrival = get_single_transaction(tableName,car_id)[1]
	d_arrival = datetime.datetime.strptime(arrival,'%Y-%m-%d %H:%M:%S')

	with open('data/'+parkingName+'.json') as data_file:
		data = json.load(data_file)


	# print str(car_id) + getWeekDayArrival(tableName,car_id)
	if (int(d_arrival.hour) <= int(data[data.keys()[0]]["Infos"][getWeekDayArrival(tableName,car_id)]["Horaires"]["FinJour"])):
		nightOrDay = 'Infos'
	else:
		nightOrDay = 'InfosNuit'

	rounded_duration        = getQuarters(tableName, car_id)
	dur 					= getDuration(tableName, car_id)
	rounded_duration_time   = rounded_duration.time()
	specialPrice			= False
	freeMinutes 			= float(data[data.keys()[0]]["Gratuit"])
	price2h4h 				= float(data[data.keys()[0]]["2h4h"])
	price4h12h 				= float(data[data.keys()[0]]["4h12h"])
	priceOver24h    		= float(data[data.keys()[0]]["Over24h"])
	sundayPricing 			= data[data.keys()[0]]['sundayPricing'] 
	
	if sundayPricing == "yes":
		specialPrice = True

	# if (rounded_duration_time < datetime.time(0,30,0)):
	# 	return car_id, 0
	if (dur.days == 0):
		if specialPrice:
			nightOrDay = 'InfosNuit'
		if nightOrDay == 'InfosNuit':
			if dur.seconds//3600 < 4:
				return car_id, price2h4h
			else:
				return car_id, price4h12h
		else:
			a = float(data[data.keys()[0]][nightOrDay][getWeekDayArrival(tableName,car_id)]["Tarifs"][str(rounded_duration_time)])
			return car_id, a
		# print 'OK!'
	else:	
		res = 0
		if specialPrice:
			nightOrDay = 'InfosNuit'

		if nightOrDay == 'InfosNuit':
			if dur.seconds//3600 < 4:
				res +=  price2h4h
			else:
				res +=  price4h12h
		else:

			# nbHours = float(dur.days*24 + rounded_duration_time.hour )
			a_day = float(data[data.keys()[0]][nightOrDay][getWeekDayArrival(tableName,car_id)]["Tarifs"][str(rounded_duration_time)])
			leftHours = dur.days*24 - 24
			a_days = leftHours*priceOver24h 
		
			a = a_day + a_days 
			res += a
	return car_id, res
		



# OBSOLETE FUNCTION, NOT USED ANYMORE! I kept it in case I need to checkup on some algorithm-logic I already used
def getOptimalPricingPolicy(tableName, car_id, parkingName):
	print 'Calculating the price for the car ' +str(car_id) +'...'

	arrival = get_single_transaction(tableName,car_id)[1]
	d_arrival = parser.parse(str(arrival))
	departure = get_single_transaction(tableName,car_id)[2]
	d_departure = parser.parse(str(departure))
	
	

	with open('data/new.json') as data_file:
		data = json.load(data_file)

	# all this is based on the premise that the car stayed less than 1 day... 
	# make a condition check for 24h, if true, split into n days and loop 
	json_finjour = data[data.keys()[0]]["InfosJour"][getWeekDayArrival(tableName,car_id)]["Horaires"]["FinJour"]	
	d_finjour = datetime.datetime.strptime(str(json_finjour), '%H')

	json_debutjour = data[data.keys()[0]]["InfosJour"][getWeekDayArrival(tableName,car_id)]["Horaires"]["DebutJour"]
	d_debutjour = datetime.datetime.strptime(str(json_debutjour), '%H')
	rounded_duration        = getQuarters(tableName, car_id)
	rounded_duration_time   = rounded_duration.time()

	res = 0
	day_iterator = 0
	day_first_loop = True
	day_final_time = rounded_duration_time

	while(day_iterator < getNumberOf24Hours(rounded_duration)):

		if (int(d_arrival.hour) < int(d_finjour.hour)):
			day_first_loop = True
			if (rounded_duration.time() < datetime.time(0,30,0)):
				print 'gratuit'
				return 0
			if (d_departure < d_finjour):
				res = getDayTimePrice(tableName, car_id, 'InfosJour', duration )
				return res					
			else:
				# How many hours will the car owner pay on day times
				extra_duration = d_departure - d_finjour
				d_extra_duration_date = (datetime.datetime.min + extra_duration).date()
				d_extra_duration_time = (datetime.datetime.min + extra_duration).time()
				d_extra_duration 	= datetime.datetime.combine(d_extra_duration_date, d_extra_duration_time) 
				
				first_loop =  True
				final_time = d_extra_duration_time
				
				dt_extra_duration = parser.parse(str(d_extra_duration_time))

				dt_12hours = parser.parse(str(datetime.time(12,0,0)))
				
				max_range = getNumberOf12Hours(dt_extra_duration)
				iterator = 0
				before_current_time = dt_extra_duration
				current_time = dt_extra_duration
				while (iterator < max_range):
					if (first_loop):
						dayOrNight = 'InfosNuit'
					else:
						dayOrNight = 'InfosJour'
					res += getDayTimePrice(tableName, car_id, dayOrNight, dt_12hours ) + getNightTimePrice(tableName, car_id, dayOrNight,  dt_12hours)
					first_loop = not first_loop
					current_time = current_time + datetime.timedelta(hours=12)
					iterator += 1
				
				if (first_loop):
					dayOrNight = 'InfosJour'
				else:
					dayOrNight = 'InfosNuit'

				res += getDayTimePrice(tableName, car_id, dayOrNight, final_time) + getNightTimePrice(tableName, car_id, dayOrNight, final_time)

				day_iterator += 1 
		else:
			day_first_loop = False
			if (rounded_duration.time() < datetime.time(0,30,0)):
				print 'gratuit'
				return 0
			if (d_departure < d_debutjour):
				res = getNightTimePrice(tableName, car_id, 'InfosJour', duration )
				return res					
			else:
				# How many hours will the car owner pay on day times
				extra_duration = d_departure - d_finjour
				d_extra_duration_date = (datetime.datetime.min + extra_duration).date()
				d_extra_duration_time = (datetime.datetime.min + extra_duration).time()
				d_extra_duration 	= datetime.datetime.combine(d_extra_duration_date, d_extra_duration_time) 
				
				first_loop =  True
				final_time = d_extra_duration_time
				
				dt_extra_duration = parser.parse(str(d_extra_duration_time))

				dt_12hours = parser.parse(str(datetime.time(12,0,0)))
				
				max_range = getNumberOf12Hours(dt_extra_duration)
				iterator = 0
				while (iterator < max_range):
					if (first_loop):
						dayOrNight = 'InfosNuit'
					else:
						dayOrNight = 'InfosJour'
					res += getDayTimePrice(tableName, car_id, dayOrNight, dt_12hours ) + getNightTimePrice(tableName, car_id, dayOrNight,  dt_12hours)
					first_loop = not first_loop
					final_time = getNumberOfRemainingHoursFrom12Hours(dt_extra_duration)
					iterator += 1
				
				
				if (first_loop):
					dayOrNight = 'InfosJour'
				else:
					dayOrNight = 'InfosNuit'

				res += getDayTimePrice(tableName, car_id, dayOrNight, extractMinutes(final_time)) + getNightTimePrice(tableName, car_id, dayOrNight, extractMinutes(final_time))

				day_iterator += 1
	
	if (day_first_loop):
		dayOrNight = 'InfosJour'
	else:
		dayOrNight = 'InfosNuit'
	
	aa =  getNumberOf24Hours(rounded_duration)*24
	bb = getNumberOfHours(rounded_duration)
	
	hours_left = datetime.datetime.strptime(str(bb-aa),"%H")
	f_final_time = hours_left
	cc = getNumberOf12Hours(hours_left)
	final_iterator = 0
	final_max_range = cc
	while (final_iterator < final_max_range):
		if (day_first_loop):
			dayOrNight = 'InfosNuit'
		else:
			dayOrNight = 'InfosJour'
		res += getDayTimePrice(tableName, car_id, dayOrNight, dt_12hours ) + getNightTimePrice(tableName, car_id, dayOrNight,  dt_12hours)
		day_first_loop = not day_first_loop
		f_final_time = getNumberOfRemainingHoursFrom12Hours(str(hours_left))
		final_iterator += 1
	
	if (day_first_loop):
		dayOrNight = 'InfosJour'
	else:
		dayOrNight = 'InfosNuit'

	print str(car_id) + ' 					- 			' +str(extractMinutes(f_final_time))
	res += getDayTimePrice(tableName, car_id, dayOrNight, extractMinutes(f_final_time)) + getNightTimePrice(tableName, car_id, dayOrNight, extractMinutes(f_final_time)) 

	return res

def getNextDay(dt):
	if (calendar.monthrange(dt.year, dt.month)[1] == 31 & dt.day == 31):
		if (dt.month == 12):
			d_nextday = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)	
		else:
			d_nextday = dt.replace(month=dt.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
	elif(calendar.monthrange(dt.year, dt.month)[1] == 30 & dt.day == 30):
		if (dt.month == 12):
			d_nextday = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		else:
			d_nextday = dt.replace(month=dt.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
	elif(calendar.monthrange(dt.year, dt.month)[1] == 29 & dt.day == 29):
		if (dt.month == 12):
			d_nextday = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		else:	
			d_nextday = dt.replace(month=dt.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
	elif(calendar.monthrange(dt.year, dt.month)[1] == 28 & dt.day == 28):
		if (dt.month == 12):
			d_nextday = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)				
		else:	
			d_nextday = dt.replace(month=dt.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)				
	else:
		d_nextday = dt.replace(day=dt.day+1, hour=0, minute=0, second=0, microsecond=0)
	return d_nextday
		

def t_getOptimalPricingPolicy(tableName, car_id, parkingName):
	# print ''
	print 'Calculating the simulated price for the car ' +str(car_id) +'...'
	print ''


	# BASIC DATA FROM TABLE
	arrival 			= get_single_transaction(tableName,car_id)[1]
	d_arrival 		= parser.parse(str(arrival))
	departure 		= get_single_transaction(tableName,car_id)[2]
	d_departure 		= parser.parse(str(departure))
	
	# DURATION THE CAR HAS STAYED 
	duration 		= d_departure - d_arrival 					# TIMEDELTA OBJECT!!!
	duration_days 		= duration.days
	duration_hours 	= duration.seconds//3600
	duration_minutes	= (duration.seconds//60)%60

	# ITERATION TIME
	current_time 		= d_arrival							# DATETIME
	progressive_duration	= d_departure - current_time 					# TIMEDELTA
	current_day		= d_arrival.date()
	if (duration.days == 0):
		print '										< 1 DAY'
		oneDay 		= False
	else:
		print '										>=1 DAY'
		oneDay	 		= True

	initial_duration		= time.strptime( "00:00:00", "%H:%M:%S")


	# print 'ARRIVAL						DURATION			DEPARTURE'
	# print str(d_arrival) + '				'+str(duration)+'			'+str(d_departure)
	
	with open('data/'+parkingName+'.json') as data_file:
		data = json.load(data_file)

	freeMinutes 	= data[data.keys()[0]]["Gratuit"]
	price2h4h 	= data[data.keys()[0]]["2h4h"]
	price4h12h 	= data[data.keys()[0]]["4h12h"]
	priceOver24h    = data[data.keys()[0]]["Over24h"]
	sundayPricing 	= data[data.keys()[0]]['sundayPricing'] 

	res = 0

	nbHours = duration.days * 24 + duration.seconds//3600
	initialHours = initial_duration.tm_hour
	print '										NB HOURS: ' +str(nbHours)
	print '										ND IN: ' +str(getNextDay(d_arrival) - d_arrival)+ ' hours'
	loopOnce = True
	loopOnceBis = True
	loopOnceThrice = True
	loopDayOnce = True
	hasLooped = False
	
	specialPrice = False

	if (nbHours >= 24):
		splits = nbHours / 24
		leftHours = nbHours - (splits*24)*duration_days
		nbHours = 24 
	else:
		splits = 1
		leftHours = 0

	currentWeekDay = getCurrentWeekDay(tableName, car_id, d_arrival)
	# print '										ARRIVAL DAY: ' + str(currentWeekDay)
	# print '										SPLITS: ' +str(splits)
	old_res = 0
	old_res_0 = 0
	old_res_2 = 0
	old_res_3 = 0
	old_res_4 = 0
	if (int(splits) >= 1):
		if (priceOver24h  == 0):
			specialPrice = True
		res += float(duration_days*24)*float(priceOver24h)

	for k in range (0, splits):
		if (specialPrice == False):
			debug_counter = 0
			while (initialHours <= nbHours ):

				if ((initialHours) > (getNextDay(d_arrival) - d_arrival).seconds//3600):
					currentWeekDay = getCurrentWeekDay(tableName, car_id, getNextDay(d_arrival))
					# print '										NEW_DAY: ' +str(currentWeekDay)
					if (initialHours <= 12):
						bla = '%dh' % (initialHours)
						old_res =+ float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
						if (old_res >= res):
							res += old_res
					
				if (initialHours <= 12):
					bla = '%dh' % (initialHours)
					old_res_2 =+ float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
					if (old_res_2 >= res):
						res += old_res_2


				if ((d_arrival.hour + initialHours) >= int(data[data.keys()[0]]["Infos"][currentWeekDay]["Horaires"]["FinJour"])):
					res += float(price2h4h)/4
					if (nbHours - initialHours > 4):
						res += float(price4h12h)/2


				if((d_arrival.hour + initialHours) <= int(data[data.keys()[0]]["Infos"][currentWeekDay]["Horaires"]["FinJour"])):

					if (initialHours <= 12):
						if (sundayPricing == 'yes'):
							if (currentWeekDay == 'Dimanche'):
								if (loopOnceBis):
									res += float(price2h4h)/4
									if (nbHours - initialHours > 4):
										res += float(price4h12h)/2
										loopOnceBis = False

						
						bla = '%dh' % ( initialHours)
						old_res_3 =+ float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
						if (old_res_3 >= res):
							res += old_res_3
	

				

				bla = '%dh' % (initialHours)	
				old_res_4 =+ float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
				if (old_res_4 >= res):
					res += old_res_4
					
				initialHours = initialHours + 1
				debug_counter += 1
			loopDayOnce = True
		
	initialHours = initial_duration.tm_hour
	if (leftHours > 1):
		nbHours = leftHours
		while (initialHours <= nbHours ):

			if ((initialHours) >= (getNextDay(getNextDay(d_arrival)) - d_arrival).seconds//3600):
				if(loopDayOnce):
					currentWeekDay = getCurrentWeekDay(tableName, car_id, getNextDay(getNextDay(d_arrival)))
					# print '										NEW_DAY: ' +str(currentWeekDay)
					
				else:
					bla = '%dh' % int((getNextDay(getNextDay(d_arrival) - d_arrival)).seconds//3600)
					res += float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
					bla = '%dh' % (initialHours)
					res += float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])

			if ((d_arrival.hour + initialHours) >= int(data[data.keys()[0]]["Infos"][currentWeekDay]["Horaires"]["FinJour"])):
				res += float(price2h4h)/4
				if (nbHours - initialHours > 4):
					res += float(price4h12h)/2

			else:
				if (initialHours <= 12):
					if (sundayPricing == 'yes'):
						if (currentWeekDay == 'Dimanche'):
								res += float(price2h4h)/4
								if (nbHours - initialHours > 4):
									res += float(price4h12h)
					else:
						bla = '%dh' % (initialHours)
						res += float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
				
				bla = '%dh' % (initialHours)	
				res += float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"][bla])
			initialHours = initialHours + 1

	if (duration_minutes > freeMinutes):
		if (duration_minutes <= (freeMinutes+15)):
			res += float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"]["1h"])/2
		else:
			res += float(data[data.keys()[0]]["Infos"][currentWeekDay]["Tarifs"]["1h"])
			
	print "										RES: " +str(res) + " euros."
	return car_id, res



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                           				#
#       given a table, and a pricing                        			#
#         policy (getPricingPolicy), returns the sales      		#
#                                                           				#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# VERSION 1, avec les anciens jsons
def getEstimatedSales(tableName,parkingName):
	salesEstimated = 0
	errorEstimated = []
	labels = []
	for r in range(1,getDataSize(tableName)):
		labels.append(r)
		car_id, v = getEstimatedPricingPolicy(tableName,r,parkingName)
		st = get_single_transaction(tableName, r)[3]
		salesEstimated += v

		if (st!=0):
			errorEstimated.append(abs((st-v))/st*100)
		else:
			errorEstimated.append(0)
		
	print 'Total estimated sales were outputed with successs.'
	return labels, salesEstimated, errorEstimated
	

# VERSION 2, nouveau JSON
def getOptimalSales(tableName,parkingName):
	print 'Starting the optimal sales calculation'
	sales = 0
	error = []
	for r in range(1,getDataSize(tableName)):
		car_id, v = tt_getOptimalPricingPolicy(tableName,r,parkingName)
		st = get_single_transaction(tableName, r)[3]
		sales += v
		if (st!=0):
			error.append(abs((st-v)/st)*100)
		else:
			error.append(0)

	print 'Total sales were outputed with successs.'
	return sales, error
	

def getEachCarPricing(tableName, parkingName):
	carPricing = []
	for r in range(1,getDataSize(tableName)):
		# SIMULATED PRICE
		car_id, s = tt_getOptimalPricingPolicy(tableName,r,parkingName)
		# ESTIMATED PRICE
		car_id, e = getEstimatedPricingPolicy(tableName,r,parkingName)
		re = get_single_transaction(tableName,r)[3]
		arrival 			= get_single_transaction(tableName,r)[1]
		d_arrival 		= parser.parse(str(arrival))
		departure 		= get_single_transaction(tableName,r)[2]
		d_departure 		= parser.parse(str(departure))

		duration = d_departure - d_arrival
		hours = duration.days * 24 + duration.seconds//3600
		mins = (duration.seconds//60)%60
		# print str(car_id) +'   :			 			DUR:' +str(dur) + ' hours.'
 		carPricing.append([car_id, e, s, re, hours, mins])

	return carPricing
	
# Permet d'obtenir le chiffre d'affaire reel
def getOriginalSales(tableName, parkingName):
	sales = 0
	for r in range(1,getDataSize(tableName)):
		sales += get_single_transaction(tableName, r)[3]
	print 'Original sales were calculated with success.'
	return sales

# getQuarters("fevrier_2017",10)
# tt_getOptimalPricingPolicy("janvier_2017", 23, "testing")
# getEstimatedSales("janvier_2017","toutes_options")
# getOptimalSales('janvier_2017', 'simulation')
# t_getOptimalPricingPolicy('janvier_2017',1,'simulation')
# t_getOptimalPricingPolicy('octobre',6,'new')
# getOptimalPricingPolicy('octobre',1,'gare_thiers')
# getOriginalSales("octobre","gare_thiers")
# getOptimalSales('octobre','new')
# getPricingPolicy('octobre', 1, 'ha_ha_ha')
# getSales('march','gare_thiers')
# py_edit_transaction('march',1,'2017-03-06 00:30:01','2017-03-06 03:58:01', 420)
# getPricingPolicy('march', 1, 'gare_thiers')
# getQuarters("march",1)
# getQuarters("march",2)
# getQuarters("march",3)
# getDay('march',1)
