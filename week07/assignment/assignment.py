"""
Course: CSE 251
Lesson Week: 07
File: assignment.py
Author: Dane Artis
Purpose: Process Task Files

Instructions:  See I-Learn

TODO

Add you comments here on the pool sizes that you used for your assignment and
why they were the best choices.


"""
import threading
from datetime import datetime, timedelta
import requests
import multiprocessing as mp
from matplotlib.pylab import plt
import numpy as np
import glob
import math

# Include cse 251 common Python files - Dont change
from cse251 import *

TYPE_PRIME = 'prime'
TYPE_WORD = 'word'
TYPE_UPPER = 'upper'
TYPE_SUM = 'sum'
TYPE_NAME = 'name'

# Global lists to collect the task results
result_primes = []
result_words = []
result_upper = []
result_sums = []
result_names = []


class RequestThread(threading.Thread):
    def __init__(self, url):
        super().__init__()

        self.url = url
        self.response = {}

    def run(self):
        self.response = requests.get(self.url)


def request_info(url):
    thread = RequestThread(url)
    thread.start()
    thread.join()
    return thread.response


def is_prime(n: int):
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


def task_prime(value):
    """
    Use the is_prime() above
    Add the following to the global list:
        {value} is prime
            - or -
        {value} is not prime
    """
    if is_prime(value):
        return f'{value:,} is prime'
    else:
        return f'{value:,} is not prime'


def task_word(word):
    """
    search in file 'words.txt'
    Add the following to the global list:
        {word} Found
            - or -
        {word} not found *****
    """
    with open('words.txt', 'r') as f:
        for w in f.readlines():
            if w.strip() == word:
                return f'{word} found'
    return f'{word} not found'


def task_upper(text):
    """
    Add the following to the global list:
        {text} ==>  uppercase version of {text}
    """
    return f'{text} ==> {text.upper()}'


def task_sum(start_value, end_value):
    """
    Add the following to the global list:
        sum of {start_value:,} to {end_value:,} = {total:,}
    """
    return f'sum of {start_value:,} to {end_value:,} = {sum(range(start_value, end_value)):,}'


def task_name(url):
    """
    use requests module
    Add the following to the global list:
        {url} has name <name>
            - or -
        {url} had an error receiving the information
    """
    response = request_info(url)
    if response.status_code == 200:
        res = response.json()
        return f'{url} has name {res["name"]}'
    else:
        return f'{url} had an error receiving the information'


def log_prime(value):
    result_primes.append(value)


def log_word(value):
    result_words.append(value)


def log_upper(value):
    result_upper.append(value)


def log_sum(value):
    result_sums.append(value)


def log_name(value):
    result_names.append(value)


def main():
    log = Log(show_terminal=True)
    log.start_timer()

    # TODO Create process pools
    prime_pool = mp.Pool(2)
    word_pool = mp.Pool(2)
    upper_pool = mp.Pool(2)
    sum_pool = mp.Pool(2)
    name_pool = mp.Pool(2)
    pools = [
        prime_pool,
        word_pool,
        upper_pool,
        sum_pool,
        name_pool
    ]

    count = 0
    task_files = glob.glob("*.task")
    for filename in task_files:
        # print()
        # print(filename)
        task = load_json_file(filename)
        print(task)
        count += 1
        task_type = task['task']
        if task_type == TYPE_PRIME:
            prime_pool.apply_async(task_prime, args=(task['value'],), callback=log_prime)
        elif task_type == TYPE_WORD:
            word_pool.apply_async(task_word, args=(task['word'],), callback=log_word)
        elif task_type == TYPE_UPPER:
            upper_pool.apply_async(task_upper, args=(task['text'],), callback=log_upper)
        elif task_type == TYPE_SUM:
            sum_pool.apply_async(task_sum, args=(task['start'], task['end']), callback=log_sum)
        elif task_type == TYPE_NAME:
            name_pool.apply_async(task_name, args=(task['url'],), callback=log_name)
        else:
            log.write(f'Error: unknown task type {task_type}')

    # TODO start and wait pools
    [pool.close() for pool in pools]
    [pool.join() for pool in pools]

    # Do not change the following code (to the end of the main function)
    def log_list(lst, log):
        for item in lst:
            log.write(item)
        log.write(' ')

    log.write('-' * 80)
    log.write(f'Primes: {len(result_primes)}')
    log_list(result_primes, log)

    log.write('-' * 80)
    log.write(f'Words: {len(result_words)}')
    log_list(result_words, log)

    log.write('-' * 80)
    log.write(f'Uppercase: {len(result_upper)}')
    log_list(result_upper, log)

    log.write('-' * 80)
    log.write(f'Sums: {len(result_sums)}')
    log_list(result_sums, log)

    log.write('-' * 80)
    log.write(f'Names: {len(result_names)}')
    log_list(result_names, log)

    log.write(f'Number of Primes tasks: {len(result_primes)}')
    log.write(f'Number of Words tasks: {len(result_words)}')
    log.write(f'Number of Uppercase tasks: {len(result_upper)}')
    log.write(f'Number of Sums tasks: {len(result_sums)}')
    log.write(f'Number of Names tasks: {len(result_names)}')
    log.stop_timer(f'Finished processes {count} tasks')


if __name__ == '__main__':
    main()
