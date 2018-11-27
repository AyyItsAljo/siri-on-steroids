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

#Custom function
def printMicrophones():
	for index, name in enumerate(sr.Microphone.list_microphone_names()):
		print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))


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


#Set up command, wait for prompt...
def command(cmd):
	if cmd == None:
		raise UnrecognisableSoundException()
	cmd = cmd.lower();
	if "good bye" in cmd:
		end();

	if "play" in cmd:
		talk("Playing music")
	elif "print the microphones" in cmd:
		talk("Those are the microphones")
		printMicrophones()
	

def waitForCall():
	os.system('color')
	#print(chr(27) + "[2J")
	while(True):
		try:
			with sr.Microphone(device_index=1, chunk_size=4096) as source:
				recogniser.adjust_for_ambient_noise(source, duration=0.5)
				audio = recogniser.listen(source, timeout=10)
			txt = recognise(audio).lower()
			if "julia" in txt or "julie" in txt:
				say("greet greet_q")
				break
		except KeyboardInterrupt:
			end();
		except:
			pass

	os.system('color 70')
	while(True):
		try:
			command(listen(10))
			break
		except UnrecognisableSoundException as use: #Poskusi seenkrat
			pass

	os.system('color')
	waitForCall()

def end():
	say("end")
	exit();



if __name__ == "__main__":
	os.system('cls')
	waitForCall()