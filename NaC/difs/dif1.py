import random


def completely_random(*args):
    common_board = args[0]
    available_moves = [i for i, x in enumerate(common_board) if not x]
    return random.choice(available_moves)
