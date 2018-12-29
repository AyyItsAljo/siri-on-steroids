import json, requests, pytz, time, datetime
from bs4 import BeautifulSoup

with open("temp/eAsistent_login.json") as login_data:
	CREDZ = json.load(login_data)

s = requests.Session()
referrer_dict = {}
referrer_dict["referer"] = "https://www.easistent.com"

s.headers.update(referrer_dict)
url = "https://www.easistent.com/p/ajax_prijava"
pre_post_js = s.post(url, data=CREDZ)

pre_post_js.encoding = 'ISO-8859-1'
pre_post_data = pre_post_js.json()

if(pre_post_data["status"] == "ok"):
	print(pre_post_data['data'])
	s.get(pre_post_data['data']['prijava_redirect'])
	get_data = s.get("https://www.easistent.com/m/timetable/weekly?from=2018-12-03&to=2018-12-09")
	get_data.encoding = 'ISO-8859-1'
	#print(get_data.content)
	with open("temp/last_eAsistent_dy.html", "wb") as wf:
		wf.write(get_data.content)


	cookie = {'name':'PHPSESSID'}
	cookie['value'] = sesid
	referrer_dict = {}
	referrer_dict["referer"] = url
	
	s.headers.update(referrer_dict)