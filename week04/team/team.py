"""
Course: CSE 251
Lesson Week: 04
File: team-bad.py
Author: Brother Comeau

Purpose: Team Activity

Instructions:

- See in I-Learn

"""

import threading
import queue
import requests
import json

# Include cse 251 common Python files
from cse251 import *

from week04.assignment.assignment import Queue251

RETRIEVE_THREADS = 4  # Number of retrieve_threads
NO_MORE_VALUES = 'No more'  # Special value to indicate no more items in the queue


class RequestThread(threading.Thread):

    # https://realpython.com/python-requests/
    def __init__(self, url):
        super().__init__()

        self.url = url
        self.response = {}

    def run(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.response = response.json()
        else:
            print('RESPONSE = ', response.status_code)


def retrieve_thread(log, url_q, number_of_urls_in_queue):  # TODO add arguments
    """ Process values from the data_queue """

    while True:
        # TODO check to see if anything is in the queue
        number_of_urls_in_queue.acquire()

        url = url_q.get()
        if url == NO_MORE_VALUES:
            break

        # TODO process the value retrieved from the queue
        print(url)

        # TODO make Internet call to get characters name and log it
        time.sleep(0.25)


def file_reader(log, url_q, number_of_urls_in_queue):  # TODO add arguments
    """ This thread reading the data file and places the values in the data_queue """

    # TODO Open the data file "data.txt" and place items into a queue
    with open('urls.txt') as f:
        for line in f:
            line = line.strip()
            url_q.put(line)
            number_of_urls_in_queue.release()

    log.write('finished reading file')

    # TODO signal the retrieve threads one more time that there are "no more values"
    for i in range(RETRIEVE_THREADS):
        url_q.put(NO_MORE_VALUES)
        number_of_urls_in_queue.release()


def main():
    """ Main function """

    log = Log(show_terminal=True)

    # TODO create queue
    url_q = Queue251()
    # TODO create semaphore (if needed)
    number_of_urls_in_queue = threading.Semaphore(0)

    # TODO create the threads. 1 filereader() and RETRIEVE_THREADS retrieve_thread()s
    # Pass any arguments to these thread need to do their job
    reader = threading.Thread(target=file_reader, args=[log, url_q, number_of_urls_in_queue])

    processes = []
    [processes.append(threading.Thread(target=retrieve_thread, args=[log, url_q, number_of_urls_in_queue])) for i in range(RETRIEVE_THREADS)]

    log.start_timer()

    # TODO Get them going - start the retrieve_threads first, then file_reader
    reader.start()
    [processor.start() for processor in processes]

    # TODO Wait for them to finish - The order doesn't matter
    [processor.join() for processor in processes]
    reader.join()

    log.stop_timer('Time to process all URLS')


if __name__ == '__main__':
    main()