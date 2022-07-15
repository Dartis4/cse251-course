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
from queue import Queue

from common import *

TOP_API_URL = 'http://127.0.0.1:8123'
NUM_GENERATIONS = 6
NUM_FAMILIES = 2 ** NUM_GENERATIONS - 1


# A few helper functions
def retrieve_person(person_id):
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

    # Check for repeats and stay within generational restraint
    if not tree.does_family_exist(family_id) and tree.get_family_count() < 3:
        # Get the family info
        family = Family(family_id, retrieve_family(family_id))

        # Generate the threads for all family members and start them running
        dad_thread = RequestThread(f'{TOP_API_URL}/person/{family.husband}')
        dad_thread.start()
        mom_thread = RequestThread(f'{TOP_API_URL}/person/{family.wife}')
        mom_thread.start()
        child_threads = [RequestThread(f'{TOP_API_URL}/person/{ident}') for ident in family.children]
        list(map(lambda t: t.start(), child_threads))

        # add family to tree
        tree.add_family(family)

        # Make sure dad thread is done
        dad_thread.join()
        # Get info
        dad = Person(dad_thread.response)
        # Add them if not in tree
        if not tree.does_person_exist(dad.id):
            tree.add_person(dad)
        # If there are parents
        if dad.parents:
            depth_fs_pedigree(dad.parents, tree)

        mom_thread.join()
        mom = Person(mom_thread.response)
        if not tree.does_person_exist(mom.id):
            tree.add_person(mom)
        if mom.parents:
            depth_fs_pedigree(mom.parents, tree)

        for c_threads in child_threads:
            c_threads.join()
            child = Person(c_threads.response)
            if not tree.does_person_exist(child.id):
                tree.add_person(child)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_id, tree):
    # implement breadth first retrieval
    queue = Queue()
    queue.put(start_id)

    while queue:
        f = queue.get()
        print(f)
        family = Family(f, retrieve_family(f))
        print(family)
        if family.husband:
            print((Person(retrieve_person(family.husband))).parents)
        # if not tree.does_family_exist(f) and tree.get_family_count() < 15:
        #     family = Family(f, retrieve_family(f))
        #     tree.add_family(family)
        #
        #     dad_thread = RequestThread(f'{TOP_API_URL}/person/{family.husband}')
        #     dad_thread.start()
        #     mom_thread = RequestThread(f'{TOP_API_URL}/person/{family.wife}')
        #     mom_thread.start()
        #     child_threads = [RequestThread(f'{TOP_API_URL}/person/{ident}') for ident in family.children]
        #     list(map(lambda t: t.start(), child_threads))
        #
        #     for c_threads in child_threads:
        #         c_threads.join()
        #         child = Person(c_threads.response)
        #         if not tree.does_person_exist(child.id):
        #             tree.add_person(child)
        #
        #     dad_thread.join()
        #     dad = Person(dad_thread.response)
        #     if not tree.does_person_exist(dad.id):
        #         tree.add_person(dad)
        #         if dad.parents:
        #             queue.put(dad.parents)
        #
        #     mom_thread.join()
        #     mom = Person(mom_thread.response)
        #     if not tree.does_person_exist(mom.id):
        #         tree.add_person(mom)
        #         if mom.parents:
        #             queue.put(mom.parents)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(start_id, tree):
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5

    pass
