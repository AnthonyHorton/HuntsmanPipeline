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
import warnings

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
    config['camera'] = {'bias_exptime': '0.09'}
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

def find_fits(dir, config):
    '''
    Convenience function to find all the FITS files within a given directory
    and its subdirectories (if any).  Uses filename extension to identify FITS 
    files, will match any of *.fit, *.FIT, *.fits and *.FITS.

    Attempts to categorise each FITS file as a bias, dark, flat or light frame
    based on the IMAGETYP and EXPTIME header values if present, otherwise will 
    make a guess based on the filename.

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
        fits_fnames = [(categorise_fits(fname, dir_listing[0], config['camera']), fname) \
                       for fname in dir_listing[2] if re.search(fits_pattern, fname)]
        if len(fits_fnames) != 0:
            fits_files.append((dir_listing[0], fits_fnames))

    return fits_files

bias_pattern = re.compile('bias', flags=re.IGNORECASE)
dark_pattern = re.compile('dark', flags=re.IGNORECASE)
flat_pattern = re.compile('flat', flags=re.IGNORECASE)

def categorise_fits(fname, path, config_camera):
    header = astropy.io.fits.getheader(os.path.join(path, fname))
    try:
        exptime = header['EXPTIME']
        try:
            imagetyp = header['IMAGETYP']
            if imagetyp == 'BIAS' or imagetyp == 'Bias Frame':
                # Definitely a bias frame
                return 'BIAS'
            elif imagetyp == 'DARK' or imagetyp == 'Dark Frame':
                # Probably a dark frame, but should check exposure time
                if exptime <= float(config_camera['bias_exptime']):
                    # Dark frame but with minimum exposure time, this is a bias frame really
                    return 'BIAS'
                else:
                    return 'DARK'
            elif imagetyp == 'FLAT' or imagetyp == 'Flat Field':
                # Definitely some sort of flat. Twilight, sky, dome, etc?
                return 'FLAT'
            elif imagetyp =='LIGHT' or imagetyp == 'Light Frame':
                return 'LIGHT'
            else:
                # Has an IMAGETYP header entry but doesn't conform to IRAF or SBIGFITSEXT
                # conventions.
                warnings.warn("FITS file '{}' has unrecognised IMAGETYP '{}'!".format(fname, imagetyp), UserWarning)
                return 'UNKNOWN'
        except KeyError:
            # No IMAGETYP header entry, will guess based on filename.
            if re.search(bias_pattern, fname):
                # Probably a bias frame...
                return 'BIAS'
            elif re.search(dark_pattern, fname):
                # Probably a dark...
                if exptime <= float(config_camera['bias_exptime']):
                    # Dark frame but with minimum exposure time, this is a bias frame really
                    return 'BIAS'
                else:
                    return 'DARK'
            elif re.search(flat_pattern, fname):
                # Probably some sort of flat.
                return 'FLAT'
            else:
                # None of the above, more likely than not a light frame.
                warnings.warn("Guessing that FITS file '{}' is a light frame!".format(fname), \
                              UserWarning)
                return 'LIGHT'
    except KeyError:
        # No EXPTIME header entry! WTH?
        warnings.warn("FITS file '{}' has no EXPTIME header entry!".format(fname), UserWarning)
        return 'UNKNOWN'

#if __name__ == "__main__":
    
