"""
Course: CSE 251, week 14
File: functions.py
Author: Dane Artis

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family = RequestThread(f'{TOP_API_URL}/family/{id}')

Requesting an individual from the server:
person = RequestThread(f'{TOP_API_URL}/person/{id}')


You will lose 10% if you don't detail your part 1 
and part 2 code below

Describe how to speed up part 1

<Add your comments here>


Describe how to speed up part 2

<Add your comments here>


10% Bonus to speed up part 3

<Add your comments here>

"""
import threading
from queue import Queue
from typing import Union

from common import *

TOP_API_URL = 'http://127.0.0.1:8123'


# A few helper functions
def retrieve_person(person_id):
    # This function is mostly for testing
    thread = RequestThread(f'{TOP_API_URL}/person/{person_id}')
    thread.start()
    thread.join()
    return thread.response


def retrieve_family(fam_id):
    thread = RequestThread(f'{TOP_API_URL}/family/{fam_id}')
    thread.start()
    thread.join()
    return thread.response


# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # implement Depth first retrieval

    def search_generation(start_id):
        # Check for repeats and stay within generational restraint
        if not tree.does_family_exist(start_id):
            # Get the family info
            family = Family(start_id, retrieve_family(start_id))
            # add family to tree
            tree.add_family(family)

            d = family.husband
            m = family.wife

            dad_thread = RequestThread(f'{TOP_API_URL}/person/{d}')
            dad_thread.start()
            mom_thread = RequestThread(f'{TOP_API_URL}/person/{m}')
            mom_thread.start()
            child_threads = [RequestThread(f'{TOP_API_URL}/person/{ident}') for ident in family.children]
            list(map(lambda th: th.start(), child_threads))

            for c_threads in child_threads:
                c_threads.join()
                child = Person(c_threads.response)
                if not tree.does_person_exist(child.id):
                    tree.add_person(child)

            threads = []

            if d and not tree.does_person_exist(d):
                dad_thread.join()
                dad = Person(dad_thread.response)
                dad_parent = dad.parents
                tree.add_person(dad)
                if dad_parent:
                    t = threading.Thread(target=search_generation, args=(dad_parent,))
                    t.start()
                    threads.append(t)

            # Add them if not in tree
            if m and not tree.does_person_exist(m):
                mom_thread.join()
                mom = Person(mom_thread.response)
                mom_parent = mom.parents
                tree.add_person(mom)
                if mom_parent:
                    t = threading.Thread(target=search_generation, args=(mom_parent,))
                    t.start()
                    threads.append(t)
            list(map(lambda th: th.join(), threads))

    search_generation(family_id)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_id, tree):
    # implement breadth first retrieval
    queue = Queue()
    queue.put(start_id)

    while not queue.empty():
        f = queue.get()
        if f and not tree.does_family_exist(f):
            family = Family(f, retrieve_family(f))
            tree.add_family(family)

            d = family.husband
            m = family.wife

            dad_thread = RequestThread(f'{TOP_API_URL}/person/{d}')
            dad_thread.start()
            mom_thread = RequestThread(f'{TOP_API_URL}/person/{m}')
            mom_thread.start()
            child_threads = [RequestThread(f'{TOP_API_URL}/person/{ident}') for ident in family.children]
            list(map(lambda th: th.start(), child_threads))

            for c_threads in child_threads:
                c_threads.join()
                child = Person(c_threads.response)
                if not tree.does_person_exist(child.id):
                    tree.add_person(child)

            if d and not tree.does_person_exist(d):
                dad_thread.join()
                dad = Person(dad_thread.response)
                dad_parent = dad.parents
                tree.add_person(dad)
                if dad_parent:
                    queue.put(dad_parent)

            if m and not tree.does_person_exist(m):
                mom_thread.join()
                mom = Person(mom_thread.response)
                mom_parent = mom.parents
                tree.add_person(mom)
                if mom_parent:
                    queue.put(mom_parent)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(start_id, tree):
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5

    pass
