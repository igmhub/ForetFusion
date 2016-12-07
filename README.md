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

Then the driver should be run as

```
mpirun -np 4 ./exec/ff_driver.py
```


