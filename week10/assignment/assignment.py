"""
Course: CSE 251
Lesson Week: 10
File: team.py
Author: Dane Artis

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  
  
- Display the numbers received by the reader printing them to the console.

- Create WRITERS writer processes

- Create READERS reader processes

- You can use sleep() statements for any process.

- You are able (should) to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s), or lock(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

  CRITICAL SECTIONS:
  - Insert index
  - Remove index
  - Managed List

  size of buffer = current_index - remove_index

  current_index += 1

  current_index % SIZE

- Not allowed to use Queue(), Pipe(), List() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

Add any comments for me:

"""
import random
import time
from multiprocessing.managers import SharedMemoryManager
from multiprocessing import shared_memory
import multiprocessing as mp

BUFFER_SIZE = 10
READERS = 1
WRITERS = 1

CURRENT = -4
WRITE_I = -3
READ_I = -2
END = -1


def send(s_list, access, buffer_spot_empty, buffer_spot_full):
    print('send started')
    while True:
        with access:
            if s_list[CURRENT] < s_list[END]:
                buffer_spot_empty.acquire()
                s_list[s_list[WRITE_I]] = s_list[CURRENT]
                # print(f'SEND: {s_list[s_list[WRITE_I]]}', flush=True)
                s_list[CURRENT] = s_list[CURRENT] + 1
                s_list[WRITE_I] = (s_list[WRITE_I] + 1) % BUFFER_SIZE
                buffer_spot_full.release()
            else:
                break
        time.sleep(0.001)


def receive(s_list, access, buffer_spot_empty, buffer_spot_full):
    print('receive started')
    while True:
        buffer_spot_full.acquire()
        with access:
            # print(s_list)
            print(f'RECEIVED: {s_list[s_list[READ_I]]}', flush=True)
            if s_list[CURRENT] == s_list[END]:
                break
            else:
                # print('r ind:', (s_list[READ_I] + 1) % BUFFER_SIZE)
                s_list[READ_I] = (s_list[READ_I] + 1) % BUFFER_SIZE
            buffer_spot_empty.release()
        time.sleep(0.001)


def main():
    # This is the number of values that the writer will send to the reader
    items_to_send = random.randint(1000, 10000)

    smm = SharedMemoryManager()
    smm.start()

    # Create a ShareableList to be used between the processes
    start = 1
    write_index = 0
    read_index = 0
    temp = [0] * BUFFER_SIZE
    temp.append(start)
    temp.append(write_index)
    temp.append(read_index)
    temp.append(items_to_send)
    shared_list = smm.ShareableList(temp)
    # print(shared_list)
    # print(shared_list[CURRENT], shared_list[WRITE_I], shared_list[READ_I], shared_list[END])

    # Create any lock(s) or semaphore(s) that you feel you need
    buffer_spot_empty = mp.Semaphore(BUFFER_SIZE)
    buffer_spot_full = mp.Semaphore(0)
    access_w = mp.Lock()
    access_r = mp.Lock()

    # create reader and writer processes
    writers = [mp.Process(target=send, args=(shared_list, access_w, buffer_spot_empty, buffer_spot_full)) for _ in range(WRITERS)]
    readers = [mp.Process(target=receive, args=(shared_list, access_r, buffer_spot_empty, buffer_spot_full)) for _ in range(READERS)]

    # Start the processes and wait for them to finish
    [p.start() for p in writers]
    [p.start() for p in readers]

    [p.join() for p in writers]
    [p.join() for p in readers]

    print(f'{items_to_send} values sent')

    # Display the number of numbers/items received by the reader.
    #        Can not use "items_to_send", must be a value collected
    #        by the reader processes.
    print(f'{shared_list[CURRENT]} values received')

    # print('values received:')
    # print(*written_values, sep=', ')

    shared_list.shm.close()
    shared_list.shm.unlink()
    smm.shutdown()


if __name__ == '__main__':
    main()
