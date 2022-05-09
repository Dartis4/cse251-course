"""
------------------------------------------------------------------------------
Course: CSE 251
Lesson Week: 03
File: assignment.py
Author: Dane Artis

Purpose: Video Frame Processing

Instructions:

- Follow the instructions found in Canvas for this assignment
- No other packages or modules are allowed to be used in this assignment.
  Do not change any of the from and import statements.
- Only process the given MP4 files for this assignment

------------------------------------------------------------------------------
"""

from matplotlib.pylab import plt  # load plot library
from PIL import Image
import numpy as np
import timeit
import multiprocessing as mp

# Include cse 251 common Python files
from cse251 import *

# 4 more than the number of cpu's on your computer
CPU_COUNT = mp.cpu_count() + 4  

FRAME_COUNT = 300

RED   = 0
GREEN = 1
BLUE  = 2


def create_new_frame(image_file, green_file, process_file):
    """ Creates a new image file from image_file and green_file """

    # this print() statement is there to help see which frame is being processed
    print(f'{process_file[-7:-4]}', end=',', flush=True)

    image_img = Image.open(image_file)
    green_img = Image.open(green_file)

    # Make Numpy array
    np_img = np.array(green_img)

    # Mask pixels 
    mask = (np_img[:, :, BLUE] < 120) & (np_img[:, :, GREEN] > 120) & (np_img[:, :, RED] < 120)

    # Create mask image
    mask_img = Image.fromarray((mask*255).astype(np.uint8))

    image_new = Image.composite(image_img, green_img, mask_img)
    image_new.save(process_file)


def gen_frame(frame_num):
    # Generate filenames
    image_file = rf'elephant/image{frame_num:03d}.png'
    green_file = rf'green/image{frame_num:03d}.png'
    process_file = rf'processed/image{frame_num:03d}.png'

    # Create the frame from the filenames
    create_new_frame(image_file, green_file, process_file)


def parallel_frame_gen(cores, frames):
    print(f'Frames processed:', flush=True)
    # Generate each frame in parallel
    start_time = timeit.default_timer()
    with mp.Pool(cores) as p:
        p.map(gen_frame, frames)
    process_time = timeit.default_timer() - start_time
    return process_time


if __name__ == '__main__':
    # single_file_processing(300)
    # print('cpu_count() =', cpu_count())

    all_process_time = timeit.default_timer()
    log = Log(show_terminal=True)

    xaxis_cpus = []
    yaxis_times = []

    # Iterate up to the possible number of cores
    num_frames = range(1, FRAME_COUNT)
    for num_cores in range(1, CPU_COUNT):
        log.write(f'Number of cores: {num_cores}')
        # Process in parallel and add results for the plot
        xaxis_cpus.append(num_cores)
        proc_time = parallel_frame_gen(num_cores, num_frames)
        log.write(f'Time To Process all images = {proc_time}\n')
        yaxis_times.append(proc_time)

    log.write(f'Total Time for ALL processing: {timeit.default_timer() - all_process_time}')

    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_cpus, yaxis_times, label=f'{FRAME_COUNT}')
    
    plt.title('CPU Core yaxis_times VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig(f'Plot for {FRAME_COUNT} frames.png')
    plt.show()
