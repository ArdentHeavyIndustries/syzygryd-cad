#!/usr/bin/perl
#
# Prepare files from pronest for execution on a Torchmate CNC plasma system
# GPL'd, if it matters.
# Ian Baker <ian@sonic.net>

use strict;

my ($infile, $feedrate) = @ARGV;

die "usage: $0 <infile> [feedrate]\n" unless $infile;

$feedrate ||= 350;

# open read/write
open(IN, "+<$infile") || die "Can't open $infile: $!\n";
my @out;
my $feed_inserted;

foreach (<IN>) {
    s/\r*\n//;
    next if /^(M07|M08|M02|G40|G41|G84)/;  #remove these
    if(!$feed_inserted) {
	if(/^G01.*F\d+/) {
	    # feedrate already present, replace it with the specified one.
	    s/F\d+/F$feedrate/;
	    $feed_inserted = 1;
	} elsif (/^G01/) {  #set feedrate?
	    $_ .= " F$feedrate";
	    $feed_inserted = 1;
	}
    }

    push(@out, $_);
}

# insert this at the 3rd line
splice(@out, 2, 0, 'G0X0Y0') unless $out[2] eq 'G0X0Y0';

seek(IN, 0, 0);

# use windows newlines
print IN join("\r\n", @out);
print IN "\r\n";
truncate(IN, tell(IN)); #truncate to current length
