"""Command line program for calculating the Forest Fire Danger Index (FFDI)"""

import argparse

import numpy as np
import xarray as xr
import xclim as xc
import dask.diagnostics
import cmdline_provenance as cmdprov
    

dask.diagnostics.ProgressBar().register()


def fix_metadata(ds, input_ds):
    """Fix FFDI metadata"""

    try:
        ds = ds.drop_vars(['height',])
    except:
        pass

    ds.attrs = input_ds.attrs
    ds['lat'].attrs = input_ds['lat'].attrs
    ds['lon'].attrs = input_ds['lon'].attrs
    ds['time'].attrs = input_ds['time'].attrs
    ds['FFDI'].attrs['long_name'] = 'Forest Fire Danger Index'
    ds['FFDI'].attrs['standard_name'] = 'forest_fire_danger_index'

    ds.attrs['variable_id'] = 'FFDI'
    ds.attrs['history'] = cmdprov.new_log()

    return ds


def main(args):
    """Run the program."""

    # Drought Factor
    kbdi_ds = xr.open_mfdataset(args.kbdi_files)
    pr_ds = xr.open_mfdataset(args.pr_files)
    pr_ds['pr'] = xc.core.units.convert_units_to(pr_ds['pr'], 'mm/day')
    df_da = xc.indices.griffiths_drought_factor(pr_ds['pr'], kbdi_ds['kbdi'])

    # FFDI
    tasmax_ds = xr.open_dataset(args.tasmax_files)
    #tasmax_ds['tasmax'] = xc.core.units.convert_units_to(tasmax_ds['tasmax'], 'degC')
    hursmin_ds = xr.open_dataset(args.hursmin_file)
    sfcWindmax_ds = xr.open_dataset(args.sfcWindmax_file)
    ffdi_da = xc.indices.mcarthur_forest_fire_danger_index(
        df_da,
        tasmax_ds['tasmax'],
        hursmin_ds['hursmin'],
        sfcWindmax_ds['sfcWindmax']
    )
    ffdi_ds = ffdi_da.to_dataset(name='FFDI')
    ffdi_ds = fix_metadata(ffdi_ds, tasmax_ds)
    ffdi_ds.to_netcdf(args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("outfile", type=str, help="output file name")
    parser.add_argument("--pr_files", nargs='*', type=str, help="input daily precipitation files")
    parser.add_argument("--tasmax_files", type=str, help="input daily maximum temperature files")
    parser.add_argument("--hursmin_files", type=str, help="input daily minimum relative humidity files")
    parser.add_argument("--sfcWindmax_files", type=str, help="input daily maximum surface wind speed files")
    parser.add_argument("--kbdi_files", type=str, help="input daily Keetch-Byram Drought Index files")
    args = parser.parse_args()
    main(args)
