#!/usr/bin/perl

# Checks MIME types of files at locations retrieved from $in_path. If the MIME
# type isn't text/html or unknown, HTML encodes the path, and outputs the
# contents of the current CSV line (with the file path encoded) to $out_path.

use strict;

use Text::CSV_XS;
use URI::Escape::XS;

my $in_path = "../outputs/new-output-final.csv";
my $out_path = "../outputs/new-encoded-out.csv";
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
  my $img_path = $row->[2];
  my $file_mime_call = `file --mime-type /storage"$img_path"`;
  my $mime = "placeholder";
  if ($file_mime_call =~ /\: (.*)$/) {
    $mime = $1;
  } else {
    warn "Can't get MIME for $img_path: $!";
  }

  # If the MIME type is text/html:
  unless ($mime eq "text/html" or $mime eq "placeholder") {
    # Get file and subdir
    my $file = (split '/', $img_path)[-1];
    my $subdir = substr($file, 0, 1);

    # URL encode the file and subdir names, because S3 reencodes each file name.
    # Each URL is already encoded, but S3 doesn't know that, so the names get double encoded.
    my $encoded_file = encodeURIComponent($file);
    my $encoded_subdir = encodeURIComponent($subdir) . "/";

    my $full_path = $img_dir . $encoded_subdir . $encoded_file;

    $csv->print($fout, [$row->[0], $row->[1], $full_path]);
  }
}

close $fh;
close $fout;
