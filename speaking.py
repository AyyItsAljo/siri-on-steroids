import speech_recognition as sr
import os, webbrowser, smtplib
import pyttsx3
import pyaudio, random, json

#Load Phrases
with open("phrases.json", "r") as read_file:
	phrases = json.load(read_file)

#My classes
class UnrecognisableSoundException (Exception):
	pass

#TTS
engine = pyttsx3.init()
def talk(audio):
	if audio == "":
		return

	print(audio)

	engine.say(audio)
	engine.runAndWait()

def say(toSay):
	for key in toSay.split(" "):
		try:
			talk(random.choice(phrases[key]))
		except KeyError:
			print("Cannot find key \"" + key + "\" in phrases.")
		except:
			raise

#Set up speach recognition
recogniser = sr.Recognizer()
recogniser.pause_threshold = 0.8
recogniser.instant_energy_threshold=300
recogniser.dynamic_energy_threshold=True
#printMicrophones()

def listen(waitTime):
	try:
		with sr.Microphone(device_index=1, chunk_size=4096) as source:
			recogniser.phrase_time_limit=waitTime
			recogniser.adjust_for_ambient_noise(source, duration=0.5)
			audio = recogniser.listen(source, timeout=10)
		return recognise(audio)
	except Exception as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))

def recognise(audio):
	try:
		toRet = recogniser.recognize_google(audio);
		print("GSR: " + toRet) #Google Speech Recognition
		return toRet
	except sr.UnknownValueError:
		#print("Google Speech Recognition could not understand audio")
		pass
	except sr.RequestError as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))

def waitForCall():
	while(True):
		try:
			with sr.Microphone(device_index=1, chunk_size=4096) as source:
				recogniser.adjust_for_ambient_noise(source, duration=0.5)
				audio = recogniser.listen(source, timeout=10)
			txt = recognise(audio).lower()
			if "siri" in txt:
				os.system('color 70') #Listeninig
				say("greet greet_q")
				break
		except KeyboardInterrupt:
			end();
		except:
			pass
	while(True):
		try:
			return listen(10)
		except UnrecognisableSoundException as use: #Poskusi seenkrat, ce ne prepozna
			pass
	return waitForCall()

	
	waitForCall()

def noticeWaitCall():
	os.system('color 07')#default color
	ret = waitForCall()
	os.system('color 07')
	return ret

def end():
	say("end")
	exit();



if __name__ == "__main__":
	waitForCall()