#!/usr/bin/env python
"""
** TODO:
    - self.THING_ID, flux, ivar
    - add comments, and del sdss_catalog
    - README has some typos, and difficult to read
"""


import  ffusion as ff
from ConfigParser import ConfigParser 
import sys

def main():
    config = initConfig()
    MPIt = initMPI(config)
    ff.automatic ()
    print "Done"
    sys.exit(0)


def initConfig():
    if len(sys.argv)!=2:
        print "Supply ini file on command line."
        sys.exit(1)
    config=ConfigParser()
    config.read(sys.argv[1])
    return config

def initMPI(config):
    useMPI=config.getboolean("Main","MPI")
    if useMPI:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    else:
        comm = None
        rank = 0
        size = 1
    return useMPI, comm,rank,size



if __name__ == "__main__":
    main()
