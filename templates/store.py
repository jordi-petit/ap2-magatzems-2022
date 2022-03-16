"""
Template file for store.py module.
"""

from dataclasses import dataclass
from typing import Optional, TextIO, List, Tuple
import curses
import time


TimeStamp = int


Position = int


Location = Tuple[int, int]


@dataclass
class TimeRange:
    start: TimeStamp
    end: TimeStamp


@dataclass
class Container:
    identifier: int
    size: int
    value: int
    arrival: TimeRange
    delivery: TimeRange


class Store:

    def __init__(self, width: int): ...

    def width(self) -> int: ...

    def height(self) -> int: ...

    def cash(self) -> int: ...

    def add_cash(self, amount: int) -> None: ...

    def add(self, c: Container, p: Position) -> None: ...

    def remove(self, c: Container) -> None: ...

    def move(self, c: Container, p: Position) -> None: ...

    def containers(self) -> List[Container]: ...

    def removable_containers(self) -> List[Container]: ...

    def top_container(self, p: Position) -> Optional[Container]: ...

    def location(self, c: Container) -> Location: ...

    def can_add(self, c: Container, p: Position) -> bool: ...

    def can_remove(self, c: Container) -> bool: ...

    def write(self, stdscr: curses.window, caption: str = ''):

        maximum = 15  # maximum number of rows to write
        delay = 0.05  # delay after writing the state

        # start: clear screen
        stdscr.clear()

        # write caption
        stdscr.addstr(0, 0, caption)
        # write floor
        stdscr.addstr(maximum + 3, 0, '—' * 2 * self.width())
        # write cash
        stdscr.addstr(maximum + 4, 0, '$: ' + str(self.cash()))

        # write containers
        for c in self.containers():
            row, column = self.location(c)
            if row < maximum:
                p = 1 + c.identifier * 764351 % 250  # some random color depending on the identifier of the container
                stdscr.addstr(maximum - row + 2, 2 * column, '  ' * c.size, curses.color_pair(p))
                stdscr.addstr(maximum - row + 2, 2 * column,
                              str(c.identifier % 100), curses.color_pair(p))

        # done
        stdscr.refresh()
        time.sleep(delay)


class Logger:

    """Class to log store actions to a file."""

    _file: TextIO

    def __init__(self, path: str, name: str, width: int):
        self._file = open(path, 'w')
        print(0, 'START', name, width, file=self._file)

    def add(self, t: TimeStamp, c: Container, p: Position):
        print(t, 'ADD', c.identifier, p, file=self._file)

    def remove(self, t: TimeStamp, c: Container):
        print(t, 'REMOVE', c.identifier, file=self._file)

    def move(self, t: TimeStamp, c: Container, p: Position):
        print(t, 'MOVE', c.identifier, p, file=self._file)

    def cash(self, t: TimeStamp, cash: int):
        print(t, 'CASH', cash, file=self._file)


def read_containers(path: str) -> List[Container]:
    """Returns a list of containers read from a file at path."""

    with open(path, 'r') as file:
        containers: List[Container] = []
        for line in file:
            identifier, size, value, arrival_start, arrival_end, delivery_start, delivery_end = map(
                int, line.split())
            container = Container(identifier, size, value, TimeRange(
                arrival_start, arrival_end), TimeRange(delivery_start, delivery_end))
            containers.append(container)
        return containers


def check_and_show(containers_path: str, log_path: str, stdscr: Optional[curses.window] = None):
    """
    Check that the actions stored in the log at log_path with the containers at containers_path are legal.
    Raise an exception if not.
    In the case that stdscr is not None, the store is written after each action.
    """

    # get the data
    containers_list = read_containers(containers_path)
    containers_map = {c.identifier: c for c in containers_list}
    log = open(log_path, 'r')
    lines = log.readlines()

    # process first line
    tokens = lines[0].split()
    assert len(tokens) == 4
    assert tokens[0] == "0"
    assert tokens[1] == "START"
    name = tokens[2]
    width = int(tokens[3])
    last = 0
    store = Store(width)
    if stdscr:
        store.write(stdscr)

    # process remaining lines
    for line in lines[1:]:
        tokens = line.split()
        time = int(tokens[0])
        what = tokens[1]
        assert time >= last
        last = time

        if what == "CASH":
            cash = int(tokens[2])
            assert cash == store.cash()

        elif what == "ADD":
            identifier, position = int(tokens[2]), int(tokens[3])
            store.add(containers_map[identifier], position)

        elif what == "REMOVE":
            identifier = int(tokens[2])
            container = containers_map[identifier]
            store.remove(container)
            if container.delivery.start <= time < container.delivery.end:
                store.add_cash(container.value)

        elif what == "MOVE":
            identifier, position = int(tokens[2]), int(tokens[3])
            store.move(containers_map[identifier], position)

        else:
            assert False

        if stdscr:
            store.write(stdscr, f'{name} t: {time}')
