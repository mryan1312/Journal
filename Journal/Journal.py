import os
import asyncio
import sqlite3
import tkinter
from tkinter import ttk
import geocoder
import python_weather
import pandas
import plotly_express
from datetime import date
import PIL
from PIL import Image, ImageDraw

# Database Operations
def open_db(db_file):                                   
    db_check = not os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    if db_check:
        init = '''create table if not exists JOURNAL(
        ENTRY INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE VARCHAR(255) NOT NULL,
        RATING INTEGER NOT NULL,
        WEATHER VARCHAR(255),
        HEALTHY BIT DEFAULT 1,
        SLEEP INTEGER,
        STEPS INTEGER,
        WEIGHT INTEGER,
        HIGHLIGHT VARCHAR(255));'''
        conn.execute(init)
    return conn

def clear_data():
    def truncate_table():
        global conn
        delete_table = '''DROP TABLE JOURNAL;'''
        init = '''create table if not exists JOURNAL(
        ENTRY INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE VARCHAR(255) NOT NULL,
        RATING INTEGER NOT NULL,
        WEATHER VARCHAR(255),
        HEALTHY BIT DEFAULT 1,
        SLEEP INTEGER,
        STEPS INTEGER,
        WEIGHT INTEGER,
        HIGHLIGHT VARCHAR(255));'''
        cur.execute(delete_table)
        cur.execute(init)
        cleardatapop.destroy()
    global cleardatapop
    cleardatapop = tkinter.Toplevel()
    cleardatapop.wm_title("WARNING")
    warning_label = ttk.Label(cleardatapop, text="Warning: This is irreversible. Data will be lost! Continue?").pack()
    clear_continue_button = ttk.Button(cleardatapop, text="Continue", command=truncate_table).pack(side=tkinter.LEFT)
    clear_cancel_button = ttk.Button(cleardatapop, text="Cancel", command=cleardatapop.destroy).pack(side=tkinter.RIGHT)
    
# Get current location for weather
def getlocation():
    currloc = geocoder.ip('me')
    return (f"{currloc.city}, {currloc.state}")

# Get current temp and weather to log
async def getweather(location):
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(location)
        return (f"{weather.current.temperature}, {weather.current.kind}")

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

# Doodle Operations
def save_doodle():
    filename = (f"{date.today()}.png")
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

# Data Variables
conn = open_db('Journal.sqlite')
cur = conn.cursor()
location = getlocation()
weather = asyncio.run(getweather(location))

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
frame1 = ttk.Frame(notebook, width=600, height=380)
frame1.pack(fill='both', expand=True)
frame2 = ttk.Frame(notebook, width=600, height=380)
frame2.pack(fill='both', expand=True)
frame3 = ttk.Frame(notebook, width=600, height=380)
frame3.pack(fill='both', expand=True)
frame4 = ttk.Frame(notebook, width=600, height=380)
frame4.pack(fill='both', expand=True)
notebook.add(frame1, text='Log Entry')
notebook.add(frame2, text='Review Entries')
notebook.add(frame3, text='Charting')
notebook.add(frame4, text='Tools')

# Buttons
log_button = ttk.Button(frame1, text="Log").pack()
doodle_button = ttk.Button(frame1, text="Doodle", command=doodler).pack()
review_button = ttk.Button(frame2, text="Review").pack()
search_button = ttk.Button(frame2, text="Search").pack()
graph_button = ttk.Button(frame3, text="Graph").pack()
cleardata_button = ttk.Button(frame4, text="Clear Data", command=clear_data).pack()

master.mainloop()
