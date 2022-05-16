"""
Course: CSE 251
Lesson Week: 04
File: assignment.py
Author: Dane Artis

Purpose: Assignment 04 - Factory and Dealership

Instructions:

- See I-Learn

"""

import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Consts - Do not change
CARS_TO_PRODUCE = 500
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

        # Display the car that has just be created in the terminal
        # self.display()

    def display(self):
        print(f'{self.make} {self.model}, {self.year}', flush=True)


class Queue251:
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []

    def size(self):
        return len(self.items)

    def put(self, item):
        self.items.append(item)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, cars_produced, full, empty, queue_stats, log):
        super().__init__()

        self.dealership_inventory = cars_produced
        self.full = full
        self.empty = empty
        self.queue_stats = queue_stats
        self.log = log

    def run(self):
        # self.log.write('FACTORY   :     Waiting for an order...')
        for i in range(CARS_TO_PRODUCE):
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
           """
            # if i == 0:
                # Car order comes in
                # self.log.write('FACTORY   :     ORDER RECEIVED')

            # New manufacture process
            # self.log.write('FACTORY   :     MANUFACTURE NEW CAR')
            self.empty.acquire()

            # Create the car object
            # self.log.write(f'FACTORY   :     CAR MADE')
            car = Car()

            # Deliver car to dealership
            # self.log.write(f'FACTORY   :     CAR SHIPPED')
            self.dealership_inventory.put(car)  # CRITICAL SECTION
            # self.log.write(f'FACTORY   :     Total cars produced: {i + 1}')

            self.full.release()

        # Let the dealer know we've finished their order
        # self.log.write('FACTORY   :     ORDER COMPLETE')
        self.empty.put('Done')
        self.full.release()


class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, cars_produced, full, empty, queue_stats, log):
        super().__init__()

        self.dealership_inventory = cars_produced
        self.full = full
        self.empty = empty
        self.queue_stats = queue_stats
        self.log = log

    def run(self):
        while True:
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            # self.log.write('DEALERSHIP:     Waiting for a shipment...')
            # Car is delivered
            self.full.acquire()
            # self.log.write('DEALERSHIP:     SHIPMENT RECEIVED')

            # How many cars are on the lot right now?
            # inventory_size = self.dealership_inventory.size()
            self.queue_stats[self.dealership_inventory.size() - 1] += 1

            # Sell the car
            car = self.dealership_inventory.get()  # CRITICAL SECTION
            if car == 'Done':
                # Stop if no more cars arrive from the factory
                break
            # self.log.write(f'DEALERSHIP:     {inventory_size} car(s) on lot')
            # self.queue_stats[inventory_size - 1] += 1
            # self.log.write(f'DEALERSHIP:     CAR SOLD')
            # self.log.write(f'DEALERSHIP:     Cars left in inventory: {self.dealership_inventory.size()}')

            # Car drives off the lot
            self.empty.release()

            # Sleep a little after selling a car
            time.sleep(random.random() / SLEEP_REDUCE_FACTOR)

        # self.log.write('DEALERSHIP:     SHIPMENTS CEASED')


def main():
    log = Log(show_terminal=True)

    full = threading.Semaphore(0)
    empty = threading.Semaphore(10)

    cars_produced = Queue251()

    # This tracks the length of the car queue during receiving cars by the dealership
    # i.e., update this list each time the dealer receives a car
    queue_stats = [0] * MAX_QUEUE_SIZE

    factory = Factory(cars_produced, full, empty, queue_stats, log)

    dealership = Dealer(cars_produced, full, empty, queue_stats, log)

    log.start_timer()

    factory.start()
    dealership.start()

    factory.join()
    dealership.join()

    log.stop_timer(f'All {sum(queue_stats)} have been created')

    xaxis = [i for i in range(1, MAX_QUEUE_SIZE + 1)]
    plot = Plots()
    plot.bar(xaxis, queue_stats, title=f'{sum(queue_stats)} Produced: Count VS Queue Size', x_label='Queue Size',
             y_label='Count')


if __name__ == '__main__':
    main()
