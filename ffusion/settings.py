#
# Settings module
#

useMPI,comm,rank,size = False, None, 0, 1
useMultiprocessing = 0 #use multiprocessing instead of MPI
rootdir="."
DRQ="/global/projecta/projectdirs/sdss/eBOSS/DR14Q_v1_1.fits"
#spPlate_dir= '/global/projecta/projectdirs/sdss/staging/ebosswork/eboss/spectro/redux/v5_10_0/'
spPlate_dir='/global/projecta/projectdirs/sdss/eBOSS/testFiles'
use_spec=False
use_spCFrame=False
mock=False
pix_dir=rootdir+"/pixs"
min_z=0
max_z=6
maxNobj=10000000
Nside=8
logl_min=3.550 #640
logl_max=4.025
logl_step=1e-4

def updateSettings(config):
    global useMPI, comm, rank, size, rootdir, DRQ, spPlate_dir, \
        pix_dir, maxNobj, Nside, logl_min, logl_max, logl_step,\
        min_z, max_z, use_spCFrame,mock, use_spec,useMultiprocessing
    
    useMPI=config.getboolean("Main","MPI")
    useMultiprocessing=config.getint("Main", "Multiprocessing")
    if useMPI and useMultiprocessing:
        print "Cannot have both MPI and multiprocessing"
    DRQ=config.get("Input","DRQ")
    spPlate_dir=config.get("Input","spPlate_dir")
    use_spCFrame=config.getboolean("Input","use_spCFrame")
    try:
    	use_spec=config.getboolean("Input","use_spec")
    	mock=config.getboolean("Input","mock")
    except:
        pass
    maxNobj=config.getint("Input","maxNobj")
    rootdir=config.get("Output","root")
    pix_dir=config.get("Output","pix_dir",raw=False)
    min_z=config.getfloat("Input", "min_z")
    max_z=config.getfloat("Input", "max_z")
    
def setMPI(comm_,rank_,size_):
    global comm,rank,size
    comm=comm_
    rank=rank_
    size=size_
    
