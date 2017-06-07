#
# Settings module
#
from __future__ import print_function, division

useMPI,comm,rank,size = False, None, 0, 1
useMultiprocessing = 0 #use multiprocessing instead of MPI
rootdir="."
DRQ="/global/projecta/projectdirs/sdss/eBOSS/DR14Q_v1_1.fits"
#spPlate_dir= '/global/projecta/projectdirs/sdss/staging/ebosswork/eboss/spectro/redux/v5_10_0/'
spPlate_dir='/global/projecta/projectdirs/sdss/eBOSS/testFiles'
use_spec=False
use_spCFrame=False
use_duplicates=False
mock=False
pix_dir=rootdir+"/pixs"
min_z=0.
max_z=6.
maxNobj=10000000
Nside=8
logl_min=3.550 #640
logl_max=4.025
logl_step=1e-4

def maybe_get(config,var,section,name):
    if type(var)==bool:
        gfunc=config.getboolean
    elif type(var)==str:
        gfunc=config.get
    elif type(var)==float:
        gfunc=config.getfloat
    elif type(var)==int:
        gfunc=config.getint
    else:
        print ("Bad variable",section,name)
        stop()
    try:
        var=gfunc(section,name)
    except:
        print ("Setting",name,"to default:",var)
    return var
    

def updateSettings(config):
    global useMPI, comm, rank, size, rootdir, DRQ, spPlate_dir, \
        pix_dir, maxNobj, Nside, logl_min, logl_max, logl_step,\
        min_z, max_z, use_spCFrame, use_spec, mock, use_duplicates,\
        useMultiprocessing
    
    useMPI=maybe_get(config, useMPI,"Main","MPI")
    useMultiprocessing=maybe_get(config, useMultiprocessing,"Main", "Multiprocessing")
    if useMPI and useMultiprocessing:
        print("Cannot have both MPI and multiprocessing")
    DRQ=maybe_get(config, DRQ,"Input","DRQ")
    spPlate_dir=maybe_get(config, spPlate_dir,"Input","spPlate_dir")
    use_spCFrame=maybe_get(config, use_spCFrame,"Input","use_spCFrame")
    use_duplicates=maybe_get(config, use_duplicates,"Input","use_duplicates")
    use_spec=maybe_get(config, use_spec,"Input","use_spec")
    mock=maybe_get(config, mock,"Input","mock")
    maxNobj=maybe_get(config, maxNobj,"Input","maxNobj")
    rootdir=maybe_get(config,rootdir,"Output","root")
    pix_dir=maybe_get(config,pix_dir,"Output","pix_dir")
    min_z=maybe_get(config,min_z,"Input", "min_z")
    max_z=maybe_get(config,max_z,"Input", "max_z")
    
def setMPI(comm_,rank_,size_):
    global comm,rank,size
    comm=comm_
    rank=rank_
    size=size_
    
