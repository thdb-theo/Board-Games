"""This programme simulates Monopoly
and tracks how many times the player has been on each street.
The streets will have Norwegian names, but can easily be translated to English
"""

import random
import time
from itertools import chain
import argparse
from collections import OrderedDict, deque
from pprint import pprint
from operator import itemgetter
import logging

import matplotlib.pyplot as plt

logging.basicConfig(filename='monopolyLog.log', level=logging.INFO)


class Street:
    index_iter = iter(range(40))

    def __init__(self, name, street_type):
        self.name = name
        self.stype = street_type
        self.index = next(self.index_iter)
        self.count = 0

    def __call__(self):
        self.count += 1


class Monopoly:
    def __init__(self):
        self.POS = 0
        self.LAPS = 0
        self.chestcards = deque(chain.from_iterable([[None] * 15, [0, 10]]))
        random.shuffle(self.chestcards)
        self.Board = (
            Street('Start', self.normal),
            Street('Parkveien', self.normal),
            Street('Prøv Lykken1', self.cchest),
            Street('Kirkeveien', self.normal),
            Street('Inntektsskatt', self.normal),
            Street('Oslo S', self.normal),
            Street('Kongens gate', self.normal),
            Street('Sjanse1', self.chance),
            Street('Prinsens gate', self.normal),
            Street('Øvre Slottsgate', self.normal),
            Street('Fengsel', self.normal),
            Street('Nedre Slottsgate', self.normal),
            Street('Oslo Lysverker', self.normal),
            Street('Trondheimsveien', self.normal),
            Street('Nobels Gate', self.normal),
            Street('Skøyen Stasjon', self.normal),
            Street('Grensen', self.normal),
            Street('Prøv Lykken2', self.cchest),
            Street('Gabels Gate', self.normal),
            Street('Ringgata', self.normal),
            Street('Gratis Parkering', self.normal),
            Street('Bygdøy Allé', self.normal),
            Street('Sjanse2', self.chance),
            Street('Skarpsno', self.normal),
            Street('Slemdal', self.normal),
            Street('Grorud Stasjon', self.normal),
            Street('Karl Johans Gate', self.normal),
            Street('Stortorget', self.normal),
            Street('Vannverket ', self.normal),
            Street('Torggata', self.normal),
            Street('Gå i Fengsel', self.prison),
            Street('Trosterudveien', self.normal),
            Street('Pilestredet', self.normal),
            Street('Prøv Lykken3', self.cchest),
            Street('Sinsen', self.normal),
            Street('Bryn Stasjon', self.normal),
            Street('Sjanse3', self.chance),
            Street('Ullevål Hageby', self.normal),
            Street('Luksusskatt', self.normal),
            Street('Rådhusplassen', self.normal),
        )

    def normal(self):
        self.Board[self.POS]()

    def cchest(self):

        org_pos = self.POS
        if not self.chestcards:
            self.chestcards = deque(
                chain.from_iterable([[None] * 15, [0, 10]]))
            random.shuffle(self.chestcards)
        item = self.chestcards.pop()
        if item is not None:
            self.POS = item
        if self.POS < org_pos and self.POS != 10:
            self.LAPS += 1

        self.Board[self.POS]()

    def chance(self):
        org_pos = self.POS
        chance_list = list(
            chain.from_iterable([[self.Board[self.POS].index] * 7,
                                 [0, 24, 11, 10, 5, 39, near_util(self.POS),
                                  near_train(self.POS), self.POS - 3]]))

        item = random.choice(chance_list)
        self.POS = item
        if self.POS < org_pos and self.POS != 10 and self.POS != org_pos - 3:
            self.LAPS += 1

        self.Board[self.POS]()

    def prison(self):

        self.POS = 10
        self.Board[self.POS]()

    def print_step(self, throw):
        print(throw)
        print(self.POS)
        print(self.Board[self.POS].name)
        print()

    def toss(self, print_steps=False):

        throw = roll_dice()
        self.POS += sum(throw)

        if self.POS >= 40:
            self.POS -= 40
            self.LAPS += 1

        self.Board[self.POS].stype()

        if print_steps:
            self.print_step(throw)

        return True if throw[0] == throw[1] else False

    def turn(self):
        for _ in range(3):
            throw = self.toss()
            if not throw:
                break
        else:
            self.prison()

    def results(self):
        default_order = OrderedDict((x.name, x.count) for x in self.Board)
        print(default_order)

        sorted_streets = OrderedDict(sorted(default_order.items(),
                                            key=itemgetter(1)), reverse=True)

        if args.sort:
            return sorted_streets
        else:
            return default_order

    def game_loop(self, loops):
        l = [(loops//10)*x for x in range(1, 11)]
        print(l)
        for i in range(loops):
            self.turn()
            if i in l:
                print('{0} %'.format(int(i/loops*100)))

        return self.results()


def near_util(street_index: int) -> int:
    if 12 < street_index <= 28:
        return 28
    else:
        return 12


def near_train(street_index: int) -> int:
    if 5 >= street_index or street_index > 35:
        return 5
    elif 5 > street_index <= 15:
        return 15
    elif 15 < street_index <= 25:
        return 25
    else:
        return 35


def roll_dice() -> tuple:
    dice1 = int(random.random() * 6) + 1
    dice2 = int(random.random() * 6) + 1
    return dice1, dice2


def create_chart():
    if args.chart in ['b', 'bar']:
        bar()
    else:
        pie()


def pie():
    global colours
    print(result)
    if args.sort:
        colours = None

    names = list(result.keys())
    nums = list(result.values())
    plt.pie(nums, labels=names, autopct='%1.1f%%', pctdistance=0.8,
            startangle=90, colors=colours, explode=[0.01] * 40,
            counterclock=False)
    wm = plt.get_current_fig_manager()
    wm.window.state('zoomed')
    plt.show()


def bar():
    global colours
    names = list(result.keys())
    xval = list(range(len(names)))
    yval = list(result.values())
    ax1 = plt.subplot(111)
    d = dict(zip(range(len(names)), names))

    if args.sort:
        colours = [None] * 40

    for j in range(len(xval)):
        ax1.bar(xval[j], yval[j], width=0.8, bottom=0., align='center',
                label=d[xval[j]],
                color=colours[j])

    ax1.set_xticks(xval)
    ax1.set_xticklabels([d[i][:2] for i in xval], )
    plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0., fontsize=8.2)
    plt.subplots_adjust(left=0.06, top=0.98, right=0.82)
    wm = plt.get_current_fig_manager()
    wm.window.state('zoomed')
    plt.show()

colours = ['blue', 'saddlebrown', 'grey', 'saddlebrown', 'goldenrod',
           'darkslategray', 'lightblue', 'silver', 'lightblue',
           'lightblue', 'firebrick', 'magenta', 'salmon', 'magenta',
           'magenta', 'darkslategray', 'orange', 'grey', 'orange',
           'orange', 'blue', 'red', 'silver', 'red', 'red',
           'darkslategray', 'yellow', 'yellow', 'salmon', 'yellow',
           'blue', 'green', 'green', 'grey', 'green', 'darkslategray',
           'silver', 'navy', 'goldenrod', 'navy']

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Monopoly Simulator')
    parser.add_argument('chart', help='\'p\' -> pie chart\'b\' -> bar chart ')
    parser.add_argument('-s', '--sort', default=False, action='store_true',
                        help='sort results')
    parser.add_argument('loops', nargs='?', default=1000000)
    args = parser.parse_args()
    if args.chart not in ['p', 'b', 'pie', 'bar']:
        raise NameError('Argument: \'' + args.chart + '\' is not valid')
    obj = Monopoly()
    a = time.time()
    result = obj.game_loop(1000000)
    b = time.time()
    print(b-a)
    pprint(result)
    create_chart()
