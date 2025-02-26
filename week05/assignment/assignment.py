"""
Course: CSE 251
Lesson Week: 05
File: team.py
Author: Dane Artis

Purpose: Assignment 05 - Factories and Dealers

Instructions:

- Read the comments in the following code.  
- Implement your code where the do comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- You are not allowed to use the normal Python Queue object.  You must use Queue251.
- the shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE

"""

from datetime import datetime, timedelta
import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Consts
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50


# NO GLOBAL VARIABLES!

class Car:
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru',
                 'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus',
                 'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE', 'Super', 'Tall', 'Flat', 'Middle', 'Round',
                  'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                  'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / SLEEP_REDUCE_FACTOR)

        # Display the car that was just created in the terminal
        self.display()

    def display(self):
        # print(f'{self.make} {self.model}, {self.year}', flush=True)
        pass


class Queue251:
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []
        self.max_size = 0

    def get_max_size(self):
        return self.max_size

    def put(self, item):
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.max_size = len(self.items)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, index, car_queue, full, empty, factory_stats, factory_barrier):
        super().__init__()
        # print("New Factory", flush=True)

        self.index = index
        self.cars_to_produce = random.randint(200, 300)  # Don't change
        self.dealership_inventory = car_queue
        self.full = full
        self.empty = empty
        self.barrier = factory_barrier
        self.cars_produced = 0
        self.stats = factory_stats

    def run(self):
        for i in range(self.cars_to_produce):
            # print(f"Factory {self.index}: produce car", flush=True)
            # produce the cars, then send them to the dealerships
            # Does the dealer have space?
            self.empty.acquire()

            # Create the car object
            car = Car()

            # Add car to the dealership inventory
            self.dealership_inventory.put(car)  # CRITICAL SECTION

            self.stats[self.index] += 1

            # Signal the dealer about cars in inventory
            self.full.release()

        # print(f"Factory {self.index}: Done.", flush=True)
        # wait until all the factories are finished producing cars
        self.barrier.wait()

        # "Wake up/signal" the dealerships one more time.  Select one factory to do this
        if self.index == 0:
            # print(f"Factory: ALL DONE", flush=True)
            self.dealership_inventory.put('done')
            self.full.release()


class Dealer(threading.Thread):
    """ This is a dealer that receives cars """
    def __init__(self, index, car_queue, full, empty, dealer_stats, dealership_barrier):
        super().__init__()

        self.index = index
        self.dealership_inventory = car_queue
        self.full = full
        self.empty = empty
        self.barrier = dealership_barrier
        self.stats = dealer_stats
        self.flag = [0]

    def run(self):
        while True:
            # print(f"Dealer {self.index}: sell car", flush=True)
            # Are there cars available in inventory?
            if self.flag[0] == 1:
                self.full.acquire()
                break
            else:
                self.full.acquire()
            # print(f"Dealer {self.index}: acquire", flush=True)

            # Sell the car
            car = self.dealership_inventory.get()  # CRITICAL SECTION
            if car == 'done':
                # Stop if factory is done
                # print(f'Dealer {self.index}: done.', flush=True)
                self.dealership_inventory.put('done')
                self.flag[0] = 1
                self.full.release()
                break
            self.stats[self.index] += 1

            # Signal the factory that a car has been sold
            self.empty.release()

            # print(f"Dealer {self.index}: sold", flush=True)

            # Sleep a little - don't change.  This is the last line of the loop
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))
        # if self.index == 0:
        #     print('Dealer: ALL DONE', flush=True)


def run_production(factory_count, dealer_count):
    """ This function will do a production run with the number of
        factories and dealerships passed in as arguments.
    """

    # Create semaphore(s)
    full = threading.Semaphore(0)
    empty = threading.Semaphore(MAX_QUEUE_SIZE)
    # Create queue
    car_queue = Queue251()
    # Create lock(s)
    lock = threading.Lock()
    # Create barrier(s)
    factory_barrier = threading.Barrier(factory_count)
    dealership_barrier = threading.Barrier(dealer_count)

    # This is used to track the number of cars receives by each dealer
    dealer_stats = list([0] * dealer_count)
    factory_stats = list([0] * factory_count)

    # create your factories
    factories = [Factory(i, car_queue, full, empty, factory_stats, factory_barrier) for i in range(factory_count)]

    # create your dealerships
    dealerships = [Dealer(i, car_queue, full, empty, dealer_stats, dealership_barrier) for i in range(dealer_count)]

    log.start_timer()

    # Start all dealerships
    [dealership.start() for dealership in dealerships]

    time.sleep(1)  # make sure all dealers have time to start

    # Start all factories
    [factory.start() for factory in factories]

    # Wait for factories and dealerships to complete
    [dealership.join() for dealership in dealerships]
    [factory.join() for factory in factories]

    run_time = log.stop_timer(f'{sum(dealer_stats)} cars have been created')

    # This function must return the following - Don't change!
    # factory_stats: is a list of the number of cars produced by each factory.
    #                collect this information after the factories are finished. 
    return run_time, car_queue.get_max_size(), dealer_stats, factory_stats


def main(log):
    """ Main function - DO NOT CHANGE! """

    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for factories, dealerships in runs:
        run_time, max_queue_size, dealer_stats, factory_stats = run_production(factories, dealerships)

        log.write(f'Factories      : {factories}')
        log.write(f'Dealerships    : {dealerships}')
        log.write(f'Run Time       : {run_time:.4f}')
        log.write(f'Max queue size : {max_queue_size}')
        log.write(f'Factory Stats  : {factory_stats}')
        log.write(f'Dealer Stats   : {dealer_stats}')
        log.write('')

        # The number of cars produces needs to match the cars sold
        assert sum(dealer_stats) == sum(factory_stats)


if __name__ == '__main__':
    log = Log(show_terminal=True)
    main(log)
