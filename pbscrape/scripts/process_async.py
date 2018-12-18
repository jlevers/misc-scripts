from concurrent.futures import ThreadPoolExecutor
import contextlib
import csv
import os
import re
from requests_futures.sessions import FuturesSession
import shutil
import sys
import timeit


class Scrape:
    def __init__(self, infile, outfile, errfile, outdir, workers):
        self.infile = infile
        self.errfile = errfile
        self.outfile = outfile
        self.outdir = outdir
        self.workers = workers

    # Get rid of old output and error files
    def clean(self):
        run = input("Are you sure you want to delete " + self.outfile + " and " + self.errfile + "? (Y/N) ")

        if run.lower() == "y":
            print("Started clean...")

            if os.path.isfile(self.outfile):
                os.remove(self.outfile)
            if os.path.isfile(self.errfile):
                os.remove(self.errfile)

            print("Finished clean...")
        else:
            print("Skipping clean...")

    # Scrape!
    def scrape(self):
        print("Started scraping...")
        start = timeit.default_timer()

        tpe = ThreadPoolExecutor(max_workers=self.workers)
        with FuturesSession(executor=tpe) as executor:
            for line in self.
            result = executor.map(self.process_line, self.get_line())

        # Create a thread for each image to be fetched
        # with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # result = executor.map(self.process_line, self.get_line())

        stop = timeit.default_timer()
        print("Finished scraping...")
        print("Time: ", stop - start)

    # Get next line in CSV
    def get_line(self):
        with open(self.infile, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                yield row

    # If the image cannot be fetched, write to the error file
    def write_error(self, row, url, error):
        with open(self.errfile, "a") as f:
            writer = csv.writer(f)
            writer.writerow(row + [error])

    # Add the fetched image to the output file
    def update_record(self, row, fpath):
        with open(self.outfile, "a") as f:
            writer = csv.writer(f)
            writer.writerow(row + [fpath])


    def process_image(row, url, fpath):
        r = requests.get(url, stream=True)
        r.raise_for_status()
        if r.status_code == 200:
            with contextlib.closing(open(fpath, 'wb')) as f:
                shutil.copyfileobj(r.raw, f)
            update_record(row, fpath)


    def process_line(self, row):
        orig_url = row[1] + "~original"
        name_slashes = re.match(r"(?:.*?\/){5}(.*)", row[1]).group(1)
        name = re.sub(r"\/", "_", name_slashes)
        subdir = os.path.join(self.outdir, name[:1])
        path = os.path.join(subdir, name)

        if not os.path.exists(subdir):
            os.makedirs(subdir)

        if not os.path.isfile(path):    # Don't download the image again if it's already been fetched
            try:
                process_image(row, orig_url, path)
            except:
                try:
                    process_image(row, row[1], path)
                except:
                    e = sys.exc_info()
                    write_error(row, orig_url, e)


if __name__ == "__main__":
    test = Scrape("./smalltest.csv", "./output.csv", "errors.csv", "./images/", 7)
    test.clean()
    test.scrape()
