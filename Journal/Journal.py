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

# Get current location for weather
def getlocation():
    currloc = geocoder.ip('me')
    return (f"{currloc.city}, {currloc.state}")

# Get current temp and weather to log
async def getweather(location):
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(location)
        return (f"{weather.current.temperature}, {weather.current.kind}")

# Doodle Capture


def save_doodle():
    filename = (f"{date.today()}.png")
    image1.save(filename)

def clear_doodle():
    canva.delete('all')

def act_paint(e):
    global lastx, lasty
    canva.bind('<B1-Motion>', paint)
    lastx, lasty = e.x, e.y

def paint(e):
    global lastx, lasty
    x, y = e.x, e.y
    canva.create_line((lastx, lasty, x, y), width=5)
    lastx, lasty = x, y

# Data Variables
conn = open_db('Journal.sqlite')
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
log_button = ttk.Button(text="Log").pack()
review_button = ttk.Button(text="Review").pack()
graph_button = ttk.Button(text="Graph").pack()

# Doodler Elements
doodler = tkinter.Toplevel()
doodler.wm_title("Doodle")
doodler.wm_geometry('500x550')
canva = tkinter.Canvas(doodler, width=500, height=500, bg='white')
image1 = PIL.Image.new('RGB', (500, 500), 'white')
draw = ImageDraw.Draw(image1)
canva.bind('<1>', act_paint)
canva.pack()
save_button = ttk.Button(doodler, text="Save", command=save_doodle).pack()
clear_button = ttk.Button(doodler, text="Clear", command = clear_doodle).pack()

master.mainloop()
