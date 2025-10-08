"""Command line program for calculating the Standardised Precipitation Evaporation Index (SPEI)"""
import pdb
import argparse

import numpy as np
import xarray as xr
import xclim as xc
import dask.diagnostics
import cmdline_provenance as cmdprov
    

dask.diagnostics.ProgressBar().register()


def main(args):
    """Run the program."""

    pr_ds = xr.open_mfdataset(args.pr_files)
    evspsblpot_ds = xr.open_mfdataset(args.evspsblpot_files)
    
    wb = pr_ds['pr'] - evspsblpot_ds['evspsblpot']
    wb.attrs['units'] = pr_ds['pr'].attrs['units']

    spei_da = xc.indices.standardized_precipitation_evapotranspiration_index(
        wb, freq='MS', window=12, cal_start='1950-01-01', cal_end='2014-12-31', dist=args.dist,
    )   

    spei_ds = spei_da.to_dataset(name='SPEI')
    spei_ds.attrs = pr_ds.attrs
    spei_ds.attrs['history'] = cmdprov.new_log()
    spei_ds.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("outfile", type=str, help="output file name")
    parser.add_argument("--pr_files", type=str, nargs='*', help="input daily precipitation files")
    parser.add_argument("--evspsblpot_files", type=str, nargs='*', help="input daily potential evapotranspiration files")
    parser.add_argument("--dist", type=str, choices=('gamma', 'fisk'), default='fisk', help="distribution for SPEI calculation")

    args = parser.parse_args()
    main(args)
