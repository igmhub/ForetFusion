#!/usr/bin/env python
"""
** TODO:
    - self.THING_ID, flux, ivar
    - add comments, and del sdss_catalog
    - README has some typos, and difficult to read
"""


import numpy as np
import  ffusion as ff
from ConfigParser import ConfigParser 
import sys

def main():
    config = initConfig()
    MPIt = initMPI(config)
    useMPI, comm,rank,size = MPIt

    dir_files = config.get("Catalog", "directory")
    file_name = config.get("Catalog", "filename")
    QSOs, chunks = initQSOcats(dir_files, file_name, MPIt)

    if QSOs.write_hist: 
        QSOs.write_stats_open(rank)
    
    if useMPI:
        chunk_pix  = comm.scatter(chunks, root=0)
    else:
        chunk_pix = chunks[0]

    ff.split_pixel(chunk_pix, QSOs)
    if useMPI:
        comm.Barrier()
        all_info  = comm.gather(QSOs.all_info, root=0)
    else:
        all_info=[QSOs.all_info]

    if QSOs.write_hist: QSOs.write_stats_close()
    if rank == 0:
        if QSOs.write_hist and QSOs.show_plots: QSOs.plot_stats(size)
        if QSOs.write_master: QSOs.master_fits(all_info)
    print  "Done."
    sys.exit(0)

def initQSOcats(dir_files, file_name, MPIt):

    spall_cols  = ['RA','DEC','THING_ID','MJD','PLATE','FIBERID','Z','Z_ERR','ZWARNING']

    useMPI,comm,rank,size = MPIt

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
        nchunk = int(np.ceil(lenpix*1./size))
        chunks = [unique_pixels[i:i+ nchunk] for i in range(0, lenpix, nchunk)]
    else:
        chunks = []
        QSOs   = None

    if useMPI:
        QSOs = comm.bcast(QSOs, root=0)

    return QSOs, chunks
    

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
