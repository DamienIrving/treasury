"""Command line program for calculating potential evapotranspiration (evspsblpot)"""
import pdb
import argparse

import numpy as np
import xarray as xr
import xclim as xc
import dask.diagnostics
import cmdline_provenance as cmdprov
    

dask.diagnostics.ProgressBar().register()


def fix_metadata(ds, input_ds):
    """Fix evspsblpot metadata"""

    try:
        ds = ds.drop_vars(['height',])
    except:
        pass

    ds.attrs = input_ds.attrs
    ds['lat'].attrs = input_ds['lat'].attrs
    ds['lon'].attrs = input_ds['lon'].attrs
    #ds['time'].attrs = input_ds['time'].attrs
    ds['evspsblpot'].attrs['long_name'] = 'Potential Evapotranspiration'
    ds['evspsblpot'].attrs['standard_name'] = 'water_potential_evaporation_flux'

    ds.attrs['variable_id'] = 'evspsblpot'
    ds.attrs['history'] = cmdprov.new_log()

    return ds


def main(args):
    """Run the program."""

    tasmax_ds = xr.open_mfdataset(args.tasmax_file)
    tasmin_ds = xr.open_mfdataset(args.tasmin_file)
    
    evspsblpot_da = xc.indices.potential_evapotranspiration(
        tasmin=tasmin_ds['tasmin'],
        tasmax=tasmax_ds['tasmax'],
        method='HG85',
    )

    evspsblpot_ds = evspsblpot_da.to_dataset(name='evspsblpot')
    evspsblpot_ds = fix_metadata(evspsblpot_ds, tasmin_ds)
    evspsblpot_ds.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("tasmin_file", type=str, help="input daily minimum temperature files")
    parser.add_argument("tasmax_file", type=str, help="input daily maximum temperature files")
    parser.add_argument("outfile", type=str, help="output file name")
    args = parser.parse_args()
    main(args)
