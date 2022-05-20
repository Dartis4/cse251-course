"""
Course: CSE 251
Lesson Week: 05
File: team-bad.py
Author: Brother Comeau

Purpose: Check for prime values

Instructions:

- You can't use thread/process pools
- Follow the graph in I-Learn 
- Start with PRIME_PROCESS_COUNT = 1, then once it works, increase it

"""
import time
import threading
import multiprocessing as mp
import random

# Include cse 251 common Python files
from cse251 import *

PRIME_PROCESS_COUNT = 4


def is_prime(n: int) -> bool:
    """Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# TODO create read_thread function
def read_thread(filename, number_queue):
    with open(filename, 'r') as f:
        for line in f:
            number_queue.put(int(line.strip()))
    number_queue.put('done')


# TODO create prime_process function
def prime_process(number_queue, primes):
    while True:
        num = number_queue.get()
        if num == 'done':
            number_queue.put('done')
            break
        if is_prime(num):
            primes.append(num)


def create_data_txt(filename):
    with open(filename, 'w') as f:
        [f.write(str(random.randint(10000000000, 100000000000000)) + '\n') for _ in range(1000)]


def main():
    """ Main function """

    filename = 'data.txt'

    # Once the data file is created, you can comment out this line
    create_data_txt(filename)

    log = Log(show_terminal=True)
    log.start_timer()

    # TODO Create shared data structures
    number_queue = mp.Manager().Queue()
    primes = mp.Manager().list()

    # TODO create reading thread
    reader_thread = threading.Thread(target=read_thread, args=(filename, number_queue))

    # TODO create prime processes
    prime_processes = [mp.Process(target=prime_process, args=(number_queue, primes)) for _ in range(PRIME_PROCESS_COUNT)]

    # TODO Start them all
    reader_thread.start()
    [process.start() for process in prime_processes]

    # TODO wait for them to complete
    reader_thread.join()
    [process.join() for process in prime_processes]

    log.stop_timer(f'All primes have been found using {PRIME_PROCESS_COUNT} processes')

    # display the list of primes
    print(f'There are {len(primes)} found:')
    for prime in primes:
        print(prime)


if __name__ == '__main__':
    main()
