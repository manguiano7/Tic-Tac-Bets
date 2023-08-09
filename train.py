# This program can be used for creating and training a computer to play
# using a database which is created by this program. Just run the program
# over and over again until satisfied with the way the program plays Tic Tac Toe.
# Program finds states so training should continue until program stops finding new states.

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tictactoe.db")

#constants for learning algorithm
learning_rate = 0.7
discount_factor = 0.5

#first starting board
original_state_string = "000000000"
state_string = original_state_string

#player is 1 or 2, NULL is 0
player = "1"

#print(state_string)

#state_string as a list datatype, not string
state_string_list = [""] * 9

#keeps track of probabilities for each position on the board
pos_n = [0.0]*9

#eventually converts dict of Q values database to list
Q_values_dict_to_list = [0.0] * 9

#keeps track of probability bins for each round of the game, for each decision that has to be made
list_of_prob_bins = [0.0] * 10

#checks if state is in database
state_id = db.execute("SELECT id FROM Q_values WHERE state_string = ?", state_string)

#if state is not found in list of states, adds state to database
if len(state_id) != 1:
    #adds state to database
    #sets all values to zeros initially
    db.execute("INSERT INTO Q_values(q1, q2, q3, q4, q5, q6, q7, q8, q9, state_string) VALUES(?,?,?,?,?,?,?,?,?,?);", pos_n[0], pos_n[1], pos_n[2],pos_n[3],pos_n[4],pos_n[5],pos_n[6],pos_n[7],pos_n[8],state_string)
    state_id = db.execute("SELECT id FROM Q_values WHERE state_string = ?", state_string)[0]['id']
else:
    state_id = state_id[0]['id']

#saves the id for the first state, to be used for each iteration of the loop
first_id = state_id

#print(state_id)

#finds previously created states and their current probabilities
Q_values_dict = db.execute("select q1, q2, q3, q4, q5, q6, q7, q8, q9 FROM Q_values WHERE id = ?", state_id)[0]

#print(Q_values_dict)

#BEFORE MAJOR LOOP
iteration = 0
#-----------------------------------------------------------------------------------------------------------

while iteration < 5000:
    #print(state_string)

    #print(player)
    #starts setting out probability bins, for each decision, eventually adds up each exponential
    #bin 1 / endpoint for bin 1
    list_of_prob_bins[0] = 0.0

    #total of denominator, using Boltzman factors exponentials e^1 + e^2 + e^3 + ... +... e^n
    sum_prob = 0.0
    for i in range(9):
        #converts dictionary to list
        Q_values_dict_to_list[i] = float(Q_values_dict['q' + str(i+1)])
        #calculates "total" of Boltzmann factors, sum of exponentials
        sum_prob += math.exp(Q_values_dict_to_list[i])

    #random number for selecting a bin - ith bin indicates where the player moves next
    random_num = random()

    #creates the remaining probability bins, within range 0, 1
    for i in range (1,10):
        #starts at bin 2 or endpoint of bin 2
        #(bin 1 is set outside the for loop above)
        list_of_prob_bins[i] = list_of_prob_bins[i-1] + (math.exp(Q_values_dict_to_list[i-1])/sum_prob)

    #binary search algorithm -> divide upper_bound - lower bound in 2 each time
    #upper_bound-lower_bound = 9 to begin with
    lower_bound = 0
    upper_bound = 9

    #set initial bin to the middle bin
    bin_lower = 4
    bin_upper = 5

    #print(list_of_prob_bins)
    i = 0

    #for making the next decision, which bin, i.e. which position to move to
    while True:
        #condition met -> found bin!
        if random_num > list_of_prob_bins[bin_lower] and random_num <= list_of_prob_bins[bin_upper]:
            break
        elif random_num > list_of_prob_bins[bin_upper]:
            lower_bound = bin_upper
            bin_lower = int((upper_bound - lower_bound)/2) + lower_bound
            bin_upper = bin_lower + 1

        else:
            upper_bound = bin_lower
            bin_lower = int((upper_bound - lower_bound)/2) + lower_bound
            bin_upper = bin_lower + 1
        #print(random_num, list_of_prob_bins[bin_lower], list_of_prob_bins[bin_upper])
        #print(lower_bound, upper_bound)
        #i += 1
    #print(bin_upper)

    #if state_string[bin_upper - 1] != '0':
     #   print("ERROR")
     #   print(bin_upper)
     #   print(Q_values_dict_to_list)
     #   print(list_of_prob_bins)

    #copies state_string into list since string is immutable, unchangeable
    for i in range(9):
        state_string_list[i] = state_string[i]

    #changes state of string
    #changes the ith position to X or O
    #this is a list not actual string!
    state_string_list[bin_upper - 1] = player

    #creates new state string (actually a string)
    state_string = state_string_list[0]

    #creates new state string
    for i in range (1,9):
        #adds list elements (i.e. characters) to state string to create new string
        state_string = state_string + state_string_list[i]
    #print("after")
    #print(state_string[0:3])
    #print(state_string[3:6])
    #print(state_string[6:9])
    #print(" ")
    #winner of game
    #print(state_string)
    winner = check_if_game_over(state_string, bin_upper)
    #print(state_string)
    #-------------------------------------------------------------------------------------
    #Q learning algorithm

    #checks if new state is in database
    new_state_id = db.execute("SELECT id FROM Q_values WHERE state_string = ?", state_string)

    #if new state is not found in list of states, adds state to database
    if len(new_state_id) != 1:
        #adds state to database
        #sets unoccupied positions to zero, occupied to -99
            #zeros out where positions are taken by previous turns
        for i in range(9):
            if state_string[i] == "0":
                pos_n[i] = 0.0
            else:
                #if position is occupied, probability of moving to the ith position is practically 0.0
                #could have made this -99 even
                pos_n[i] = -30.0
        db.execute("INSERT INTO Q_values(q1, q2, q3, q4, q5, q6, q7, q8, q9, state_string) VALUES(?,?,?,?,?,?,?,?,?,?);", pos_n[0], pos_n[1], pos_n[2],pos_n[3],pos_n[4],pos_n[5],pos_n[6],pos_n[7],pos_n[8],state_string)
        new_state_id = db.execute("SELECT id FROM Q_values WHERE state_string = ?", state_string)[0]['id']
    else:
        #since this is a dictionary, need to find id
        new_state_id = new_state_id[0]['id']


    if winner == player:
        #if game is over, Q is equal to reward for winning
        Q = 1.0

    elif winner == '9':
        #if game is over Q is equal to reward for draw
        Q = 0.1

    else:
        #this executes if the game is not over, Q is updated iteratively for each turn taken
        #for getting the max reward for the new state
        Q_values_dict = db.execute("select q1, q2, q3, q4, q5, q6, q7, q8, q9 FROM Q_values WHERE id = ?", new_state_id)[0]

        #print(Q_values_dict)
        #print(state_string[0:3])
        #print(state_string[3:6])
        #print(state_string[6:9])

        #remember "Q" value from previous state, this led to previous decision
        Q = Q_values_dict_to_list[bin_upper-1]

        #print("Q is" + str(Q))

        #converts dictionary to list
        for i in range(9):
            Q_values_dict_to_list[i] = float(Q_values_dict['q' + str(i+1)])

        #negative since the new Q list is for the other player!!!!
        next_max_reward = -1.0 * max(Q_values_dict_to_list)
        reward = 0.0

        Q = Q + (learning_rate * (reward + (discount_factor * next_max_reward) - Q))

    #print("Q is" + str(Q))

    #needs to be state_id not new state_id
    db.execute("UPDATE Q_values SET ? = ? WHERE id = ?;", 'q' + str(bin_upper), Q, state_id)

    state_id = new_state_id

    #changes player turn
    if player == "1":
        #saves the last state id for player 1
        #last_1_id = state_id
        #last_1_position = bin_upper
        player = "2"
    else:
        #saves the last state id for player 2
        #last_2_id = state_id
        #last_2_position = bin_upper
        player = "1"

    #resets state string if the game is over
    if winner != '0':
        #print("Game over!")
        #print("winner is " + str(winner))
        #print(state_string[0:3])
        #print(state_string[3:6])
        #print(state_string[6:9])
        state_string = original_state_string
        state_id = first_id
        Q_values_dict = db.execute("select q1, q2, q3, q4, q5, q6, q7, q8, q9 FROM Q_values WHERE id = ?", state_id)[0]

        player = "1"
        iteration += 1


    #iteration += 1