import datetime, time

english_day_names = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

interactions = {
    "greet_q": [
        "What can I do for you?", 
        "How can I help?", 
        "How can I help you?",
        "What do you want me to do?"
    ], 
    "greet": [
        "Hi!", 
        "Hello!",
        "Whats up?"
    ],
	"end": [
        "Bye!", 
        "See ya soon!", 
        "Goodbye!", 
        "Catch you up later"
    ]
}

def extractTimestamp(input_dt):
    #timestamp[int]
    return int((time.mktime(input_dt.timetuple()) + input_dt.microsecond/1000000.0)*1000)

def extractDatetime(int_ts):
    return datetime.datetime.fromtimestamp(int_ts / 1e3)

def nameDate(time_stamp):
    dt = extractDatetime(time_stamp)
    print(list(dt.timetuple()))