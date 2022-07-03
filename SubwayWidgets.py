# TODO: A/C trains on weekends

import os
from tkinter import *
from tkinter.ttk import *
from datetime import datetime, timedelta
import string
from underground import metadata, SubwayFeed
from PIL import ImageTk, Image
from dataclasses import dataclass

os.environ['MTA_API_KEY'] = "th38DAYhJu8cU1j45I2bm4uxnTe4d5hfajVbR6Ty"


@ dataclass
class SubwayObject:
    time: datetime
    direction: string

    def __lt__(self, other):
        return self.time < other.time


class SubwayWidget(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.icon = ImageTk.PhotoImage(
            Image.open(
                ("assets/subway/" +
                 "ftrain" +
                 ".png")).resize(
                (35,
                 35),
                Image.LANCZOS)
        )
        self.iconLabel = Label(self, image=self.icon)
        self.iconLabel.pack(side="left")
        self.iconLabel.image = self.icon

        self.label = Label(self, text="__town", anchor="center",
                           font=('calibri', 32, 'bold'),
                           #    background='black',
                           foreground='black')
        self.label.pack(side="left")

        self.time = Label(self, text="... min", anchor="e",
                          font=('calibri', 32, 'bold'),
                          #    background='black',
                          foreground='black')
        self.time.pack(side="right")

    def update(self, text, seconds):
        self.label.config(text=text)
        if seconds >= 60:
            self.time.config(text=str((seconds // 60)) + " min")
        else:
            self.time.config(text="~" + str(seconds // 10 + 1) + "0 sec")


class SubwayWidgets:
    API_KEY = os.getenv('th38DAYhJu8cU1j45I2bm4uxnTe4d5hfajVbR6Ty')
    ROUTE = 'F'

    URL = metadata.resolve_url(ROUTE)

    SUBWAY_CHECK_INTERVAL = 60
    LABEL_UPDATE_INTERVAL = 5
    SUBWAY_DISPLAY_BOXES = 4

    #TIMEZONE_OFFSET = 0

    def __init__(self, root):
        self.listOfTrains = []
        self.subwayWidgets = []
        for i in range(SubwayWidgets.SUBWAY_DISPLAY_BOXES):
            self.subwayWidgets.append(SubwayWidget(root))
        self.checkSubway()
        self.organizeSubwayLabels()

    def organizeSubwayLabels(self):
        now = datetime.now() #- timedelta(hours=SubwayWidgets.TIMEZONE_OFFSET)

        for i in range(min(len(self.listOfTrains),
                           SubwayWidgets.SUBWAY_DISPLAY_BOXES)):
            # Remove old trains
            # if (listOfTrains[i].time.replace(tzinfo=None) - now).days < 0:
            print("line 88... i == " + str(i))
            if self.listOfTrains[i].time.replace(tzinfo=None) < now:
                del self.listOfTrains[i]
                continue

            # Update the times on the subwayWidgets
            self.subwayWidgets[i].update(
                text=(
                    "Uptown" if self.listOfTrains[i].direction == 'U' else "Downtown"), seconds=(
                    self.listOfTrains[i].time.replace(
                        tzinfo=None) - now).seconds)
            self.subwayWidgets[i].pack(fill=X)
        for i in range(SubwayWidgets.SUBWAY_DISPLAY_BOXES -
                       min(len(self.listOfTrains), SubwayWidgets.SUBWAY_DISPLAY_BOXES)):
            self.subwayWidgets[SubwayWidgets.SUBWAY_DISPLAY_BOXES -
                               i].pack_forget()

    def checkSubway(self):
        feed = SubwayFeed.get(SubwayWidgets.URL)
        fTrains = feed.extract_stop_dict()['F']
        downtownSubways = fTrains['F14S'][:SubwayWidgets.SUBWAY_DISPLAY_BOXES]
        uptownSubways = fTrains['F14N'][:SubwayWidgets.SUBWAY_DISPLAY_BOXES]

        self.listOfTrains.clear()

        # Get three subways in each direction, sort by time
        print("Appending downtown subways")
        for key in downtownSubways:
            print(key.strftime("%I:%M:%S"))
            self.listOfTrains.append(SubwayObject(key, 'D'))

        print("Appending uptown subways")
        for key in uptownSubways:
            print(key.strftime("%I:%M:%S"))
            self.listOfTrains.append(SubwayObject(key, 'U'))

        self.listOfTrains.sort()
        self.organizeSubwayLabels()
        # updateSubwayLabels()
