
# To give the code some chance of running in Python 2
from __future__ import division, unicode_literals, print_function

import ccdproc
import astropy.io.fits
import os.path
import glob
import configparser

def default_conf(path=''):
    config = configparser.ConfigParser()
    config['paths'] = {'raw_data': '/mnt/data/HuntsmanEye/raw', \
                       'red_data': '/mnt/data/HuntsmanEye/red'}
    with open(os.path.join(path, 'hp.conf'), 'w') as configfile:
        config.write(configfile)

def read_conf(fname='hp.conf'):
    config = configparser.ConfigParser()
    config.read(fname)
    return config


#if __name__ == "__main__":
    
