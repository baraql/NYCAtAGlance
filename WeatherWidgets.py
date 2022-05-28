from tkinter import *
from tkinter.ttk import *
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests
from Sun import Sun
from PIL import ImageTk, Image
import colorsys


class WeatherWidget(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        Frame.pack(self, expand=True, fill=X, side="bottom")
        self.time = Label(self, text="0 AM", anchor="center",
                          font=('calibri', 14, 'bold'),
                          #  background='black',
                          foreground='black')
        self.time.pack(side="bottom")

        self.uv = Label(self, text="_ UV", anchor="s",
                        font=('calibri', 16, 'bold'),
                        #    background='black',
                        foreground='black')
        self.uv.pack(side="bottom")

        self.temp = Label(self, text="_ F", anchor="center",
                          font=('calibri', 28, 'bold'),
                          #    background='black',
                          foreground='black')
        self.temp.pack(side="bottom")

        '''
            self.code = Label(self, text="0000", anchor="center",
                            font=('calibri', 10, 'bold'),
                            #  background='black',
                            foreground='black')
            self.code.pack(side="bottom")
            '''
        self.code = ImageTk.PhotoImage(
            WeatherWidgets.getWeatherCodeImage(1000))
        self.codeLabel = Label(self, image=self.code)
        self.codeLabel.pack(side="bottom")
        self.codeLabel.image = self.code

    def update(self, uv, temp, time, code):
        hue = 255 - ((temp) / 80) * 240
        self.temp.config(
            text=temp, foreground=WeatherWidgets.hslToHex(hue, .7, .5))
        self.uv.config(text=uv, foreground=WeatherWidgets.uvColor(uv))

        self.time.config(text=time.lstrip('0'))

        # self.code = PhotoImage(
        # file=getWeatherCodeImageString(code))
        # print("Changing image code to " + str(self.code))
        self.codeLabel.pack_forget()
        self.code = ImageTk.PhotoImage(
            WeatherWidgets.getWeatherCodeImage(code))
        self.codeLabel = Label(self, image=self.code)
        self.codeLabel.pack(side="bottom")
        self.codeLabel.image = self.code

# parent.create_image(20, 20, self.code)


class WeatherWidgets:
    WEATHER_DISPLAY_BOXES = 12
    API_URL = "https://api.tomorrow.io/v4/timelines"
    COORDS = {'longitude': -73.986623, 'latitude': 40.722718}

    sunrise = 0
    sunset = 0

    def __init__(self, root):
        self.weatherHours = []
        self.weatherWidgets = []

        # global secondsUntilUpdateLabels
        self.secondsUntilCheckSubway = 0
        self.weatherFrame = Frame(root)
        self.weatherFrame.pack(side="bottom", fill=X, expand=True)
        # self.getSun()
        self.getWeather()
        for i in range(WeatherWidgets.WEATHER_DISPLAY_BOXES):
            print("appended " + str(i))
            self.weatherWidgets.append(WeatherWidget(self.weatherFrame))
        self.organizeWeatherLabels()
        # for hour in weatherHours:
        #     print(hour.date.strftime("%m/%d, %I:%M:%S") + ": " +
        #           str(hour.temp) + " " + str(hour.weatherCode))

    querystring = {
        # "location": "40.722718, -73.986623",
        "location": (str(COORDS['latitude']) + ", " + str(COORDS['longitude'])),
        "fields": ["temperatureApparent", "uvIndex", "weatherCode"],
        "units": "imperial",
        "timesteps": "1h",
        "timezone": "America/New_York",
        "apikey": "ASPKCVnrURpVM1DIssX8ZwqwoNyX1VTx"
    }

    def getSun(self):
        sun = Sun()
        self.sunrise = sun.getSunriseTime(
            WeatherWidgets.COORDS)['decimal']
        self.sunset = sun.getSunsetTime(
            WeatherWidgets.COORDS)['decimal']

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

        # t = response.json()[
        # 'data']['timelines'][0]['intervals'][0]['values']['temperatureApparent']

        if response.status_code // 100 == 2:
            print(response)
            results = response.json()['data']['timelines'][0]['intervals']
            # now = datetime.datetime.now() - timedelta(hours=TIMEZONE_OFFSET)
            for daily_result in results:
                date = datetime.strptime(
                    daily_result['startTime'], '%Y-%m-%dT%H:%M:%S-04:00')
                print("Given date: " +
                      str(daily_result['startTime']) +
                      "   extracted date:" +
                      str(date))
                # temp = round(daily_result['values']['temperatureApparent'])
                temp = round(daily_result['values']['temperatureApparent'])

                try:
                    uvIndex = daily_result['values']['uvIndex']
                except KeyError:
                    uvIndex = -1
                weatherCode = daily_result['values']['weatherCode']
                # print(date.day.replace(tzinfo=None) - now)
                # print("At", date.strftime('%I %p'), ("today" if date.day == 0 else "yesterday" if date.day >
                #  1 else "tomorrow" if date.day < 0 else "error"), "it will be", temp, "F")
                # temperatures.append(round(daily_result['values']['temperature']))
                # uvIndicies.append(daily_result['values']['uvIndex'])
                self.weatherHours.append(
                    WeatherWidgets.WeatherHour(
                        temp=temp,
                        uvIndex=uvIndex,
                        date=date,
                        weatherCode=weatherCode))
        else:
            print("Error downloading weather: " + response.status_code)

    def getWeatherCodeImage(code):
        return Image.open(
            ("assets/weather/" +
             str(code) +
                "0" +
                ".png")).resize(
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
            # Remove old trains
            # if (listOfTrains[i].time.replace(tzinfo=None) - now).days < 0:
            # if weatherHours[i].date.replace(tzinfo=None) < now:
            #     del weatherHours[i]
            #     continue

            # Update the times on the weatherWidgets
            self.weatherWidgets[i].update(
                uv=self.weatherHours[i].uvIndex,
                temp=self.weatherHours[i].temp,
                time=self.weatherHours[i].date.strftime("%I%p"),
                code=self.weatherHours[i].weatherCode)
            self.weatherWidgets[i].pack(side="left")
        # for i in range(WEATHER_DISPLAY_BOXES - min(len(weatherHours), WEATHER_DISPLAY_BOXES)):
        #     weatherWidgets[WEATHER_DISPLAY_BOXES-i].pack_forget()
