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
from asyncio.windows_events import NULL
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showinfo
import tkinter as tk
from PIL import Image, ImageTk
import json
from uuid import uuid4
from ctypes import *
import networkx as nx
import matplotlib.pyplot as plt

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
        self.data = {"file_check": "data_marcel_manager", "bikes": [], "stations": [], "last_bike_number": 0}
        img = Image.open("img/pin.png")
        img = img.resize((10, 10), Image.LANCZOS)
        self.pin_image = ImageTk.PhotoImage(img)
        img = Image.open("img/bin.png")
        img = img.resize((10,10), Image.LANCZOS)
        self.bin_image = ImageTk.PhotoImage(img)
        img = Image.open("img/bike.png")
        img = img.resize((10,10), Image.LANCZOS)
        self.bike_image = ImageTk.PhotoImage(img)
        self.stations_sort = 0
        self.bikes_sort = 0

    ## @brief display the shortest path to visit all the stations
    def maintenance(self):
        fc = CDLL('./tsp.o') # load the library
        fc.tsp.argtypes = (c_int, POINTER(c_int)) # set the arguments' type of the function
        fc.tsp.restype = POINTER(c_int) # set the return type of the function
        list = [0, 0] # create the list containing the stations' coordinates (x, y), the first element is the start station (warehouse)
        for station in self.data["stations"]:
            list.append(station["x"])
            list.append(station["y"])
        length = len(list)
        args = c_int * length
        result_list = fc.tsp(length, args(*list)) # call the function and store the result

        ordered_stations = [] # list of stations by visit order
        for i in range(0, int(length/2)):
            if result_list[i]-2 >= 0:
                ordered_stations.append(self.data["stations"][result_list[i]-2]["name"])
        
        G = nx.Graph() # instantiate a graph
    
        # create and seed a node list with the stations' name and coordinates
        nodes = [("Warehouse", {"coords": (0, 0)})]
        for station in ordered_stations:
            for station_data in self.data["stations"]:
                if station_data["name"] == station:
                    nodes.append((station_data["name"], {"coords": (station_data["x"], station_data["y"])}))
                    break
        G.add_nodes_from(nodes) # add the nodes to the graph

        # create and seed an edge list
        edges = [("Warehouse", ordered_stations[0])]
        for i in range(0, len(ordered_stations)-1):
            edges.append((ordered_stations[i], ordered_stations[i+1]))
        G.add_edges_from(edges) # add the edges to the graph

        coords = nx.get_node_attributes(G, "coords") # get the coordinates of the nodes

        nx.draw(
            G,
            pos = coords,
            with_labels = True,
            font_weight = 'bold',
            node_size = 400,
            node_color = '#e3fafb',
            edge_color = '#8c8d8d',
            arrows = True,
            arrowsize = 15,
            arrowstyle = "-|>",
            font_color = "#8B0000"
        )

        plt.show()

    ## @brief load the application in the administrator mode
    def load_admin_widgets(self):
        for widget in self.winfo_children(): # clear the application (reload process)
            widget.destroy()

        # import / export data
        self.data_management_frame = ttk.Frame(self)
        self.data_management_frame.grid(row=0, column=0, padx=10, sticky="w") 
        tk.Button(self.data_management_frame, text="Import Data", width=15, command= lambda: self.import_action("data_marcel_manager")).grid(row=0, column=0)
        tk.Button(self.data_management_frame, text="Export Data", width=15, command= lambda: self.export_action("data", self.data)).grid(row=0, column=1)

        # summary & pass day button
        def pass_day():
            for bike in self.data["bikes"]:
                bike["nb_days"] += 1
            showinfo("Pass day", "One day has passed")
        
        summ_frame = ttk.Frame(self)
        summ_frame.grid(row=0, column=1, padx=10, sticky="e")
        summ_frame.columnconfigure(0, weight=1)
        tk.Button(summ_frame, text="Summary", command=self.summary_action).grid(row=0, column=0, padx=0, sticky="e")
        tk.Button(summ_frame, text="Maintenance", command=self.maintenance).grid(row=0, column=1, padx=10, sticky="e")
        tk.Button(summ_frame, text="Pass day", command=pass_day).grid(row=0, column=2, sticky="e")

        # change user mode
        self.user_mode_frame = ttk.Frame(self)
        self.user_mode_frame.grid(row=0, column=3, padx=10, sticky="e")
        ttk.Label(self.user_mode_frame, text="Current mode").grid(row=0, column=0, sticky="w")
        self.usermode_button = tk.Button(self.user_mode_frame, text=self.administrator_mode, fg=self.usermode_button_foreground, width=10, command=self.change_user_mode)
        self.usermode_button.grid(row=1, column=0)

        # bike list
        self.bike_list = ttk.Frame(self, relief="ridge", borderwidth=3)
        self.bike_list.grid(row=1, column=0, padx=10, pady=3, sticky="w")
        self.bike_list.grid_rowconfigure(0, weight=1)
        self.bike_list.grid_columnconfigure(0, weight=1)
        
        self.load_bike_list()

        # station list
        self.station_list = ttk.Frame(self, relief="ridge", borderwidth=3)
        self.station_list.grid(row=1, column=1, padx=10, pady=3, sticky="w")
        self.station_list.grid_rowconfigure(0, weight=1)
        self.station_list.grid_columnconfigure(0, weight=1)
        
        self.load_station_list()

        # add bike and station buttons
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
        for bike in self.data["bikes"]:
            ttk.Label(self.bikes_frame_data, text=bike["number"]).grid(row=index, column=0) # bike number
            ttk.Label(self.bikes_frame_data, text=bike["battery_level"]).grid(row=index, column=1) # bike battery

            # station name
            station_found = False
            for station in self.data["stations"]:
                if station["id"] == bike["station_id"]:
                    ttk.Label(self.bikes_frame_data, text=station["name"]).grid(row=index, column=2)
                    station_found = True
                    break
            if not station_found:
                ttk.Label(self.bikes_frame_data, text="Unknown").grid(row=index, column=2)

            ttk.Button(self.bikes_frame_data, text="", image=self.pin_image, command=lambda bike=bike: self.change_bike_station_window(bike)).grid(row=index, column=3, padx=5) # change location
            ttk.Button(self.bikes_frame_data, text="", image=self.bin_image, command=lambda id=bike["id"]: [self.remove_bike(id), self.load_bike_list(), self.load_station_list()]).grid(row=index, column=4, padx=5) # remove the bike
            

            index += 1

        self.bikes_frame_data.update_idletasks()  # update geometry of the frame

        self.bike_list_canvas.config(width=200 + self.bike_list_scrollbar.winfo_width(), height=300) # update the canvas size
        self.bike_list_canvas.config(scrollregion=self.bike_list_canvas.bbox("all")) # update the scroll region

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

        # seed the list with the stations' info
        index = 1
        for station in self.data["stations"]:
            ttk.Label(self.stations_frame_data, text=station["name"]).grid(row=index, column=0)
            ttk.Label(self.stations_frame_data, text=str(len(station["docked_bikes"]))).grid(row=index, column=1)

            ttk.Button(self.stations_frame_data, text="", image=self.bike_image, command=lambda id=station["id"]: self.display_bikes_window(id)).grid(row=index, column=2, padx=5) # display the bikes docked to the station
            ttk.Button(self.stations_frame_data, text="", image=self.bin_image, command=lambda id=station["id"]: [self.remove_station(id), self.load_bike_list(), self.load_station_list()]).grid(row=index, column=3, padx=5) # remove the station

            index += 1

        self.stations_frame_data.update_idletasks()  # update geometry of the frame

        self.station_list_canvas.config(width=200 + self.station_list_scrollbar.winfo_width(), height=300) # update the canvas size
        self.station_list_canvas.config(scrollregion=self.station_list_canvas.bbox("all")) # update the scroll region

    ## @brief display the bikes docked to a station
    def display_bikes_window(self, station_id):
        for station in self.data["stations"]:
            if station["id"] == station_id:

                # check if there are bikes docked to the station
                if len(station["docked_bikes"]) == 0:
                    tk.messagebox.showinfo("No bikes", "There are no bikes docked to this station")
                    return

                # create a top-level window with a bike list 
                bikes_window = tk.Toplevel(self)
                bikes_window.title("Bikes docked at " + station["name"])
                bikes_window.geometry("300x130")
                bikes_window.resizable(False, True)

                ttk.Label(bikes_window, text="Bike n°").grid(row=0, column=0, pady=10)
                ttk.Label(bikes_window, text="Battery level").grid(row=0, column=1, pady=10)

                index = 1
                for bike_id in station["docked_bikes"]:
                    for bike in self.data["bikes"]:
                        if bike["id"] == bike_id:
                            ttk.Label(bikes_window, text=bike["number"]).grid(row=index, column=0)
                            ttk.Label(bikes_window, text=bike["battery_level"]).grid(row=index, column=1)
                            index += 1
                            break
                
                ttk.Button(bikes_window, text="Close", command=bikes_window.destroy).grid(row=index+1, column=0, padx=50, pady=20)

                bikes_window.mainloop()

    ## @brief display the add bike window
    def add_bike_window(self):
        if self.data["stations"] == []: # block if there is no station in the database
            tk.messagebox.showinfo("Error", "You need to add a station before adding a bike.")
            return

        toplevel = Toplevel()
        toplevel.title("Add a new bike")
        toplevel.geometry("300x115")
        toplevel.resizable(False, False)

        # defining the variables that will be used in the window
        bike_id = str(uuid4()) #generate a new unique id using the uuid library
        self.data["last_bike_number"] = self.data["last_bike_number"] + 1 # update the last bike number
        bike_number = str(self.data["last_bike_number"])

        # variables that will be used for the dropdown menu
        station_list = []
        for station in self.data["stations"]:
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
                x = int(station_x.get())
                y = int(station_y.get())
            except ValueError:
                tk.messagebox.showinfo("Error", "The coordinates must be integers.")
                return
            
            if x == 0 and y == 0:
                tk.messagebox.showinfo("Error", "There is already the main warehouse at these coordinates.")
                return

            if not -100 <= x <= 100 or not -100 <= y <= 100:
                tk.messagebox.showinfo("Error", "The coordinates must be between -100 and 100.")
                return

            for station in self.data["stations"]:
                if station["x"] == x and station["y"] == y:
                    tk.messagebox.showinfo("Error", "There is already a station at these coordinates.")
                    return

            self.add_station(station_id, station_name.get(), x, y)
            toplevel.destroy()

        toplevel.mainloop()

    ## @brief add a new bike to the database
    def add_bike(self, bike_id, bike_number, battery_level, station_name):

        # get the id of the station from the name
        station_id = None
        for station in self.data["stations"]:
            if station["name"] == station_name:
                station_id = station["id"]
                break
        
        if station_id == None: # if the station doesn't exist (should not happen)
            tk.messagebox.showinfo("Error", "Something bad has happened, seems like the station doesn't exist anymore.")
            print(f"ERROR: station with name {station_name} doesn't exist anymore")
            return
        
        self.data["bikes"].append(
            {
                "id": bike_id, 
                "number": bike_number, 
                "battery_level": battery_level, 
                "station_id": station_id, 
                "nb_days": 0, 
                "nb_rents": 0
            }
        ) # add the bike to the database
        
        for station in self.data["stations"]:
            if station["id"] == station_id:
                station["docked_bikes"].append(bike_id) # add the bike to the station
        
        self.load_bike_list() # refresh the bike list
        self.load_station_list() # refresh the station list (to update the docked_bikes list)

    ## @brief add a new station to the database
    def add_station(self, station_id, station_name, station_x, station_y):
        self.data["stations"].append(
            {
                "id": station_id,
                "name": station_name,
                "x": station_x,
                "y": station_y,
                "docked_bikes": [],
                "nb_rents": 0,
                "nb_returns": 0
            }
        ) # add the station to the database

        self.load_station_list() # refresh the station list

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
        for station in self.data["stations"]:
            station_list.append(station["name"])
        selected_station = tk.StringVar(toplevel)
        selected_station.set(station_list[0]) # default value

        ttk.OptionMenu(toplevel, selected_station, station_list[0], *station_list).grid(row=0, column=1, padx=10, pady=3) # dropdown menu, updating selected_station
        ttk.Button(toplevel, text="Confirm", command=lambda: confirm()).grid(row=1, column=0, pady=3)

        def confirm(): # update the database
            
            the_station = NONE
            for station in self.data["stations"]:
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

        index = self.data["bikes"].index(bike)

        # change the station id in bike database
        self.data["bikes"][index]["station_id"] = new_station["id"]

        # remove the bike from the previous station db
        for station in self.data["stations"]:
            if bike["id"] in station["docked_bikes"]:
                station["docked_bikes"].remove(bike["id"])

        # add the bike to the new station db
        for station in self.data["stations"]:
            if station["name"] == new_station["name"]:
                station["docked_bikes"].append(bike["id"])

    ## @brief remove a bike from the database
    def remove_bike(self, bike_id):
        for station in self.data["stations"]:
            if bike_id in station["docked_bikes"]:
                station["docked_bikes"].remove(bike_id) # remove the bike from the stations
        
        for bike in self.data["bikes"]:
            if bike["id"] == bike_id:
                self.data["bikes"].remove(bike) # remove the bike from the database

    ## @brief remove a station from the database
    def remove_station(self, station_id):
        for station in self.data["stations"]:
            if station["id"] == station_id:
                if station["docked_bikes"] == []: # check if the station is empty
                    self.data["stations"].remove(station) # remove the station from the database
                else:
                    tk.messagebox.showinfo("Error", "The station is not empty, please move all the bikes before removing the station.")
                    return

    ## @brief display a window with the overall system summary
    def summary_action(self):
        if self.data["bikes"] == []:
            tk.messagebox.showinfo("Error", "There are no bikes in the database. You must add some bikes before you can see the summary.")
            return

        # create the top-level window
        summary_window = tk.Toplevel(self)
        summary_window.title("Le Marcel Manager : Summary")
        summary_window.geometry("700x380")
        summary_window.resizable(False, False)

        # configure the grid weights
        summary_window.rowconfigure(0, weight=0)
        summary_window.columnconfigure(0, weight=1)
        summary_window.rowconfigure(1, weight=0)
        summary_window.rowconfigure(3, weight=1)

        # title frame
        title_frame = ttk.Frame(summary_window)
        title_frame.grid(row=0, column=0, columnspan=2,sticky="nwes")
        title_frame.columnconfigure(0, weight=1)
        title_frame.columnconfigure(1, weight=1)
        tk.Button(title_frame, text="BIKES").grid(row=0, column=0, sticky="news")
        tk.Button(title_frame, text="STATIONS").grid(row=0, column=1, sticky="news")

        # row 1 : bikes number and average overall battery level
        row_1_frame = ttk.Frame(summary_window)
        row_1_frame.grid(row=1, column=0, columnspan=2, sticky="nwe")
        row_1_frame.columnconfigure(0, weight=1)
        row_1_frame.columnconfigure(1, weight=1)
        bikes_number = len(self.data["bikes"])
        average_overall_battery_level = 0
        for bike in self.data["bikes"]:
            average_overall_battery_level += bike["battery_level"]
        average_overall_battery_level /= bikes_number
        tk.Label(row_1_frame, text="Number of bikes : " + str(bikes_number)).grid(row=0, column=0, sticky="new")
        tk.Label(row_1_frame, text="Average overall battery level : " + str(average_overall_battery_level)).grid(row=0, column=1, sticky="new")

        # row 2 : sort selection
        sort_selection = ttk.Frame(summary_window)
        sort_selection.grid(row=2, column=0, columnspan=2,sticky="nwes")
        sort_selection.columnconfigure(0, weight=1)
        sort_selection.columnconfigure(1, weight=1)
        sort_selection.columnconfigure(2, weight=1)
        sort_selection.columnconfigure(3, weight=1)
        ttk.Button(sort_selection, text="Days in use", command= lambda: [change_sort("bikes", 0), load_bike_list()]).grid(row=0, column=0, sticky="news")
        ttk.Button(sort_selection, text="Times rented", command= lambda: [change_sort("bikes", 1), load_bike_list()]).grid(row=0, column=1, sticky="news")
        ttk.Button(sort_selection, text="Nb Rents", command= lambda: [change_sort("stations", 0), load_station_list()]).grid(row=0, column=2, sticky="news")
        ttk.Button(sort_selection, text="Nb Returns", command= lambda: [change_sort("stations", 1), load_station_list()]).grid(row=0, column=3, sticky="news")

        # row 3 : lists
        bike_list_frame = ttk.Frame(summary_window)
        bike_list_frame.grid(row=3, column=0, sticky="nwes")
        station_list_frame = ttk.Frame(summary_window)
        station_list_frame.grid(row=3, column=1, sticky="nwes")

        def change_sort(list, sort_id):
            if list == "bikes":
                self.bikes_sort = sort_id
            elif list == "stations":
                self.stations_sort = sort_id

        def load_bike_list():
            for widget in bike_list_frame.winfo_children(): # delete the frame content (refresh process)
                widget.destroy()
        
            bike_list_canvas = tk.Canvas(bike_list_frame) # create the canvas that will contain the scrollbar and the list
            bike_list_canvas.grid(row=0, column=0, sticky="nsew")
            
            bike_list_scrollbar = ttk.Scrollbar(bike_list_frame, orient="vertical", command=bike_list_canvas.yview) # create the scrollbar and link it to the canvas
            bike_list_scrollbar.grid(row=0, column=1, sticky="ns")
            bike_list_canvas.configure(yscrollcommand=bike_list_scrollbar.set)

            bike_frame_data = tk.Frame(bike_list_canvas) # create the frame that will contain the data
            bike_list_canvas.create_window((0, 0), window=bike_frame_data, anchor='nw')

            ttk.Label(bike_frame_data, text="Bike n°").grid(row=0, column=0, padx=4) #create the headers
            ttk.Label(bike_frame_data, text="Battery").grid(row=0, column=1, padx=4)
            ttk.Label(bike_frame_data, text="Station").grid(row=0, column=2, padx=4)
            ttk.Label(bike_frame_data, text="Days in use").grid(row=0, column=3, padx=4)
            ttk.Label(bike_frame_data, text="Times rented").grid(row=0, column=4, padx=4)

            data = self.data["bikes"]
            if self.bikes_sort == 0:
                data.sort(key= lambda x: x["nb_days"], reverse=True)
            elif self.bikes_sort == 1:
                data.sort(key= lambda x: x["nb_rents"], reverse=True)

            # seed the list with the stations' info
            index = 1
            for bike in data:
                for station in self.data["stations"]:
                    if station["id"] == bike["station_id"]:
                        station_name = station["name"]
                        break
                
                ttk.Label(bike_frame_data, text=bike["number"]).grid(row=index, column=0)
                ttk.Label(bike_frame_data, text=bike["battery_level"]).grid(row=index, column=1)
                ttk.Label(bike_frame_data, text=station_name).grid(row=index, column=2)
                ttk.Label(bike_frame_data, text=bike["nb_days"]).grid(row=index, column=3)
                ttk.Label(bike_frame_data, text=bike["nb_rents"]).grid(row=index, column=4)

                index += 1

            bike_frame_data.update_idletasks()  # update geometry of the frame

            bike_list_canvas.config(width=310 + bike_list_scrollbar.winfo_width(), height=300) # update the canvas size
            bike_list_canvas.config(scrollregion=bike_list_canvas.bbox("all")) # update the scroll region

        def load_station_list():
            for widget in station_list_frame.winfo_children(): # delete the frame content (refresh process)
                widget.destroy()
        
            station_list_canvas = tk.Canvas(station_list_frame) # create the canvas that will contain the scrollbar and the list
            station_list_canvas.grid(row=0, column=0, sticky="nsew")
            
            station_list_scrollbar = ttk.Scrollbar(station_list_frame, orient="vertical", command=station_list_canvas.yview) # create the scrollbar and link it to the canvas
            station_list_scrollbar.grid(row=0, column=1, sticky="ns")
            station_list_canvas.configure(yscrollcommand=station_list_scrollbar.set)

            stations_frame_data = tk.Frame(station_list_canvas) # create the frame that will contain the data
            station_list_canvas.create_window((0, 0), window=stations_frame_data, anchor='nw')

            ttk.Label(stations_frame_data, text="Station name").grid(row=0, column=0, padx=4) #create the headers
            ttk.Label(stations_frame_data, text="Docked bikes").grid(row=0, column=1, padx=4)
            ttk.Label(stations_frame_data, text="Rents").grid(row=0, column=2, padx=4)
            ttk.Label(stations_frame_data, text="Returns").grid(row=0, column=3, padx=4)
            ttk.Label(stations_frame_data, text="Av. battery").grid(row=0, column=4, padx=4)

            data = self.data["stations"]
            if self.stations_sort == 0:
                data.sort(key= lambda x: x["nb_rents"], reverse=True)
            elif self.stations_sort == 1:
                data.sort(key= lambda x: x["nb_returns"], reverse=True)

            # seed the list with the stations' info
            index = 1
            for station in data:
                
                if station["docked_bikes"] != []:
                    av_battery = 0
                    for bike_id in station["docked_bikes"]: # compute the av. battery of the station's bikes
                        for bike in self.data["bikes"]:
                            if bike["id"] == bike_id:
                                av_battery += bike["battery_level"]
                                break
                    
                    av_battery /= len(station["docked_bikes"])
                else:
                    av_battery = "-"

                ttk.Label(stations_frame_data, text=station["name"]).grid(row=index, column=0)
                ttk.Label(stations_frame_data, text=str(len(station["docked_bikes"]))).grid(row=index, column=1)
                ttk.Label(stations_frame_data, text=station["nb_rents"]).grid(row=index, column=2)
                ttk.Label(stations_frame_data, text=station["nb_returns"]).grid(row=index, column=3)
                ttk.Label(stations_frame_data, text=str(av_battery)).grid(row=index, column=4)

                index += 1

            stations_frame_data.update_idletasks()  # update geometry of the frame

            station_list_canvas.config(width=310 + station_list_scrollbar.winfo_width(), height=300) # update the canvas size
            station_list_canvas.config(scrollregion=station_list_canvas.bbox("all")) # update the scroll region

        load_bike_list()
        load_station_list()
        summary_window.mainloop()

    ## @brief load the application in the user mode
    def load_user_widgets(self):
        for widget in self.winfo_children(): # clear the application (reload process)
            widget.destroy()

        # user mode widgets
        user_mode_frame = ttk.Frame(self)
        user_mode_frame.grid(row=0, column=1, padx=10, sticky="ne")
        ttk.Label(user_mode_frame, text="Current mode").grid(row=0, column=0, sticky="w")
        usermode_button = tk.Button(user_mode_frame, text=self.administrator_mode, fg=self.usermode_button_foreground, width=10, command=self.change_user_mode)
        usermode_button.grid(row=1, column=0)

        # station list widgets
        rent_frame = ttk.Frame(self)
        rent_frame.grid(row=1, column=0, columnspan=2, padx=10, sticky="news")

        rent_frame.rowconfigure(0, weight=1)
        rent_frame.columnconfigure(0, weight=1)
        rent_frame.columnconfigure(1, weight=2)

        station_selection_frame = ttk.Frame(rent_frame)
        station_selection_frame.grid(row=0, column=0, sticky="nsew")

        station_selection_frame.columnconfigure(0, weight=1)

        ttk.Label(station_selection_frame, text="Station list").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        stations = []
        for station in self.data["stations"]:
            stations.append(station["name"])
        
        station_var = tk.StringVar(value=stations)

        listbox =tk.Listbox(
            station_selection_frame,
            listvariable=station_var,
            height=18
        )
        listbox.grid(row=1, column=0, padx=10, pady=5, sticky="news")

        # rent a bike widgets
        bike_list_frame = ttk.Frame(rent_frame)
        bike_list_frame.grid(row=0, column=1, padx=5, sticky="news")
        bike_list_frame.rowconfigure(1, weight=1)
        ttk.Label(bike_list_frame, text="Available bikes").grid(row=0, column=0, padx=10, pady=5, sticky="news")

        self.user_bike_list = tk.Frame(bike_list_frame, highlightbackground="black", highlightthickness=1)
        self.user_bike_list.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # handle selection
        def items_selected(event):
            # load the bike list for the selected station
            station_name = stations[listbox.curselection()[0]]
            for station in self.data["stations"]:
                if station["name"] == station_name:
                    self.load_user_bike_list(station["id"])
                    break

        listbox.bind("<<ListboxSelect>>", items_selected)

    ## @brief load the bike list in the listbox
    def load_user_bike_list(self, station_id):
        for widget in self.user_bike_list.winfo_children(): # clear the frame (reload process)
            widget.destroy()

        bike_list_canvas = tk.Canvas(self.user_bike_list) # create the canvas that will contain the scrollbar and the list
        bike_list_canvas.grid(row=0, column=0, sticky="w")
        
        bike_list_scrollbar = ttk.Scrollbar(self.user_bike_list, orient="vertical", command=bike_list_canvas.yview) # create the scrollbar and link it to the canvas
        bike_list_scrollbar.grid(row=0, column=1, sticky="ns")
        bike_list_canvas.configure(yscrollcommand=bike_list_scrollbar.set)

        bikes_frame_data = tk.Frame(bike_list_canvas) # create the frame that will contain the data
        bike_list_canvas.create_window((0, 0), window=bikes_frame_data, anchor='nw')

        ttk.Label(bikes_frame_data, text="Bike n°").grid(row=0, column=0, padx=5) #create the headers
        ttk.Label(bikes_frame_data, text="Battery").grid(row=0, column=1, padx=5)

        data = self.data["bikes"]
        data.sort(key= lambda x: x["battery_level"], reverse=True) # sort the bikes by battery level

        # seed the list with the bikes' info
        index = 1
        for bike in data:
            battery_color = "black"
            if bike["station_id"] != station_id: # if the bike is not in the selected station, skip it
                continue
            if bike["battery_level"] <= 2: # if the bike is low on battery, skip it
                continue
            if bike["battery_level"] <= 20: # if the bike is low on battery, change the color of the battery level
                battery_color = "red"

            ttk.Label(bikes_frame_data, text=bike["number"]).grid(row=index, column=0) # bike number
            tk.Label(bikes_frame_data, text=bike["battery_level"], fg=battery_color).grid(row=index, column=1) # bike battery

            ttk.Button(bikes_frame_data, text="Rent", command=lambda bike=bike: self.rent_bike(bike)).grid(row=index, column=3, padx=5) # change location
            
            index += 1

        bikes_frame_data.update_idletasks()  # update geometry of the frame

        bike_list_canvas.config(width=230 + bike_list_scrollbar.winfo_width(), height=286) # update the canvas size
        bike_list_canvas.config(scrollregion=bike_list_canvas.bbox("all")) # update the scroll region

    ## @brief rent a bike, moving it from one station to another, updating the battery level and the stations' & bike's data
    def rent_bike(self, bike):
        # top level window
        rent_window = tk.Toplevel(self)
        rent_window.title("Rent a bike")
        rent_window.geometry("250x100")
        rent_window.resizable(False, False)
        rent_window.columnconfigure(0, weight=1)
        rent_window.columnconfigure(1, weight=1)

        # variables that will be used for the dropdown menu
        station_list = []
        for station in self.data["stations"]:
            station_list.append(station["name"])
        selected_station = tk.StringVar(rent_window)
        selected_station.set(station_list[0]) # default value

        # variable that will be used for the Entry widget
        rent_time = tk.StringVar(rent_window)

        # widgets
        ttk.Label(rent_window, text="Return station").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.OptionMenu(rent_window, selected_station, station_list[0], *station_list).grid(row=0, column=1, padx=10, pady=5, sticky="ew") # dropdown menu, updating selected_station
        ttk.Label(rent_window, text="Rent time (mn)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(rent_window, textvariable=rent_time).grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # handle the confirm button
        def confirm():
            
            target_station = NONE
            for station in self.data["stations"]:
                if station["name"] == selected_station.get():
                    target_station = station
                    break

            # managing exceptions

            if target_station == NONE:
                showinfo("Error", "The station isn't in the data anymore. If this problem persist, please reload the application.")
                return

            try:
                rent_time_value = int(rent_time.get())
            except ValueError:
                showinfo("Error", "The rent time must be an integer.")
                return

            if not 0 < rent_time_value <= 50:
                showinfo("Error", "The rent time must be between 1 and 50 minutes.")
                return

            if 2*rent_time_value > bike["battery_level"]:
                showinfo("Error", "This bike doesn't have enough battery to be rented for that long.")
                return

            # update the bike's data
            bike_index = self.data["bikes"].index(bike)
            self.data["bikes"][bike_index]["battery_level"] = bike["battery_level"] - 2*rent_time_value # update the battery level
            self.data["bikes"][bike_index]["nb_rents"] += 1 # update the number of rents

            # update the current station's data
            current_station = NULL
            for station in self.data["stations"]:
                if station["id"] == bike["station_id"]:
                    current_station = station
                    break
            if current_station == NULL:
                showinfo("Error", "The station isn't in the data anymore. If this problem persist, please reload the application.")
                return
            station_index = self.data["stations"].index(current_station)
            self.data["stations"][station_index]["nb_rents"] += 1 # update the number of rents

            # update the target station's data
            target_station_index = self.data["stations"].index(target_station)
            self.data["stations"][target_station_index]["nb_returns"] += 1 # update the number of returns

            self.move_bike(bike, target_station) # move the bike

            rent_window.destroy() # close the window
            self.load_user_bike_list(current_station["id"]) # reload the bike list

        ttk.Button(rent_window, text="Confirm", command=confirm).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        rent_window.mainloop()

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
                    self.data = result # importing the data

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
