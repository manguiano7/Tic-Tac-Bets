# Tic Tac Bets
#### Video Demo:  https://youtu.be/K6R_BjNBs-4
#### Description:

## 1. Training the Computer to Play

The program train.py is used to train the computer to play Tic Tac Toe.
Essentially, the program uses a Q-learning algorithm (a reinforcement learning algorithm).
The program does not need any inputs as the program creates and finds Tic Tac Toe states, and learns as it runs.
The program adds states and associated Q values for actions in the database table "Q_values" in tictactoe.db.
Simply run the file by entering the following in the command line:

python3 train.py

However, due to long training cycles, this program will have to be run many times, so the above command must be repeated a few times (or alternatively, the variable iterations should be made larger). The number of iterations is set to 5000 so that the progam does not run all day. Knowing when to stop running the program (which also stops learning) can be difficult. I stopped after probably around 50,000-100,000 iterations. I observed when the number of states in the Q_values table stayed relatively constant (meaning the program stopped finding new states), and then trained about 20,000 more times after that. It is not so necessary for the program to play perfectly since the computer will be slightly probabilistic for randomness and for fun.

To help me decide when to stop training, I created a very simple program called

difference.py

The above program calculates a difference of Q values between two Q value tables, squares the differences, and adds them together. Tictactoe databases have to be manually renamed so the old database has the name:

tictactoe_old.db

and the new database has the name:

tictactoe.db

If the total squared difference becomes small (50-100) and stays relatively constant, it may be ok to stop training. Ultimately, I decided to stop training when I felt like the program knew how to play. In the end, the website did not depend so much on a program that can play Tic Tac Toe well. Rather, in the end, I made it more probabilistic than deterministic, and added betting to make it more "fun."

Turning back to the first program, train.py, this program creates/finds new Tic Tac Toe states as it plays against itself. For example, the empty board is:
000000000

The first state found (through programmed rules and probabilistic selections) was
100000000

The second state found was
100000002

The number "0" indicates an empty space on the board, "1" indicates the first player position (could be "O" or "X" depending on the user's selection), and "2" indicates the second player position (could be "O" or "X"). The computer or the user (human) can be either the first or second player depending on the user's selection. Numbers 0, 1, and 2 were used  to simplify the states using the symmetry of the game, and it allows us to minimize the number of states in the table, i.e., avoid redundant states. I considered using "X" and "O" in the Q values table but the user can change if they want to play as "X" or play as "O" which would have caused me to create a second redundant table (one where X goes first and one where O goes first). Here, "1" ALWAYS goes first which makes logical sense. "2" goes second.

The Q learning algorithm is somewhat simple. For every state of the board there are 9 positions / available moves (even occupied positions which will be detailed hereafter). For every state, a Q value is assigned to each position /move on the board. For a winning game, the winning move gets a Q value of 1. A draw game results in a Q value of 0.1 for the last move. For occupied positions, (a position having "1" or "2"), the Q value is -30, essentially resulting in an extremely low chance of moving to a position that is already occupied. Technically an occupied state is available during training but the chance of moving to that state is exponentially small (~e^-30), basically 0. During training, no last move is a losing move as every last move results in either a draw or win. Moves before the end of the game get a Q value according to the Q learning algorithm:

Q = Q + (learning_rate * (reward + (discount_factor * next_max_reward) - Q))

The learning_rate, reward, and discount_factor are predetermined and are between 0 and 1. Details on choosing the values of these variables can be found online.

The next_max_reward is

-1.0 * max(Q_values_dict_to_list)

The Q_values_dict_to_list are the Q values of the next state resulting from the move that took you there. The max of these Q values (for the next state) is used for the Q value of the move (i.e., action) that took you from the last state to the next state, and it is this term that connects states together. There is a negative sign out in front of the max function because players play against each other. So the Q values of one state (played by e.g., human) and another state (played by e.g., computer) connected by a single move should oppose each other in some way.  Your opponent's gains are your losses; your losses are your opponent's gains. This negative sign is not traditionally included in the Q learning algorithm, at least not explicitly, but a training problem was discovered while testing the program. The negative sign solved it.

To select any available position / move (i.e., action) for any given state of the board, the training program uses Boltzmann factors:

Prob(moving to i) = e^(Q_i) / sum_j (e^(Q_j))

where Q_i is the Q value for moving to the ith position on the board, and the denominator is a sum of exponentials of Q values for all available moves. The above equation is probabilistic and allows the training program to find new states not previously inserted into the tictactoe database.

The train.py uses a program check_if_game_over in helpers.py to check if the game is over. It checks horizontal, vertical, and diagonal rows /columns and returns the player (1 or 2) that had matching rows /columns. It also returns a value 9 if the game was a draw, or a value 0 if the game is not over yet.

## 2. The Tic Tac Toe Website
The Tic Tac Toe website is based on on an app.py file, the helpers.py file that has functions for the app.py file, html pages in the templates folder, and css file in the static folder.

There are many parts to the website, let's talk about a few things.

### The Index Page

The Index.html page has a tic tac toe board and buttons:
-Computer Goes First, which allows the computer to make the first move
-Play as 'O' (or Play as 'X') to allow the user to change their character on the board
-Bet 10x to bet 10 coins
-Bet 50x to bet 50 coins
-Bet 100x to bet 100 coins

and the page has a coin count.

The front end of the game is in Index.html, the javascript code on the same page, and the associated css file. All buttons get disabled after any player (human or computer) makes the first move. This prevents the user from making a change to the game when the game already started or to prevent the user from betting mid-game (e.g., right before they are about to win). At the end of every game, these buttons get enabled.

The back end of the game is in app.py. The session variables in app.py include:
-state_list to keep track of board states
-user_id to store the user's id and keep track of logged in users
-comp_player to keep track of who went first, if 1, the computer went first. If 2, computer went second.
-human_player, redundant variable to store if human went first / second (redundant in view of comp_player)
-bet_id to keep track of bets made
-num_moves to keep track of number of moves made while game is played

The session variable state_list in app.py is updated as each selection (i.e., move) is made on the Index.html page, and is updated based on the selected positions of the board. The user selects positions by selecting squares on the board. The computer selects positions via app.py and the functions get_next_move and get_next_move_gamble in the helpers.py file. The program is designed to update the cookie file based only on selected positions to prevent a nefarious user from feeding app.py a finished board state. Also, the Index.html page is updated as each move is made.

### Difficulty Level (i.e., more probabilistic vs. more deterministic)
There are two functions in helpers.py to help the computer select positions in app.py: get_next_move and get_next_move_gamble; in combination, these two functions make the game partially deterministic (more difficult) and partially probabilistic (less difficult). A completely deterministic game would have been boring. For each move, the function get_next_move selects the position with the maximum Q value and so is completely deterministic. The function get_next_move_gamble selects positions similar to how train.py selects positions during training, i.e., it selects positions by using Boltzmann factors. That is, get_next_move_gamble is not completely random; it still selects positions based on Q values and the higher the Q value for a position is, the higher the chance for selecting that position. For every move, a decision is made to decide between using the deterministic function get_next_move and the probabilistic function get_next_move_gamble. This decision is made by using a random number between 0 and 1, and is designed so that app.py uses the deterministic function about 70% of the time which is a good balance. This can be tweaked by tweaking prob_threshold which is presently 0.7.

Each time a move is made (by the user or computer) the same function check_if_game_over used during training is used here to check if the game is over in app.py / helpers.py. When a game is over, several session variables are reset (state_list, comp_player, human_player, bet_id, num_moves). If a user wins, they obtain 3 coins (to prevent the user from running out of coins), and the coins variable in the table users in the tictactoe.db database file is updated.

Likewise, when a game is over, the Index.html page is notified and an overlay screen pops up to let the user know who won (them or the computer). It also allows the user to play again by selecting the Play Again button. After selecting this button, the board on the Index page is reset. Also, the Index page is updated to reflect the updated amount of coins.

On the Index.html page, all bet buttons get disabled after selecting any one of them. That is, only a single bet can be placed for any game.

When a bet is placed, a request is made on app.py and the corresponding amount of coins gets deducted from the coins variable in the table users in the tictactoe.db database file, and a new bet entry is added to the bets table in the same database file, with the bet_id user_id, bet amount, time bet placed, and bet status=PENDING. The session variable bet_id keeps track of the bet placed. Upon winning, twice the amount of coins bet is added to the users table(since a single amount was previously deducted). After the end of every game, the app.py program checks if a bet was placed and if so, updates the bets table to reflect whether the status of the bet is WON or LOST, and the time at which the bet was WON or LOST. A draw game is considered a LOST bet.

### The Past Bets Page
Upon clicking on Past Bets, a table showing all bets placed by the user, the coins won or lost from bets placed, the coins won from playing, and the total coins, is displayed. The table includes the bet amount, the time the bet was placed, the time the bet was settled, the bet status (won, lost, or pending).

### Running the App
To run, in terminal, type: "export FLASK_APP=app.py"
Then type "flask run"
