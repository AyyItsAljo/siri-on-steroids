import geopy, requests, json
from pprint import PrettyPrinter
from geopy.geocoders import Nominatim

class InvalidSearchName(Exception):
	pass

pp = PrettyPrinter(indent=4)

data = {
	"lat":None,
	"lon":None,
	"units":"metric",
	"appid":"4480dc2e68e7def57cad849b47ca443b"
}

def getLatLon(query_string):
	geolocator = Nominatim(user_agent="python-app")
	location = geolocator.geocode(query_string)
	if location == None:
		raise InvalidSearchName("Cannot find '%s'"%query_string)
	pp.pprint(location.raw)
	return (location.latitude, location.longitude)

def forecast_5day_3h(**kwargs):
	url5d3a = "http://api.openweathermap.org/data/2.5/forecast"
	if "name" in kwargs:
		data["lat"], data["lon"] = getLatLon(kwargs["name"])
	elif "lat" in kwargs and "lon" in kwargs:
		data["lat"], data["lon"] = kwargs["lat"], kwargs["lon"]
	else:
		print("Location Error")

	post_req = requests.post(url5d3a, params=data)
	post_req.encoding = 'ISO-8859-1'

	print(post_req.url)
	req_json = post_req.json()

	pp.pprint(req_json["city"])
	pp.pprint(req_json["list"][0:4])

def current_weather(**kwargs):
	urlnow = "http://api.openweathermap.org/data/2.5/weather"
	if "name" in kwargs:
		data["lat"], data["lon"] = getLatLon(kwargs["name"])
	elif "lat" in kwargs and "lon" in kwargs:
		data["lat"], data["lon"] = kwargs["lat"], kwargs["lon"]
	else:
		print("Location Error")

	post_req = requests.post(urlnow, params=data)
	post_req.encoding = 'ISO-8859-1'

	print(post_req.url)
	req_json = post_req.json()

	pp.pprint(req_json["name"])
	pp.pprint(req_json["main"])

if __name__ == '__main__':
	forecast_5day_3h(name = "Spodnja Lipnica, Radovljica, Slovenija")
	current_weather(name = "Spodnja Lipnica, Radovljica, Slovenija")

