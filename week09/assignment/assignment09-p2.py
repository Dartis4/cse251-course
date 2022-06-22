"""
Course: CSE 251 
Lesson Week: 09
File: assignment09-p2.py 
Author: Dane Artis

Purpose: Part 2 of assignment 09, finding the end position in the maze

Instructions:
- Do not create classes for this assignment, just functions
- Do not use any other Python modules other than the ones included
- Each thread requires a different color by calling get_color()


This code is not interested in finding a path to the end position,
However, once you have completed this program, describe how you could 
change the program to display the found path to the exit position.

What would be your strategy?  

If we have a global path variable that we can append the correct path to,
then we could keep track of the paths and once the end is found, we
append the found path to that variable as we return out of the recursion.


Why would it work?

Since we have many different paths that are using threads, we can keep
track up to each fork in the maze. As we return out, this method of saving
the path allows us to record the correct fork path and use the global path
as the final path.

"""
import math
import threading
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 251 common Python files - Dont change
from cse251 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
COLORS = (
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (128, 0, 0),
    (128, 128, 0),
    (0, 128, 0),
    (128, 0, 128),
    (0, 128, 128),
    (0, 0, 128),
    (72, 61, 139),
    (143, 143, 188),
    (226, 138, 43),
    (128, 114, 250)
)

# Globals
current_color_index = 0
thread_count = 0
stop = False


def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


def solve_find_end(maze):
    """ finds the end position using threads.  Nothing is returned """
    # When one of the threads finds the end position, stop all of them
    global stop, thread_count
    thread_count = 0
    start = maze.get_start_pos()
    start_color = get_color()

    def pathfinder(position, color):
        global stop, thread_count
        if not stop:
            path = threading.Thread(target=find_path, args=(position, color))
            thread_count += 1
            path.start()

    def find_path(current_pos, color):
        global stop

        # Move to the location if possible
        if maze.can_move_here(*current_pos):
            maze.move(*current_pos, color)

        # If the current position is the end, stop and return
        if maze.at_end(*current_pos):
            stop = True
            return

        if not stop:
            # Find routes
            possible = maze.get_possible_moves(*current_pos)
            # If no paths, return
            if not possible:
                return
            elif len(possible) == 1:
                pathfinder(possible[0], color)
            else:
                # Iterate available routes
                pathfinder(possible[0], color)
                for p in possible[1:]:
                    pathfinder(p, get_color())
    find_path(start, start_color)
    stop = False


def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count

    # create a Screen Object that will contain all the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    speed = 1
    while not done:
        if screen.play_commands(speed):
            key = cv2.waitKey(0)
            if key == ord('+'):
                speed = max(0, speed - 1)
            elif key == ord('-'):
                speed += 1
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('verysmall.bmp', True),
        ('verysmall-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()
