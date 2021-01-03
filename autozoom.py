import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import time
import json
import webbrowser
import pyautogui
import schedule
import pyautogui
import os
import sys
import cv2

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2",os.path.abspath("."))

    return os.path.join(base_path, relative_path)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("227x185")
        self.title("autozoom")
        self.resizable(height = False, width = False)

        self.nb = self.create_notebook()
        self.scheduleLoop()

    def create_notebook(self):
        tabs = ttk.Notebook(self)

        main = MainPage(tabs, self)
        a = Profile(tabs, "A", self)
        b = Profile(tabs, "B", self)
        c = Profile(tabs, "C", self)
        tabs.add(main, text="Main")
        tabs.add(a, text="A Day")
        tabs.add(b, text="B Day")
        tabs.add(c, text="Library")

        tabs.pack()
        return tabs

    def openZoom(self, name, dayFile):
        with open(dayFile) as file:
            self.data = json.load(file)

        link = self.data[name]['link']
        pwd = self.data[name]['pwd']

        #Open webbrowser and link
        webbrowser.open(link)
        time.sleep(2)

        #Find open zoom applicaiton dialog
        box = self.locateCoords('open.png')

        #If failed to find it return
        if box is None:
            return
        #Open it
        x, y = box
        pyautogui.click(x, y, button='left')

        #Close tab
        pyautogui.click(x, y, button='left')
        pyautogui.keyDown('ctrl')
        pyautogui.press('w')
        pyautogui.keyUp('ctrl')

        #Find password box
        password = self.locateCoords('password.png')

        #Password needed
        if password is not None:
            x, y = password
            pyautogui.click(x, y, button='left')
            pyautogui.typewrite(pwd)
            pyautogui.typewrite(['enter'])

        #Try joining without video for 5 minutes
        video = self.locateCoords('join.png')
        if video is not None:
            x, y = video
            pyautogui.click(x, y, button='left')
            return

    def schedule(self, dayFile, early):

        schedule.clear()

        with open(dayFile) as file:
            self.data = json.load(file)

        #Iterate through all zooms added
        for period in self.data.items():

            name = period[0]

            if early:
                time = period[1]['early']
            else:
                time = period[1]['time']

            schedule.every().day.at(time).do(self.openZoom, name, dayFile)

    def scheduleLoop(self):
        schedule.run_pending()
        self.after(1000, self.scheduleLoop)

    def locateCoords(self, file):
        #try 5 times
        coord = None
        for i in range(10):
            coord = pyautogui.locateCenterOnScreen(file, confidence=.5)
            if coord is not None:
                return coord
        return coord

class Profile(tk.Frame):
    def __init__(self, parent, day, app):
        tk.Frame.__init__(self, parent)

        self.app = app
        self.parent = parent

        #Json file to read from
        if day == 'A':
            self.dayFile = 'scheduleA.json'
        if day == 'B':
            self.dayFile = 'scheduleB.json'
        if day == 'C':
            self.dayFile = 'scheduleC.json'

        #Get data from
        with open(self.dayFile) as file:
            self.data = json.load(file)

        self.buttonInit()

    def buttonInit(self):
        #Create launch, config, add, and delete buttons
        self.launch = tk.Button(self, text="Launch", command=self.launchZoom)
        self.config = tk.Button(self, text="Edit", command=self.configZoom)
        self.add = tk.Button(self, text="Add", command=self.entryAdd)
        self.delete = tk.Button(self, text="Delete", command=self.deleteEntry)
        #Gridding all buttons
        self.launch.grid(column=0, row=0)
        self.config.grid(column=1, row=0)
        self.add.grid(column=2, row=0)
        self.delete.grid(column=3, row=0)

        #Create listbox
        self.lb = tk.Listbox(self, selectmode="SINGLE")
        self.lb.grid(column=0, row=1, columnspan=4)

        self.updateList()

    def updateList(self):
        try:
            self.lb.delete(0,self.lb.size()-1)
        except:
            pass
        #Get schedule from json
        with open(self.dayFile) as file:
            self.data = json.load(file)

        for key in self.data.keys():
            self.lb.insert('end', key)

    def launchZoom(self):
        name = self.getCursor()
        if name is None:
            return

        self.app.openZoom(name, self.dayFile)

    def configZoom(self):
        name = self.getCursor()
        if name is None:
            return

        ConfigWindow(self, self.dayFile, name=name)

    def entryAdd(self):
        ConfigWindow(self, self.dayFile)

    def deleteEntry(self):
        name = self.getCursor()
        if name is None:
            return

        #Delete entry
        self.data.pop(name)
        #Update json
        with open(self.dayFile, 'w') as file:
            json.dump(self.data, file, sort_keys=True, indent=4)
        #Update listbox
        self.updateList()

    def getCursor(self):
        select = self.lb.curselection()
        if select == ():
            return None
        else:
            return self.lb.get(select)




class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, dayFile, name=None):
        tk.Toplevel.__init__(self, parent)

        self.oldName = name
        self.dayFile = dayFile
        self.parent = parent

        self.name = tk.StringVar()
        self.link = tk.StringVar()
        self.pwd = tk.StringVar()
        self.time = tk.StringVar()
        self.early = tk.StringVar()

        with open(self.dayFile) as file:
            self.data = json.load(file)

        #Get schedule
        if self.oldName is not None:
            self.name.set(name)
            self.link.set(self.data[name]['link'])
            self.pwd.set(self.data[name]['pwd'])
            self.time.set(self.data[name]['time'])
            self.early.set(self.data[name]['early'])

        self.buttonInit()

    def buttonInit(self):
        #Name
        tk.Label(self, text="Name").grid(column=2, row=0, columnspan=5)
        tk.Entry(self, textvariable=self.name).grid(column=2, row=1, columnspan=5, padx=10, pady=5)

        #Link and password: password optional
        tk.Label(self, text="Zoom Link and Password (Optional)", fg="grey",font=('Arial', 10)).grid(column=2, row=2, columnspan=5)
        #Link
        tk.Label(self, text="Link").grid(column=2, row=3, columnspan=5)
        tk.Entry(self, textvariable=self.link, width=75).grid(column=2, row=4, columnspan=5, padx=10, pady=5)
        #Password
        tk.Label(self, text="Password").grid(column=2, row=5, columnspan=5)
        tk.Entry(self, textvariable=self.pwd).grid(column=2, row=6, columnspan=5, padx=10, pady=5)

        if self.dayFile != 'scheduleC.json':
            #Time: must be in %H:%M military time. Ex: 9 am is 09:00, 4 pm is 16:00
            tk.Label(self, text="Time: must be in %H:%M military time. Ex: 9 am is 09:00, 4 pm is 16:00", fg="grey",font=('Arial', 10)).grid(column=2, row=7, columnspan=5)
            #Time
            tk.Label(self, text="Time").grid(column=2, row=8, columnspan=5)
            tk.Entry(self, textvariable=self.time).grid(column=2, row=9, columnspan=5, padx=10, pady=5)
            #Early release time
            tk.Label(self, text="Early Release Time").grid(column=2, row=10, columnspan=5)
            tk.Entry(self, textvariable=self.early).grid(column=2, row=11, columnspan=5, padx=10, pady=5)

        #Save and close
        tk.Button(self, text="Save and Close", command=self.save, activebackground="grey", relief="solid").grid(column=2, row=12, columnspan=5, padx=10, pady=10)

    def save(self):

        if not self.check():
            return

        #Delete old schedule
        if self.oldName is not None:
            self.data.pop(self.oldName)

        #Get new schedule
        newSchedule = {self.name.get(): {"link":self.link.get(), "pwd":self.pwd.get(), "time":self.time.get(), "early":self.early.get()} }
        self.data.update(newSchedule)

        #Save to json file
        with open(self.dayFile, 'w') as file:
            self.data = json.dump(self.data, file, sort_keys=True, indent=4)

        self.destroy()
        self.update()
        self.parent.updateList()

    def check(self):
        #Check if the name and times are correct
        if self.name.get() == '':
            messagebox.showerror('autozoom', 'Name cannot be empty.')
            return False

        if self.dayFile != 'scheduleC.json':
            try:
                time = datetime.datetime.strptime(self.time.get(), '%H:%M')
                early = datetime.datetime.strptime(self.early.get(), '%H:%M')
            except ValueError:
                messagebox.showerror('autozoom', 'Time must be in %H:%M format!', )
                return False

            #Set time to proper format
            self.time.set(time.strftime('%H:%M'))
            self.early.set(early.strftime('%H:%M'))

        return True

class MainPage(tk.Frame):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)

        self.app = app
        self.parent = parent
        self.scheduled = False
        #self.time = datetime.datetime.now()

        self.buttonInit()
        self.updateClock()

    def buttonInit(self):
        #Main clock
        self.clock = tk.Label(self, text="", font=("Courier New Bold", 50), borderwidth=2, relief="solid")
        self.clock.grid(column=0, row=0, padx=10, pady=10, columnspan=3, rowspan=2)

        #A/B Day buttons
        self.day = tk.IntVar()
        self.aBtn = tk.Radiobutton(self, value=1, variable=self.day, text="A Day")
        self.bBtn = tk.Radiobutton(self, value=2, variable=self.day, text="B Day")
        self.aBtn.grid(column=0, row=4, sticky=tk.W, padx=0, pady=5)
        self.bBtn.grid(column=1, row=4, sticky=tk.W, padx=0, pady=5)

        #Early checkbutton
        self.chk_state = tk.BooleanVar()
        self.chk_state.set(False)
        self.check = tk.Checkbutton(self, text = "Early Release", var=self.chk_state)
        self.check.grid(row = 4, column = 2, sticky = tk.W, columnspan = 2)

        #Schedule button
        self.btn = tk.Button(self, text="Schedule", command=self.schedule, width=30)
        self.btn.grid(column=0, row=5, sticky=tk.S, columnspan=3)

    def schedule(self):
        #1 is A, 2 is B
        day = self.day.get()
        if day == 1:
            dayFile = 'scheduleA.json'
        elif day == 2:
            dayFile = 'scheduleB.json'
        else:
            return

        #Early release
        early = self.chk_state.get()

        #Schedule
        app.schedule(dayFile, early)

        self.scheduled = True
        #window.geometry("227x100")

    def updateClock(self):
        timeStr = datetime.datetime.now().time().strftime("%H:%M")
        self.clock.configure(text=timeStr)
        self.after(1000, self.updateClock)

if __name__ == '__main__':
    app = App()
    app.mainloop()
