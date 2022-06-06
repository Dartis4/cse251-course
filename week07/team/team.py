"""
Course: CSE 251
Lesson Week: 7
File: team.py
Author: Brother Comeau

Purpose: Retrieve Star Wars details from a server

Instructions:

- Each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- Run the server.py program from a terminal/console program.  Simply type
  "python server.py"
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information from the
  server.
- You need to match the output outlined in the description of the assignment.
  Note that the names are sorted.
- You are required to use a threaded class (inherited from threading.Thread) for
  this assignment.  This object will make the API calls to the server. You can
  define your class within this Python file (i.e., no need to have a separate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary(JSON).  Do NOT have
this dictionary hard coded - use the API call to get this.  Then you can use
this dictionary to make other API calls for data.

{
   "people": "http://127.0.0.1:8790/people/",
   "planets": "http://127.0.0.1:8790/planets/",
   "films": "http://127.0.0.1:8790/films/",
   "species": "http://127.0.0.1:8790/species/",
   "vehicles": "http://127.0.0.1:8790/vehicles/",
   "starships": "http://127.0.0.1:8790/starships/"
}
"""

from datetime import datetime, timedelta
import requests
import json
import threading
import multiprocessing as mp

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'
PROCESSES = 4

# Global Variables
call_count = 0
global_results = {
    'characters': [],
    'planets': [],
    'starships': [],
    'vehicles': [],
    'species': []
}


class RequestThread(threading.Thread):

    # https://realpython.com/python-requests/
    def __init__(self, url):
        super().__init__()

        self.url = url
        self.response = {}

    def run(self):
        global call_count
        response = requests.get(self.url)
        if response.status_code == 200:
            self.response = response.json()
            call_count += 1
        else:
            print('RESPONSE = ', response.status_code)


def request_info(url):
    thread = RequestThread(url)
    thread.start()
    thread.join()
    return thread.response


def process_url(url):
    results = []
    p = RequestThread(url, results)
    p.start()
    p.join()
    return results


def call_back1(results):
    print("callback 1", flush=True)
    global_results['characters'].append(results)


def call_back2(results):
    global_results['planets'].append(results)


def call_back3(results):
    global_results['starships'].append(results)


def call_back4(results):
    global_results['vehicles'].append(results)


def call_back5(results):
    global_results['species'].append(results)


def get_all_data_threads(urls, pool, cb):
    [pool.apply_async(process_url, args=(url,), callback=cb) for url in urls]


def print_data(info, category, log):
    log.write(f"{category[0].upper() + category[1:]}: {len(info[category])}")
    # for item in info[category]:
    #     thread = RequestThread(item)
    #     thread.start()
    #     threads.append(thread)
    # for thread in threads:
    #     thread.join()
    #     items.append(thread.response['name'])
    # items.sort()
    # print(*items, sep=", ", flush=True)


def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    urls = request_info(TOP_API_URL)

    info = request_info(f"{urls['films']}6/")

    print(info, flush=True)

    log.write('-' * 40)
    log.write(f"Title   : {info['title']}")
    log.write(f"Director: {info['director']}")
    log.write(f"Producer: {info['producer']}")
    log.write(f"Released: {info['release_date']}\n\n")

    pool = mp.Pool(PROCESSES)

    categories = ['characters', 'planets', 'starships', 'vehicles', 'species']

    callbacks = {
        'characters': call_back1,
        'planets': call_back2,
        'starships': call_back3,
        'vehicles': call_back4,
        'species': call_back5
    }

    [get_all_data_threads(info[category], pool, lambda result: global_results[category].append(result)) for category in categories]

    pool.close()
    pool.join()

    time.sleep(0.01)
    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')


if __name__ == "__main__":
    main()