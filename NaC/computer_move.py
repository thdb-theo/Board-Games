# noinspection PyUnresolvedReferences
from difs import dif1, dif2, dif3, dif4
import numpy as np


def next_move(difficulty, *args):
    difficulties = {
        1: dif1.completely_random,  # random element in avalable moves
        2: dif2.winning_or_block_then_random,  # Order: win, block, random in available moves
        3: dif3.get_two_winning_moves,  # Order: win, block, get two winning, middle, random corner, random side
        4: dif4.minimax  # Calculates best move, unbeatable
    }

    return np.array(difficulties[difficulty](*args)).take(0)  # I use np.array because .take(0) returns first element regardless of dimnetion
