import os
from random import random
import math
from cs50 import SQL
import requests
from functools import wraps
from flask import redirect, render_template, request, session
from datetime import datetime

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tictactoe.db")

# CHECKS IF GAME IS OVER AND IF OVER
# RETURNS WHO WINNER IS
def check_if_game_over(state_string, position):
    #checks if first position is zero. If zero, it is not occupied
    if position == 1:
        #checks all wins where winner occupied zero "0" position
        #checks top horizontal row of tic tac toe
        if state_string[0] == state_string[1]:
            if state_string[1] == state_string[2]:
                #returns winner, whatever is at position 0
                return state_string[0]

        #checks left vertical row of tic tac toe
        if state_string[0] == state_string[3]:
            if state_string[3] == state_string[6]:
                #returns winner, whatever is at position 0
                return state_string[0]

        #checks diagonal left of tic tac toe
        if state_string[0] == state_string[4]:
            if state_string[4] == state_string[8]:
                #returns winner, whatever is at position 4 for example since they are all the same
                return state_string[4]

    elif position == 2:
        #checks top horizontal row of tic tac toe
        if state_string[0] == state_string[1]:
            if state_string[1] == state_string[2]:
                #returns winner, whatever is at position 0
                return state_string[0]

        #checks vertical middle
        if state_string[1] == state_string[4]:
            if state_string[4] == state_string[7]:
                #returns winner, whatever is at position 4
                return state_string[4]

    elif position == 3:
        #checks top horizontal row of tic tac toe
        if state_string[0] == state_string[1]:
            if state_string[1] == state_string[2]:
                #returns winner, whatever is at position 0
                return state_string[0]
        #right vertical row
        if state_string[2] == state_string[5]:
            if state_string[5] == state_string[8]:
                #returns winner, whatever is at position 8
                return state_string[8]
        #checks diagonal right
        if state_string[2] == state_string[4]:
            if state_string[4] == state_string[6]:
                #returns winner, whatever is at position 4
                return state_string[4]

    elif position == 4:
        #checks horizontal middle
        if state_string[3] == state_string[4]:
            if state_string[4] == state_string[5]:
                #returns winner, whatever is at position 4
                return state_string[4]

        #checks left vertical row of tic tac toe
        if state_string[0] == state_string[3]:
            if state_string[3] == state_string[6]:
                #returns winner, whatever is at position 0
                return state_string[0]

    elif position == 5:
        #checks diagonal left of tic tac toe
        if state_string[0] == state_string[4]:
            if state_string[4] == state_string[8]:
                #returns winner, whatever is at position 4 for example since they are all the same
                return state_string[4]

        #checks diagonal right
        if state_string[2] == state_string[4]:
            if state_string[4] == state_string[6]:
                #returns winner, whatever is at position 4
                return state_string[4]

        #checks vertical middle
        if state_string[1] == state_string[4]:
            if state_string[4] == state_string[7]:
                #returns winner, whatever is at position 4
                return state_string[4]

        #checks horizontal middle
        if state_string[3] == state_string[4]:
            if state_string[4] == state_string[5]:
                #returns winner, whatever is at position 4
                return state_string[4]

    elif position == 6:
        #checks horizontal middle
        if state_string[3] == state_string[4]:
            if state_string[4] == state_string[5]:
                #returns winner, whatever is at position 4
                return state_string[4]
        #right vertical row
        if state_string[2] == state_string[5]:
            if state_string[5] == state_string[8]:
                #returns winner, whatever is at position 8
                return state_string[8]

    elif position == 7:
        #bottom horizontal row
        if state_string[6] == state_string[7]:
            if state_string[7] == state_string[8]:
                #returns winner, whatever is at position 8
                return state_string[8]
        #checks left vertical row of tic tac toe
        if state_string[0] == state_string[3]:
            if state_string[3] == state_string[6]:
                #returns winner, whatever is at position 0
                return state_string[0]
        #checks diagonal right
        if state_string[2] == state_string[4]:
            if state_string[4] == state_string[6]:
                #returns winner, whatever is at position 4
                return state_string[4]

    elif position == 8:
        #checks positions where winner occupied last "8" position
        #bottom horizontal row
        if state_string[6] == state_string[7]:
            if state_string[7] == state_string[8]:
                #returns winner, whatever is at position 8
                return state_string[8]

        #middle vertical row
        if state_string[1] == state_string[4]:
            if state_string[4] == state_string[7]:
                #returns winner, whatever is at position 4
                return state_string[4]


    #last position is position 9
    elif position == 9:
        #checks positions where winner occupied last "8" position
        #bottom horizontal row
        if state_string[6] == state_string[7]:
            if state_string[7] == state_string[8]:
                #returns winner, whatever is at position 8
                return state_string[8]

        #right vertical row
        if state_string[2] == state_string[5]:
            if state_string[5] == state_string[8]:
                #returns winner, whatever is at position 8
                return state_string[8]
        #checks diagonal left of tic tac toe
        if state_string[0] == state_string[4]:
            if state_string[4] == state_string[8]:
                #returns winner, whatever is at position 4 for example since they are all the same
                return state_string[4]
    #position = 0 means empty board. means computer goes first
    if position == 0:
        return '0'
    else:
        sum = 0
        #if above checks fail, draw or no winner yet
        #checks for draw
        for i in range(9):
            if state_string[i] == '0':
                sum += 1

        #draw if all other checks fail
        if sum == 0:
            return '9'
        else:
            return '0'

#returns next position of computer, deterministic version
def get_next_move(state_list):
    #gets computer's next move based on max Q values
    #print(player)
    state_string = ''
    for i in range(9):
        state_string = state_string + state_list[i]

    #finds state in database
    state_id = db.execute("SELECT id FROM Q_values WHERE state_string = ?", state_string)[0]['id']

    Q_values_dict = db.execute("select q1, q2, q3, q4, q5, q6, q7, q8, q9 FROM Q_values WHERE id = ?", state_id)[0]

    max_i = 0
    #keeps track of max Q value
    max = -30.0

    #finds max Q value
    for i in range(9):
        #converts dictionary to list
        if float(Q_values_dict['q' + str(i+1)]) > max:
            max = float(Q_values_dict['q' + str(i+1)])
            max_i = i + 1
    #the computer's next position, position having highest Q value
    return max_i

#computer's next move, probabilistic version
#similar to how program trained
def get_next_move_gamble(state_list):
    #print(player)
    #starts setting out probability bins, for each decision, eventually adds up each exponential
    #bin 1 / endpoint for bin 1
    #reduction factor makes values more the same, introduces more risk, more randomness into decision
    reduction_factor = 1.0

    list_of_prob_bins = [0.0] * 10

    Q_values_dict_to_list = [0.0] * 9

    state_string = ''
    for i in range(9):
        state_string = state_string + state_list[i]

    #will be used as denominator, calculated using Boltzman factors exponentials e^1 + e^2 + e^3 + ... +... e^n
    sum_prob = 0.0
    #Q values from database
    Q_values_dict = db.execute("select q1, q2, q3, q4, q5, q6, q7, q8, q9 FROM Q_values WHERE state_string = ?", state_string)[0]

    for i in range(9):
        #converts dictionary to list
        Q_values_dict_to_list[i] = reduction_factor * float(Q_values_dict['q' + str(i+1)])
        #calculates "total" of Boltzmann factors, sum of exponentials
        #~e^(Q)
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
    #computer's next move, similar to how program was trained
    return bin_upper

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#function to update bets database since this is reused a lot
def update_bets(status, user_id, bet):
    #bet can be bet id or bet can be "clear_all" indicating all open bets are to be cleared
    if bet == "clear_all":
        #finds open bets
        bet_id = db.execute("SELECT bet_id FROM bets WHERE user_id = ? AND bet_status = 'PENDING';", user_id)

        for id in bet_id:
            #updates each open bet
            db.execute("UPDATE bets SET bet_status = ?, time_bet_settled = ? WHERE bet_id = ?", status, str(datetime.utcnow())[0:-7], id['bet_id'])
    elif bet != None:
        db.execute("UPDATE bets SET bet_status = ?, time_bet_settled = ? WHERE bet_id = ?", status, str(datetime.utcnow())[0:-7], bet)