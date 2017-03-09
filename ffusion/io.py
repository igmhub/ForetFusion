#!/usr/bin/env python

import os, sys
import fitsio
import numpy as np

def read_fits(file_name, fits_cols, maxnum=0):
    """Read selected columns in the .fits file. Return a DataFrame"""
    if not os.path.isfile(file_name):
        print('File not found: {}'.format(file_name))
        MPI.COMM_WORLD.Abort()
    fits       = fitsio.FITS(file_name)
    #http://stackoverflow.com/questions/30283836/
    # creating-pandas-dataframe-from-numpy-array-leads-to-strange-errors
    fits_read  = fits[1].read(columns= fits_cols)
    return fits_read[:maxnum]


def read_spframe(dir_fits, triplet):
    plate,mjd,fiber=triplet
    fname=dir_fits+"/%i/spPlate-%i-%i.fits"%(plate,plate,mjd)
    if not os.path.isfile(fname):
        print('File not found: {}'.format(fname))
        sys.exit(1)
    fits       = fitsio.FITS(fname)
    flux = fits[0].read()[fiber-1]
    ivar = fits[1].read()[fiber-1]
    andmask = fits[2].read()[fiber-1]
    ormask = fits[3].read()[fiber-1]
    head=fitsio.read_header(fname)
    loglam = head['COEFF0']+head['COEFF1']*np.arange(len(flux))
    dtype=[('loglam','f4'),('flux','f4'),('ivar','f4'),('andmask','i4'),('ormask','i4')]
    N=len(flux)
    ar=np.zeros(N,dtype=dtype)
    ar['loglam']=loglam
    ar['flux']=flux
    ar['ivar']=ivar
    ar['andmask']=andmask
    ar['ormask']=ormask
    return ar


