from itertools import permutations, chain, cycle
from itertools import count, product, combinations, islice
from colorama import init, Fore, Style
from collections import namedtuple
import operator
import re
import argparse
import logging
import datetime

init()
p1_colour = Fore.LIGHTRED_EX
p2_colour = Fore.LIGHTGREEN_EX

logging.basicConfig(filename='DaBLog.log', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('LEN', nargs='?', default=4,
                    help='number of horizontal dots')
parser.add_argument('HEIGHT', nargs='?', default=0,
                    help='number of vertical dots')
args = parser.parse_args()
LEN = int(args.LEN)
HEIGHT = int(args.HEIGHT) or LEN  # args.HEIGHT if its True, else LEN

assert 1 < LEN < 35 > HEIGHT > 0

amnt_lines = 2 * HEIGHT * LEN - HEIGHT - LEN

logging.info('{0}\nLEN: {1}, HEIGHT: {2}'
             .format(datetime.datetime.now(), LEN, HEIGHT))


def create_boxes():
    boxes = {}
    i = count()
    for column, row in product(range(HEIGHT-1), range(LEN-1)):
        top = column * (LEN * 2 - 1) + row
        left = top + LEN - 1
        right = left + 1
        bottom = top + LEN * 2 - 1
        boxes.update({frozenset({top, left, right, bottom}): next(i)})
    return boxes


def create_lines():
    axises = islice(cycle(chain([0] * (LEN - 1), [1] * LEN)), amnt_lines)
    lines = {}
    index = count()
    tops = count()
    lefts = filter(lambda x: (x + 1) % LEN, count())
    for a in axises:
        if a:  # Vertical line
            top = next(tops)
            lines.update({frozenset({top, top + LEN}): next(index)})
        else:  # Horizontal line
            left = next(lefts)
            lines.update({frozenset({left, left + 1}): next(index)})
    return lines


class DotsAndBoxes:
    signs = iter([1, -1])
    colours = iter([p1_colour, p2_colour])
    board = [0] * amnt_lines
    boxes_dict = create_boxes()
    boxes_set = set(boxes_dict)
    lines = create_lines()
    fin_boxes = [' '] * ((LEN - 1) * HEIGHT)

    def __init__(self):
        self.colour = next(self.colours)
        self.sign = next(self.signs)
        self.score = 0

    def __str__(self):
        axises = islice(cycle(chain([0] * (LEN - 1), [1] * LEN)), amnt_lines)
        colour_subs = {0: Fore.WHITE, self.sign: self.colour,
                       -self.sign: p2_colour if self.sign == 1 else p1_colour}
        boxes_iter = iter(self.fin_boxes)
        colour_iter = (colour_subs.get(x) for x in self.board)
        rval = ''
        straight_downs = 0
        for i, axis in enumerate(axises):
            if i and not i % (LEN * 2 - 1) or not (i + LEN) % (LEN * 2 - 1):
                if axis:
                    rval += '●'
                rval += '\n'
            if not axis:
                rval += '●' + next(colour_iter) + '───' + Style.RESET_ALL
            else:
                rval += next(colour_iter) + '│ ' + Style.RESET_ALL
                straight_downs += 1
                if straight_downs % LEN:
                    rval += '{} '.format(next(boxes_iter))
        rval += '●'
        return rval

    def complete_box(self):
        indexes = [i for i, c in enumerate(self.board) if c]
        for c in combinations(indexes, 4):
            c = frozenset(c)
            if c in self.boxes_set:
                yield
                self.score += 1
                self.fin_boxes[self.boxes_dict[c]] = int(-self.sign / 2 + 1.5)
                self.boxes_set.remove(c)
                logging.info(' square: {0}, player: {1.sign}, score: {1.score}'
                             .format(set(c), self))
        return

    def make_move(self):
        move = namedtuple('move', ('from_from', 'from_to', 'to_from', 'to_to'))
        while True:
            userinput = input('Spiller {}: '.format(int(-self.sign / 2 + 1.5)))
            if re.fullmatch(r'^([^\d]+\d+){4}[^\d]*$', ' ' + userinput):
                line = move(*map(int, re.findall(r'\d+', userinput)))
                from_ = line.from_from + line.from_to * LEN
                to = line.to_from + line.to_to * LEN
                rval = frozenset({from_, to})
                if rval in self.lines.keys():
                            return rval
                else:
                    print('Ugyldig svar, prøv igjen')
            else:
                print('Ugyldig svar, prøv igjen')

    def change_board(self, move):
        self.board[self.lines[move]] = self.sign
        del self.lines[move]

    def turn(self):
        """:return -> 0: Game over, 1: Completed box, -1: No completed box """
        print(self)
        move = self.make_move()
        self.change_board(move)
        complete_boxes = list(self.complete_box())
        if complete_boxes:
            return bool(self.lines)
        else:
            return -bool(self.lines)


def game_over(playing, other):
    print(playing)
    if playing.score == other.score:
        print('Det ble uavgjort')
    else:
        winner = min([playing, other], key=operator.attrgetter('score'))
        print('Spiller {} vant!'.format(int(-winner.sign / 2 + 1.5)))


def main():
    p1 = DotsAndBoxes()
    p2 = DotsAndBoxes()
    for playing, other in cycle(permutations([p1, p2])):
        result = 1
        while result == 1:
            result = playing.turn()
        if result == 0:
            game_over(playing, other)
            return

if __name__ == '__main__':
    main()
