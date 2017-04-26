"""Traditional Battleships where you can play against the computer or another player.
You can also change the size of the board and the lengths of the ships"""

import random
import copy
import sys
import itertools
import collections
import re
from recordclass import recordclass
import argparse
import os

import numpy as np

__author__ = 'Theodor Tollersud'
__version__ = '2.0'

flatten = itertools.chain.from_iterable
alphabet = 'abcdefghijklmnopqrstuvwxyzæøå'
lmap = lambda f, i: list(map(f, i))

parser = argparse.ArgumentParser('Battleships')
parser.add_argument('-l', '--lazy', default=False, action='store_true')
parser.add_argument('LEN', nargs='?', default=10)
parser.add_argument('Ships', nargs='?', default='2,3,3,4,5')
cmd_args = parser.parse_args()
LEN = int(cmd_args.LEN)
ship_lens = np.array(lmap(int, re.findall(r'\d+', cmd_args.Ships)))

assert 0 < LEN < 30
assert sum(ship_lens) < LEN ** 2
assert (ship_lens <= LEN).all()
assert (ship_lens > 0).all()


class Board:
    def __init__(self):
        coordinate = recordclass('Coordinate', ('idx', 'status'))
        self.coords = collections.OrderedDict(zip(
            (s+str(n) for n, s in itertools.product(range(1, LEN + 1), alphabet[:LEN])),
            (coordinate(i, '-') for i in range(LEN ** 2))
        ))

    def __str__(self):
        s = ''
        nums = itertools.count(1)
        s += self.header() + '\n{}  '.format(next(nums))
        for i, v in enumerate(self.coords.values(), 1):
            s += v.status + ' '
            if i % LEN == 0 and i != LEN ** 2:
                s += '\n{0: <3}'.format(next(nums))
        s += '\n'
        return s

    @staticmethod
    def header():
        return '   ' + ' '.join(alphabet[:LEN])


class Parent:
    def __init__(self, name):
        self.board = Board()
        self.unused = copy.deepcopy(self.board)
        self.guessed = copy.deepcopy(self.board)
        self.ships, self.hits = [], []
        self.name = name

    def has_won(self, other):
        return set(self.hits) == set(flatten(other.ships))

    def mark_pos(self, pos):
        for i in flatten(pos):
            self.board.coords[i].status = 'X'
        return

    def n(self, s):
        return self.board.coords[s].idx

    def s(self, n):
        return list(self.board.coords.keys())[n]

    def random_ships(self):
        dirs = lambda: random.sample([1, -1, LEN, -LEN], 4)

        def create_ship(amnt_coords):
            ship = random.choice(list(self.board.coords.keys()))

            directions = dirs()
            direction = directions.pop()
            while True:
                if not directions:
                    directions = dirs()
                    direction = directions.pop()
                    ship = random.choice(list(self.board.coords.keys()))
                try:
                    nums = [self.n(ship) + direction * n for n in
                            range(1, amnt_coords)]
                except IndexError:
                    direction = directions.pop()
                    continue
                else:
                    if outside_board(direction, self.n(ship), *nums):
                        direction = directions.pop()
                        continue
                    break

            yield ship
            if amnt_coords > 1:
                for n in nums:
                    yield self.s(n)

        ships = []
        while len(set(flatten(ships))) != sum(ship_lens):
            ships = []
            for i in ship_lens:
                ships.append(tuple(create_ship(i)))

        return ships


class Human(Parent):
    def __init__(self, name):
        super().__init__(name)
        if not cmd_args.lazy:
            self.ships = self.input_ships()
        else:
            self.ships = self.random_ships()

    def guess(self, other):
        print('{}s skudd:'.format(self.name))
        print(self.guessed)
        input_guess = alts_input(': ', self.unused.coords.keys(),
                                 map(reverse_str, self.unused.coords.keys()),
                                 ['quit'])
        if input_guess[0].isdigit():
            input_guess = reverse_str(input_guess)
        if input_guess == 'quit':
            sys.exit()
        os.system('clear'); os.system('cls')
        self.unused.coords.pop(input_guess)

        if other.board.coords[input_guess].status != '-':
            print('Du traff!')
            self.guessed.coords[input_guess].status = 'T'
            self.hits.append(input_guess)
        else:
            print('Du bomma!')
            self.guessed.coords[input_guess].status = 'B'

        return input_guess

    def input_ships(self):
        valid = copy.deepcopy(self.board)
        print(self.board)

        def next_coo(coord, direction):
            num = self.n(coord) + direction
            return self.s(num)

        def filter_neighbour(coo_dir, amnt):
            coord, dr = coo_dir
            outside_list = range(coord - dr, coord + (amnt + 1) * dr, dr)
            for n in range(amnt + 1):
                try:
                    if self.s(coord + dr * n) not in valid.coords:
                        return False
                except IndexError:
                    return False
            else:
                return not outside_board(dr, *outside_list)

        def create_coords(amnt_coords, ship_nr):
            co1 = alts_input('Skip{}: '.format(ship_nr), valid.coords.keys(),
                             map(reverse_str, valid.coords.keys()), ['quit'])
            if co1 == 'quit':
                sys.exit()
            if co1[0].isdigit():
                co1 = reverse_str(co1)
            co1_num = self.n(co1)
            del valid.coords[co1]
            neighbours = (
                (co1_num + 1, 1), (co1_num - 1, -1),
                (co1_num + LEN, LEN), (co1_num - LEN, -LEN)
            )
            neighbours = dict(
                x for x in neighbours if filter_neighbour(x, amnt_coords))

            if not neighbours:
                print('Koordinatet du skrev inn har ikke plass til skipet,'
                      ' prøv igjen')
                yield from create_coords(amnt_coords, ship_nr)

            else:
                yield co1
                if amnt_coords > -1:
                    str_neighbours = lmap(self.s, neighbours.keys())
                    rev_neighbours = lmap(reverse_str, str_neighbours)
                    print(', '.join(str_neighbours))
                    co2 = alts_input(': ', str_neighbours, rev_neighbours,
                                     ['quit'])
                    if co2 == 'quit':
                        sys.exit()
                    if co2[0].isdigit():
                        co2 = reverse_str(co2)
                    del valid.coords[co2]
                    co2_dir = neighbours[self.n(co2)]
                    yield co2

                    next_coord = co2
                    for _ in range(amnt_coords):
                        next_coord = next_coo(next_coord, co2_dir)
                        del valid.coords[next_coord]
                        yield next_coord

        ships = []
        for i, a in enumerate(ship_lens - 2, 1):
            ship = tuple(create_coords(a, i))
            print('Skip{}: {}\n'.format(i, ', '.join(ship)))
            ships.append(ship)

        self.mark_pos(ships)
        print(self.name + 's skip:')
        print(self.board)
        return ships


class AI(Parent):
    def __init__(self, name, print_ships=False):
        super().__init__(name)
        self.ships = self.random_ships()
        self.mark_pos(self.ships)
        self.print_ships = print_ships

    def guess(self, other):
        random_guess = random.choice(list(self.unused.coords.keys()))
        del self.unused.coords[random_guess]
        if other.board.coords[random_guess].status != '-':
            print('{} traff på {}!'.format(self.name, random_guess))
            self.hits.append(random_guess)
            self.guessed.coords[random_guess].status = 'T'
        else:
            print('{} bomma! Han tippa {}'.format(self.name, random_guess))
            self.guessed.coords[random_guess].status = 'B'
        if self.print_ships:
            print('{}s skudd:'.format(self.name))
            print(self.guessed)

        return random_guess


def outside_board(direction, *args):
    for i in args:
        if i < 0 or i >= LEN ** 2:
            return True
    else:
        if direction in [-1, 1]:
            len_rows = len({i // LEN for i in args})
            if len_rows > 1:
                return True
    return False


def alts_input(spm, *alts):
    alts = set(flatten(alts))
    svar = ''
    while svar not in alts:
        svar = input(spm).lower()
        if svar not in alts:
            print('Ugyldig koordinat, prøv igjen')

    return svar


def reverse_str(s):
    if not isinstance(s, str):
        return s
    strs, nums = '', ''
    for i in s:
        if i.isdigit():
            nums += i
        else:
            strs += i
    if s[0].isdigit():
        return strs + nums
    else:
        return nums + strs


def game_over(winner):
    print(winner.guessed)
    print('{} vant!'.format(winner.name))
    return


def game_loop(p1, p2):
    while True:
        p1.guess(p2)
        if p1.has_won(p2):
            game_over(p1)
            return p1.name
        p2.guess(p1)
        if p2.has_won(p1):
            game_over(p2)
            return p2.name


if __name__ == '__main__':
    player1 = Human('Richard')
    player2 = AI('Michael')
    game_loop(player1, player2)
