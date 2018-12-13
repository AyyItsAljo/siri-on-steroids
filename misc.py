import speech_recognition as sr

def listMicrophones():
	temp_cycle = sr.Microphone.list_microphone_names()
	ret = ""
	for index, name in enumerate(temp_cycle):
		ret+=print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`\n".format(index, name))
	return "Microphones:\n'%s'"%ret