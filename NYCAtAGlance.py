# TODO: A/C trains on weekends

import os
# importing whole module
from tkinter import *
from tkinter.ttk import *

# importing strftime function to
# retrieve system's time
from time import strftime
from datetime import datetime, timedelta
import string
from underground import metadata, SubwayFeed
from dataclasses import dataclass

os.environ['MTA_API_KEY'] = "th38DAYhJu8cU1j45I2bm4uxnTe4d5hfajVbR6Ty"

API_KEY = os.getenv('th38DAYhJu8cU1j45I2bm4uxnTe4d5hfajVbR6Ty')
ROUTE = 'F'
'''
feed = SubwayFeed.get(ROUTE, api_key=API_KEY)

alerts = SubwayFeed.get(
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts", api_key=API_KEY)
'''

# request will read from $MTA_API_KEY if a key is not provided
# feed = SubwayFeed.get(ROUTE)
URL = metadata.resolve_url(ROUTE)

SUBWAY_CHECK_INTERVAL = 60
LABEL_UPDATE_INTERVAL = 5
SUBWAY_DISPLAY_BOXES = 4

TIMEZONE_OFFSET = -3

# creating tkinter window
root = Tk()
'''root.title('Clock')'''


global secondsUntilCheckSubway
# global secondsUntilUpdateLabels
secondsUntilCheckSubway = 0

listOfTrains = []


@dataclass
class SubwayObject:
    time: datetime
    direction: string

    def __lt__(self, other):
        return self.time < other.time


class CustomWidget(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.label = Label(self, text="__town", anchor="center",
                           font=('calibri', 40, 'bold'),
                           #    background='black',
                           foreground='black')
        self.label.pack(side="left")

        self.time = Label(self, text="... min", anchor="e",
                          font=('calibri', 40, 'bold'),
                          #    background='black',
                          foreground='black')
        self.time.pack(side="right")

    def update(self, text, seconds):
        self.label.config(text=text)
        if seconds >= 60:
            self.time.config(text=str((seconds//60)) + " min")
        else:
            self.time.config(text="<" + str(seconds//10 + 1) + "0 sec")


widgets = []
for i in range(SUBWAY_DISPLAY_BOXES):
    widgets.append(CustomWidget(root))


def updateSubwayLabels():
    print("--------------------------------")

    now = datetime.now() - timedelta(hours=TIMEZONE_OFFSET)
    print("NOW:" + now.strftime("%I:%M:%S"))
    print(
        "TRAIN:" + listOfTrains[0].time.replace(tzinfo=None).strftime("%I:%M:%S"))
    print("ARRIVAL: " +
          str(listOfTrains[0].time.replace(tzinfo=None) - now))


def organizeSubwayLabels():
    now = datetime.now() - timedelta(hours=TIMEZONE_OFFSET)

    for i in range(min(len(listOfTrains), SUBWAY_DISPLAY_BOXES)):
        # Remove old trains
        if (listOfTrains[i].time.replace(tzinfo=None) - now).days < 0:
            del listOfTrains[i]
            continue

        # Update the times on the widgets
        widgets[i].update(
            text=(
                "Uptown" if listOfTrains[i].direction == 'U' else "Downtown"),
            seconds=(listOfTrains[i].time.replace(tzinfo=None) - now).seconds)
        widgets[i].pack(fill=X)
    for i in range(SUBWAY_DISPLAY_BOXES - min(len(listOfTrains), SUBWAY_DISPLAY_BOXES)):
        widgets[SUBWAY_DISPLAY_BOXES-i].pack_forget()


def checkSubway():
    feed = SubwayFeed.get(URL)
    fTrains = feed.extract_stop_dict()['F']
    downtownSubways = fTrains['F14S'][:SUBWAY_DISPLAY_BOXES]
    uptownSubways = fTrains['F14N'][:SUBWAY_DISPLAY_BOXES]

    listOfTrains.clear()

    # Get three subways in each direction, sort by time
    print("Appending downtown subways")
    for key in downtownSubways:
        print(key.strftime("%I:%M:%S"))
        listOfTrains.append(SubwayObject(key, 'D'))

    print("Appending uptown subways")
    for key in uptownSubways:
        print(key.strftime("%I:%M:%S"))
        listOfTrains.append(SubwayObject(key, 'U'))

    listOfTrains.sort()
    organizeSubwayLabels()
    # updateSubwayLabels()


clock = Label(root, font=('calibri', 72, 'bold'),
              #   background='purple',
              foreground='black')
clock.pack(anchor='center')


def time():
    global secondsUntilCheckSubway
    # global secondsUntilUpdateLabels

    string = strftime('%I:%M:%S %p')
    clock.config(text=string)

    secondsUntilCheckSubway -= 1
    # secondsUntilUpdateLabels -= 1

    if secondsUntilCheckSubway <= 0:
        checkSubway()
        secondsUntilCheckSubway = SUBWAY_CHECK_INTERVAL
    elif secondsUntilCheckSubway % LABEL_UPDATE_INTERVAL == 0:
        organizeSubwayLabels()
        # updateSubwayLabels()
        # secondsUntilUpdateLabels = LABEL_UPDATE_INTERVAL

    clock.after(1000, time)


time()
mainloop()
