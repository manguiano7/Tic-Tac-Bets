import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from random import random
import math
from helpers import check_if_game_over

#from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db1 = SQL("sqlite:///tictactoe.db")

db2 = SQL("sqlite:///tictactoe_old.db")
Q_values_1 = db1.execute("select * FROM Q_values")
Q_values_2 = db2.execute("select * FROM Q_values")

sum = 0.0
for i in range(5478):
    for j in range(1,10):
        var = Q_values_2[i]['q' + str(j)] - Q_values_1[i]['q' + str(j)]
        sum = sum + (var * var)
print(sum)
