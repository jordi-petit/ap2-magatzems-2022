"""
Template file for simple.py module.
"""


import sys
import curses

from store import *


class Strategy:

    """Implementation of the simple strategy."""

    def __init__(self, width: int, log_path: str): ...

    def cash(self) -> int: ...

    def exec(self, c: Container): ...


def init_curses():
    """Initializes the curses library to get fancy colors and whatnots."""

    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, curses.COLOR_WHITE, i)


def execute_strategy(containers_path: str, log_path: str, width: int):
    """Execute the strategy on an empty store of a certain width reading containers from containers_path and logging to log_path."""

    containers = read_containers(containers_path)
    strategy = Strategy(width, log_path)
    for container in containers:
        strategy.exec(container)


def main(stdscr: curses.window):
    """main script"""

    init_curses()

    containers_path = sys.argv[1]
    log_path = sys.argv[2]
    width = int(sys.argv[3])

    execute_strategy(containers_path, log_path, width)
    check_and_show(containers_path, log_path, stdscr)


# start main script when program executed
if __name__ == '__main__':
    curses.wrapper(main)
