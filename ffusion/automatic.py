#
# main driver
#

import settings as st
from io import *
import healpy as hp
# we let drive initialize MPI everything else we do here
def automatic ():
    ltodo = loadDRQandPixelize()
    for i,pixinfo in enumerate(ltodo):
        if (i%st.size==st.rank):
            processPixel(*pixinfo)



        
def loadDRQandPixelize():
    spall_cols  = ['RA','DEC','THING_ID','MJD','PLATE','FIBERID','Z']
    if st.rank == 0:
        drq = read_fits(st.DRQ, spall_cols, st.maxNobj)
        ## first filter for quasars
        #w=np.where(drq['CLASS']=="QSO" & (drq['OBJTYPE']=='QSO' | drq['OBJTYPE']=='QSO') & drq['THING_ID']!=-1)
        #drq=drq[w]
        print "We have ",len(drq)," quasars after filtering."
        phi_rad   = lambda ra : ra*np.pi/180.
        theta_rad = lambda dec: (90.0 - dec)*np.pi/180.
        pixs = hp.ang2pix(st.Nside, theta_rad(drq['DEC']), phi_rad(drq['RA']))
        # find unique pixels
        uniqpix=set(pixs)
        outlist=[]
        for pix in uniqpix:
            # first find which one belong to this pixel
            w=np.where(pixs==pix)
            tids=drq['THING_ID'][w] ## these are my thing ids
            mjd=drq['MJD'][w]
            plate=drq['PLATE'][w]
            fiber=drq['FIBERID'][w]
            ## now find unique tids
            uniqtids=set(tids)
            # so now make triplets sorted by thing id.
            pixlist=[]
            for ctid in uniqtids:
                obslist=[]
                cw=np.where(tids==ctid)
                for p,m,f in zip(plate[cw], mjd[cw], fiber[cw]):
                    obslist.append((p,m,f))
                pixlist.append((ctid,obslist))
            outlist.append((pix,pixlist))
    if st.useMPI:
        cchunk=st.comm.scatter(outlist,root=0) ## make sure this is the right thing
    else:
        cchunk=outlist
    return cchunk
    

def processPixel(pixel, pixlist):
    print "processing pixel", pixel
    Nq=len(pixlist)
    loga=np.arange(st.logl_min, st.logl_max, st.logl_step)
    Np=len(loga)
    ## now collect all data
    Fl=np.zeros((Np,Nq),dtype='f4')
    Iv=np.zeros((Np,Nq),dtype='f4')
    Am=np.zeros((Np,Nq),dtype='i4')
    Om=np.zeros((Np,Nq),dtype='i4')
    ii=0
    for tid, subl in pixlist:
        fl=np.zeros(Np,dtype='f4')
        iv=np.zeros(Np,dtype='f4')
        am=np.zeros(Np,dtype='i4')
        om=np.zeros(Np,dtype='i4')
        for tc,trip in enumerate(subl):
            print trip
            ar=read_spframe(st.spPlate_dir,trip)
            ndx=np.array([int(v) for v in ((ar['loglam']-st.logl_min)/st.logl_step+0.5)])
            fl[ndx]+=ar['flux']*ar['ivar']
            iv[ndx]+=ar['ivar']
            if tc==0:
                am[ndx]=ar['andmask']
            else:
                am[ndx]=(am[ndx]&ar['andmask'])
            om[ndx]=(om[ndx]|ar['ormask'])
        ndx=np.where(iv>0)
        fl[ndx]/=iv[ndx]
        Fl[:,ii]=fl
        Iv[:,ii]=iv
        Am[:,ii]=am
        Om[:,ii]=om
        ii+=1
    ## now just save the bloody thing
    file_name = os.path.join(st.pix_dir, 'pix_%i.fits'%(pixel))
    fits = fitsio.FITS(file_name, 'rw', clobber=True)
    ## first thingids
    tids=np.array([p[0] for p in pixlist])# ,dtype=[('THING_ID','i4')])
    fits.write(tids, header={},
               extname="THING_ID_MAP")
    lams=np.array(loga)#, dtype=[('LOGLAM','f4')])
    fits.write(lams,header={}, extname="LOGLAM_MAP")
    fits.write(Fl, header={}, extname="FLUX")
    fits.write(Iv, header={}, extname="IVAR")
    fits.write(Am, header={}, extname="ANDMASK")
    fits.write(Om, header={}, extname="ORMASK")
