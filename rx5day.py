"""Command line program for calculating the annual maximum 5-day precipitation (Rx5day)"""

import argparse

import numpy as np
import xarray as xr
import xclim as xc
import dask.diagnostics
import cmdline_provenance as cmdprov
    

dask.diagnostics.ProgressBar().register()


def main(args):
    """Run the program."""

    pr_file1 = args.pr_files[0]
    if 'zarr' in pr_file1:
        pr_ds = xr.open_dataset(args.pr_files[0], engine='zarr')
    else:
        pr_ds = xr.open_mfdataset(args.pr_files, attrs_file=args.pr_files[-1])

    if args.ausclip:
        pr_ds = pr_ds.sel({'lat': slice(-44.5, -10), 'lon': slice(112, 156.25)})

    pr_ds = pr_ds.compute()
    pr_ds['pr'] = xc.core.units.convert_units_to(pr_ds['pr'], 'mm/day')

    rx5day_da = xc.indices.max_n_day_precipitation_amount(pr_ds['pr'], window=5, freq='YS')   

    rx5day_ds = rx5day_da.to_dataset(name='Rx5day')
    rx5day_ds.attrs = pr_ds.attrs
    rx5day_ds.attrs['history'] = cmdprov.new_log()
    rx5day_ds.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("outfile", type=str, help="output file name")
    parser.add_argument("pr_files", type=str, nargs='*', help="input daily precipitation files")
    parser.add_argument("--ausclip", action="store_true", default=False, help="Clip lat and lon bounds to Australia")
    args = parser.parse_args()
    main(args)
