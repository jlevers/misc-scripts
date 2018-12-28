from concurrent.futures import ThreadPoolExecutor, as_completed
import contextlib
import csv
import os
import re
import requests
import shutil
import sys
import timeit
import urllib.request

# Get rid of old output and error files
def clean():
    run = input("Are you sure you want to delete " + OUTPUT_FILE + " and " + ERROR_FILE + "? (y/n) ")
    if run == "y":
        print("Running clean...")
        if os.path.isfile(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        if os.path.isfile(ERROR_FILE):
            os.remove(ERROR_FILE)
    else:
        print("Skipping clean...")


def scrape_images():
    start = timeit.default_timer()

    # Create a thread for each image to be fetched
    with ThreadPoolExecutor() as executor:
        futures = executor.map(process_line, get_line())

    stop = timeit.default_timer()
    print("Time: ", stop - start)


# Get next line in CSV
def get_line():
    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            yield row


# If the image cannot be fetched, write to the error file
def write_error(row, url, error):
    with open(ERROR_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow(row + [url, error, timeit.default_timer()])


# Add the fetched image to the output file
def update_record(row, fpath):
    with open(OUTPUT_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow(row + [fpath])


def process_image(row, url, fpath):

    with contextlib.closing(urllib.request.urlopen(url)) as img, open(fpath, 'wb') as f:
        shutil.copyfileobj(img, f)
    update_record(row, fpath)


def process_line(row):
    orig_url = row[1] + "~original"
    name_slashes = re.match(r"(?:.*?\/){5}(.*)", row[1]).group(1)
    name = re.sub(r"\/", "_", name_slashes)
    subdir = os.path.join(IMAGE_DIR, name[:1])
    path = os.path.join(subdir, name)

    if not os.path.exists(subdir):
        try:
            os.makedirs(subdir)
        except FileExistsError as e:
            pass
        except:
            raise

    if not os.path.isfile(path):    # Don't download the image again if it's already been fetched
        try:
            process_image(row, orig_url, path)
        except:
            try:
                process_image(row, row[1], path)
            except Exception as e:
                write_error(row, orig_url, e)


if __name__ == "__main__":
    INPUT_FILE = "../inputs/testing.csv"
    OUTPUT_FILE = "../output.csv"
    ERROR_FILE = "../errors.csv"
    IMAGE_DIR = "../images/"
    clean()

    scrape_images()
