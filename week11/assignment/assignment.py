"""
Course: CSE 251
Lesson Week: 11
File: Assignment.py
"""

import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE = 'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE = 'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'


def cleaner_waiting():
    time.sleep(random.uniform(0, 2))


def cleaner_cleaning(id):
    print(f'Cleaner {id}')
    time.sleep(random.uniform(0, 2))


def guest_waiting():
    time.sleep(random.uniform(0, 2))


def guest_partying(id):
    print(f'Guest {id}')
    time.sleep(random.uniform(0, 1))


def cleaner(ident, key_lock, guests_partying, start_time, cleanings_completed):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    while time.time() - start_time < TIME:
        cleaner_waiting()
        with key_lock:
            if guests_partying.value == 0:
                print(STARTING_CLEANING_MESSAGE)
                cleanings_completed.value += 1
                cleaner_cleaning(ident)
                print(STOPPING_CLEANING_MESSAGE)


def guest(ident, key_lock, party_lock, guests_partying, start_time, parties_completed):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    while time.time() - start_time < TIME:
        guest_waiting()
        with key_lock:
            with party_lock:
                if not guests_partying.value:
                    print(STARTING_PARTY_MESSAGE)
                    parties_completed.value += 1
                guests_partying.value += 1
        guest_partying(ident)
        with party_lock:
            guests_partying.value -= 1
            if guests_partying.value <= 0:
                print(STOPPING_PARTY_MESSAGE)
                guests_partying.value = 0


def main():
    # Start time of the running of the program.
    start_time = time.time()

    # add any variables, data structures, processes you need
    # Guest count
    guests_partying = mp.Value('L', 0)

    # To control race condition
    party_lock = mp.Lock()
    # Not for race condition, just access
    key_lock = mp.Lock()

    # Track cleanings and parties
    cleanings_completed = mp.Value('L', 0)
    parties_completed = mp.Value('L', 0)

    # add any arguments to cleaner() and guest() that you need
    cleaners = [mp.Process(target=cleaner, args=(i, key_lock, guests_partying, start_time, cleanings_completed)) for i in range(CLEANING_STAFF)]
    guests = [mp.Process(target=guest, args=(i, key_lock, party_lock, guests_partying, start_time, parties_completed)) for i in range(HOTEL_GUESTS)]

    list(map(lambda proc: proc.start(), [*cleaners, *guests]))
    list(map(lambda proc: proc.join(), [*cleaners, *guests]))

    cleaned_count = cleanings_completed.value
    party_count = parties_completed.value

    # Results
    print(f'Room was cleaned {cleaned_count} times, there were {party_count} parties')


if __name__ == '__main__':
    main()
