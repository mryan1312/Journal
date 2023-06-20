import os
import asyncio
import sqlite3
import tkinter
from tkinter import ttk
from tkinter import messagebox
import geocoder
import python_weather
import pandas
import plotly_express
from datetime import date
import PIL
from PIL import Image, ImageDraw, ImageTk
import csv
from tabulate import tabulate

# Database Operations
def open_db(db_file):                                   
    db_check = not os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    if db_check:
        init = '''create table if not exists JOURNAL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE TEXT,
        RATING INTEGER NOT NULL,
        WEATHER TEXT,
        HEALTHY BIT DEFAULT 1,
        SLEEP INTEGER,
        STEPS INTEGER,
        WEIGHT INTEGER,
        HIGHLIGHT TEXT);'''
        conn.execute(init)
    return conn
def review_data(log_id):
    sql = f"SELECT * FROM JOURNAL WHERE ID = '{log_id}';"
    cursor = conn.cursor()
    # Selecting index 0 in the tuple to return data as list
    try:
        data = (cursor.execute(sql).fetchall())[0]
    except:
        data = ('',"No Data",'','','','','','','')
    return data
def get_last_log():
    # Returning last log ID for starting point of entry browsing
    sql = "SELECT ID FROM JOURNAL ORDER BY ID DESC LIMIT 1;"
    try:
        last_log = (conn.execute(sql).fetchall()[0])[0]
        return last_log
    except:
        pass
def insert_data(date, rating, weather, healthy, sleep, steps, weight, highlight):
    # Checking date of last log entry, only want one per day
    datecheck = "SELECT DATE FROM JOURNAL ORDER BY ID DESC LIMIT 1;"
    try:
        last_date = str(conn.execute(datecheck).fetchall()[0][-2|-3])
    except:
        last_date = "Never"
    if last_date == str(date.today()):
        messagebox.showerror("Logging Failed", "There is already a log for today. Undo it first if you want to update.")
    else:
        inserter = f'''INSERT INTO JOURNAL(
        DATE,RATING,WEATHER,HEALTHY,SLEEP,STEPS,WEIGHT,HIGHLIGHT)
        VALUES(
        '{date}',{rating},'{weather}',{healthy},{sleep},{steps},{weight},'{highlight}');'''
        conn.execute(inserter)
        conn.commit()        
        messagebox.showinfo("Logging Complete", "All data has been saved")
def select_today():
    def query_data():
        query = f"SELECT * FROM JOURNAL WHERE DATE = '{date.today()}';"
        rows = conn.execute(query).fetchall()
        return rows
    res = query_data()
    print(res)
    messagebox.showinfo("Result", res)
def undo_today():
    undotoday = f"DELETE FROM JOURNAL WHERE DATE='{date.today()}';"
    conn.execute(undotoday)
    messagebox.showinfo("Done", "Daily log cleared.")
def clear_data():
    def truncate_table():
        global conn
        delete_table = '''DROP TABLE JOURNAL;'''
        init = '''create table if not exists JOURNAL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE TEXT,
        RATING INTEGER NOT NULL,
        WEATHER TEXT,
        HEALTHY BIT DEFAULT 1,
        SLEEP INTEGER,
        STEPS INTEGER,
        WEIGHT INTEGER,
        HIGHLIGHT TEXT);'''
        conn.execute(delete_table)
        conn.execute(init)
        cleardatapop.destroy()
    global cleardatapop
    cleardatapop = tkinter.Toplevel()
    cleardatapop.wm_title("WARNING")
    warning_label = ttk.Label(cleardatapop, text="Warning: This is irreversible. Data will be lost! Continue?").pack()
    clear_continue_button = ttk.Button(cleardatapop, text="Continue", command=truncate_table).pack(side=tkinter.LEFT)
    clear_cancel_button = ttk.Button(cleardatapop, text="Cancel", command=cleardatapop.destroy).pack(side=tkinter.RIGHT)
def export_data():
    sql = "SELECT * FROM JOURNAL"
    data = conn.execute(sql)
    with open("Export_Data.csv", "w", newline='') as file:
        writer = csv.writer(file)
        header = ['ID', 'Date', 'Rating', 'Weather', 'Healthy?', 'Sleep Hours', 'Steps', 'Weight', 'Highlight']
        writer.writerow(header)
        for row in data:
            writer.writerow(row)
    messagebox.showinfo("Success", "Data has been exported to Export_Data.csv")

# Get current location and weather
def getlocation():
    currloc = geocoder.ip('me')
    return (f"{currloc.city}, {currloc.state}")
async def getweather(location):
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(location)
        return (f"{weather.current.temperature} and {weather.current.kind}")

# Doodler Elements
def doodler():
    global canva
    global image1
    global draw
    doodler = tkinter.Toplevel()
    doodler.wm_title("Doodle")
    doodler.wm_geometry('500x530')
    canva = tkinter.Canvas(doodler, width=500, height=500, bg='white')
    image1 = PIL.Image.new('RGB', (500, 500), 'white')
    draw = ImageDraw.Draw(image1)
    canva.bind('<1>', act_paint)
    canva.pack()
    save_button = ttk.Button(doodler, text="Save", command=save_doodle).pack(side=tkinter.RIGHT)
    clear_button = ttk.Button(doodler, text="Clear", command = clear_doodle).pack(side=tkinter.LEFT)
def save_doodle():
    if not os.path.isdir(".\Doodles"):
        os.makedirs(".\Doodles")
    filename = (f".\Doodles\{date.today()}.png")
    image1.save(filename)
def clear_doodle():
    draw.rectangle((0, 0, 500, 500), fill='white')
    canva.delete('all')
def act_paint(e):
    global lastx, lasty
    canva.bind('<B1-Motion>', paint)
    lastx, lasty = e.x, e.y
def paint(e):
    global lastx, lasty
    x, y = e.x, e.y
    canva.create_line((lastx, lasty, x, y), width=5)
    draw.line((lastx, lasty, x, y), fill='black', width=5)
    lastx, lasty = x, y

# Reading entries from the database
def log_veiwer():
    def grab_data(log_id):
        global ins_img
        data = list(review_data(log_id))
        curr_date = data[1]
        df = pandas.DataFrame({"Date": [data[1]], "Rating": [data[2]], "Weather": [data[3]], "Healthy": [data[4]], "Sleep": [data[5]], "Steps": [data[6]], "Weight": [data[7]], "Highlight": [data[8]]})
        textview.delete('1.0',"end")
        textview.insert('1.0', tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        if os.path.isfile(f".\Doodles\{curr_date}.png"):
            img = Image.open(f".\Doodles\{curr_date}.png")
            ins_img = ImageTk.PhotoImage(img)
            textview.image_create('end', image=ins_img)
        if log_id <= 0:
            textview.insert('1.0', "No more logs this way!")
        if log_id > get_last_log():
            textview.insert('1.0', "No more logs this way!")
        return curr_date
    def prev_id():
        global log_id
        log_id -= 1
        grab_data(log_id)
    def next_id():
        global log_id
        log_id += 1
        grab_data(log_id)
    global log_id
    global ins_img
    log_id = get_last_log()
    logview = tkinter.Toplevel()
    logview.wm_title("View Entries")
    previous_btn = ttk.Button(logview, text="Previous", command=lambda: prev_id()).grid(row=0, column=0, sticky='W')
    next_btn = ttk.Button(logview, text="Next", command=lambda: next_id()).grid(row=0, column=3, sticky='E')
    textview = tkinter.Text(logview, height=45, width=100)
    textview.grid(row=1, column=1, columnspan=2, sticky='W'+'E')
    grab_data(log_id)


# Data Variables
conn = open_db('Journal.sqlite')
location = getlocation()
weather = str(asyncio.run(getweather(location)))

# GUI Setup
master = tkinter.Tk()
master.title('Life Journal')
master.geometry('600x400')
style = ttk.Style()

# GUI Elements
location_label = ttk.Label(text=location).pack()
weather_label = ttk.Label(text=weather).pack()
date_label = ttk.Label(text=(date.today())).pack()
# Notebook setup for Organization
notebook = ttk.Notebook(master, width=600, height=380)
notebook.pack(pady=10, expand=True)
# Logging Frame
frame1 = ttk.Frame(notebook, width=600, height=380)
rating_entry = tkinter.IntVar(frame1, 1)
healthy_entry = tkinter.IntVar(frame1, 1)
sleep_entry = tkinter.IntVar(frame1, 0)
steps_entry = tkinter.IntVar(frame1, 0)
weight_entry = tkinter.IntVar(frame1, 0)
highlights_entry = tkinter.StringVar(frame1, ":3")
frame1.pack(fill='both', expand=True)
frame1.rowconfigure(7, weight=1)
frame1.rowconfigure(8, weight=1)
frame1.rowconfigure(9, weight=5)
intro_label = ttk.Label(frame1, text="Complete your daily logging. Dont forget the doodle!").grid(row=0, column=1, columnspan=1)
ratinglabel = ttk.Label(frame1, text="Enter mood rating 1-5").grid(column=0, row=1, sticky="W")
ratingbox = ttk.Spinbox(frame1, from_=1, to=5, textvariable=rating_entry).grid(column=2, row=1, sticky="E")
healthy_label = ttk.Label(frame1, text="Were you healthy today?").grid(column=0, row=2, sticky="W")
health_check_yes = ttk.Radiobutton(frame1, text="Yes", variable=healthy_entry, value=1).grid(column=1, row=2, sticky="E")
health_check_no = ttk.Radiobutton(frame1, text="No", variable=healthy_entry, value=0).grid(column=2, row=2, sticky="E")
sleep_label = ttk.Label(frame1, text="How many hours did you sleep?").grid(column=0, row=3, sticky="W")
sleep_entrybox = ttk.Entry(frame1, textvariable=sleep_entry).grid(column=2, row=3, columnspan=1, sticky="E")
steps_label = ttk.Label(frame1, text="How many steps did you take?").grid(column=0, row=4, sticky="W")
steps_entrybox = ttk.Entry(frame1, textvariable=steps_entry).grid(column=2, row=4, columnspan=1, sticky="E")
weight_label = ttk.Label(frame1, text="What was your weight today?").grid(column=0, row=5, sticky="W")
weight_entrybox = ttk.Entry(frame1, textvariable=weight_entry).grid(column=2, row=5, columnspan=1, sticky="E")
highlights_label = ttk.Label(frame1, text="What was your daily highlight?").grid(column=0, row=6, sticky="W")
Highlights_entry = ttk.Entry(frame1, textvariable=highlights_entry).grid(column=1, row=6, columnspan=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
doodle_button = ttk.Button(frame1, text="Doodle", command=doodler).grid(column=0, row=9, sticky="SW")
log_button = ttk.Button(frame1, text="Log", command=lambda : insert_data(date.today(), rating_entry.get(), weather, healthy_entry.get(), sleep_entry.get(), steps_entry.get(), weight_entry.get(), highlights_entry.get())).grid(column=2, row=9, sticky="SE")
# Review Frame
frame2 = ttk.Frame(notebook, width=600, height=380)
frame2.pack(fill='both', expand=True)
review_button = ttk.Button(frame2, text="Review", command=log_veiwer).pack()
search_button = ttk.Button(frame2, text="Search").pack()
# Charting Frame
frame3 = ttk.Frame(notebook, width=600, height=380)
frame3.pack(fill='both', expand=True)
graph_button = ttk.Button(frame3, text="Graph").pack()
# Tools Frame
frame4 = ttk.Frame(notebook, width=600, height=380)
frame4.pack(fill='both', expand=True)
undotoday_button = ttk.Button(frame4, text="Undo Today", command=undo_today).pack()
cleardata_button = ttk.Button(frame4, text="Clear All Data", command=clear_data).pack()
exportdata_button = ttk.Button(frame4, text="Export All Data", command=export_data).pack()
# Adding frames to notebook
notebook.add(frame1, text='Log Entry')
notebook.add(frame2, text='Review Entries')
notebook.add(frame3, text='Charting')
notebook.add(frame4, text='Tools')

master.mainloop()
