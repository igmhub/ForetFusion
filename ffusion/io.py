#!/usr/bin/env python

import os, sys
import fitsio
from glob import glob
import numpy as np

def read_fits(file_name, fits_cols, maxnum=0):
    """Read selected columns in the .fits file. Return a DataFrame"""
    if not os.path.isfile(file_name):
        print('File not found: {}'.format(file_name))
        exit(1)
    fits       = fitsio.FITS(file_name)
    #http://stackoverflow.com/questions/30283836/
    # creating-pandas-dataframe-from-numpy-array-leads-to-strange-errors
    fits_read  = fits[1].read(columns= fits_cols)
    return fits_read[:maxnum]


def read_spplate(dir_fits, triplet):
    plate,mjd,fiber=triplet
    fname=dir_fits+"/%i/spPlate-%i-%i.fits"%(plate,plate,mjd)
#    if not os.path.isfile(fname):
#        print('File not found: {}'.format(fname))
#        sys.exit(1)
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

def read_spec(dir_fits, triplet,mock=False):
    plate,mjd,fiber=triplet
    prefix="spec"
    if mock:
        prefix="mock"
    sfib="%i"%fiber
    if fiber<10:
        sfib="0"+sfib
    if fiber<100:
        sfib="0"+sfib
    if fiber<1000:
        sfib="0"+sfib
    ext="fits"
    if mock:
        ext="fits.gz"
    fname=dir_fits+"/%i/%s-%i-%i-%s.%s"%(plate,prefix,plate,mjd,sfib,ext)
    if not os.path.isfile(fname):
        print('File not found: {}'.format(fname))
        sys.exit(1)
    fits       = fitsio.FITS(fname)
    flux = fits[1]["flux"][:]
    ivar = fits[1]["ivar"][:]
    andmask = fits[1]["and_mask"][:]
    ormask = np.zeros(len(andmask),dtype=bool)
    loglam = fits[1]["loglam"][:]
    dtype=[('loglam','f4'),('flux','f4'),('ivar','f4'),('andmask','i4'),('ormask','i4')]
    N=len(flux)
    ar=np.zeros(N,dtype=dtype)
    ar['loglam']=loglam
    ar['flux']=flux
    ar['ivar']=ivar
    ar['andmask']=andmask
    ar['ormask']=ormask
    return ar

def read_spcframe(dir_fits, triplet):
    plate,mjd,fiber=triplet
    camera=1
    if fiber>500:
        fiber-=500
        camera=2
    fnameglob=dir_fits+"/%i/spCFrame-?%i-*.fits"%(plate,camera)
    fnamelist=glob(fnameglob)
    if len(fnamelist)==0:
        print("No files found:",fnameglob)
        sys.exit(1)
    arl=[]
    for fname in fnamelist:
        head=fitsio.read_header(fname)
        ddays=mjd-head['MJD']
        if (ddays<0) or (ddays>5):
              #print "Skipping ",mjd,head['MJD'],ddays
              continue
        #print "Keeping:",mjd,head['MJD'],ddays
        fits = fitsio.FITS(fname)
        flux = fits[0].read()[fiber-1]
        ivar = fits[1].read()[fiber-1]
        andmask = fits[2].read()[fiber-1]
        ormask = andmask
        loglam = fits[3].read()[fiber-1]
        dtype=[('loglam','f4'),('flux','f4'),('ivar','f4'),('andmask','i4'),('ormask','i4')]
        N=len(flux)
        ar=np.zeros(N,dtype=dtype)
        ar['loglam']=loglam
        ar['flux']=flux
        ar['ivar']=ivar
        ar['andmask']=andmask
        ar['ormask']=ormask
        arl.append(ar)
    return arl


