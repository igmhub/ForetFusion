#
# main driver
#

import settings as st
import io
import numpy as np
import os, fitsio
import healpy as hp


# we let drive initialize MPI everything else we do here
def automatic ():
    ltodo = loadDRQandPixelize()
    if (st.useMultiprocessing):
        import multiprocessing
        pool=multiprocessing.Pool(processes=st.useMultiprocessing)
        pool.map(processPixel, ltodo)
    else:
        for i,pixinfo in enumerate(ltodo):
            if (i%st.size==st.rank):
                processPixel(pixinfo)
    
def loadDRQandPixelize():
    spall_cols  = ['RA','DEC','THING_ID','MJD','PLATE','FIBERID','Z']
    if st.rank == 0:
        drq = io.read_fits(st.DRQ, spall_cols, st.maxNobj)
        ## first filter for quasars
        #w=np.where(drq['CLASS']=="QSO" & (drq['OBJTYPE']=='QSO' | drq['OBJTYPE']=='QSO') & drq['THING_ID']!=-1)
        w=np.where(drq['THING_ID']>0) #note we have both 0s and -1s
        drq=drq[w]
        print "We have ",len(drq)," quasars after filtering."
        w=np.where((drq['Z']>st.min_z) & (drq['Z']<st.max_z))
        drq=drq[w]
        print "we have", len(drq)," quasars after z filtering."
        phi_rad   = lambda ra : ra*np.pi/180.
        theta_rad = lambda dec: (90.0 - dec)*np.pi/180.
        pixs = hp.ang2pix(st.Nside, theta_rad(drq['DEC']), phi_rad(drq['RA']))
        # find unique pixels
        uniqpix=set(pixs)
        print "We have ",len(uniqpix),"unique pixels."
        print "We have ",len(drq), "observations with ", len(set(drq['THING_ID'])), " unique thing ids."
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
        saveMasterFile (outlist)
    else:
        outlist=[]
    if (st.useMPI):
        outlist=st.comm.broadcast(outlist, root=0)
    return outlist

def saveMasterFile (outlist):
    outl=[]
    for pix, pixlist in outlist:
        for tid,trips in pixlist:
            for p,m,f in trips:
                outl.append((tid,pix,p,m,f))
    outl=np.array(outl, dtype=[('THING_ID','i4'), ('PIX','i4'),('PLATE','i4'), ('MJD','i4'),('FIBER','i4')])
    file_name = os.path.join(st.rootdir, 'master.fits')
    fits = fitsio.FITS(file_name, 'rw', clobber=True)
    fits.write(outl, header={"NSIDE":st.Nside},
               extname="MASTER TABLE")
    fits.close()
    
def processPixel(pixinfo):
    pixel, pixlist=pixinfo
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
            try:
                if st.use_spec:
                    lar=[io.read_spec(st.spPlate_dir,trip,mock=st.mock)]
                elif st.use_spCFrame:
                    lar=[io.read_spcframe(st.spPlate_dir,trip)]
                else:
                    lar=[io.read_spplate(st.spPlate_dir,trip)]
            except:
                continue
            for ar in lar:
                ndx=np.array([int(v) for v in ((ar['loglam']-st.logl_min)/st.logl_step+0.5)])
                wf=np.where((ndx>=0) & (ndx<len(fl)))
                ndx=ndx[wf]
                ar=ar[wf]
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
    fits.close()
