#!/usr/bin/perl

# This script searches $img_dir for images that're listed (by URL) in $in_path.
# If a given image exists, it gets added to the $out_path CSV, with the same
# fields as in the $in_path CSV, plus the path to the image in $img_dir.

# Functional interface
use Text::CSV_XS;

my $in_path = "../inputs/records.csv";
my $out_path = "../outputs/new-output-final.csv";
my $img_dir = "/storage/images/";

unless(-e $out_path) {
    # Create the out file if it doesn't exist
    open my $fc, ">", $out_path;
    close $fc;
}

my @rows;
# Read/parse CSV
my $csv = Text::CSV_XS->new({
  binary => 1,
  auto_diag => 1,
  eol => "\n",
  quote_char => undef,
  escape_char => undef
});
open my $fh, "<:encoding(utf8)", $in_path or die "$in_path: $!";
open my $fout, ">:encoding(utf8)", $out_path or die "$out_path: $!";

while (my $row = $csv->getline($fh)) {
  $row_url = $row->[1];
  my $fname;

  if ($row_url =~ /(?:.*?\/){5}(.*)$/) {  # Get info after 5th slash, if it exists

    if (($match = $1) =~ s/\//_/g) {  # Replace slashes with underscores

      $fname = $match;
      $subdir = substr($fname, 0, 1) . "/";
      $full_path = $img_dir . $subdir . $fname;

      if (-e $full_path) {
        $csv->print($fout, [@$row, "/images/" . $subdir . $fname]);
      }
    }
  }
}

close $fh;
close $fout;
