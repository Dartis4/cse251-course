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

To speed up part 1, we want to get to the bottom of each branch as fast as possible. We
can do this by joining the threads at the base case of the recursion, meaning we don't
join a thread until the subtree of a branch has been explored. This will allow us to
have the maximum number of threads possible working at the same time and allow us to
have the least amount of idle time. We can also save the processing of the children for
the end of the function since they do not need to be added right away, and we can do
this much faster in one large group.

Describe how to speed up part 2

To speed up part 2, we can get each generation first, which would be from the previous
generation for every generation except the first. By doing this, we can make all the
requests and do all the work needed to get the next generation of family ID's
concurrently. We are essentially creating mini-trees that are each processed in
parallel, meaning each family in the generation is process in its own thread, each
parent from that family is then processed its own thread, and then their parent family
(the next generation) is pushed to the queue and the process will start over for the
next generation. This allows us to have the highest number of concurrent threads
possible despite the generational limitation that comes with a breadth first search.

10% Bonus to speed up part 3

This part utilizes the same concepts of part 2, however to limit the function to a max
of 5 concurrent threads, we can essentially pool the ID's that need to be fetched from
the server into a list and then loop through that list in batches of 5. We can do this
by creating a request queue with a maximum size restraint which we will pull from to
initiate a thread and make the server request. If we do this at each step of the
process, it is significantly slower than the search algorithm in part 2, but will
utilize the restricted resources provided best.

"""
from queue import Queue

from common import *

TOP_API_URL = 'http://127.0.0.1:8123'

tree_lock = threading.Lock()


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


def person_request(identity):
    thread = RequestThread(f'{TOP_API_URL}/person/{identity}')
    thread.start()
    return thread


def family_request(identity):
    thread = RequestThread(f'{TOP_API_URL}/family/{identity}')
    thread.start()
    return identity, thread


# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # implement Depth first retrieval

    def seen_person(identity):
        with tree_lock:
            return tree.does_person_exist(identity)

    def seen_family(identity):
        with tree_lock:
            return tree.does_family_exist(identity)

    seen_families = []

    def search_generation(start_id):
        # Check for repeats and stay within generational restraint

        if not seen_family(start_id):
            # Get the family info
            family = Family(start_id, retrieve_family(start_id))
            # add family to tree
            with tree_lock:
                tree.add_family(family)
            seen_families.append(family)

            d = family.husband
            m = family.wife

            dad_thread = person_request(d)
            mom_thread = person_request(m)

            threads = []

            if d and not seen_person(d):
                dad_thread.join()
                dad = Person(dad_thread.response)
                dad_parent = dad.parents
                with tree_lock:
                    tree.add_person(dad)
                if dad_parent:
                    t = threading.Thread(target=search_generation, args=(dad_parent,))
                    t.start()
                    threads.append(t)

            # Add them if not in tree
            if m and not seen_person(m):
                mom_thread.join()
                mom = Person(mom_thread.response)
                mom_parent = mom.parents
                with tree_lock:
                    tree.add_person(mom)
                if mom_parent:
                    t = threading.Thread(target=search_generation, args=(mom_parent,))
                    t.start()
                    threads.append(t)
            list(map(lambda th: th.join(), threads))

    search_generation(family_id)
    all_children = []
    for family in seen_families:
        for child in family.children:
            all_children.append(child)
    child_threads = [person_request(child) for child in all_children]
    for c_threads in child_threads:
        c_threads.join()
        child = Person(c_threads.response)
        if not seen_person(child.id):
            with tree_lock:
                tree.add_person(child)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_id, tree):

    def seen_person(identity):
        with tree_lock:
            return tree.does_person_exist(identity)

    def seen_family(identity):
        with tree_lock:
            return tree.does_family_exist(identity)

    queue = Queue()
    queue.put(start_id)

    seen_families = []

    while not queue.empty():
        generation = []
        while not queue.empty():
            generation.append(queue.get())
        fam_threads = [family_request(family) for family in generation]
        parent_threads = []
        for f_id, f_thread in fam_threads:
            f_thread.join()
            if not seen_family(f_id):
                family = Family(f_id, f_thread.response)
                with tree_lock:
                    tree.add_family(family)
                seen_families.append(family)
                d = family.husband
                m = family.wife
                if d:
                    parent_threads.append(person_request(d))
                if m:
                    parent_threads.append(person_request(m))
        for p_thread in parent_threads:
            p_thread.join()
            parent = Person(p_thread.response)
            grandparent = parent.parents
            with tree_lock:
                tree.add_person(parent)
            if grandparent:
                queue.put(grandparent)

    child_threads = []
    for family in seen_families:
        for kid in family.children:
            child_threads.append(person_request(kid))
    for c_thread in child_threads:
        c_thread.join()
        child = Person(c_thread.response)
        if not seen_person(child.id):
            with tree_lock:
                tree.add_person(child)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(start_id, tree):
    # - implement breadth first retrieval
    # - Limit number of concurrent connections to the FS server to 5
    request_queue = Queue(maxsize=5)

    def seen_person(identity):
        with tree_lock:
            return tree.does_person_exist(identity)

    def seen_family(identity):
        with tree_lock:
            return tree.does_family_exist(identity)

    # implement breadth first retrieval
    queue = Queue()
    queue.put(start_id)

    seen_families = []

    while not queue.empty():
        generation = []
        while not queue.empty():
            generation.append(queue.get())

        done = False
        parent_ids = []
        family_counter = 0
        while not done:
            while not request_queue.full() and family_counter < len(generation):
                request_queue.put(family_request(generation[family_counter]))
                family_counter += 1
            while not request_queue.empty():
                f_identity, f_thread = request_queue.get()
                f_thread.join()
                family = Family(f_identity, f_thread.response)
                with tree_lock:
                    tree.add_family(family)
                seen_families.append(family)

                d = family.husband
                m = family.wife
                if d:
                    parent_ids.append(d)
                if m:
                    parent_ids.append(m)
            if family_counter >= len(generation):
                done = True

        done = False
        parent_counter = 0
        while not done:
            while not request_queue.full() and parent_counter < len(parent_ids):
                request_queue.put(person_request(parent_ids[parent_counter]))
                parent_counter += 1
            while not request_queue.empty():
                p_thread = request_queue.get()
                p_thread.join()
                parent = Person(p_thread.response)
                grandparent = parent.parents
                with tree_lock:
                    tree.add_person(parent)
                if grandparent:
                    queue.put(grandparent)
            if parent_counter >= len(parent_ids):
                done = True

    all_children = []
    for family in seen_families:
        for c in family.children:
            all_children.append(c)
    done = False
    child_counter = 0
    while not done:
        while not request_queue.full() and child_counter < len(all_children):
            request_queue.put(person_request(all_children[child_counter]))
            child_counter += 1
        while not request_queue.empty():
            c_thread = request_queue.get()
            c_thread.join()
            child = Person(c_thread.response)
            if not seen_person(child.id):
                with tree_lock:
                    tree.add_person(child)
        if child_counter >= len(all_children):
            done = True
