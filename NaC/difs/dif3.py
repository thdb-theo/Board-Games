import random
from collections import Counter
from itertools import chain

import numpy as np


def get_two_winning_moves(*args):
    self = np.array([0 if x == -1 else x for x in args[0]])
    other = np.array([0 if x == 1 else -x for x in args[0]])
    self.resize(3, 3)
    other.resize(3, 3)
    available_moves = [i for i, x in enumerate(args[0]) if not x]

    possible_wins = set(win_next(self))
    other_played = {i for i, x in enumerate(chain.from_iterable(other)) if x}
    win_moves = possible_wins - other_played
    if win_moves:
        return win_moves.pop()

    possible_blockss = set(win_next(other))
    self_played = {i for i, x in enumerate(chain.from_iterable(self)) if x}
    blocks = possible_blockss - self_played
    if blocks:
        return win_moves.pop()

    # slik at du får to vinnende trekk
    get_two_winning = set()
    for i in available_moves:
        board_copy = self.copy()
        board_copy[divmod(i, 3)] = 1
        pos_wins = set(win_next(board_copy))
        wins = pos_wins - other_played
        if len(wins) > 1:
            get_two_winning.add(i)
    if get_two_winning:
        return get_two_winning.pop()

    if 4 in available_moves:
        return 4
    # et hjørne
    valid_corners = list(set(available_moves).intersection([0, 2, 6, 8]))
    if valid_corners:
        return random.choice(valid_corners)

    # en side
    valid_sides = list(set(available_moves).intersection([1, 3, 5, 7]))
    return random.choice(valid_sides)


def future(unused, board, other_played, n=1):
    rset = set()
    for i in unused:
        board_copy = board.copy()
        board_copy[divmod(i, 3)] = 1
        pos_wins = set(win_next(board_copy))
        wins = list(filter(lambda x: x not in other_played, pos_wins))
        if len(wins) > n:
            rset.add(i)
    return rset


def win_next(played):
    # diagonal top-venstre -> bunn-høyre
    diags = played.diagonal()
    if Counter(diags)[1] == 2:
        a = np.where(1 - diags)[0][0]
        yield 4 * a

    # diagonal top-høyre -> bunn-venstre
    rev_diags = np.fliplr(played).diagonal()
    if Counter(rev_diags)[1] == 2:
        a = np.where(1 - rev_diags)[0][0]
        yield 2 * a + 2

    # horisontalt
    for row in range(3):
        if Counter(played[row])[1] == 2:
            column = np.where(1 - played[row])[0][0]
            yield column + row * 3

    # vertikalt
    for row in range(3):
        if Counter(played[:, row])[1] == 2:
            column = np.where(1 - played[:, row])[0][0]
            yield column * 3 + row


if __name__ == '__main__':
    print(get_two_winning_moves([-1, 1,-1,
                                 -1, 1,-1,
                                  1, 0, 1]))
