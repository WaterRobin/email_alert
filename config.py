import datetime

from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
app.config['SECRET_KEY'] = '320213829f2b99c5a69ab1bbc32d8826f7cb183b'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=10)

cluster = MongoClient("mongodb+srv://Robin:aBkea7qLvgNnGJeA@cluster0.an4ea.mongodb.net/gena?retryWrites=true&w=majority")
db = cluster["gena"]
