from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime, pytz
import re

# try:
# 	import argparse
# 	flags = argparse.ArgumentParser(parents = [tools.argparser]).parse_args()
# except ImportError:
# 	flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET = 'private/client_secret.json'
store = file.Storage('private/storage.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
	creds = tools.run_flow(flow, store)  #\
		#if flags else tools.run_flow(flow, store)

CAL = build('calendar','v3', http = creds.authorize(Http()))
GMT_OFF = pytz.utc

def addEvent(start, end, summary, GMT_OFF = '+01:00'):
	EVENT = {
		'summary': summary,
		'start': {'dateTime':'%s' % (start.isoformat())},
		'end': {'dateTime':'%s' % (end.isoformat())}
	}

	e = CAL.events().insert(calendarId = 'primary', sendNotifications = True, body = EVENT).execute()
	print('''*** %r event added:
		Start: %s
		End:   %s''' % (e['summary'].encode('utf-8'),
			e['start']['dateTime'], e['end']['dateTime']))

#AddingEvent

# beginning = datetime.datetime(2018, 9, 4, 19, tzinfo = GMT_OFF)
# ending = datetime.datetime(2018, 9, 4, 20, tzinfo = GMT_OFF)
# bodying = 'myCustomText'
# addEvent(beginning, ending, bodying)

#GoogleDrive
#files = SERVICE.files().list().execute().get('items',[])
#for f in files:
#	print(f['title'])

def dtToGCString(datetimeObject):
	if(type(datetimeObject) == datetime.date):
		return datetime.datetime.combine(datetimeObject, datetime.datetime.min.time()).isoformat() + 'Z'
	elif(type(datetimeObject) == datetime.time):
		return datetime.datetime.combine(datetime.date.today(), datetimeObject).isoformat() + 'Z'
	elif(type(datetimeObject) == datetime.datetime):
		return datetimeObject.isoformat()+'Z'
	elif(type(datetimeObject) == None):
		return None

def getTags(event):
	description = event.get("description", "")
	TAGS = re.compile('(?:(?<=^)#.*$)', re.M)
	return TAGS.findall(description)

def getQuery(query, calendarId = 'primary',maxResults = None,timeTuple = (None, None),log=True):
	start_time, end_time = [dtToGCString(t) for t in timeTuple]#datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	if log:
		print('Getting %supcoming %s events'%("the " if not maxResults else str(maxResults), query))

	events_result = CAL.events().list(calendarId = calendarId, timeMin = start_time, timeMax = end_time, 
										q = query, singleEvents = True, maxResults = maxResults,
										orderBy = 'startTime').execute()
	events_result["calendarId"] = calendarId
	if not log:
		return events_result

	events = events_result.get('items', [])
	if not events:
		print('No upcoming events found.')
	else:
		print('Found %i event/s'%len(events))
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		print(start+" "+ event['summary']+" Tags:'%s'"%(", ".join(getTags(event))))
	print()
	return events_result

def filterEvents(events, **kwargs):
	filters = {}
	if "filter_dict" in kwargs:
		filters = kwargs["filter_dict"]
	else:
		filters = kwargs

	""" filter looks like:
	filters = {
		"summary":None,
		"summary_r":None,
		"description":None,
		"description_r":None
		"tags":[""],
		"no_tags":[""]
	}
	"""
	def filterFunction(x):
		for field, fil in filters.items():
			#No entry at field
			if fil == None:
				continue

			if field == "tags":
				tags_in_event = getTags(x)
				for tag in fil:
					if tag not in tags_in_event:
						return False
			elif field == "no_tags":
				tags_in_event = getTags(x)
				for tag in fil:
					if tag in tags_in_event:
						return False
			elif field[-2:] == '_r':
				#fil is a re.compile
				if not re.match(fil, x[field[:-2]]):
					return False
			else:
				#fil is a str
				if not x[field] == fil:
					return False
		return True

	ret = events
	ret["items"] = list(filter(filterFunction, events["items"]))
	return ret

def pprintEvent(event):
	if("date" in event["start"]):
		parse_pattern = "%Y-%m-%d"
		event_start = event['start']['date']
		event_end  =  event['end']['date']
	else:
		parse_pattern = "%Y-%m-%dT%H:%M:%S%z"
		event_start = event['start']['dateTime'][:22] + event['start']['dateTime'][23:]
		event_end  =  event['end']['dateTime'][:22] + event['end']['dateTime'][23:]
	#YYYY-mm-ddTHH:MM:SS+01:00 #get rid of last :

	event_start = datetime.datetime.strptime(event_start, parse_pattern)
	event_end  =  datetime.datetime.strptime(event_end, parse_pattern)
	difference = event_end - event_start
	location = " @ %s"%event["location"] if "location" in event else ""
	display_pattern = "%d.%m.%Y %H:%M:%S"
	if "description" in event:
		tags, description = list(evaluateDescriptionEvent(event).values())
		if description:
			description = "'%s'"%(description.replace("\n", "\t").replace("\r", ""))
			description = "\n"+re.sub(r'(?<!\n)\n(?!\n)|\n{3,}', '\n', description)
			description = re.sub(r'(?<!\s)\s(?!\s)|\s{3,}', ' ', description)
		else:
			description = ""
		if tags:
			tags = "\ntags:%s"%", ".join([x[1:] for x in tags])
		else:
			tags = ""
	else:
		tags = ""
		description = ""
	print("%s - %s (%s):\n%s%s%s%s\n"%(datetime.datetime.strftime(event_start, display_pattern),
						datetime.datetime.strftime(event_end, display_pattern),
						str(difference),
						event["summary"], location, description, tags))
	#TODO add parser and formater

def evaluateDescriptionEvent(event):
	input_data = event["description"]
	TAG_RE = re.compile('(?:(#.+)\n)')
	DESCRIPTION_RE = re.compile('(?:#[^\n.]*\n)+\n*(.*)$', re.DOTALL)

	tags = getTags(event)
	description = DESCRIPTION_RE.findall(input_data)
	if not description:
		description = ""
	else:
		description = description[0]
	return {
		"tags":tags,
		"description":description
	}

def updateEventsTags(events, descriptionTags = [], filter_dict=None):
	if filter_dict:
		events = filterEvents(events, filter_dict)

	events_list = events.get("items", [])
	calendarId = events["calendarId"] 

	if(type(descriptionTags) == list):
		description_prefix = strip("\n".join(descriptionTags))
	else:
		description_prefix = descriptionTags

	for event in events_list:
		BODY = {
			"description":  strip("%s\n%s"%(description_prefix, event.get("description", "")))
		}
		e = CAL.events().patch(calendarId = calendarId, eventId = event["id"], body = BODY).execute()
		if not e:
			raise Exception(e)

if __name__ == '__main__':


	import pprint, json
	pprint = pprint.PrettyPrinter(indent = 4)
	#print(json.dumps(CAL.calendarList().list().execute(), indent = 3))
	TODAY = datetime.date.today()
	AFTER = TODAY+datetime.timedelta(days = 10)
	with open("private/pers_data.json") as read_file:
		my_mail = json.load(read_file)["mail"]

	eventz = getQuery("", calendarId = my_mail, timeTuple = (TODAY, AFTER), log=False)
	pprintEvent(eventz["items"][3])

	"""
	day_after = tomorrow_date+datetime.timedelta(days = 1)
	getQuery("KN", calendarId = my_mail, timeTuple = (TODAY, None))["items"]"""