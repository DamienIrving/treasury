"""Command line program for calculating the Warm Spell Duration Index (WSDI)"""

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
    ds['tasmax'] = xc.core.units.convert_units_to(ds['tasmax'], 'degC')
    
    tx90 = xc.core.calendar.percentile_doy(
        ds['tasmax'].sel(time=slice('1950-01-01', '2014-12-31')),
        window=5,
        per=90
    )
    tx90 = tx90.compute()
    tx90 = tx90.sel(percentiles=90)

    wsdi_da = xc.indicators.icclim.WSDI(
        tasmax=ds['tasmax'],
        tasmax_per=tx90,
        freq='YS',
    )

    wsdi_ds = wsdi_da.to_dataset()
    wsdi_ds.attrs = ds.attrs
    wsdi_ds.attrs['history'] = cmdprov.new_log()
    wsdi_ds.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )     
    parser.add_argument("infiles", type=str, nargs='*', help="input tasmax files")
    parser.add_argument("outfile", type=str, help="output file name")
    args = parser.parse_args()
    main(args)
