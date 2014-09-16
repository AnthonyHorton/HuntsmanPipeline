#!/usr/bin/env python3

# To give the code some chance of working in Python 2
from __future__ import division, unicode_literals, print_function

import ccdproc
import astropy.io.fits
import os
import os.path
import glob
import configparser
import re

def default_conf(path=''):
    '''
    Creates config file 'hp.conf' with default config

    Arguments:

    path - optional, path to directory to write the config file to. If not
           given will write to current working directory.
    '''
    config = configparser.ConfigParser()
    config['paths'] = {'raw_data': '/mnt/data/HuntsmanEye/raw', \
                       'red_data': '/mnt/data/HuntsmanEye/red'}
    with open(os.path.join(path, 'hp.conf'), 'w') as configfile:
        config.write(configfile)

def read_conf(fname='hp.conf'):
    '''
    Read config file and return configparser.ConfigParser object.

    Arguments:

    fname - optional, default 'hp.conf', path to config file

    Returns:

    config - configparser.ConfigParser object
    '''
    config = configparser.ConfigParser()
    config.read(fname)
    return config

fits_pattern = re.compile('\.fits?$', flags=re.IGNORECASE)

def find_fits(dir):
    '''
    Convenience function to find all the FITS files within a given directory
    and its subdirectories (if any).  Uses filename extension to identify FITS 
    files, will match any of *.fit, *.FIT, *.fits and *.FITS.

    Arguments:

    dir - path of directory in which to search of FITS files

    Returns:

    fits_files - list of 2-tuples, the first element of the tuple is a 
                 string containing the path of the directory or subdirectory, 
                 the second element is a list of filenames of the FITS files
                 within that (sub)directory.

    Note: does not follow symbolic links into other directory trees (limitation
    of os.walk()).
    '''
    fits_files = []
    for dir_listing in os.walk(dir):
        fits_fnames = [fname for fname in dir_listing[2] if re.search(fits_pattern, fname)]
        if len(fits_fnames) != 0:
            fits_files.append((dir_listing[0], fits_fnames))

    return fits_files

#if __name__ == "__main__":
    
