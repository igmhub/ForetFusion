#!/usr/bin/env python
"""
 using mpi4py

** TODO:
    - self.THING_ID, flux, ivar
    - add comments, and del sdss_catalog
    - README has some typos, and difficult to read
"""


import numpy as np
from mpi4py import MPI
import  ffusion as ff

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


dir_files = 'data/'
file_name = 'DR14Q_v1_1.fits'

spall_cols  = ['RA','DEC','THING_ID','MJD','PLATE','FIBERID','Z','Z_ERR','ZWARNING']

if rank == 0:
    df_fits = ff.read_fits(dir_files, file_name, spall_cols)
    QSOs    = ff.QSO_catalog(df_fits, verbose = True)

    QSOs.rep_thid    = 1
    QSOs.write_master= True
    QSOs.write_ffits = True
    QSOs.show_plots  = True
    QSOs.write_names = False
    QSOs.write_hist  = True
    QSOs.need_files  = True

    QSOs.own_filter()
    #QSOs.filtering_qsos(condition= QSOs.condition)
    unique_pixels = QSOs.adding_pixel_column()
    #print (QSOs.df_qsos.query('PIX == 6219 & THING_ID == 77964771'))

    if QSOs.write_names: QSOs.write_file_names()
   
    lenpix = len(unique_pixels)
    nchunk = int(math.ceil(lenpix*1./size))
    chunks = [unique_pixels[i:i+ nchunk] for i in range(0, lenpix, nchunk)]
else:
    chunks = []
    QSOs   = None


QSOs = comm.bcast(QSOs, root=0)
if QSOs.write_hist: QSOs.write_stats_open(rank)

chunk_pix  = comm.scatter(chunks, root=0)
split_pixel(chunk_pix, QSOs)
comm.Barrier()

all_info  = comm.gather(QSOs.all_info, root=0)

if QSOs.write_hist: QSOs.write_stats_close()
if rank == 0:
    if QSOs.write_hist and QSOs.show_plots: QSOs.plot_stats(size)
    if QSOs.write_master: QSOs.master_fits(all_info)


