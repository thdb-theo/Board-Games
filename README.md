# Board-Games

Includes Battleships, Nought and Crosses (aka tictactoe), Dots and Boxes and simulating Monopoly.

## Install:

1. Clone the repository like so: `git clone "https://github.com/thdb-theo/Board-Games"`
2. Change directory into the new directory
3. Follow the instructions for the game you want to play which are below.

## Requirements:

mumpy for Battleships and Noughts and Crosses.

matplotlib for monopoly

colorama for Dots and Boxes

### Battleships

To start a game type: `python Battleships.py`

To see command line argunments, type `python Battleships.py -h`:

To input a ships location type the coordinate you want the ship's head and then the coordinate in the direction the ship will go.

For example if you want a ship beween d1 and d5; First type d1 and then d2. If you want it from d1 to h1; First type d1, then e1.

### Monopoly

To start a simulation, type: `python Monopoly/monopoly.py`

To see command line argunments, type `python Monopoly/monopoly.py -h`:

The first argumnet must be either -p for a piw chart or -b for a bar chart.

TODO: Write all of this
