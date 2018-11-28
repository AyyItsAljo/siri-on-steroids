from speaking import *

#Custom function
def printMicrophones():
	for index, name in enumerate(sr.Microphone.list_microphone_names()):
		print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

#Set up command, wait for prompt...
def myCommand(cmd):
	if cmd == None:
		raise UnrecognisableSoundException()
	cmd = cmd.lower();
	if "good bye" in cmd:
		end();

	if "play music" in cmd:
		talk("Playing music")
	elif "list the microphones" in cmd:
		talk("Those are the microphones")
		printMicrophones()

if __name__ == "__main__":
	os.system('cls')
	print("Welcome to Julia personal assistent!")
	while True:
		command = noticeWaitCall()
		myCommand(command)