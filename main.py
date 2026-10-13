import speech_recognition as sr
import pyttsx3 
import os
import webbrowser
import datetime
import pyautogui
import requests
import feedparser
import time
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
from send2trash import send2trash
import psutil
import subprocess
import socket
import urllib.parse
import threading
import json
from word2number import w2n
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
from win10toast import ToastNotifier
import re
from ollama import Client

MEMORY_FILE = "memory.json"

 
# ==========================
# MAIN ANSWER BY AGANI A.I.
# ==========================
client = Client()  
def ai_response(prompt): 
     
     try:
          response = client.chat(
               model="llama3.2:latest",
               messages=[{"role": "user", "content":prompt}]
          )
          return response["message"]["content"].strip().strip("'").strip('"') 

     except Exception:
          return "Sorry sir, I could not connect to my AI brain right now."

# ==========================
# VOLUME CONTROL RULES
# ==========================
devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(  
     IAudioEndpointVolume._iid_,
     CLSCTX_ALL,
     None
) 

volume = cast(interface, POINTER(IAudioEndpointVolume))


# ==========================
# VOSK SETUP
# ==========================

SetLogLevel(-1)

VOSK_MODEL_PATH = r"D:\Python\AganiAI\vosk-model"

vosk_model = Model(VOSK_MODEL_PATH)


# ==========================
# TEXT TO SPEECH (Speak) Response by AI
# ==========================

def say(text):
    
    engine = pyttsx3.init()

    print(f"AganiAI : {text}")
    engine.say(text)
    engine.runAndWait()
        
# ==========================
# SPEECH TO TEXT (Listen) Our Command to AI
# ==========================

def take_Command():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:

        r.pause_threshold = 2.5
        r.energy_threshold = 300
        r.adjust_for_ambient_noise(source, duration=1)

        say("Listening...")

        try:
             audio = r.listen(source, timeout=7)

        except sr.WaitTimeoutError:
             say("I did not hear anything.")
             return ""

    try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"You : {query}")
            return query.lower()
    
    except sr.UnknownValueError:
         say("Sorry sir, I could not understand.")
         return ""

    except sr.RequestError:
         say("Sorry sir, the speech service is unavailable.")
         return ""

def take_Short_Command():

    short_grammar = json.dumps([
        "yes",
        "no",
        "nope",
        "okay",
        "ok",
        "sure"
    ])

    recognizer = KaldiRecognizer(
        vosk_model,
        16000,
        short_grammar
    )

    audio_queue = queue.Queue()

    def callback(indata, frames, time, status):

        if status:
            print(status)

        audio_queue.put(bytes(indata))

    say("Listening...")

    try:

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=4000,
            dtype="int16",
            channels=1,
            callback=callback
        ):

            while True:

                data = audio_queue.get()

                if recognizer.AcceptWaveform(data):

                    result = json.loads(
                        recognizer.Result()
                    )

                    text = result.get("text", "").strip().lower()

                    if text:
                        return text.lower()

    except Exception as e:

        say("Sorry sir, I could not process that command.")
        return ""

def take_Number_Command():

    number_grammar = json.dumps([
        "zero",

        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",

        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",

        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",

        "one hundred",
        "two hundred",
        "three hundred",
        "four hundred",
        "five hundred",
        "six hundred",
        "seven hundred",
        "eight hundred",
        "nine hundred",

        "one hundred fifty",
        "two hundred fifty",
        "three hundred fifty",
        "four hundred fifty",
        "five hundred fifty"
    ])

    recognizer = KaldiRecognizer(
        vosk_model,
        16000,
        number_grammar
    )

    audio_queue = queue.Queue()

    def callback(indata, frames, time, status):

        if status:
            print(status)

        audio_queue.put(bytes(indata))

    say("Listening for number...")

    try:

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback
        ):

            while True:

                data = audio_queue.get()

                if recognizer.AcceptWaveform(data):

                    result = json.loads(
                        recognizer.Result()
                    )

                    text = result.get("text", "").strip()

                    if text:
                        return text.lower()

    except Exception as e:

        say("Sorry sir, I could not process the number.")
        return ""
    
def extract_number(text):

     if not text:
          return None

     text = text.lower().strip()

     words = text.split()

     for word in words:
          if word.isdigit():
               return int(word)

     number_words = []

     valid_number_words = {
        "zero", "one", "two", "three", "four",
        "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen",
        "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen", "twenty",
        "thirty", "forty", "fifty", "sixty",
        "seventy", "eighty", "ninety",
        "hundred", "thousand"}

     for word in words:
          if word in valid_number_words:
               number_words.append(word)

     if not number_words:
          return None

     try:
          return w2n.word_to_num(" ".join(number_words))

     except:
          return None
     
# ==========================
# Command Functions
# ==========================
def search_website(query, site):

     prompt = f"""
               Extract only what the user wants to search.

               Sentence:
               {query}

               Website:
               {site}

               Rules:
               - Return only the search query.
               - Remove command words such as "search", "search for", "look for", "find", "open", "on".
               - Remove the website name.
               - Keep the actual search topic exactly as intended by the user.
               - Do not remove words that are part of the search topic.
               - Do not add explanation.
               - Do not add quotation marks.
               - If no search query is found, return exactly: None

               Examples:
               "Open YouTube and search Python tutorial"
               -> Python tutorial

               "Search Django tutorial on Google"
               -> Django tutorial

               "Search laptops on Amazon"
               -> laptops

               "Find machine learning courses on YouTube"
               -> machine learning courses

               "Search Batman and Superman on Google"
               -> Batman and Superman
               """

     search_query = ai_response(prompt).strip()

     if not search_query or search_query.lower() == "none" or "could not connect to my ai brain" in search_query.lower():
          say("Sorry sir, I could not understand what you want to search.")
          return

     encoded_query = urllib.parse.quote_plus(search_query) 

     url = search_sites[site].format(encoded_query) 

     say(f"Searching {search_query} on {site}.")

     webbrowser.open(url)

def tell_time():
     current_time = datetime.datetime.now().strftime("%I:%M %p") 
     say(f"Sir, The current time is {current_time}")

def tell_day():
     current_day = datetime.datetime.now().strftime("%A")
     say(f"Sir, Today is {current_day}")

def tell_date():
     current_date = datetime.datetime.now().strftime("%d %B %Y") 
     say(f"Sir, Today's date is {current_date}")

def take_screenshot(): 
     os.makedirs("Screenshots", exist_ok=True) 

     filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

     screenshot = pyautogui.screenshot()

     screenshot.save(f"Screenshots/{filename}.png")
     say("Sir, Screenshot saved successfully!")

def copy_text():
     pyautogui.hotkey("ctrl", "c")
     say("Copied successfully.")

def paste_text():
     pyautogui.hotkey("ctrl", "v")
     say("Pasted successfully.")

def cut_text():
     pyautogui.hotkey("ctrl", "x")
     say("Cut successfully.")

def select_all():
     pyautogui.hotkey("ctrl", "a")
     say("Selected all.")

def shutdown_pc():
     say("Are you sure you want to shut down your computer?")
     answer = take_Short_Command().lower()

     if "yes" in answer:
          say("Ok Ashish, Shutting down your computer")
          os.system("shutdown /s /t 5") 

     else:
          say("Shutdown cancelled.")

def restart_pc():
     say("Are you sure you want to restart your computer?")
     answer = take_Short_Command().lower()

     if "yes" in answer:
          say("Ok Ashish, Restarting your computer")
          os.system("shutdown /r /t 5") 

     else:
          say("Restart cancelled.")

def lock_pc():
     say("Ok Ashish, Locking your computer")
     os.system("rundll32.exe user32.dll,LockWorkStation")

def tell_weather():
     while True:

          say("Which city's weather would you like to know sir?")
          query = take_Command()
          if not query:  
               say("Sorry, I could not hear you. please say the city name again.")
               continue

          city_prompt = f"""
                    Extract only the city name from this sentence.
                    
                    Sentence: {query}
                    
                    Rules:
                    - Return only the city name.
                    - Do not write any explanation.
                    - Do not add punctuation.
                    - If there is no city, return exactly: None
                    """
          
          city = ai_response(city_prompt).strip()

          if city.lower() == "none":
               say("I could not find the city name. please say it again.")
               continue

          encoded_city = urllib.parse.quote_plus(city)

          url = f"https://wttr.in/{encoded_city}?format=j1"

          try:
               weather_response = requests.get(url, timeout=10)

               data = weather_response.json()

               if "current_condition" not in data:
                    say("Sorry, I could not get the weather information right now.")
                    continue

          except Exception:
               say("I could not connect to the weather service. please try again later.")
               break

          current = data["current_condition"][0]

          temperature = current["temp_C"]
          feels_like = current["FeelsLikeC"]
          humidity = current["humidity"]
          description = current["weatherDesc"][0]["value"]
          wind = current["windspeedKmph"]

          say(
               f"The weather in {city} is {description}. "
               f"The temperature is {temperature} degrees Celsius. "
               f"It feels like {feels_like} degrees Celsius. "
               f"The humidity is {humidity} percent. "
               f"The wind speed is {wind} kilometers per hour"
          )

          say("Would you like to know the weather for another city?")
          time.sleep(0.1)
          answer = take_Short_Command().lower()

          if "yes" in answer:
               continue

          elif "no" in answer:
               say("Alright. Let me know if you need anything else.")
               break

          else:
               say("I could not understand your answer. Alright, I'm ready for next command.")
               break

def tell_news():
     while True:

          say("Which topic would you like the latest news about?")
          query = take_Command()
          if not query:
               say("Soory, I could not hear you. Please say the topic again.")
               continue

          topic_prompt = f"""
                    Extract only the news topic from this sentence.

                    sentence: {query}
                    
                    Rules:
                    - Return only the topic.
                    - Do not write any explanation.
                    - Do not add punctuation.
                    - If no topic is found, return exactly: None
                    """

          topic = ai_response(topic_prompt)
          if topic.lower() == "none":
               say("I could not find the news topic. Please say it again.")
               continue

          while True:

               say("How many news headlines would you like?")

               count = take_Number_Command()

               news_count = extract_number(count)

               if news_count is not None:
                    break

               say("I could not understand the number. Please say it again.")

          encoded_topic = urllib.parse.quote_plus(topic)
          url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-IN&gl=IN&ceid=IN:en"

          feed = feedparser.parse(url)

          if len(feed.entries) == 0:
               say(f"Sorry, I could not find any news about {topic}.")
               continue

          news_count = min(news_count, len(feed.entries))

          say(f"I found {news_count} latest news articles about {topic}. "
              f"I will read all of them for you.") 

          for i, news in enumerate(feed.entries[:news_count], start=1):

               say(f"News {i}")

               say(news.title)

               time.sleep(0.2)

          say("Would you like news on another topic?")

          answer = take_Short_Command().lower()

          if "yes" in answer.lower():
               continue

          elif "no" in answer.lower():
               say("Alright. Let me know if you need anything else.")
               break

          else:
               say("I could not understand your answer. Alright, I am ready for next command.")
               break

def control_volume(query):
     current = int(volume.GetMasterVolumeLevelScalar() * 100)


     if "maximum volume" in query or query == "volume maximum" or "set volume to maximum" in query or "set volume to hundred" in query or "set volume to 100" in query:
        volume.SetMasterVolumeLevelScalar(1.0, None)
        say("The volume has been set to 100 percent.")
        return

     if "minimum volume" in query or query == "volume minimum" or "set volume to minimum" in query or "set volume to zero" in query or "set volume to 0" in query:
        say("The volume has been set to 0 percent.")
        volume.SetMasterVolumeLevelScalar(0.0, None)
        return

     if "mute volume" in query or query == "mute":
        say("Volume muted.")
        volume.SetMute(1, None)
        return

     if "unmute volume" in query or query == "unmute":
        volume.SetMute(0, None)
        say("Volume unmuted.")
        return

     prompt = f"""
          You are a volume command parser.

          User command:
          {query}

          Your ONLY job is to convert the command into ONE exact output.

          Allowed outputs:

          increase:NUMBER
          decrease:NUMBER
          set:NUMBER
          None

          Rules:
          - "volume to NUMBER" -> set:NUMBER
          - "set volume to NUMBER" -> set:NUMBER
          - "increase volume by NUMBER" -> increase:NUMBER
          - "increase volume NUMBER" -> increase:NUMBER
          - "decrease volume by NUMBER" -> decrease:NUMBER
          - "decrease volume NUMBER" -> decrease:NUMBER
          - NUMBER must be copied exactly from the user's command.
          - Never calculate the NUMBER.
          - Never subtract the NUMBER from another number.
          - Never use the current volume.
          - Never invent a NUMBER.
          - If the required NUMBER is missing, return None.
          - Return ONLY the command. No explanation.

          Examples:

          User: volume to 62
          Output: set:62

          User: set volume to 62
          Output: set:62

          User: volume to 100
          Output: set:100

          User: increase volume by 20
          Output: increase:20

          User: increase volume 20
          Output: increase:20

          User: decrease volume by 15
          Output: decrease:15

          User: decrease volume 15
          Output: decrease:15

          User: volume to
          Output: None

          User: set volume to
          Output: None                        
          """

     result = ai_response(prompt).strip().lower()

     if result == "none":
          say("Sorry, I could not understand the volume command.")
          return

     try:
          action, value = result.split(":", 1)
          value = int(value)

     except ValueError:
          say("Invalid volume command.")
          return

     if action == "increase":
          new = min(current + value, 100)

     elif action == "decrease":
          new = max(current - value , 0)

     elif action == "set":
          new = min(max(value, 0), 100)

     else:
          say("Unknown volume action.")
          return

     volume.SetMasterVolumeLevelScalar(new / 100, None)

     say(f"The volume has been set to {new} percent.")

def control_brightness(query):
     current = sbc.get_brightness(display=0)[0]  


     if "maximum brightness" in query or "brightness maximum" in query or "set brightness to maximum" in query or "set brightness to hundred" in query  or "set brightness to 100" in query:
         sbc.set_brightness(100, display=0)
         say("The brightness has been set to 100 percent.")
         return

     if "minimum brightness" in query or "brightness minimum" in query or "set brightness to minimum" in query or "set brightness to zero" in query  or "set brightness to 0" in query:
         sbc.set_brightness(0, display=0)
         say("The brightness has been set to 0 percent.")
         return

     prompt = f"""
               You are a brightness command parser.

               User command:
               {query}

               Your ONLY job is to convert the command into ONE exact output.

               Allowed outputs:

               increase:NUMBER
               decrease:NUMBER
               set:NUMBER
               None

               Rules:
               - "brightness to NUMBER" -> set:NUMBER
               - "set brightness to NUMBER" -> set:NUMBER
               - "increase brightness by NUMBER" -> increase:NUMBER
               - "increase brightness NUMBER" -> increase:NUMBER
               - "decrease brightness by NUMBER" -> decrease:NUMBER
               - "decrease brightness NUMBER" -> decrease:NUMBER
               - NUMBER must be copied exactly from the user's command.
               - Never calculate the NUMBER.
               - Never subtract the NUMBER from another number.
               - Never use the current brightness.
               - Never invent a NUMBER.
               - If the required NUMBER is missing, return None.
               - Return ONLY the command. No explanation.

          Examples:

          User: brightness to 62
          Output: set:62

          User: set brightness to 62
          Output: set:62

          User: brightness to 100
          Output: set:100

          User: increase brightness by 20
          Output: increase:20

          User: increase brightness 20
          Output: increase:20

          User: decrease brightness by 15
          Output: decrease:15

          User: decrease brightness 15
          Output: decrease:15

          User: brightness to
          Output: None

          User: set brightness to
          Output: None
          """

     result = ai_response(prompt).strip().lower()

     if result == "none":
          say("Sorry, I could not understand the brightness command.")
          return

     try:
          action, value = result.split(":", 1) 
          value = int(value)

     except ValueError:
          say("Sorry, I could not understand the brightness command.")
          return

     if action == "increase":
          new = min(current + value, 100)

     elif action == "decrease":
          new = max(current - value, 0)

     elif action == "set":
          new = min(max(value, 0), 100)

     else:
          say("Unknown brightness action.")
          return

     sbc.set_brightness(new, display=0)

     say(f"The brightness has been set to {new} percent.")

def clean_filename(text):

     text = text.lower().strip()

     text = text.replace("(", "")
     text = text.replace(")", "")
     text = text.replace("-", "")
     text = text.replace(".", "")
     text = text.replace("_", "")

     return text

def open_file(query):
     
     prompt = f"""
          You are a file-name extraction system for a Windows computer.

          User command:
          {query}

          Your task:
          Extract ONLY the actual file or folder name that the user wants to open.

          Rules:
          1. Remove command words such as:
          open, launch, start, show, run, access, file, folder
          2. Do NOT include these command words in the answer.
          3. Keep the actual name exactly as spoken.
          4. Keep numbers that are part of the name.
          5. Keep words like one, two, three if they are part of the name.
          6. Ignore punctuation differences such as:
          ( ), -, _, .
          7. Do not add words that were not in the user's command.
          8. Do not explain anything.
          9. Return ONLY the name.
          10. If the user did not provide a file or folder name, return exactly:
          None

          Examples:

          "open Ashish IM file" -> Ashish IM
          "open title 1" -> title 1
          "open title (1)" -> title (1)
          "open my project folder" -> my project
          "launch AganiAI.py" -> AganiAI.py
          "open report-final.pdf" -> report-final.pdf
          "show Python folder" -> Python
          "open result" -> result
          "open sem 4" -> sem 4
          "open" -> None

          """

     filename = ai_response(prompt)

     if not filename or filename.lower() == "none":
          say("I could not understand the file name.")
          return

     filename = clean_filename(filename)

     drives = [                 
               os.path.expanduser("~/Desktop"),
               os.path.expanduser("~/Documents"),
               os.path.expanduser("~/Downloads"),
               "D:\\",
               "E:\\"
               ]

     for drive in drives:

          if not os.path.exists(drive):
            continue

          for root, dirs, files in os.walk(drive):

               for file in files:

                    clean_file = clean_filename(file)  

                    if filename.lower() in clean_file.lower():

                         full_path = os.path.join(root, file)
                         say(f"I found {file}. Opening it.")

                         try:
                              os.startfile(full_path)
                              return

                         except FileNotFoundError:
                              say("Sorry sir, I found the file but could not open it.")
                              continue

                         except OSError:
                              say("Sorry sir, Windows could not open this file.")
                              continue

                         except Exception:
                              say("Sorry sir, I could not open this file.")
                              continue
                         
     say(f"Sorry sir, I could not find {filename}.")

def delete_file(query):

     prompt = f"""
               You are a file-name extraction system for a Windows computer.

               User command:
               {query}

               Your task:
               Extract ONLY the actual file or folder name that the user wants to delete.

               Rules:
               1. Remove action words such as:
                  delete, remove, erase, trash
               2. Remove generic type words such as:
                  file, folder, document
               3. Do NOT include those words in the answer.
               4. Keep the actual file or folder name.
               5. Keep numbers that are part of the name.
               6. Keep words like one, two, three if they are part of the name.
               7. Do not invent or change the file/folder name.
               8. Do not add words that were not spoken.
               9. Ignore punctuation differences such as:
                  ( ), -, _, .
               10. Return ONLY the file or folder name.
               11. If no file or folder name is provided, return exactly:
               None

               Examples:

               "delete Ashish IM file" -> Ashish IM
               "delete title 1" -> title 1
               "delete title (1)" -> title (1)
               "remove my project folder" -> my project
               "erase AganiAI.py" -> AganiAI.py
               "delete report-final.pdf" -> report-final.pdf
               "remove Python folder" -> Python
               "delete result" -> result

               IMPORTANT:
               Your response must contain ONLY the file or folder name.
               Do not repeat the rules.
               Do not repeat any instruction.
               Do not write any explanation.
               Do not write a second line.
               Do not write quotation marks.
               Return exactly ONE line.
               """   

     filename = ai_response(prompt)  

     if not filename or filename.lower() == "none":
          say("I could not understand the file name.")
          return

     filename = clean_filename(filename)

     search_paths = [
                    os.path.expanduser("~/Desktop"),
                    os.path.expanduser("~/Documents"),
                    os.path.expanduser("~/Downloads"),
                    "D:\\", 
                    "E:\\"]

     for path in search_paths:
          
          if not os.path.exists(path):
                      continue

          for root, dirs, files in os.walk(path):

               for file in files:

                    clean_file = clean_filename(file) 
                    
                    if filename.lower() in clean_file.lower():
                         
                         full_path = os.path.join(root, file)

                         say(f"I found {file}.")     
                         say("Are you sure you want to delete it?")

                         answer = take_Short_Command().lower()

                         if "yes" in answer:
                              
                              try:
                                   full_path = os.path.abspath(os.path.normpath(full_path))

                                   send2trash(full_path)
                                   say("File moved to recycle bin successfully.")

                              except FileNotFoundError:
                                   say("Sorry sir, the file could not be found.")

                              except Exception:
                                   say("Sorry sir, I could not delete the file.") 

                         else:
                              say("Deletion cancelled.")  

                         return
   
               for folder in dirs:

                    clean_folder = clean_filename(folder)
                    
                    if filename.lower() in clean_folder.lower():

                         full_path = os.path.join(root, folder)

                         say(f"I found folder {folder}.")
                         say("Are you sure you want to delete it?") 

                         answer = take_Short_Command().lower()

                         if "yes" in answer:
                              
                              try:
                                   full_path = os.path.abspath(os.path.normpath(full_path))

                                   send2trash(full_path)
                                   say("Folder moved to recycle bin successfully.")

                              except FileNotFoundError:
                                   say("Sorry sir, the folder could not be found.")

                              except Exception:
                                   say("Sorry sir, I could not delete the folder.")

                         else:
                              say("Deletion cancelled.")  

                         return

     say("Sorry sir, I could not find that file or folder.")                                                                   

def bettery_percentage():

     battery = psutil.sensors_battery()

     if battery is None:
          say("Sorry sir, Battery information is not available.")
          return

     percent = int(battery.percent)

     if battery.power_plugged:
          say(f"Battery is {percent} percent and the charger is connected.")

     else:
          say(f"Battery is {percent} percent and the charger is not connected.")

def cpu_information(): 

     processor = subprocess.check_output(
          "wmic cpu get name", 
          shell=True).decode().split("\n")[1].strip() 

     usage = psutil.cpu_percent(interval=1) 

     say(f"The processor is {processor}")
     say(f"Current CPU usage is {usage} percent.")

def ram_usage():

     memory = psutil.virtual_memory()

     used = round(memory.used / (1024 ** 3), 2) 
     total = round(memory.total / (1024 ** 3), 2) 
     percent = memory.percent

     say(f"You are using {used} GB out of {total} GB RAM. Usage is {percent} percent.")

def disk_usage():  

     drives = ["C:\\", "D:\\", "E:\\"]
     names = ["C", "D", "E"]

     for drive,name in zip(drives, names):

          if not os.path.exists(drive):
               continue
          
          disk = psutil.disk_usage(drive)

          used = round(disk.used / (1024 ** 3), 2)
          total = round(disk.total / (1024 ** 3), 2) 
          percent = disk.percent

          say(f"The {name} drive is {used} GB used out of {total} GB. Usage is {percent} percent.")

def ip_address():

     ip = socket.gethostbyname(socket.gethostname())  
     say(f"Your IP address is {ip}")

def computer_name():

     name = socket.gethostname()
     say(f"The computer name is {name}")

def set_reminder(query):

     query = query.lower().strip()

     amount = extract_number(query)

     if amount is None or amount <= 0:
          say("Sorry sir, I could not understand the reminder time.")
          return

     if "second" in query or "sec" in query:
          seconds = amount

     elif "minute" in query or "min" in query:
        seconds = amount * 60

     elif "hour" in query or "hr" in query:
         seconds = amount * 3600

     else:
          say("Please specify seconds, minutes, or hours, sir.")
          return

     say("Okay sir, I will remind you.")

     toast = ToastNotifier()

     timer = threading.Timer( 
          seconds,
          lambda: toast.show_toast(
               "AganiAI Reminder", "Sir, you asked me to remind you.", duration=5, threaded=True) )

     timer.daemon = True 
     timer.start()

# ==========================
# MEMORY FUNCTIONS
# ==========================
def load_memory():

     if not os.path.exists(MEMORY_FILE):
          return {}

     try:
          with open(MEMORY_FILE, "r", encoding="utf-8") as file:
               data = json.load(file)

          if isinstance(data, dict): 
               return data

          return {}

     except(json.JSONDecodeError, OSError):
          return {}

     
def save_memory(memory): 
     try:
          with open(MEMORY_FILE, "w", encoding="utf-8") as file:
               json.dump(memory, file, indent=4, ensure_ascii=False) 

          return True

     except OSError:
          return False

def remember_memory(query): 
     prompt = f"""
               You are the memory extraction module of AganiAI.

               The user wants AganiAI to permanently remember information.

               USER:
               {query}

               Your job is ONLY to extract the information that the user wants to save.

               Return exactly ONE line:

               KEY: VALUE

               Rules:

               1. KEY must describe what the information is about.
               2. KEY must be lowercase.
               3. KEY may contain lowercase letters, numbers, and underscores.
               4. VALUE must contain only the information actually provided by the user.
               5. Never invent or guess any information.
               6. Do not use the user's actual value as the key.
               7. If the user gives a new value for an existing type of information, use the same logical key.
               8. The information can be ANYTHING:
                  name, college, course, favorite_language, favorite_food,
                  city, hobby, pet, goal, friend, family information,
                  preferred_browser, favorite_game, project_name, etc.
               9. Do NOT restrict yourself to the examples above.
               10. If there is no clear information to save, return:
               NONE
               11. Return only KEY: VALUE.
               12. Do not return explanation.
               13. Do not return markdown.
               """

     result = ai_response(prompt).strip()

     if not result or result.lower() == "none":
          say("Sorry sir, I could not understand what you want me to remember.")
          return

     if ":" not in result:
          say("Sorry sir, I could not understand what you want me to remember.")
          return

     key, value = result.split(":", 1)

     key = key.strip('"\'').lower()
     value = value.strip('"\' ')

     if not key or not value:
         say("Sorry sir, I could not understand what you want me to remember.")
         return

     # Key ko clean karo
     key = re.sub(r"[^a-z0-9_ ]", "", key)
     key = re.sub(r"\s+", "_", key)

     if not key:
         say("Sorry sir, I could not create a memory key.")
         return

     memory = load_memory()

     memory[key] = value

     save_memory(memory)

     say("Okay sir, I will remember that.")

def recall_memory(query): 
     
     memory = load_memory()

     if not memory:
          say("Sorry sir, I do not have anything saved in my memory.")
          return

     memory_text = "\n".join(f"{key}: {value}" for key, value in memory.items())

     prompt = prompt = f"""
               You are AganiAI, a personal memory assistant.

               Saved memory:
               {memory_text}

               User's question:
               {query}

               Instructions:

               - Use ONLY the saved memory.
               - If the user asks what you know about them,
                 what you remember about them,
                 what information they gave you,
                 or asks to tell/show their saved information,
                 list ALL saved information.
               - If the user asks about one specific fact,
                 answer using the matching saved information.
               - Never invent information.
               - Never say the memory is empty if information is present.
               - If the requested information is not present,
                 say: "I do not have that information in my memory."
               - Keep the answer short and clear.
               """

     answer = ai_response(prompt).strip()

     if not answer:
          say("Sorry sir, I could not find an answer in my memory.")
          return

     say(answer)

def forget_memory(query): 

     memory = load_memory()

     if not memory:
          say("Sorry sir, my memory is already empty.")
          return

     memory_text = "\n".join(f"{key}: {value}" for key, value in memory.items())

     prompt = f"""
               You are AganiAI's memory manager.

               Saved memory:
               {memory_text}

               User request:
               {query}

               Task:
               Identify which saved memory entry the user wants to forget.

               Rules:
               - Read all entries in the saved memory.
               - Match the user's request with the meaning of a saved key or its value.
               - The saved memory may contain any kind of information, not only name, college, or language.
               - Return the exact key as it appears in the saved memory.
               - Never invent a key.
               - Return only one key.
               - Do not return the value.
               - Do not add explanation or quotation marks.
               - If no saved entry matches the request, return exactly: NONE
               """

     key = ai_response(prompt).strip().lower()

     if not key or key == "none":
          say("Sorry sir, I could not find that information in my memory.")
          return

     if key not in memory:
        say("Sorry sir, I could not find that information in my memory.")
        return

     del memory[key]

     save_memory(memory)

     say(f"Okay sir, I have forgotten {key}")

# ==========================
# Agani A.I. Answer Format
# ==========================
def answer_by_aganiai(query):

     prompt = f"""
               You are AganiAI, a helpful personal AI assistant.

               User's question:
               {query}
               
               Answer according to the user's request.

               IMPORTANT RESPONSE RULES:

               1. DEFAULT:
                  - Give a short, direct and useful answer.
                  - Normally keep the answer around 2 to 5 sentences.
                  - Do not give unnecessary background information.
                  - Do not repeat the user's question.
                  - Do not add unnecessary examples.

               2. DETAILED ANSWER:
                  If the user explicitly asks for:
                  - a long answer
                  - a detailed answer
                  - a descriptive answer
                  - a full explanation
                  - an explanation in detail
                  - explain deeply
                  - explain everything
                  - more details
                  - elaborate
                  - a complete explanation

                  then give a detailed and well-structured answer.
                  Use headings, bullet points and examples when useful.

               3. FOLLOW-UP REQUESTS:
                  If the user asks something like:
                  - "tell me more"
                  - "explain more"
                  - "give more details"
                  - "go deeper"
   
                  then provide more detail than the previous answer.

               4. SIMPLE QUESTIONS:
                  If the question is simple and does not ask for details,
                  answer simply and directly.

               5. CODE:
                  If the user asks for code:
                  - Give working and relevant code.
                  - Keep the explanation brief unless the user asks for a detailed explanation.
                  - Do not add unnecessary code.

               6. CONVERSATIONAL STYLE:
                  - Answer naturally like a helpful personal AI assistant.
                  - Be clear and easy to understand.
                  - Do not start with unnecessary phrases like "Sure!" or "Certainly!".
                  - Do not mention these instructions.

""" 
     return ai_response(prompt)


# ==========================
# Main Code
# ==========================

if __name__=='__main__':
    say("Welcome to Agani A.I.")
    print("ollama serve RUN IT ON CMD...") 
    say("How can I assist you?, sir")
    
    while True:
        query = take_Command().strip().lower()

        if not query:
             continue
# ==========================
# 1. SEARCH WEBSITES
# ==========================
        search_sites = {
             "youtube":"https://www.youtube.com/results?search_query={}",
             "google":"https://www.google.com/search?q={}",
             "amazon":"https://www.amazon.in/s?k={}",
             "flipkart":"https://www.flipkart.com/search?q={}",
             "wikipedia":"https://en.wikipedia.org/wiki.Special:Search?search={}"
        }  
        matched = False
           
        for site in search_sites:
             if site in query and "search" in query:
                  search_website(query, site)
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 2. WEBSITES
# ==========================  
        sites = { 
             "youtube":"https://www.youtube.com",
             "google":"https://www.google.com",
             "gmail":"https://www.gmail.com",
             "wikipedia":"https://www.wikipedia.com",
             "chat":"https://chatgpt.com",
             "github":"https://github.com"
          }  
        matched = False
           
        for site in sites:
             if site in query:
                  say(f"opening {site} sir,...")
                  webbrowser.open(sites[site])
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 3. WINDOWS APPS
# ==========================
        apps = {
             "notepad":"notepad",
             "whatsapp":"whatsapp:",
             "calculator":"calc",
             "paints":"mspaint",
             "cmd":"cmd",
             "explorer":"explorer",
             "task manager":"taskmgr",
             "control panel":"control",
             "settings":"ms-settings:"
        }  
        matched = False
            
        for app in apps:
             if app in query:
                  say(f"Openning.. {app} sir,")
                  os.system(f"start {apps[app]}")
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 4. WINDOWS FOLDERS
# ==========================
        folders = {
             "desktop":r"C:\Users\hp\OneDrive\Desktop",
             "documents":r"C:\Users\hp\OneDrive\Documents",
             "downloads":r"C:\Users\hp\Downloads",
             "pictures":r"C:\Users\hp\OneDrive\Pictures",
             "videos":r"C:\Users\hp\Videos",
             "music":r"C:\Users\hp\Music"
        }  
        matched = False
           
        for folder in folders:
             if folder in query:
                  say(f"Opening..{folder} sir,")
                  os.system(f'explorer "{folders[folder]}"')
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 5. COMMANDS
# ==========================
        commands = {
             "time": tell_time,
             "day": tell_day,
             "date": tell_date,

             "screenshot": take_screenshot,
             "copy": copy_text,
             "paste": paste_text,
             "cut": cut_text,
             "select all": select_all,

             "shutdown": shutdown_pc,
             "restart": restart_pc,
             "lock": lock_pc,

             "weather": tell_weather,
             "news": tell_news
        }  
        matched = False
           
        for command in commands:
             if command in query:
                  commands[command]()
                  matched = True
                  break

        if matched:
             continue
# ==========================
# 6. VOLUME COMMAND
# ==========================
        volume_commands = [
             "increase volume", 
             "decrease volume",
             "volume up", "up volume",
             "volume down", "down volume", 
             "set volume", "set the volume", "set to volume",
             "mute",
             "unmute",
             "maximum volume",
             "minimum volume"
             ]  
        matched = False
           
        for cmd in volume_commands:
             if cmd in query:
                  control_volume(query)
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 7. BRIGHTNESS COMMAND
# ==========================
        brightness_commands = [
             "brightness",
             "screen brightness", "screen light",
             "dim", 
             "maximum brightness",
             "minimum brightness"
             ]  
        matched = False
           
        for cmd in brightness_commands:
             if cmd in query:
                  control_brightness(query)
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 8. FILE_OPEN COMMAND
# ==========================
        file_open_commands = ["find", "open", "play"] 
        matched = False
                   
        for cmd in file_open_commands:
               if cmd in query:
                  open_file(query)
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 9. FILE_DELETE COMMAND
# ==========================
        file_delete_commands = ["delete", "remove"] 
        matched = False
                   
        for cmd in file_delete_commands:
               if cmd in query:
                  delete_file(query)
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 10. System Information
# ==========================
        system_info_commands = {
             "battery":bettery_percentage,
             "charging":bettery_percentage,

             "cpu":cpu_information,
             "processor":cpu_information,

             "ram":ram_usage,
             "memory":ram_usage,

             "disk":disk_usage,
             "storage":disk_usage,
             "free space":disk_usage,

             "ip":ip_address,

             "computer name":computer_name,
             "device name":computer_name,
             "pc name":computer_name,
             "laptop name":computer_name
        }  
        matched = False
           
        for command in system_info_commands:
             if command in query:
                  system_info_commands[command]()
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 11. REMINDER ME PART
# ==========================
        reminder_commands = ["remind", "reminder"] 
        matched = False
                   
        for cmd in reminder_commands:
               if cmd in query:
                  set_reminder(query)
                  matched = True
                  break

        if matched:
             continue

# ==========================
# 12. Memory Ma Conversation Store Karav va
# ==========================
        remember_commands = [
             "remember",
             "do not forget that",
             "don't forget that",
             "keep in mind that",
             "note this",
             "note that"
        ]
        matched = False
                           
        for cmd in remember_commands:
             if cmd in query.lower():
                  remember_memory(query)
                  matched = True
                  break
        
        if matched:
             continue

# ==========================
# 13. Memory Ma Conversation Store Karav yu he e Puchva
# ==========================
        recall_commands = [
             # Specific memory
             "what is my name",
             "what is my college",
             "what is my college name",
             "what is my favorite language",

             # General memory
             "what do you know about me",
             "what do you remember about me",
             "what do you remember about me so far",

             # Remember questions
             "do you remember my name",
             "do you remember my college",
             "do you remember my favorite language",
             "do you remember what i told you",
             "do you remember anything about me",

             # Previous information
             "what information i tell you",
             "what did i tell you",
             "what did i tell you about myself",
             "what did i tell you about me",
             "what did i ask you to remember",
             "what information did i give you",
             "what information do you have about me",

             # Tell / show
             "tell me what you remember",
             "tell me what you know about me",
             "tell me what you know",
             "show me what you remember",
             "show me what you know about me",

             # General
             "what have you remembered about me",
             "what have you saved about me",
             "what information have you remembered",
             "what information have you saved",
             "what have you stored about me",
             "what do you have saved about me",

             # Direct memory
             "check your memory",
             "check my memory",
             "check what you remember",
             "look in your memory",
             "look at my memory",
             "tell me my saved information"
        ]
        matched = False
                           
        for cmd in recall_commands:
             if cmd in query.lower():
                  recall_memory(query)
                  matched = True
                  break
        
        if matched:
             continue

# ==========================
# 14. Memory Ma Conversation Store Karav vyu hatu e Delete Karva
# ==========================
        forget_commands = [
             "forget this",
             "forget that",
             "forget my",
             "forget what i told you",
             "forget what i said",
             "don't remember",
             "do not remember",
             "remove from memory",
             "delete from memory",
             "erase from memory"
        ]
        matched = False
                           
        for cmd in forget_commands:
             if cmd in query.lower():
                  forget_memory(query)
                  matched = True
                  break
        
        if matched:
             continue

# ==========================
# 15. EXIT
# ==========================
        exit_commands = [
                     "exit aganiai", 
                     "quit aganiai",
                     "close aganiai",
                     "end conversation",
                     "end aganiai",
                     "close the conversation",
                     "close conversation",
                     "end the conversation",
                     "stop aganiai",
                     "goodbye aganiai"
                ]

        if any(cmd in query for cmd in exit_commands):
             say("Alright sir, I will be ready whenever you need me. Goodbye!")
             break

# ==========================
# 16. ANSWER BY AGANI A.I.
# ==========================
        answer = answer_by_aganiai(query)
        say(answer)
