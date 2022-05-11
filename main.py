## 
# @mainpage Le Marcel Manager
#
# @section description_main Description
# A docking stations manager for an electrical bike rental service.
#
# @author Vincent Gonnet
#
# @date 2022


## @file main.py
#
# @brief Main file for the application.
# @brief Contains the main window and the main loop.
#
# @section libraries_main Libraries/Modules
# - tkinter
#
# @author Vincent Gonnet
#
# @date 2022/05/10


from fileinput import filename
from msilib.schema import Class
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter as tk
import json
from tkinter.messagebox import showinfo

"""! @brief definition of the global variables """
administratorMode = False

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Le Marcel Manager")
        self.resizable(False, False)
        self.geometry("400x400")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.init_variables()
        self.admin_widgets()

    def init_variables(self):
        self.administratorMode = "Administrator"
        self.userModeBtnFG = "red"
        self.bikesDB = {"fileCheck": "bikes123"}
        self.stationsDB = {"fileCheck": "stations123"}

    def admin_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.topLeftFrame = ttk.Frame(self)
        self.topLeftFrame.grid(row=0, column=0, padx=10, sticky="w") 
        tk.Button(self.topLeftFrame, text="Import Bikes DB", width=15, command= lambda: self.import_action("bikes123", self.bikesDB)).grid(row=0, column=0)
        tk.Button(self.topLeftFrame, text="Import Stations DB", width=15, command= lambda:  self.import_action("stations123", self.stationsDB)).grid(row=1, column=0)
        tk.Button(self.topLeftFrame, text="Export Bikes DB", width=15, command= lambda: self.export_action("bikesDB", self.bikesDB)).grid(row=0, column=1)
        tk.Button(self.topLeftFrame, text="Export Stations DB", width=15, command= lambda:  self.export_action("stationsDB", self.stationsDB)).grid(row=1, column=1)

        self.topRightFrame = ttk.Frame(self)
        self.topRightFrame.grid(row=0, column=1, padx=10, sticky="e")

        ttk.Label(self.topRightFrame, text="Current mode").grid(row=0, column=0, sticky="w")
        self.userModeBtn = tk.Button(self.topRightFrame, text=self.administratorMode, fg=self.userModeBtnFG, width=10, command=self.change_user_mode)
        self.userModeBtn.grid(row=1, column=0)


    def user_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.topRightFrame = ttk.Frame(self)
        self.topRightFrame.grid(row=0, column=1, padx=10, sticky="e")

        ttk.Label(self.topRightFrame, text="Current mode").grid(row=0, column=0, sticky="w")
        self.userModeBtn = tk.Button(self.topRightFrame, text=self.administratorMode, fg=self.userModeBtnFG, width=10, command=self.change_user_mode)
        self.userModeBtn.grid(row=1, column=0)

    def change_user_mode(self):
        if self.administratorMode == "User" :
            self.administratorMode = "Administrator"
            self.userModeBtnFG = "red"
            self.admin_widgets()
        else:
            self.administratorMode = "User"
            self.userModeBtnFG = "black"
            self.user_widgets()

    def import_action(self, exceptedDB, data):
        file  = filedialog.askopenfile(
            title="Import a database",
            initialdir="./data/",
            filetypes=(('JSON files', '*.json'),)
        )
        result = json.loads(file.read())
        try:
            if exceptedDB == result["fileCheck"]:
                data = result
                print(data)
            else:
                showinfo("Wrong file selected", "This file holds incompatible data with the database you selected. Please make sure you are trying to import the right file.")
        except KeyError:
            showinfo("Incompatible file", "Please provide a JSON file generated with this software")

    def export_action(self, fileName, data):
        file = filedialog.asksaveasfile(filetypes=(('JSON files', '*.json'),), defaultextension=json, initialfile=fileName, initialdir="./data/")
        self.writeJSONtoFile(file, data)

    def writeJSONtoFile(self, file, data):
        json.dump(data, file)
        

app = App()
app.mainloop()
