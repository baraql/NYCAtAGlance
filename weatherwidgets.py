from tkinter import *
from tkinter.ttk import *
from datetime import datetime
from dataclasses import dataclass
import requests
from sun import Sun
from PIL import ImageTk, Image
import colorsys
import os
from os.path import exists

dirname = os.path.dirname(__file__)


class WeatherWidget(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        Frame.pack(self, expand=True, fill=X, side="bottom")

        self.uv = Label(self, text="_ UV", anchor="s",
                        font=('calibri', 16, 'bold'),
                        foreground='black')
        self.uv.pack(side="bottom")

        self.temp = Label(self, text="_ F", anchor="center",
                          font=('calibri', 28, 'bold'),
                          foreground='black')
        self.temp.pack(side="bottom")

        self.code = ImageTk.PhotoImage(
            WeatherWidgets.getWeatherCodeImage(1000, datetime.now()))
        self.codeLabel = Label(self, image=self.code)
        self.codeLabel.pack(side="bottom")
        self.codeLabel.image = self.code

        self.time = Label(self, text="0 AM", anchor="center",
                          font=('calibri', 14, 'bold'),
                          foreground='black')
        self.time.pack(side="bottom")

    def update(self, uv, temp, time, code):
        # TODO Fix hue equation
        hue = 255 - ((temp) / 80) * 240
        self.temp.config(
            text=temp, foreground=WeatherWidgets.hslToHex(hue, .7, .5))
        self.uv.config(text=uv, foreground=WeatherWidgets.uvColor(uv))

        self.time.config(text=time.strftime("%I%p").lstrip('0'))

        self.codeLabel.pack_forget()
        self.code = ImageTk.PhotoImage(
            WeatherWidgets.getWeatherCodeImage(code, time))
        self.codeLabel = Label(self, image=self.code)
        self.codeLabel.pack(side="bottom")
        self.codeLabel.image = self.code

        self.time.pack_forget()
        self.time.pack(side="bottom")


class WeatherWidgets:
    WEATHER_DISPLAY_BOXES = 8
    API_URL = "https://api.tomorrow.io/v4/timelines"
    COORDS = {'longitude': -73.986623, 'latitude': 40.722718}

    # Cache the sunrises and sunsets
    sunsets = []
    sunrises = []
    sun = Sun()

    def __init__(self, root):
        self.weatherHours = []
        self.weatherWidgets = []
        self.secondsUntilCheckSubway = 0
        self.weatherFrame = Frame(root)
        self.weatherFrame.pack(side="bottom", fill=X, expand=True)
        self.getWeather()
        for i in range(WeatherWidgets.WEATHER_DISPLAY_BOXES):
            print("appended " + str(i))
            self.weatherWidgets.append(WeatherWidget(self.weatherFrame))
        self.organizeWeatherLabels()

    querystring = {
        "location": (str(COORDS['latitude']) + ", " + str(COORDS['longitude'])),
        "fields": ["temperatureApparent", "uvIndex", "weatherCode"],
        "units": "imperial",
        "timesteps": "1h",
        "timezone": "America/New_York",
        "apikey": "ASPKCVnrURpVM1DIssX8ZwqwoNyX1VTx"
    }

    @ dataclass
    class WeatherHour:
        temp: int
        uvIndex: int
        weatherCode: int
        date: datetime

    def getWeather(self):
        response = requests.request(
            "GET", WeatherWidgets.API_URL, params=WeatherWidgets.querystring)
        print(response.text)

        if response.status_code // 100 == 2:
            print(response)
            results = response.json()['data']['timelines'][0]['intervals']
            for daily_result in results:
                date = datetime.strptime(
                    daily_result['startTime'], '%Y-%m-%dT%H:%M:%S-04:00')
                print("Given date: " +
                      str(daily_result['startTime']) +
                      "   extracted date:" +
                      str(date))
                temp = round(daily_result['values']['temperatureApparent'])

                try:
                    uvIndex = daily_result['values']['uvIndex']
                except KeyError:
                    uvIndex = -1
                weatherCode = daily_result['values']['weatherCode']
                self.weatherHours.append(
                    WeatherWidgets.WeatherHour(
                        temp=temp,
                        uvIndex=uvIndex,
                        date=date,
                        weatherCode=weatherCode))
        else:
            print("Error downloading weather: " + response.status_code)

    def isTheSunUp(time):
        date = (time.day, time.month, time.year)
        sunrise = 0
        for e in WeatherWidgets.sunrises:
            if e[0] == date:
                sunrise = (e[1], e[2])
        if sunrise == 0:
            sunrise = WeatherWidgets.sun.getSunriseTime(date,
                                                        WeatherWidgets.COORDS)
            sunrise = (sunrise['hr'] - 4, sunrise['min'])
            WeatherWidgets.sunrises.append(
                (date, sunrise[0], sunrise[1]))
            print("hadToAppendNewSunrise at " +
                  str(sunrise[0]) + ":" + str(sunrise[1]))

        sunset = 0
        for e in WeatherWidgets.sunsets:
            if e[0] == date:
                sunset = (e[1], e[2])
        if sunset == 0:
            sunset = WeatherWidgets.sun.getSunsetTime(date,
                                                      WeatherWidgets.COORDS)
            sunset = (24 + sunset['hr'] - 4, sunset['min'])
            WeatherWidgets.sunsets.append(
                (date, sunset[0], sunset[1]))
            print("hadToAppendNewSunset at " +
                  str(sunset[0]) + ":" + str(sunset[1]))

        hourAndMinute = (time.hour, time.minute)
        print("HOUR AND MINUTE: " + str(hourAndMinute) +
              "  SUNRISE: " + str(sunrise) + "  SUNSET: " + str(sunset) + "  (sunrise < hourAndMinute): " + str(sunrise < hourAndMinute) + "  (hourAndMinute < sunset): " + str(hourAndMinute < sunset))
        if sunrise < hourAndMinute and hourAndMinute < sunset:
            return True
        return False

    def getWeatherCodeImage(code, time):
        if not WeatherWidgets.isTheSunUp(time) and exists("assets/weather/" + str(code) + "1.png"):
            return Image.open(os.path.join(dirname,
                                           ("./assets/weather/" +
                                            str(code) +
                                               "1.png"))).resize(
                (30,
                 30),
                Image.LANCZOS)
        else:
            return Image.open(os.path.join(dirname,
                                           ("./assets/weather/" +
                                            str(code) +
                                               "0.png"))).resize(
                (30,
                 30),
                Image.LANCZOS)

    def hslToHex(h, s, l):
        r, g, b = [round(num * 255)
                   for num in colorsys.hls_to_rgb(h / 360, l, s)]
        return f'#{r:02x}{g:02x}{b:02x}'

    def uvColor(uv):
        if uv <= 2:
            return "#8dc443"
        elif uv <= 5:
            return "#fcd836"
        elif uv <= 7:
            return "#ffb300"
        elif uv <= 10:
            return "#d1394a"
        else:
            return "#954f71"

    def organizeWeatherLabels(self):
        print("organizeWeatherLabels: " + str(len(self.weatherWidgets)))
        for i in range(WeatherWidgets.WEATHER_DISPLAY_BOXES):
            # Update the times on the weatherWidgets
            self.weatherWidgets[i].update(
                uv=self.weatherHours[i].uvIndex,
                temp=self.weatherHours[i].temp,
                time=self.weatherHours[i].date,
                code=self.weatherHours[i].weatherCode)
            self.weatherWidgets[i].pack(side="left")
