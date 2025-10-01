"""Command line program for calculating the annual precipitation climatology"""

import argparse

import numpy as np
import xarray as xr
import xclim as xc
import dask.diagnostics
import cmdline_provenance as cmdprov
    

dask.diagnostics.ProgressBar().register()


def main(args):
    """Run the program."""

    ds = xr.open_mfdataset(args.infiles)
    ds['pr'] = xc.core.units.convert_units_to(ds['pr'], 'mm/day')
    ds = ds.sel(time=slice(args.start_date, args.end_date))
    ds_annual = ds.resample(time='YE').sum('time').mean('time')
    ds_annual['pr'].attrs['units'] = 'mm/year'
    ds_annual['pr'].attrs['long_name'] = 'Precipitation'
    ds_annual['pr'].attrs['standard_name'] = 'precipitation_flux'
    ds_annual.attrs = ds.attrs
    ds_annual.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("infiles", type=str, nargs='*', help="input daily precipitation files")
    parser.add_argument("start_date", type=str, help="start date in YYYY-MM-DD format")
    parser.add_argument("end_date", type=str, help="end date in YYYY-MM-DD format")
    parser.add_argument("outfile", type=str, help="output file name")
    args = parser.parse_args()
    main(args)
