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
# - json
#
# @author Vincent Gonnet
#
# @date 2022/05/10

## @brief importation of the libraries
from cmath import exp
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showinfo
import tkinter as tk
import json
from uuid import uuid4

class App(tk.Tk):

    ## @brief initialize the main window
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Le Marcel Manager")
        self.resizable(False, False)
        self.geometry("500x400")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.init_variables()
        self.load_admin_widgets()

    ## @brief initialize the variables
    def init_variables(self):
        self.administrator_mode = "Administrator"
        self.usermode_button_foreground = "red"
        self.bikes_db = {"fileCheck": "bikes123", "bikes": {}}
        self.stations_db = {"fileCheck": "stations123"}

    ## @brief load the application in the administrator mode
    def load_admin_widgets(self):
        for widget in self.winfo_children(): # clear the application (reload process)
            widget.destroy()

        self.usermode_button_frame = ttk.Frame(self)
        self.usermode_button_frame.grid(row=0, column=0, padx=10, sticky="w") 
        tk.Button(self.usermode_button_frame, text="Import Bikes DB", width=15, command= lambda: self.import_action("bikes123")).grid(row=0, column=0)
        tk.Button(self.usermode_button_frame, text="Import Stations DB", width=15, command= lambda:  self.import_action("stations123")).grid(row=1, column=0)
        tk.Button(self.usermode_button_frame, text="Export Bikes DB", width=15, command= lambda: self.export_action("bikesDB", self.bikes_db)).grid(row=0, column=1)
        tk.Button(self.usermode_button_frame, text="Export Stations DB", width=15, command= lambda:  self.export_action("stationsDB", self.stations_db)).grid(row=1, column=1)

        self.import_export_frame = ttk.Frame(self)
        self.import_export_frame.grid(row=0, column=1, padx=10, sticky="e")

        ttk.Label(self.import_export_frame, text="Current mode").grid(row=0, column=0, sticky="w")
        self.usermode_button = tk.Button(self.import_export_frame, text=self.administrator_mode, fg=self.usermode_button_foreground, width=10, command=self.change_user_mode)
        self.usermode_button.grid(row=1, column=0)

        self.bike_list = ttk.Frame(self, relief="ridge", borderwidth=3)
        self.bike_list.grid(row=1, column=0, padx=10, pady=3, sticky="w")
        self.bike_list.grid_rowconfigure(0, weight=1)
        self.bike_list.grid_columnconfigure(0, weight=1)
        
        self.load_bike_list(self.bike_list)

    ## @brief load the bikes into a table
    def load_bike_list(self, frame):
        for widget in frame.winfo_children(): # delete the frame content (refresh process)
            widget.destroy()
        
        self.bike_list_canvas = tk.Canvas(self.bike_list) # create the canvas that will contain the scrollbar and the list
        self.bike_list_canvas.grid(row=0, column=0, sticky="nsew")
        
        self.bike_list_scrollbar = ttk.Scrollbar(self.bike_list, orient="vertical", command=self.bike_list_canvas.yview) # create the scrollbar and link it to the canvas
        self.bike_list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.bike_list_canvas.configure(yscrollcommand=self.bike_list_scrollbar.set)

        self.frame_data = tk.Frame(self.bike_list_canvas) # create the frame that will contain the data
        self.bike_list_canvas.create_window((0, 0), window=self.frame_data, anchor='nw')

        ttk.Label(self.frame_data, text="Bike n°").grid(row=0, column=0) #create the headers
        ttk.Label(self.frame_data, text="Battery Left").grid(row=0, column=1)

        # seed the list with the bikes' info
        index = 1
        for bike in self.bikes_db["bikes"]:
            ttk.Label(self.frame_data, text=index).grid(row=index, column=0)
            ttk.Label(self.frame_data, text=bike["battery_level"]).grid(row=index, column=1)
            index += 1

        self.frame_data.update_idletasks()  # update geometry of the frame

        self.bike_list_canvas.config(width=100 + self.bike_list_scrollbar.winfo_width(), height=300) # update the canvas size
        self.bike_list_canvas.config(scrollregion=self.bike_list_canvas.bbox("all")) # update the scroll region

    ## @brief load the application in the user mode
    def load_user_widgets(self):
        for widget in self.winfo_children(): # clear the application (reload process)
            widget.destroy()

        self.import_export_frame = ttk.Frame(self)
        self.import_export_frame.grid(row=0, column=1, padx=10, sticky="e")

        ttk.Label(self.import_export_frame, text="Current mode").grid(row=0, column=0, sticky="w")
        self.usermode_button = tk.Button(self.import_export_frame, text=self.administrator_mode, fg=self.usermode_button_foreground, width=10, command=self.change_user_mode)
        self.usermode_button.grid(row=1, column=0)

    ## @brief change the user mode between administrator and user, reloading the application 
    def change_user_mode(self):
        if self.administrator_mode == "User" :
            self.administrator_mode = "Administrator"
            self.usermode_button_foreground = "red"
            self.load_admin_widgets()
        else:
            self.administrator_mode = "User"
            self.usermode_button_foreground = "black"
            self.load_user_widgets()

    ## @brief importation of the data from a JSON file
    def import_action(self, excepted_db):
        file  = filedialog.askopenfile(
            title="Import a database",
            initialdir="./data/",
            filetypes=(('JSON files', '*.json'),)
        ) # opening the file
        try:
            result = json.loads(file.read()) # loading the data from the file

            try:
                if excepted_db == result["file_check"]: # checking if the file is the correct one
                    if excepted_db == "bikes123": # saving the data in the right variable
                        self.bikes_db = result
                    else:
                        self.stations_db = result
                    print(result)

                    if self.administrator_mode == "Administrator": # refresh the bike list
                        self.load_bike_list(self.bike_list)
                    
                else: # file not generated by the program
                    showinfo("Wrong file selected", "This file holds incompatible data with the database you selected. Please make sure you are trying to import the right file.")
            except KeyError: # file not generated by the program
                showinfo("Incompatible file", "Please provide a JSON file generated with this software")
        except json.decoder.JSONDecodeError: # no data / corrupted data in the JSON file
            showinfo("Incompatible file", "Please provide a JSON file generated with this software")
            pass
        # except AttributeError: no file selected
        #     print("No file provided")
        #     pass
        
    ## @brief export the data to a JSON file
    def export_action(self, file_name, data):
        file = filedialog.asksaveasfile(filetypes=(('JSON files', '*.json'),), defaultextension=json, initialfile=file_name, initialdir="./data/") # opening the file
        try:
            self.writeJSONtoFile(file, data) # writing the data in the file
        except AttributeError: # no file selected
            print("No file provided")
            pass

    ## @brief write the data in a JSON file
    def writeJSONtoFile(self, file, data):
        json.dump(data, file)        

app = App()
app.mainloop()
