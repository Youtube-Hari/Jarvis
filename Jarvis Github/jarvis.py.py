import datetime
from flask import request
from flask import jsonify
from flask import Flask, render_template
import requests
import speech_recognition as sr
import pyttsx3
import pyaudio
from flask import Flask, render_template
import playsound
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import struct
import pvporcupine
import wikipedia
import webbrowser as wb
import threading
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from jboy import play_music
from jboy import weather
from jboy import time
from jboy import date
from jboy import refresh
import pyaudio
import struct
import math
import os
import imaplib
from subprocess import call
import webbrowser
INITIAL_TAP_THRESHOLD = 0.1  # 0.01 - 1.5
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME


def get_rms(block):
    count = len(block)/2
    format = "%dh" % (count)
    shorts = struct.unpack(format, block)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt(sum_squares / count)


class TapTester(object):

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1
        self.quietcount = 0
        self.errorcount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range(self.pa.get_device_count()):
            devinfo = self.pa.get_device_info_by_index(i)
            # print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    # print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print("No preferred input found; using default input device.")

        return device_index

    def open_mic_stream(self):
        device_index = self.find_input_device()

        stream = self.pa.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=INPUT_FRAMES_PER_BLOCK)

        return stream

    def listen(self):

        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)

        except IOError as e:
            self.errorcount += 1
            print("(%d) Error recording: %s" % (self.errorcount, e))
            self.noisycount = 1
            return

        amplitude = get_rms(block)

        if amplitude > self.tap_threshold:
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > OVERSENSITIVE:

                self.tap_threshold *= 1.1
        else:

            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                return "True-Mic"
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > UNDERSENSITIVE:
                self.tap_threshold *= 2


def Tester():

    tt = TapTester()

    while True:
        kk = tt.listen()

        if "True-Mic" == kk:
            print("")
            print("> Clap Detected : Starting Jarvis.")
            print("")
            # os.startfile("MAIN_JARVIS_FILE_PATH")
            return "True-Mic"


credentials = json.load(open("secrets.json"))

api_server_url = "localhost"

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[0].id)
engine.setProperty('voices', voices[len(voices) - 1].id)

# Define the vectorize_text function

# def speak(audio):
#     engine.say(audio)
#     print(audio)
#     engine.runAndWait()


# def SpeakText(command):

#     # Initialize the engine
#     engine = pyttsx3.init()
#     engine.say(command)
#     engine.runAndWait()


def speak(message):
    print("working")
    msg = message  # "hello test"
    voice = requests.get(
        f"https://api.carterapi.com/v0/speak/{'YpGA8DTL8pBp32RiyKJeuvADqZrTfldV'}/{msg}", stream=True)
    with open('temp.mp3', 'wb') as f:
        for chunk in voice.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    try:
        print(f"Friday: {message}")
        playsound.playsound('temp.mp3')
        # remove temp file
        os.remove('temp.mp3')
        return render_template("index.html")
    except Exception as error:
        print(f"An error has showed up : {error}")


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def get_unread_emails():
    EMAIL = "#@gmail.com"
    PASS = '#'
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        # Login to the account
        mail.login(EMAIL, PASS)

        # Select the inbox
        mail.select("inbox")

        # Search for unread messages
        status, response = mail.search(None, 'UnSeen')

        # Count the number of unread messages
        unread_msg_nums = response[0].split()
        total_unread = len(unread_msg_nums)

        main_unread_emails = {'emails': f'{total_unread}'}
        speak(jsonify(main_unread_emails))
    except Exception as e:
        speak(jsonify({'error': str(e)}))
        print("error")
    finally:
        mail.logout()


def alarm(query):
    timehere = open("Alarmtext.txt", "a")
    timehere.write(query)
    timehere.close()
    call(["python", "alarm.py"])
    os.startfile("alarm.py")


Nameforai = "jarvis"


@app.route("/startListening")
def startListening():
    # speak("Hello tiktok Happy New Year Welcome to 2023")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 400
        audio = r.listen(source)
        print("Recognizing")
        try:
            query = r.recognize_google(audio, language='en-in')
            # query = input("How can I help you? ")
            print(query)
            if "Jarvis" in query:
                query = query.replace("Jarvis", "")
                r = requests.post('https://api.carterapi.com/v0/chat', json={
                    'api_key': credentials["carter"]["token"],  # change it
                    'query': query,
                    'uuid': "user-id-123",  # change
                })
                print(r.json())
                agent_response = r.json()
                speak(agent_response['output']['text'])

                if agent_response["triggers"][0]["type"] == "play music":
                    play_music()

                if agent_response["triggers"][0]["type"] == "weather":
                    api_key = "#"
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
                        speak(" Temperature = " + str(current_temperature) +
                              "\n description = " + str(weather_description))

                if agent_response["triggers"][0]["type"] == "stop":
                    print("ok")
                    return "stop"

                if agent_response["triggers"][0]["type"] == "date and time":
                    now = datetime.datetime.now()
                    speak("the current date and time is... ")
                    speak(now.strftime("%Y-%m-%d the time is %H:%M:%S"))

                if agent_response["triggers"][0]["type"] == "how much emails":
                    speak("ok")
                    speak("yes")
                    get_unread_emails()

                if agent_response["triggers"][0]["type"] == "set alarm":
                    print("input time example:- 10 and 10 and 10")
                    speak("Set the time")
                    a = input("Please tell the time :- ")
                    alarm(a)
                    speak("Done,sir")

                if agent_response["triggers"][0]["type"] == "tony stark music":
                    webbrowser.open(
                        "https://www.youtube.com/watch?v=bcyvZIoQp9A&ab_channel=WadeWojcik")

        except Exception as e:
            print("Sorry, I didn't get that")
            return "waiting for command"


app.run(host="0.0.0.0", port=80)
# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host='0.0.0.0', port=80)
