#!/usr/bin/env python
##################################################################################################
"""This script renames all JPG files based on the DateTime attribute in the image's exif data
   Rename all '*.JPG' and '*.jpg' in the current directory and optionally, all
   subdirectories using the images' embedded exif data to form a file name
   based on the DateTime attribute.

   File names take the form: DATE_TIME_DAYOFWEEK.jpg for example
   '2015-03-18_12-58-21_Wednesday.jpg'.
"""

##################################################################################################

import os
import calendar
import datetime
import fnmatch
import argparse
import glob
import exifread

##################################################################################################
PARSER = argparse.ArgumentParser()
PARSER.add_argument('-r',
                    dest='recurse_subdirectories',
                    action='store_true',
                    help='include subdirectories'
                   )
PARSER.add_argument('-v',
                    dest='verbose',
                    action='store_true',
                    help='display old and new file names'
                   )
PARSER.add_argument('-n',
                    dest='no_op',
                    action='store_true',
                    help="don't rename any files, generally used with -v"
                   )
PARSER.add_argument('-q',
                    dest='quiet',
                    action='store_true',
                    help="don't complain about files that can't be renamed"
                   )
ARGS = PARSER.parse_args()

##################################################################################################
def find_exif_datetime(fname):
    """Returns the DateTime attribute for the JPG file or "None" if not found """
    fhandle = open(fname, 'rb')
    tags = exifread.process_file(fhandle, stop_tag='DateTime', details=False)
    for tag in tags.keys():
        if tag == 'Image DateTime':
            return str(tags[tag])
    return

##################################################################################################
def make_filename_from_datetime(rootdir, datetimestring):
    """Returns a new file name based on the datetimestring or None if datetimestring is invalid"""
    if int(datetimestring[0:4]) != 0:
        # assumes datetimestring looks like "YYYY:MM:DD HH:MM:SS"
        # replace ":" with '-' and " " with "_" to make new file name work on Windows
        datetimestring = datetimestring.replace(':', '-')
        datetimestring = datetimestring.replace(' ', '_')
        #make a datetime object to retrieve the name of the week day
        filedate = datetime.datetime(int(datetimestring[0:4]),
                                     int(datetimestring[5:7]),
                                     int(datetimestring[8:10])
                                    )
        return os.path.join(rootdir,
                            datetimestring +
                            '_' +
                            calendar.day_name[filedate.weekday()] +
                            '.jpg'
                           )
    return


##################################################################################################
def make_unique_name(fname):
    """appends a numeric string to the end of a jpg file name to make it unique,
       expects four character file extension for example 'image.jpg'
    """
    for number in range(2, 100):
        unique_name = fname[0:-4] + '_' + str(number) + fname[-4:]
        if not os.path.isfile(unique_name):
            return unique_name
    return

##################################################################################################
def rename_image(rootdir, basename):
    """renames a JPG file based on the DateTime attribute in the image's exif data"""
    fname = os.path.join(rootdir, basename)
    datetimestring = find_exif_datetime(fname)
    if datetimestring is None:
        if not ARGS.quiet:
            # some files have corrupt or unrecognizable exif data
            print "Can't retrieve DateTime from ", fname
        return

    newname = make_filename_from_datetime(rootdir, datetimestring)
    if newname is None:
        if not ARGS.quiet:
            print "Invalid DateTime attribute in", fname, "("+datetimestring+")"
        return

    if newname == fname:
        # nothing to do
        return

    if os.path.isfile(newname):
        newname = make_unique_name(newname)
        if newname is None:
            print "Can't make unique file name for", + fname
            return

    if ARGS.no_op:
        return

    if ARGS.verbose:
        print fname, '-->', newname

    os.rename(fname, newname)


##################################################################################################
if ARGS.recurse_subdirectories:
    # recurse through current directory and all subdirectories
    for root, dirs, files in os.walk("."):
        for filename in files:
            if fnmatch.fnmatch(filename, '*.jpg') or fnmatch.fnmatch(filename, '*.JPG'):
                rename_image(root, filename)
else:
    # Just the current directory
    for filename in glob.glob('*.jpg') + glob.glob('*.JPG'):
        rename_image('.', filename)

##################################################################################################

