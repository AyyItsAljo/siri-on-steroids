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


def getQuery(query, calendarId = 'primary',maxResults = None,timeTuple = (None, None)):
	start_time, end_time = [dtToGCString(t) for t in timeTuple]#datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

	print('Getting %s upcoming %s events'%("the" if not maxResults else str(maxResults), query))

	events_result = CAL.events().list(calendarId = calendarId, timeMin = start_time, timeMax = end_time, 
										q = query, singleEvents = True, maxResults = maxResults,
										orderBy = 'startTime').execute()

	events = events_result.get('items', [])
	if not events:
		print('No upcoming events found.')
	else:
		print('Found %i event/s'%len(events))
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		print(start, event['summary'])

	events_result["calendarId"] = calendarId
	return events_result

def getTags(event):
	summary = event.get("description", "")
	TAGS = re.compile('(?:(?<=^)#.*$)', re.M)
	return TAGS.findall(summary)

def filterEvents(events, **kwargs):
	print(kwargs)
	filters = {}
	if "filter_dict" in kwargs:
		filters = kwargs["filter_dict"]
	else:
		filters = kwargs

	"""
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


def evaluateDescription(input_data):
	TAG_RE = re.compile('(?:(#.+)\n)')
	DESCRIPTION_RE = re.compile('(?:#[^\n.]*\n)+\n*(.*)$', re.DOTALL)

	if HAS_TAG.match(input_data):
		tags = TAG_RE.findall(input_data)
		description = DESCRIPTION_RE.findall(input_data)

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
	pprint = pprint.PrettyPrinter(indent = 4).pprint
	#print(json.dumps(CAL.calendarList().list().execute(), indent = 3))
	TODAY = datetime.date.today()
	TOMORROW = TODAY+datetime.timedelta(days = 1)
	with open("private/pers_data.json") as read_file:
		my_mail = json.load(read_file)["mail"]

	eventz = getQuery("#bus", calendarId = my_mail, timeTuple = (TODAY, None))
	#updateEventsTags(eventz, "#bus", {"no_tags":"#bus"})

	for f_e in filterEvents(evs, {"summary_r":".*KN"})["items"]:
		start = f_e['start'].get('dateTime', f_e['start'].get('date'))
		pprint(start+" "+ f_e['summary']+" "+", ".join(getTags(f_e)))
	"""
	day_after = tomorrow_date+datetime.timedelta(days = 1)
	getQuery("KN", calendarId = my_mail, timeTuple = (TODAY, None))["items"]"""