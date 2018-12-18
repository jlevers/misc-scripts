import csv
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import os
import re
import sys
import timeit
from urllib import request


def clean():
    if os.path.isfile(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    if os.path.isfile(ERROR_FILE):
        os.remove(ERROR_FILE)


# Run with multiple processors
def run_pool(workers):
    start = timeit.default_timer()

    pool = Pool(workers)
    file_gen = get_line()  # Generator for CSV file

    for line in file_gen:
        pool.map(process_line, (line,))

    # Close pool and wait for all threads to finish
    pool.close()
    pool.join()

    stop = timeit.default_timer()
    print("Pool time: ", stop - start)


# Run with multiple threads
def run_thread_pool(workers):
    start = timeit.default_timer()

    pool = ThreadPool(workers)
    file_gen = get_line()  # Generator for CSV file

    for line in file_gen:
        pool.map(process_line, (line,))

    # Close pool and wait for all threads to finish
    pool.close()
    pool.join()

    stop = timeit.default_timer()
    print("ThreadPool time: ", stop - start)


# Run normally (using a loop)
def run_loop():
    start = timeit.default_timer()
    file_gen = get_line()  # Generator for CSV file

    for line in file_gen:
        process_line(line)

    stop = timeit.default_timer()
    print("Loop time: ", stop - start)


# Get next line in CSV
def get_line():
    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            yield row


def write_error(row, url, error):
    with open(ERROR_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow(row + [url, error, timeit.default_timer()])


def update_record(row, fname):
    with open(OUTPUT_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow(row + [fname])


def process_image(row, url, fname):
    request.urlretrieve(url, fname)
    update_record(row, fname)


def process_line(row):
    orig_url = row[1] + "~original"
    name_slashes = re.match(r"(?:.*?\/){5}(.*)", row[1]).group(1)
    name = re.sub(r"\/", "_", name_slashes)
    fp = IMAGE_DIR + name
    if not os.path.isfile(fp):
        try:
            process_image(row, orig_url, fp)
        except:
            try:
                process_image(row, row[1], fp)
            except:
                e = sys.exc_info()
                write_error(row, orig_url, e)


if __name__ == "__main__":
    INPUT_FILE = "./smalltest.csv"
    OUTPUT_FILE = "./output.csv"
    ERROR_FILE = "./errors.csv"
    IMAGE_DIR = "./images/"

    clean()

    run_thread_pool(8)
