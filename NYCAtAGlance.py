from tkinter import *
from tkinter.ttk import *
from time import strftime
import schedule
import WeatherWidgets
import SubwayWidgets

root = Tk()

clock = Label(root, font=('calibri', 72, 'bold'),
              foreground='black')
clock.pack(anchor='center')


def time():
    string = strftime('%I:%M:%S %p').lstrip('0')
    clock.config(text=string)

    schedule.run_pending()
    clock.after(1000, time)


weather = WeatherWidgets.WeatherWidgets(root)
subways = SubwayWidgets.SubwayWidgets(root)

schedule.every(5).seconds.do(subways.organizeSubwayLabels)
schedule.every(60).seconds.do(subways.checkSubway)
schedule.every(30).minutes.do(weather.organizeWeatherLabels)
schedule.every(1).hour.do(weather.getWeather)

time()
mainloop()
