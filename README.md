# ForetFusion
Code to compute coadds for Lya-forest data in BOSS and eBOSS, new gen.

This is a refactoring of the code of the same name, initially put together by Jose Vazquez and Anze Slosar
(here github.com/slosar/ForetFusion and github.com/ja-vazquez/ForetFusion). Due to weight of the previously created repo, this is a freshly created repo.


## Installation

The package comprises of the ffusion module and a driver in `exec/ff_driver.py`

First install the module by running

```
./setup.py install
```

or to leaving things within your own area on e.g. NERSC:

```
./setup.py install --user
```

Then the driver should be run like this, specifying config file

```
./exec/ff_driver.py config/nersc.ini
```

Multiprocessing is supporter either by MPI or by multiprocessing module. See config file.
Config file format should be fairly self-explanatory.

## Output format

Output format is composed of a master fits file and per healpix pixel spectra files.

### master file

is a FITS formatted file in `root/master.fits` with a single table, containing THING_ID, PIX, PLATE, MJD, FIBER. PIX is the healpix pixel (NSIDE in header's NSIDE entry). Data are ordered by PIX, then THING_ID.

### pixel files

are FITS fromatted files in `root/pixs/pix/pix_###.fits`. It contains the following extensions:
 * Extension 0 `THING_ID_MAP` contains a single vector of size Nq for Nq quasars, mapping indices 1..Nq to THING_IDs
 * Extension 1 `LOGLAM_MAP` contains a single vector of size Np for Np pixel, mapping indices 1..Np to log lambda (observed)
 * Extension 2 `FLUX` is a Np rows x Nq columns matrix containing fluxes
 * Extension 3 `IVAR` is a Np rows x Nq columns matrix containing ivars
 * Extension 4 `ANDMASK` is a Np rows x Nq columns matrix containing AND masks
 * Extension 5 `ORMASK` is a Np rows x Nq columns matrix containing OR masks


