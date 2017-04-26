"""A simple noughts and crosses game with two players or against the computer.
Difficultu level is set with cmd argument between 1 and 4,
1 being complety random and 4 unbeatable"""

import sys
import textwrap
import argparse
import itertools
import operator

import numpy as np

from computer_move import next_move

parse = argparse.ArgumentParser('Noughts and Crosses')
parse.add_argument('dif', nargs='?', default='4', help='AI difficulty level. ')
args = parse.parse_args()
args.dif = int(args.dif)
assert 0 < args.dif < 5


class Board:
    board = np.array([0] * 9)
    player_sign = iter(np.random.permutation([1, -1]))

    def __init__(self, name):
        self.name = name
        self.sign = next(self.player_sign)

    def __str__(self):
        subs = {0: '-', 1: 'X', -1: 'O'}
        as_str = [subs.get(x) for x in self.board]
        return textwrap.dedent(
            '''
            ┌─┬─┬─┐\t\t┌─┬─┬─┐
            │{0}│{1}│{2}│\t\t│1│2│3│
            ├─┼─┼─┤\t\t├─┼─┼─┤
            │{3}│{4}│{5}│\t\t│4│5│6│
            ├─┼─┼─┤\t\t├─┼─┼─┤
            │{6}│{7}│{8}│\t\t│7│8│9│
            └─┴─┴─┘\t\t└─┴─┴─┘
            '''.format(*as_str)
        )

    @staticmethod
    def check_game_over(board):
        board.resize(3, 3)
        return (
            all(board.diagonal()) or
            all(np.fliplr(board).diagonal()) or
            any(board.all(axis=0)) or
            any(board.all(axis=1))
        )

    def available_moves(self):
        return [i for i, x in enumerate(self.board) if not x]

    def draw(self):
        np_board = np.array(self.board)
        player = itertools.cycle((self.sign, -self.sign))
        opens = self.available_moves()
        for future in itertools.permutations(opens, len(opens)):
            copy_squares = np_board.copy()
            for move in future:
                copy_squares[move] = next(player)
            for p in [self.sign, -self.sign]:
                p_wins = copy_squares.copy()
                p_wins[p_wins == p] = 0
                if self.check_game_over(p_wins):
                    return False
                elif len(opens) == 1:
                    return True
        else:
            return True

    def take_turn(self):
        move = self.get_move()
        self.board[move] = self.sign
        personal_board = self.board.copy()
        personal_board[personal_board == -self.sign] = 0
        if self.check_game_over(personal_board):
            self.game_over()
        elif self.draw():
            self.game_over(draw=True)

    def game_over(self, draw=False):
        print(self)
        if draw:
            print('Det ble uavgjort')
        else:
            print('\n{0} vant!\n'.format(self.name))
        sys.exit()

    def get_move(self):
        raise NotImplementedError('This is supposted to be overwritten,'
                                  ' but you ran it always you muppet!')


class Human(Board):
    def get_move(self):
        print(self)
        alts = self.available_moves()
        answ = ''
        while answ not in alts:
            try:
                answ = int(input('{}: '.format(self.name))) - 1
            except ValueError:
                print('Ugyldig svar, prøv igjen')
            else:
                if answ not in alts:
                    print('Ugyldig svar, prøv igjen')

        return answ


class AI(Board):
    def get_move(self):
        answ = int(next_move(args.dif, self.board, self.sign, self.sign))
        print('{0} spilte {1}!'.format(self.name, answ + 1))
        return answ


def game_loop():
    p1 = Human('Mike')
    p2 = AI('Freddy')
    p1, p2 = reversed(sorted([p1, p2], key=operator.attrgetter('sign')))
    while True:
        p1.take_turn()
        p2.take_turn()


if __name__ == '__main__':
    print('Velkommen til Bondesjakk!')
    game_loop()
