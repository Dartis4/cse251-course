"""
Course: CSE 251
Lesson Week: 02
File: assignment.py
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

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

# Global Variables
call_count = 0


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


def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    urls = request_info(TOP_API_URL)

    info = request_info(f"{urls['films']}6/")

    print("-----------------------------------------")
    print(f"Title   : {info['title']}")
    print(f"Director: {info['director']}")
    print(f"Producer: {info['producer']}")
    print(f"Released: {info['release_date']}")
    print()

    categories = ['characters', 'planets', 'starships', 'vehicles', 'species']

    for category in categories:
        threads = []
        print(f"{category[0].upper() + category[1:]}: {len(info[category])}")
        for item in info[category]:
            thread = RequestThread(item)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
            print(f"{thread.response['name']}", end=", ")
        print("\n")

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')
    

if __name__ == "__main__":
    main()
