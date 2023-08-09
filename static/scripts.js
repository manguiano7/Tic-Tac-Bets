

//makes alerts hidden by default
document.getElementById("alert-funds").style.display = "none";
document.getElementById("alert-bet").style.display = "none";


//keeps track of turns, prevents multiple selections at one time
let turn = 1;
let human_player_letter = 'X';

if (human_player_letter == 'X') {
    comp_player_letter = 'O';
} else {
    comp_player_letter = 'X';
}

//changes button text for button that changes player letter
document.getElementById("change_comp_char").innerHTML = "Play as '" + comp_player_letter + "'";

async function compstartFunction(){
document.getElementById("bet10").disabled = true;
document.getElementById("bet50").disabled = true;
document.getElementById("bet100").disabled = true;
document.getElementById("compstart").disabled = true;
document.getElementById("change_comp_char").disabled = true;
 //removes alerts after first move is made
 document.getElementById("alert-funds").style.display = "none";
 document.getElementById("alert-bet").style.display = "none";

//sets computer player as first player
let response = await fetch('/comp_goes_first');

let position = "0";

//issues a request, triggers python code on app.py, via the next_move route
response = await fetch('/next_move?position=' + position );

// gets the text from the rendered html page
let next_move = await response.text();

//first move by computer
document.getElementById("pos" + next_move).innerHTML = comp_player_letter;
}

async function playFunction(position) {
    //disables buttons once bet is placed
    document.getElementById("bet10").disabled = true;
    document.getElementById("bet50").disabled = true;
    document.getElementById("bet100").disabled = true;
    document.getElementById("compstart").disabled = true;
    document.getElementById("change_comp_char").disabled = true;
    //removes alerts after first move is made
    document.getElementById("alert-bet").style.display = "none";
    document.getElementById("alert-funds").style.display = "none";


    if (turn == 1) {
        //keeps track of turns, prevents multiple selections at once
        turn = 2;

        //the selected box gets filled only if empty
        if (document.getElementById("pos" + position).innerHTML == "") {

            document.getElementById("pos" + position).innerHTML = human_player_letter;

            //console.log("message 1");
            //issues a request, triggers python code on app.py, via the next_move route
            let response = await fetch('/next_move?position=' + position);
            //console.log("message 2");
            // gets the text from the rendered html page
            let next_move = await response.text();

            //result of the computer's selection, determines if the game is over or if it is still in play

            if (next_move.length == 1) {
                // the game is not over, computer moves
                document.getElementById("pos" + next_move).innerHTML = comp_player_letter;
            } //length of next move = 2 means draw OR human won, i.e., since click generated win
            else if (next_move.length == 2) {
                if (next_move == '-9') {
                    document.getElementById("game_over_message").innerHTML = "DRAW!";
                    //adds overlay effect
                    game_over();
                }
                else if (human_player_letter == 'X') {
                    document.getElementById("pos" + next_move[1]).innerHTML = "X";
                    document.getElementById("game_over_message").innerHTML = "YOU WIN!";
                    //updates coin count
                    coins();
                    //adds overlay effect
                    game_over();

                }
                else if (human_player_letter == 'O') {
                    document.getElementById("pos" + next_move[1]).innerHTML = "O";
                    document.getElementById("game_over_message").innerHTML = "YOU WIN!";
                    //updates coin count
                    coins();
                    //adds overlay effect
                    game_over();

                }
            } //else length is 3, means computer wins or draw
            else {
                //leads to draw
                if (next_move[1] == '9') {
                    if (comp_player_letter == 'X') {
                        //fills box with X before showing overlay
                        document.getElementById("pos" + next_move[2]).innerHTML = "X";
                    }
                    else {
                        //fills box with O before showing overlay
                        document.getElementById("pos" + next_move[2]).innerHTML = "O";
                    }
                    //overlay with message
                    document.getElementById("game_over_message").innerHTML = "DRAW!";
                    //does overlay
                    game_over();
                }
                else if (comp_player_letter == 'X') {
                    //fills box with X before doing overlay
                    document.getElementById("pos" + next_move[2]).innerHTML = "X";
                    document.getElementById("game_over_message").innerHTML = "COMPUTER WINS!";
                    //adds overlay effect
                    game_over();
                }
                else if (comp_player_letter == 'O') {
                    //fills box with O before doing overlay
                    document.getElementById("pos" + next_move[2]).innerHTML = "O";
                    document.getElementById("game_over_message").innerHTML = "COMPUTER WINS!";
                    //adds overlay effect
                    game_over();
                }
            }
            } //end if statement checking if inner html of box is empty
            turn = 1;
        } //end if statement for turn
}

function game_over() {
    //overlay effect at the end of a game
    document.getElementById("overlay").style.display = "block";

    //makes bet buttons active again
    document.getElementById("bet10").disabled = false;
    document.getElementById("bet50").disabled = false;
    document.getElementById("bet100").disabled = false;
    document.getElementById("compstart").disabled = false;
    document.getElementById("change_comp_char").disabled = false;
}

async function reset() {
    //sets human player as first player by default
    let response = await fetch('/human_goes_first');

    //shows screen again, removes overlay
    document.getElementById("overlay").style.display = "none";
    //resets board
    for (let i = 1; i <= 9; i++) {
        document.getElementById("pos" + String(i)).innerHTML = "";
    }
}

//to be used to change the letter of the players
function change_comp_char() {
    //switches human and comp player letters
    let dummy_letter = human_player_letter;
    human_player_letter = comp_player_letter;
    comp_player_letter = dummy_letter;

    //updates button
    document.getElementById("change_comp_char").innerHTML = "Play as '" + comp_player_letter + "'";
}
//allows a user to place a bet
async function bet(bet_amount){
    //makes bet buttons disabled after any bet is made, to prevent more than one bet at a time
    document.getElementById("bet10").disabled = true;
    document.getElementById("bet50").disabled = true;
    document.getElementById("bet100").disabled = true;


    //issues a request, triggers python code on app.py
    //also updates bet table in database
    let response = await fetch('/bet?bet_amount=' + bet_amount);

    // gets the coins from the rendered html page, coins are subtracted for bet
    let coins_updated = await response.json();

    //console.log(coins_updated)
    //updates current html page with coins taken for bet
    document.getElementById("coins").innerHTML = coins_updated[0]['coins'] + "&#65504;";

      //checks for error message
    if (coins_updated[0]['error'] == 'insufficient_funds'){
        document.getElementById("alert-funds").style.display = "block";
        //resets buttons to display, since bet could not be placed
        document.getElementById("bet10").disabled = false;
        document.getElementById("bet50").disabled = false;
        document.getElementById("bet100").disabled = false;
    } else {
        document.getElementById("alert-bet").style.display = "block";
    }

}
//updates coins when winner wins
async function coins(){

    //issues a request, triggers python code on app.py
    let response = await fetch('/coins');

    // gets the coins from the rendered html page
    let coins = await response.json();

    //updates coins, sometimes nothing happens (if human lost), if human won, coins are added to
    document.getElementById("coins").innerHTML = coins[0]['coins'] + "&#65504;";

}
