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
from PIL import Image, ImageTk
import json
from uuid import uuid4

class App(tk.Tk):

    ## @brief initialize the main window
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Le Marcel Manager")
        self.resizable(False, False)
        self.geometry("600x400")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.init_variables()
        self.load_admin_widgets()

    ## @brief initialize the variables
    def init_variables(self):
        self.administrator_mode = "Administrator"
        self.usermode_button_foreground = "red"
        self.bikes_db = {"file_check": "bikes123", "bikes": [], "last_bike_number": 0}
        self.stations_db = {"file_check": "stations123", "stations": []}
        img = Image.open("pin.png")
        img = img.resize((10, 10), Image.ANTIALIAS)
        self.pin_image = ImageTk.PhotoImage(img)

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
        
        self.load_bike_list()

        self.station_list = ttk.Frame(self, relief="ridge", borderwidth=3)
        self.station_list.grid(row=1, column=1, padx=10, pady=3, sticky="w")
        self.station_list.grid_rowconfigure(0, weight=1)
        self.station_list.grid_columnconfigure(0, weight=1)
        
        self.load_station_list()

        ttk.Button(self, text="Add bike", command=self.add_bike_window).grid(row=2, column=0, padx=10, pady=3, sticky="w")
        ttk.Button(self, text="Add station", command=self.add_station_window).grid(row=2, column=1, padx=10, pady=3, sticky="w")

    ## @brief load the bikes into a table
    def load_bike_list(self):
        for widget in self.bike_list.winfo_children(): # delete the frame content (refresh process)
            widget.destroy()
        
        self.bike_list_canvas = tk.Canvas(self.bike_list) # create the canvas that will contain the scrollbar and the list
        self.bike_list_canvas.grid(row=0, column=0, sticky="nsew")
        
        self.bike_list_scrollbar = ttk.Scrollbar(self.bike_list, orient="vertical", command=self.bike_list_canvas.yview) # create the scrollbar and link it to the canvas
        self.bike_list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.bike_list_canvas.configure(yscrollcommand=self.bike_list_scrollbar.set)

        self.bikes_frame_data = tk.Frame(self.bike_list_canvas) # create the frame that will contain the data
        self.bike_list_canvas.create_window((0, 0), window=self.bikes_frame_data, anchor='nw')

        ttk.Label(self.bikes_frame_data, text="Bike n°").grid(row=0, column=0) #create the headers
        ttk.Label(self.bikes_frame_data, text="Battery").grid(row=0, column=1)
        ttk.Label(self.bikes_frame_data, text="Station").grid(row=0, column=2)

        # seed the list with the bikes' info
        index = 1
        for bike in self.bikes_db["bikes"]:
            ttk.Label(self.bikes_frame_data, text=bike["number"]).grid(row=index, column=0) # bike number
            ttk.Label(self.bikes_frame_data, text=bike["battery_level"]).grid(row=index, column=1) # bike battery

            # station name
            station_found = False
            for station in self.stations_db["stations"]:
                if station["id"] == bike["station_id"]:
                    ttk.Label(self.bikes_frame_data, text=station["name"]).grid(row=index, column=2)
                    station_found = True
                    break
            if not station_found:
                ttk.Label(self.bikes_frame_data, text="Unknown").grid(row=index, column=2)

            tk.Button(self.bikes_frame_data, text="", image=self.pin_image, command=lambda: self.change_bike_station_window(bike)).grid(row=index, column=3, padx=5) # change location
            
            index += 1

        self.bikes_frame_data.update_idletasks()  # update geometry of the frame

        self.bike_list_canvas.config(width=200 + self.bike_list_scrollbar.winfo_width(), height=300) # update the canvas size
        self.bike_list_canvas.config(scrollregion=self.bike_list_canvas.bbox("all")) # update the scroll region

    ## @brief move a bike to another station (admin mode)
    def change_bike_station_window(self, bike):
        toplevel = Toplevel() # create the toplevel window
        toplevel.title = ""
        toplevel.geometry("200x70")
        toplevel.resizable(False, False)
        toplevel.rowconfigure(3, weight=3)
        toplevel.columnconfigure(0, weight=1)
        toplevel.columnconfigure(1, weight=2)

        ttk.Label(toplevel, text="Move bike to").grid(row=0, column=0)


        # variables that will be used for the dropdown menu
        station_list = []
        for station in self.stations_db["stations"]:
            station_list.append(station["name"])
        selected_station = tk.StringVar(toplevel)
        selected_station.set(station_list[0]) # default value

        ttk.OptionMenu(toplevel, selected_station, station_list[0], *station_list).grid(row=0, column=1, padx=10, pady=3) # dropdown menu, updating selected_station
        ttk.Button(toplevel, text="Confirm", command=lambda: confirm()).grid(row=1, column=0, pady=3)

        def confirm(): # update the database
            
            the_station = NONE
            for station in self.stations_db["stations"]:
                if station["name"] == selected_station.get():
                    the_station = station
                    break

            if the_station != NONE:
                self.move_bike(bike, the_station)
            
            toplevel.destroy() #close the toplevel window
            self.load_bike_list() # refresh the bike list
            self.load_station_list() # refresh the station list

        toplevel.mainloop()

    ## @brief move a bike to another station
    def move_bike(self, bike, new_station):

        index = self.bikes_db["bikes"].index(bike)

        # change the station id in bike database
        self.bikes_db["bikes"][index]["station_id"] = new_station["id"]

        # remove the bike from the previous station db
        for station in self.stations_db["stations"]:
            if bike["id"] in station["docked_bikes"]:
                station["docked_bikes"].remove(bike["id"])

        # add the bike to the new station db
        for station in self.stations_db["stations"]:
            if station["name"] == new_station["name"]:
                station["docked_bikes"].append(bike["id"])


    ## @brief load the stations into a table
    def load_station_list(self):
        for widget in self.station_list.winfo_children(): # delete the frame content (refresh process)
            widget.destroy()
        
        self.station_list_canvas = tk.Canvas(self.station_list) # create the canvas that will contain the scrollbar and the list
        self.station_list_canvas.grid(row=0, column=0, sticky="nsew")
        
        self.station_list_scrollbar = ttk.Scrollbar(self.station_list, orient="vertical", command=self.station_list_canvas.yview) # create the scrollbar and link it to the canvas
        self.station_list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.station_list_canvas.configure(yscrollcommand=self.station_list_scrollbar.set)

        self.stations_frame_data = tk.Frame(self.station_list_canvas) # create the frame that will contain the data
        self.station_list_canvas.create_window((0, 0), window=self.stations_frame_data, anchor='nw')

        ttk.Label(self.stations_frame_data, text="Station name").grid(row=0, column=0) #create the headers
        ttk.Label(self.stations_frame_data, text="Docked bikes").grid(row=0, column=1)

        # seed the list with the bikes' info
        index = 1
        for station in self.stations_db["stations"]:
            ttk.Label(self.stations_frame_data, text=station["name"]).grid(row=index, column=0)
            ttk.Label(self.stations_frame_data, text=str(len(station["docked_bikes"]))).grid(row=index, column=1)
            index += 1

        self.stations_frame_data.update_idletasks()  # update geometry of the frame

        self.station_list_canvas.config(width=200 + self.station_list_scrollbar.winfo_width(), height=300) # update the canvas size
        self.station_list_canvas.config(scrollregion=self.station_list_canvas.bbox("all")) # update the scroll region

    ## @brief display the add bike window
    def add_bike_window(self):
        if self.stations_db["stations"] == []: # block if there is no station in the database
            tk.messagebox.showinfo("Error", "You need to add a station before adding a bike.")
            return

        toplevel = Toplevel()
        toplevel.title("Add a new bike")
        toplevel.geometry("300x115")
        toplevel.resizable(False, False)

        # defining the variables that will be used in the window
        bike_id = str(uuid4()) #generate a new unique id using the uuid library
        self.bikes_db["last_bike_number"] = self.bikes_db["last_bike_number"] + 1 # update the last bike number
        bike_number = str(self.bikes_db["last_bike_number"])

        # variables that will be used for the dropdown menu
        station_list = []
        for station in self.stations_db["stations"]:
            station_list.append(station["name"])
        selected_station = tk.StringVar(toplevel)
        selected_station.set(station_list[0]) # default value

        # variable that will be used for the Entry widget
        battery_level = tk.StringVar(toplevel)
        battery_level.set("100")

        # creating the widgets
        ttk.Label(toplevel, text="Bike n°").grid(row=0, column=0, padx=10, pady=3)
        ttk.Label(toplevel, text="Battery level").grid(row=1, column=0, padx=10, pady=3)
        ttk.Label(toplevel, text="Station").grid(row=2, column=0, padx=10, pady=3)

        ttk.Label(toplevel, text=bike_number).grid(row=0, column=1, padx=10, pady=3)
        ttk.Entry(toplevel, textvariable=battery_level).grid(row=1, column=1, padx=10, pady=3)
        ttk.OptionMenu(toplevel, selected_station, station_list[0], *station_list).grid(row=2, column=1, padx=10, pady=3) # dropdown menu, updating selected_station

        toplevel.rowconfigure(3, weight=3)
        toplevel.columnconfigure(0, weight=1)
        toplevel.columnconfigure(1, weight=2)
        ttk.Button(toplevel, text="Confirm", command=lambda: confirm()).grid(row=3, column=0, pady=3) # add the bike and close the window
        
        # @brief check the entry format, and add the bike if it's correct then close the window if the format is correct
        def confirm():
            if not battery_level.get().isnumeric(): # check if the battery level is a number
                tk.messagebox.showinfo("Error", "The battery level must be a number.")
                return
            
            if  0 <= int(battery_level.get()) <= 100: # check if the battery level is between 0 and 100
                self.add_bike(bike_id, bike_number, int(battery_level.get()), selected_station.get())
                toplevel.destroy()
            else:
                tk.messagebox.showinfo("Error", "The battery level must be between 0 and 100.")
                return

        toplevel.mainloop()

    ## @brief display the add station window
    def add_station_window(self):

        toplevel = Toplevel()
        toplevel.title("Add a new station")
        toplevel.geometry("300x115")
        toplevel.resizable(False, False)

        # defining the variables that will be used in the window
        station_id = str(uuid4()) #generate a new unique id using the uuid library

        # variable that will be used by the Entry widgets
        station_name = tk.StringVar(toplevel)
        station_name.set("")
        station_x = tk.StringVar(toplevel)
        station_x.set("")
        station_y = tk.StringVar(toplevel)
        station_y.set("")

        # creating the widgets
        ttk.Label(toplevel, text="Station name").grid(row=0, column=0, padx=10, pady=3)
        ttk.Label(toplevel, text="X coordinate").grid(row=1, column=0, padx=10, pady=3)
        ttk.Label(toplevel, text="Y coordinate").grid(row=2, column=0, padx=10, pady=3)

        ttk.Entry(toplevel, textvariable=station_name).grid(row=0, column=1, padx=10, pady=3)
        ttk.Entry(toplevel, textvariable=station_x).grid(row=1, column=1, padx=10, pady=3)
        ttk.Entry(toplevel, textvariable=station_y).grid(row=2, column=1, padx=10, pady=3)

        toplevel.rowconfigure(3, weight=3)
        toplevel.columnconfigure(0, weight=1)
        toplevel.columnconfigure(1, weight=2)
        ttk.Button(toplevel, text="Confirm", command=lambda: confirm()).grid(row=3, column=0, pady=3) # add the station and close the window
        
        # @brief check the entry format, and add the station if it's correct then close the window if the format is correct
        def confirm():
            if station_name.get() == "" : # check if a name has been entered
                tk.messagebox.showinfo("Error", "Please enter a name for the station")
                return
            
            try:
                self.add_station(station_id, station_name.get(), int(station_x.get()), int(station_y.get()))
                toplevel.destroy()
            except ValueError:
                tk.messagebox.showinfo("Error", "The coordinates must be integers.")
                return

        toplevel.mainloop()

    ## @brief add a new bike to the database
    def add_bike(self, bike_id, bike_number, battery_level, station_name):

        # get the id of the station from the name
        station_id = None
        for station in self.stations_db["stations"]:
            if station["name"] == station_name:
                station_id = station["id"]
                break
        
        if station_id == None: # if the station doesn't exist (should not happen)
            tk.messagebox.showinfo("Error", "Something bad has happened, seems like the station doesn't exist anymore.")
            print(f"ERROR: station with name {station_name} doesn't exist anymore")
            return
        
        self.bikes_db["bikes"].append({"id": bike_id, "number": bike_number, "battery_level": battery_level, "station_id": station_id}) # add the bike to the database
        
        for station in self.stations_db["stations"]:
            if station["id"] == station_id:
                station["docked_bikes"].append(bike_id) # add the bike to the station
        
        self.load_bike_list() # refresh the bike list
        self.load_station_list() # refresh the station list (to update the docked_bikes list)

    def add_station(self, station_id, station_name, station_x, station_y):
        self.stations_db["stations"].append({"id": station_id, "name": station_name, "x": station_x, "y": station_y, "docked_bikes": []}) # add the station to the database       
        self.load_station_list() # refresh the station list

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
                        self.load_bike_list()
                        self.load_station_list()
                    
                else: # file not generated by the program
                    showinfo("Wrong file selected", "This file holds incompatible data with the database you selected. Please make sure you are trying to import the right file.")
            except KeyError: # file not generated by the program
                showinfo("Incompatible file", "Please provide a JSON file generated with this software")
        except json.decoder.JSONDecodeError: # no data / corrupted data in the JSON file
            showinfo("Incompatible file", "Please provide a JSON file generated with this software")
            pass
        except AttributeError: # no file selected
            print("No file provided")
            pass
        
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
