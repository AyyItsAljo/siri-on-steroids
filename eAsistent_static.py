import requests, time, datetime
from datetime import timezone
from bs4 import BeautifulSoup

def getCurrentSchoolWeek(ts=time.time()):
	isoCal = datetime.datetime.fromtimestamp(ts)
	firstSchoolWeek = datetime.datetime(isoCal.year + (0 if isoCal.month >= 9 else -1), 9, 1)

	while(firstSchoolWeek.isocalendar()[2] > 5):
		firstSchoolWeek += datetime.timedelta(days=1) #date of first school day

	while(isoCal.isocalendar()[2] >= 5):
		isoCal += datetime.timedelta(days=1)

	return (isoCal.isocalendar()[1] - firstSchoolWeek.isocalendar()[1] +1, isoCal.isocalendar()[0])
	#return st

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


	urnik = {}
	soup = BeautifulSoup(post_data.content, 'html.parser')

	main_table = soup.find("table", class_="ednevnik-seznam_ur_teden")


	for day_col in main_table.find("tr").findChildren("th")[1:]: #ignore "Ura"
		print(day_col.find_all("div")[1].getText() + " %i"%week[1])
		day_date = datetime.datetime.strptime(day_col.find_all("div")[1].getText() + " %i"%week[1], '%d. %m. %Y')
		urnik[(day_date- datetime(1970, 1, 1)).total_seconds()] = {}
		
	print (urnik)
	for i, current_row in enumerate(main_table.findChildren("tr", recursive=False)[1:]):
		urnik[0] = {}
		print(i)

if __name__ == "__main__":
	getData()