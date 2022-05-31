"""
Course: CSE 251
Lesson Week: 06
File: team-bad.py
Author: Brother Comeau

Purpose: Team Activity

Instructions:

- Implement the process functions to copy a text file exactly using a pipe

After you can copy a text file word by word exactly
- Change the program to be faster (Still using the processes)

"""

import multiprocessing as mp
from multiprocessing import Value, Process
import filecmp 

# Include cse 251 common Python files
from cse251 import *


BLOCK_SIZE = (1024 * 4)

END_MESSAGE = 'ALL DONE'


def sender(conn, num_words, filename, log):
    """ function to send messages to other end of pipe """
    '''
    open the file
    send all contents of the file over a pipe to the other process
    Note: you must break each line in the file into words and
          send those words through the pipe
    '''
    log.write('sender awake')
    with open(filename, 'rb') as f:
        done = False
        while not done:
            block = f.read(BLOCK_SIZE)
            if block:
                conn.send(block)
                num_words.value += 1
                log.write('word sent')
            else:
                done = True
    conn.send(END_MESSAGE)
    conn.close()
    log.write('sender done')


def receiver(conn, filename, log):
    """ function to print the messages received from other end of pipe """
    ''' 
    open the file for writing
    receive all content through the shared pipe and write to the file
    Keep track of the number of items sent over the pipe
    '''
    log.write('receiver awake')
    with open(filename, 'wb') as f:
        while True:
            next_word = conn.recv()
            if next_word == END_MESSAGE:
                break
            f.write(next_word)
            log.write('word received')
    conn.close()
    log.write('receiver done')


def are_files_same(filename1, filename2):
    """ Return True if two files are the same """
    return filecmp.cmp(filename1, filename2, shallow=False)


def copy_file(log, source_filename, target_filename):
    # TODO create a pipe
    parent_conn, child_conn = mp.Pipe()
    
    # TODO create variable to count items sent over the pipe
    num_words = mp.Value('L', 0)

    # TODO create processes
    send_proc = mp.Process(target=sender, args=(parent_conn, num_words, source_filename, log))
    receive_proc = mp.Process(target=receiver, args=(child_conn, target_filename, log))

    log.start_timer()
    start_time = log.get_time()

    # TODO start processes
    send_proc.start()
    receive_proc.start()

    # TODO wait for processes to finish
    send_proc.join()
    receive_proc.join()

    stop_time = log.get_time()

    log.stop_timer(f'Total time to transfer content = {num_words.value}: ')
    log.write(f'items / second = {num_words.value / (stop_time - start_time)}')

    if are_files_same(source_filename, target_filename):
        log.write(f'{source_filename} - Files are the same')
    else:
        log.write(f'{source_filename} - Files are different')


if __name__ == "__main__": 

    log = Log(show_terminal=True)

    copy_file(log, 'gettysburg.txt', 'gettysburg-copy.txt')
    
    # After you get the gettysburg.txt file working, uncomment this statement
    copy_file(log, 'bom.txt', 'bom-copy.txt')

