#!/usr/bin/env python
import os
from os.path import join
from glob import glob
from pbs import queue
import argparse
import sys
from os.path import abspath


if __name__=="__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--spplate-dir",type=str,required=False,
                        default="/uufs/chpc.utah.edu/common/home/sdss02/ebosswork/"+
                        "eboss/spectro/redux/v5_10_0/",help="plates")
    parser.add_argument("--drq",type=str,required=False, 
                        default="/uufs/chpc.utah.edu/common/home/sdss00/ebosswork/eboss/"+
                        "sandbox/qso/QSOcatalog/DR14Q/DR14Q_v2_0.fits",help="plates")
    parser.add_argument("--mock",action="store_true",required=False,help="plates")
    parser.add_argument("--use-spec",action="store_true",required=False,help="plates")
    parser.add_argument("--use-duplicates",action="store_true",required=False,help="plates")
    parser.add_argument("--use-spcframe",action="store_true",required=False,help="plates")
    parser.add_argument("--root",type=str,required=True,help="plates")
    parser.add_argument("--mpi",action="store_true",required=False,help="plates")
    parser.add_argument("--multiprocessing",type=int,required=False,default=0,help="plates")
    parser.add_argument("--nobjs",type=int,default=1000000,required=False,help="plates")
    parser.add_argument("--z-min",type=float,default=0.,required=False,help="plates")
    parser.add_argument("--z-max",type=float,default=6.,required=False,help="plates")

    args = parser.parse_args()

    pars="[Main]\n"
    pars+="MPI={}\nmultiprocessing={}\n".format(args.mpi,args.multiprocessing)

    pars+="[Input]\n"
    pars+="DRQ={}\n".format(abspath(args.drq))
    pars+="spPlate_dir={}\n".format(abspath(args.spplate_dir))
    pars+="mock={}\n".format(args.mock)
    pars+="use_spec={}\n".format(args.use_spec)
    pars+="use_duplicates={}\n".format(args.use_duplicates)
    pars+="use_spCFrame={}\n".format(args.use_spcframe)
    pars+="maxNobj={}\n".format(args.nobjs)
    pars+="min_z={}\n".format(args.z_min)
    pars+="max_z={}\n".format(args.z_max)

    pars+="[Output]\n"
    pars+="root={}\n".format(args.root)
    pars+="pix_dir=%(root)s/\n"

    queue = queue()
    queue.verbose = True
    queue.create(label='foretfusion',nodes=1,walltime='24:00:00')
    queue.client.config.set_job_dir(queue.client.member.username,queue.client.job.label,queue.client.job.key)


    script=os.environ["HOME"]+'/igmhub/ForetFusion/exec/ff_driver.py <( echo "{}")'.format(pars)
    queue.append(script,dir=join(queue.client.config.job_dir,"forefusion"))

    queue.commit(hard=True,submit=True)
