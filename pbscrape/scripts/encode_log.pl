#!/usr/bin/perl

# Iterates over a list of file paths retrieved from the $in_path CSV, encodes
# them, and outputs the updated data to $out_path.

use strict;
use Text::CSV_XS;
use URI::Escape::XS;

my $in_path = "./remove.log";
my $out_path = "./encoded-remove.log";
my $img_dir = "/images/";

unless (-e $out_path) {
    # Create the out file if it doesn't exist
    open my $fc, ">", $out_path;
    close $fc;
}

my $csv = Text::CSV_XS->new({
  binary => 1,
  auto_diag => 1,
  eol => "\n",
  quote_char => undef,
  escape_char => undef
});

# Open files
open my $fh, "<:encoding(utf8)", $in_path or die "$in_path: $!";
open my $fout, ">:encoding(utf8)", $out_path or die "$out_path: $!";

# Iterate over input file
while (my $row = $csv->getline($fh)) {
  my $img_path = $row->[0];

  # Get file and subdir
  my $file = (split '/', $img_path)[-1];
  my $subdir = substr($file, 0, 1);

  # URL encode the file and subdir names, because S3 reencodes each file name.
  # Each URL is already encoded, but S3 doesn't know that, so the names get double encoded.
  my $encoded_file = encodeURIComponent($file);
  my $encoded_subdir = encodeURIComponent($subdir) . "/";

  print $encoded_file . "\n";

  my $full_path = $img_dir . $encoded_subdir . $encoded_file;

  $csv->print($fout, [$full_path]);
}

close $fh;
close $fout;
