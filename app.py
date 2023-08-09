import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import get_next_move
from helpers import get_next_move_gamble
from helpers import check_if_game_over
from helpers import login_required
from helpers import update_bets
from random import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Configure PC as a server on local network
#if __name__ == '__main__':
#    app.run(host='192.168.1.101', port=5000)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tictactoe.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    #gets coins to show on index page
    coins = db.execute("SELECT coins FROM users WHERE user_id = ?;", session["user_id"])[0]['coins']

    #sets some sessions variables to default values, basically clears board and resets players 
    #sets human as first player by default, computer as second player
    reset_sessions()

    #if user refreshes or navigates away and comes back, current bet is automatically settled to lost
    #this is to prevent refreshing when user is about to lose at the end of a game
    if session['bet_id'] != None:
        update_bets("LOST",session['user_id'], session['bet_id'])
        session['bet_id'] = None

    return render_template("index.html", coins = coins)

@app.route("/next_move", methods=["GET","POST"])
@login_required
def next_move():

    #if (session['num_moves'] == 0):
       # session['comp_player'] = request.args.get("comp_player")
       # session['human_player'] = '2'

    #keeps track of number of moves, used to make sure functions (comp_goes_first, human_goes_first) work only for blank board
    session['num_moves'] += 1

    #position is selected position from index page, used to update the board state: session['state_list']
    position = int(request.args.get("position"))
    #if position=0, computer goes first, but may as well check to make sure it is within bounds [1,9]
    if position >= 1 and position <= 9:
        #print("position is " + str(position))
        #updates board
        session['state_list'][position - 1] = session['human_player']

        #checks if there is a winner, uses the last selected position for faster execution
        winner = check_if_game_over(session['state_list'], position)
        #print("1  - winner is "+ winner)

        #draw or human wins here regardless of whether human was first or second player
        if winner != '0':
            #resets some sessions variables, similar as before on index page
            reset_sessions()
            #means draw
            if winner == '9':
                #checks if bet was placed
                if session['bet_id'] != None:
                    #if placed, updates bet status to lost
                    update_bets("LOST",session['user_id'], session['bet_id'])
                    #resets sessions variable that keeps track of bets
                    session['bet_id'] = None
                #-9 means draw
                next_1 = '-9'

                return render_template("next_move.html", next_1=next_1)

            #gets coins for adding to later; if bet won, major gain of coins, otherwise small gain of coins
            coins = db.execute("SELECT coins FROM users WHERE user_id = ?;", session["user_id"])[0]['coins']

            #IF ABOVE IF STATEMENT IS NOT TRUE, HUMAN WON, WIN IS BASED ON CLICK
            #checks if bet was placed
            if session['bet_id'] != None:

                #gets bet amount based on previous id, for adding this to coins in user database
                bet_amount = db.execute("SELECT bet_amount FROM bets WHERE bet_id = ?;", session['bet_id'])[0]['bet_amount']

                #updates coins based on bet amount
                # 3 is added for each bin, regardless if bet was placed (this allows users to accumulate coins by playing)
                #coins will be updated in database soon after this
                coins = coins + (2 * bet_amount) + 3

                #bet status updated to WON
                db.execute("UPDATE bets SET bet_status = ?, time_bet_settled = ? WHERE bet_id = ?", "WON", str(datetime.utcnow())[0:-7], session['bet_id'] )
                #reset bet id session variable to None, to indicate no bet is placed
                session['bet_id'] = None
            else:
                #just adds 3 if no bet was placed (because human WON the game)
                #coins will be updated in database soon after
                coins = coins + 3
            #updates coins in user database to add funds from bet (major gain) or from just winning (small gain)
            db.execute("UPDATE users SET coins = ? WHERE user_id = ?", coins, session["user_id"])

            if winner == '1':
                #-1 means 1st player (player to go 1st) wins
                next_1 = '-1'
                return render_template("next_move.html", next_1=next_1)

            elif winner == '2':
                #-2 means 2nd player (player to go 2nd) wins
                next_1 = '-2'

                return render_template("next_move.html", next_1=next_1)

    #adds some randomness to the decisions
    #makes game partially deterministic, partially probabilistic
    random_num = random()
    #if game is not over, next move is determined

    #prob threshold for making decision between deterministic and probabilistic functions
    prob_threshold = 0.62
    #random makes this more or less deterministic
    if random_num <= prob_threshold:
        #deterministic version of next move function (based on max Q values)
        next_1 = get_next_move(session['state_list'])
    else:
        #probabilistic version of next move function (less deterministic but still deterministic)
        next_1 = get_next_move_gamble(session['state_list'])

    #updates board to reflect the computer's decided move
    session['state_list'][next_1 - 1] = session['comp_player']

    #checks again if there is winner
    winner = check_if_game_over(session['state_list'], next_1)

    #print(string_to_list)
    #print("2  - winner is "+ winner)
    #print("2 string is "+ str(session['state_list']))
    #computer always wins here. but computer can be first or second player
    if winner != '0':
        #resets sessions
        reset_sessions()

        #checks if bet was placed
        if session['bet_id'] != None:
            #if bet placed, bet lost
            update_bets("LOST",session['user_id'], session['bet_id'])
            #clears session for bet
            session['bet_id'] = None
        if winner == '1':
            #indicates which player (1 or 2) won - in either case, computer won not human
            next_1 = '-1' + str(next_1)

        elif winner == '2':
            next_1 = '-2' + str(next_1)

        elif winner == '9':
            next_1 = '-9' + str(next_1)
    #print("3 string is "+ str(session['state_list']))
    #used to update the index page - update where the computer moved to
    return render_template("next_move.html", next_1=next_1)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    #reset error code
    code = 100

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            #error code
            code = 400
            message = "Please provide username."
            return render_template("login.html", code=code, message=message), code

        # Ensure password was submitted
        elif not request.form.get("password"):
            code = 400
            message = "Please provide password."
            return render_template("login.html", code=code, message=message), code

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            code = 400
            message = "Invalid username and/or password."
            return render_template("login.html", code=code, message=message), code

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        #keeps track of bets
        session['bet_id'] = None

        #resets sessions to default values
        reset_sessions()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        message = ""
        return render_template("login.html", code=code, message=message)

@app.route("/logout")
def logout():
    """Log user out"""

    #if user logs out, all open bets are automatically settled to lost
    update_bets("LOST", session['user_id'], "clear_all")

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    #reset error code
    code = 100
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        #checks if username was submitted and is unique
        if request.form.get("username"):
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            #checks if database already has that username
            if len(rows) != 0:
                #error code
                code = 400
                message = "Username already exists."
                return render_template("register.html", code=code, message=message), code

        # if username not submitted
        elif not request.form.get("username"):
            code = 400
            message = "Please provide username."
            return render_template("register.html", code=code, message=message), code

        #new if statements
        # Ensure password was submitted
        if not request.form.get("password"):
            code = 400
            message = "Please provide password."
            return render_template("register.html", code=code, message=message), code

        
        elif not request.form.get("confirmation"):
            code = 400
            message = "Please confirm password."
            return render_template("register.html", code=code, message=message), code


        elif request.form.get("password") != request.form.get("confirmation"):
            code = 400
            message = "Passwords must match."
            return render_template("register.html", code=code, message=message), code

        #adds user to database - only gets executed if all above tests are passed
        else:
            db.execute("INSERT INTO users(username, hash) VALUES(?,?);", request.form.get("username"), generate_password_hash(request.form.get("password")))
            return render_template("login.html")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        message = ""
        return render_template("register.html", code=code, message=message)

@app.route("/bet", methods=["GET","POST"])
@login_required
def bet():
    #gets bet from javascript, stores in session variable, so that it can be used to update coins in user database later if necessary
    bet_amount = int(request.args.get("bet_amount"))

    #gets coins from database
    coins = db.execute("SELECT coins FROM users WHERE user_id = ?;", session["user_id"])[0]['coins']

    #initializes error, used to keep track of if user has sufficient funds to place bets
    error = ''
    #makes sure user has enough funds
    #also makes sure bet amount is equal to or less than max amount allowed by buttons (100)
    if coins >= bet_amount and bet_amount <= 100:
        #subtracts bet amount from coins in database
        coins = coins - bet_amount

        #updates database to reflect bet placed and reduced coin amount
        db.execute("UPDATE users SET coins = ? WHERE user_id = ?", coins, session["user_id"])

        #adds bet entry to bets database
        #db.execute INSERT automatically returns primary key, i.e., bet_id
        session['bet_id'] = db.execute("INSERT INTO bets (user_id, bet_amount, time_bet_placed, bet_status) VALUES(?,?,?,?)", session['user_id'],bet_amount, str(datetime.utcnow())[0:-7],"PENDING")
    else:
        error = 'insufficient_funds'
        #resets session bet id
        session['bet_id'] = None
    #redirects to tic tac toe page
    return render_template("coins.html", coins=coins, error=error)

@app.route("/coins", methods=["GET","POST"])
@login_required
def coins():
    coins = db.execute("SELECT coins FROM users WHERE user_id = ?", session["user_id"])[0]['coins']
    return render_template("coins.html", coins=coins)

@app.route("/comp_goes_first", methods=["GET","POST"])
@login_required
def comp_goes_first():
    #makes sure we have blank board
    if session['num_moves'] == 0:
        #computer is set to first player
        session['comp_player'] = '1'
        session['human_player'] = '2'
    #print("comp first session comp is " + session['comp_player'])
    #print("comp first session human is " + session['human_player'])
    return '0'

@app.route("/human_goes_first", methods=["GET","POST"])
@login_required
def human_goes_first():
    #used when human goes first - human is the first player
    #makes sure we have blank board
    if session['num_moves'] == 0:
        #computer is second player
        session['comp_player'] = '2'
        session['human_player'] = '1'
    #print("human first session comp is " + session['comp_player'])
    #print("human first session human is " + session['human_player'])
    return '0'

@app.route("/past_bets", methods=["GET","POST"])
@login_required
def past_bets():
    #gets all bets for user in database, used for past bets web page
    past_bets = db.execute("SELECT * FROM bets WHERE user_id = ?", session['user_id'])
    #sign is positive or negative, keeps track of wins (positive) and losses (negative)
    coins_won_bets = 0
    for bet in past_bets:
        if bet['bet_status'] == "WON":
            sign = 1
        else:
            sign = -1
        #keeps track of how many coins user has won
        coins_won_bets = coins_won_bets + (sign * bet['bet_amount'])

    total_coins = db.execute("SELECT coins FROM users WHERE user_id = ?;", session["user_id"])[0]['coins']
    #1000 is default initial coin amount
    coins_won_playing = total_coins - coins_won_bets - 1000

    return render_template("past_bets.html", past_bets=past_bets, coins_won_bets=coins_won_bets, coins_won_playing=coins_won_playing,total_coins=total_coins)

def reset_sessions():
    #resets board
    session['state_list'] = ['0'] * 9
    #keeps track of number of moves
    session['num_moves'] = 0
    #computer is second player by default
    session['comp_player'] = '2'
    #human is first player
    session['human_player'] = '1'

@app.route("/changepassword", methods=["GET", "POST"])
def changepw():
    """ChangePW"""

    # Forget any user_id
    session.clear()
    code = 100
    message = ""

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            code = 400
            message = "Please provide username."
            return render_template("changepw.html", code=code, message=message), code

        # Ensure password was submitted
        elif not request.form.get("password"):
            code = 400
            message = "Please provide old password."
            return render_template("changepw.html", code=code, message=message), code

        # Ensure new password was submitted
        elif not request.form.get("newpassword"):
            code = 400
            message = "Please provide new password."
            return render_template("changepw.html", code=code, message=message), code

        # Ensure password was confirmed
        elif not request.form.get("confirmation"):
            code = 400
            message = "Please confirm new password."
            return render_template("changepw.html", code=code, message=message), code

        #ensure passwords match
        elif request.form.get("newpassword") != request.form.get("confirmation"):
            code = 400
            message = "Passwords must match."
            return render_template("changepw.html", code=code, message=message), code


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            message = "Invalid username and/or password."
            code = 400
            return render_template("changepw.html", code=code, message=message), code
            
        #changes password in database
        db.execute("UPDATE users SET hash = ? WHERE username = ?;", generate_password_hash(request.form.get("newpassword")),request.form.get("username"))

        #returns to login
        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepw.html")

