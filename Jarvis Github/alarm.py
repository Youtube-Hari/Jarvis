import pyttsx3
import datetime
import os
import requests
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 200)

# 06:45:00


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


extractedtime = open("Alarmtext.txt", "rt")
time = extractedtime.read()
Time = str(time)
extractedtime.close()

deletetime = open("Alarmtext.txt", "r+")
deletetime.truncate(0)
deletetime.close()


def weather():
    api_key = "2ff81b590c6dd344b80a2ff9f4132c07"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = "London"
    complete_url = base_url + "appid=" + \
        'd850f7f52bf19300a9eb4b0aa6b80f0d' + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        z = x["weather"]
        weather_description = z[0]["description"]
        speak(" Temperature = " +
              str(current_temperature) + "\n description = " + str(weather_description))


def ring(time):
    timeset = str(time)
    timenow = timeset.replace("jarvis", "")
    timenow = timenow.replace("set an alarm", "")
    timenow = timenow.replace(" and ", ":")
    Alarmtime = str(timenow)
    print(Alarmtime)
    while True:
        currenttime = datetime.datetime.now().strftime("%H:%M:%S")
        if currenttime == Alarmtime:
            os.startfile("music.mp3")
            speak("Alarm ringing,sir")
            weather()
            speak("i trust you slept well")
            speak("you need to go to your bus stop at 7:14 make sure you get ready")

        elif currenttime + "00:00:30" == Alarmtime:  # You can choose any music or ringtone
            exit()


ring(time)
