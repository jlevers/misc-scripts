#!/usr/bin/perl

# UNFINISHED. Checks MIME types of files, and deletes them from the filesystem
# and the output CSV if they do/don't match (that part isn't complete).

use strict;
use Text::CSV_XS;

my $in_path = "../outputs/new-output-final.csv";
my $out_path = "../outputs/html.csv";
my $img_dir = "/storage/images/";

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
# open my $fout, ">:encoding(utf8)", $out_path or die "$out_path: $!";

# Iterate over input file
while (my $row = $csv->getline($fh)) {
  my $img_path = "/storage" . $row->[2];
  my $file_mime_call = `file --mime-type "$img_path"`;
  my $mime = "placeholder";
  if ($file_mime_call =~ /\: (.*)$/) {
    $mime = $1;
  } else {
    warn "Can't get MIME for $img_path: $!\n";
  }

  print "$img_path: $mime" . "\n";

  # If the MIME type is text/html:
  # unless ($mime eq 'text/html') {
    # Get file and subdir
    # my $file = (split '/', $img_path)[-1];
    # my $subdir = substr($file, 0, 1);

    # URL encode the file and subdir names, because S3 reencodes each file name.
    # Each URL is already encoded, but S3 doesn't know that, so the names get double encoded.
    # my $encoded_file = $uri->encode($file);
    # my $encoded_subdir = $uri->encode($subdir) . "/";

    # my $full_path = $img_dir . $encoded_subdir . $encoded_file;

    # $csv->print($fout, [$row->[0], $row->[1], $full_path]);
  # }
}

close $fh;
