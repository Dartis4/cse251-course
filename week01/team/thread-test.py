"""
Course: CSE 251
Lesson Week: 01 - Team Acvitiy
File: team-solution.py
Author: Brother Comeau

Purpose: Find prime numbers

"""

from datetime import datetime, timedelta
import threading


# Include cse 251 common Python files
from cse251 import *

COUNT = 2000000

count = 0


def thread_function():
    global count
    for i in range(COUNT):
        count += 1


if __name__ == '__main__':

    threads = []
    # Create threads and give each one a range to test
    for i in range(10):
        t = threading.Thread(target=thread_function(), args=())
        threads.append(t)

    # Start all threads
    for t in threads:
        t.start()

    # Wait for them to finish
    for t in threads:
        t.join()

    print(count)