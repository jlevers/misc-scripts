import csv
import os
import re
import shutil
import sys
import timeit
import urllib.request

class Scrape:
    def __init__(self, infile, outfile, errfile, outdir):
        self.infile = infile
        self.errfile = errfile
        self.outfile = outfile
        self.outdir = outdir

    # Get rid of old output and error files
    def clean(self):
        run = input("Are you sure you want to delete " + self.outfile + " and " + self.errfile + "? (y/n) ")

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

        with open(self.outfile, "a") as outf, open(self.errfile, "a") as errf:
            out_writer = csv.writer(outf)
            err_writer = csv.writer(errf)

            for line in self.get_line():
                result = self.process_line(line)

                if 'err' in result:
                    err_writer.writerow(line + [result['err']])
                else:
                    out_writer.writerow(line + [result['fpath']])

        stop = timeit.default_timer()
        print("Finished scraping...")
        print("Time: ", stop - start)


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
                img_orig = self.process_image(row, orig_url, path)
                return img_orig
            except:
                try:
                    img = self.process_image(row, row[1], path)
                    return img
                except Exception as err:
                    return { 'row': row, 'url': row[1], 'err': err }

        return { 'row': row, 'url': row[1], 'err': "File has already been downloaded" }


    def process_image(self, row, url, fpath):
        with urllib.request.urlopen(url) as img, open(fpath, 'wb') as f:
            shutil.copyfileobj(img, f)
            return { 'row': row, 'fpath': fpath }


    # Get next line in CSV
    def get_line(self):
        with open(self.infile, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                yield row


if __name__ == "__main__":
    test = Scrape("../inputs/test-in.csv", "../outputs/output.csv", "../outputs/errors.csv", "../images/")
    test.clean()
    test.scrape()
