"""Command line program for calculating potential evapotranspiration (evspsblpot)"""

import argparse

import numpy as np
import xarray as xr
import xclim as xc
import dask.diagnostics
import cmdline_provenance as cmdprov
    

dask.diagnostics.ProgressBar().register()


def fix_metadata(ds, input_ds, method):
    """Fix evspsblpot metadata"""

    try:
        ds = ds.drop_vars(['height',])
    except:
        pass

    ds.attrs = input_ds.attrs
    ds['lat'].attrs = input_ds['lat'].attrs
    ds['lon'].attrs = input_ds['lon'].attrs
    ds['time'].attrs = input_ds['time'].attrs
    ds['evspsblpot'].attrs['long_name'] = 'Potential Evapotranspiration'
    ds['evspsblpot'].attrs['standard_name'] = 'water_potential_evaporation_flux'
    ds['evspsblpot'].attrs['method'] = method

    ds.attrs['variable_id'] = 'evspsblpot'
    ds.attrs['history'] = cmdprov.new_log()

    return ds


def main(args):
    """Run the program."""

    tasmax_ds = xr.open_dataset(args.tasmax_file)
    tasmin_ds = xr.open_dataset(args.tasmin_file)

    if args.method == 'hargreaves85':
        evspsblpot_da = xc.indices.potential_evapotranspiration(
            tasmin=tasmin_ds['tasmin'],
            tasmax=tasmax_ds['tasmax'],
            method=args.method,
        )
    elif args.method == 'allen98':
        hurs_ds = xr.open_dataset(args.hurs_file)
        sfcWind_ds = xr.open_dataset(args.sfcWind_file)
        rsds_ds = xr.open_dataset(args.rsds_file)
        rsus_ds = xr.open_dataset(args.rsus_file)
        rlds_ds = xr.open_dataset(args.rlds_file)
        rlus_ds = xr.open_dataset(args.rlus_file)
        evspsblpot_da = xc.indices.potential_evapotranspiration(
            tasmin=tasmin_ds['tasmin'],
            tasmax=tasmax_ds['tasmax'],
            hurs=hurs_ds['hurs'],
            sfcWind=sfcWind_ds['sfcWind'],
            rsds=rsds_ds['rsds'],
            rsus=rsus_ds['rsus'],
            rlds=rlds_ds['rlds'],
            rlus=rlus_ds['rlus'],
            method=args.method,
        )
    else:
        raise ValueError(f'unrecognised method: {method}')

    evspsblpot_ds = evspsblpot_da.to_dataset(name='evspsblpot')
    evspsblpot_ds = fix_metadata(evspsblpot_ds, tasmin_ds, args.method)
    evspsblpot_ds.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("outfile", type=str, help="output file name")
    parser.add_argument("method", type=str, choices=('hargreaves85', 'allen98'), help="method for calculating evspsblpot")
    parser.add_argument("--tasmin_file", type=str, help="input daily minimum temperature file")
    parser.add_argument("--tasmax_file", type=str, help="input daily maximum temperature file")
    parser.add_argument("--hurs_file", type=str, help="input daily relative humidity file")
    parser.add_argument("--sfcWind_file", type=str, help="input daily surface wind speed file")
    parser.add_argument("--rsds_file", type=str, help="input daily surface downwelling shortwave file")
    parser.add_argument("--rsus_file", type=str, help="input daily surface upwelling shortwave file")
    parser.add_argument("--rlds_file", type=str, help="input daily surface downwelling longwave file")
    parser.add_argument("--rlus_file", type=str, help="input daily surface upwelling longwave file")
    args = parser.parse_args()
    main(args)
