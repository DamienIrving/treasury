## Data for Reserve Bank modelling

To generate the data submit a job:

```
qsub -v metric=wsdi,model=MPI-ESM1-2-LR,ssp=ssp370,run=r25i1p1f1,grid=gn,version='v*' cmip6.job
```

The csv files from numerous runs can then be merged using `concat_csv.py`.

Don't forget to clean up afterwards (i.e. delete all files except the final csv files):

```
bash wsdi_cmip6.sh MPI-ESM1-2-LR ssp370 r25i1p1f1 gn 'v*' -c 
```

(The data generation and clean up steps can be achived by running `run.sh`.)

The ensemble of runs used for the WSDI and SPEI
are all models that archived daily data for at least five common runs
across ssp126, ssp245, ssp370 and ssp585:
- EC-Earth3 (57 runs)
- CanESM (50)
- ACCESS-ESM1-5 (40)
- MPI-ESM1-2-LR (13)
- ACCESS-CM2 (10)
- IPSL-CM6A-LR (6)
- UK-ESM1-0-LL (5)
- EC-Earth3-Veg (5)

The ensemble of runs used for FFDI are any/any models that
archived the required daily variables (pr, tasmax, hursmin, sfcWindmax):
- ACCESS-ESM1-5 (40)
- EC-Earth-Veg (2)
- EC-Earth3 (1)
- CNRM-ESM2-1 (1)
- CMCC-ESM2 (1)


