import requests, time, datetime, pytz, json
from datetime import timezone
from bs4 import BeautifulSoup

def getCurrentSchoolWeek(ts=time.time()):
	isoCal = datetime.datetime.fromtimestamp(ts)
	firstSchoolWeek = datetime.datetime(isoCal.year + (0 if isoCal.month >= 9 else -1), 9, 1)

	while(firstSchoolWeek.isocalendar()[2] > 5):
		firstSchoolWeek += datetime.timedelta(days=1) #date of first school day

	while(isoCal.isocalendar()[2] >= 5):
		isoCal += datetime.timedelta(days=1)

	#(week[int], leto[int])
	return (isoCal.isocalendar()[1] - firstSchoolWeek.isocalendar()[1] + 1, isoCal.isocalendar()[0]) 

def extractTimestamp(input_dt):
	#timestamp[int]
	return int((time.mktime(input_dt.timetuple()) + input_dt.microsecond/1000000.0)*1000)


def getData(specials=True, log=False, full=False, week=getCurrentSchoolWeek()):
	form = {}
	form["id_profesor"] = 0
	form["id_ucilnica"] = 0
	form["qversion"] = 1

	#week = (teden, leto)
	form["teden"] = week[0]
	form["id_sola"] = "632"
	form["id_razred"] = "304912"
	form["id_dijak"] = "8823701"
	url = "https://www.easistent.com/urniki/ajax_urnik"
	s = requests.Session()

	post_data = s.post(url, data=form)
	post_data.encoding = 'ISO-8859-1'

	if log:
		with open("temp/last_eAsistent_static.html", "wb") as wf:
			wf.write(post_data.content)




	#handling the table
	dnevi = []
	urnik = {}
	posebnosti = {}
	soup = BeautifulSoup(post_data.content, 'html.parser')

	main_table = soup.find("table", class_="ednevnik-seznam_ur_teden")

	for day_col in main_table.find("tr").findChildren("th")[1:]: #ignore "Ura"
		#print(day_col.find_all("div")[1].getText() + " %i"%week[1])
		day_date = datetime.datetime.strptime(day_col.find_all("div")[1].getText() + " %i"%week[1], '%d. %m. %Y')#.astimezone(pytz.utc)
		day_name = day_col.find_all("div")[0].getText()
		#(datetime, String)
		dnevi.append((day_date, day_name))
		
	print (dnevi)
	for row_index, current_row in enumerate(main_table.findChildren("tr", recursive=False)[1:]):
		urnik[1] = []
		cells = current_row.findChildren("td", recursive=False)
		time_offset = abs(datetime.datetime.strptime(cells[0].find_all("div")[1].getText().split(" - ")[0], '%H:%M') - datetime.datetime(1900, 1, 1, 0, 0, 0, 0))
		#(time of the day[time_delta], name[String])
		day_time_tuple = (time_offset, cells[0].find_all("div")[0].getText())
		cells = cells[1:]
		for col_num, current_subject in enumerate(cells):
			subject_data = {
				"subject_abbr":"N/A",
				"subject":"N/A",
				"time":0,
				"time_print":"",
				"change":None,
				"prof":"N/A",
				"place":"N/A"
			}
			print(current_subject.getText() is "")
			#(datetime of subject[datetime], name[String])
			tuple_of_subject_time = (dnevi[col_num][0] + day_time_tuple[0], dnevi[col_num][1] + ", " +day_time_tuple[1])
			print(tuple_of_subject_time)

			subject_parse, prof_place = current_subject.find("div").findChildren(True , recursive=False)

			grpL_name_spec = subject_parse.find("tr").findChildren("td", recursive=False)
			subject_name, specialty, = grpL_name_spec[:2]

			print(specialty)


			subject_data["subject"] = subject_name.find("span")["title"]
			subject_data["subject_abbr"] = subject_name.getText()
			subject_data["prof"], subject_data["place"] = prof_place.getText().strip().split(", ")
			subject_data["time"] = extractTimestamp(tuple_of_subject_time[0])
			subject_data["time_print"] = tuple_of_subject_time[1]
			print(json.dumps(subject_data, indent=4))
			#urnik[tuple_of_subject_time[0]]
			break
		print()

if __name__ == "__main__":
	getData(log=True, week=(12, 2018))
