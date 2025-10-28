"""Command line program for calculating the Forest Fire Danger Index (FFDI)"""
import pdb
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
    ntime = len(kbdi_ds['KBDI'].time)
    nlat = len(kbdi_ds['KBDI'].lat)
    nlon = len(kbdi_ds['KBDI'].lon)
    kbdi_ds = kbdi_ds.chunk({'time': ntime, 'lat': nlat, 'lon': nlon})
    pr_ds = xr.open_dataset(args.pr_zarr, engine='zarr')
    pr_ds['pr'] = xc.core.units.convert_units_to(pr_ds['pr'], 'mm/day')
    df_da = xc.indices.griffiths_drought_factor(pr_ds['pr'], kbdi_ds['KBDI'])

    # FFDI
    tasmax_ds = xr.open_dataset(args.tasmax_zarr, engine='zarr')
    #tasmax_ds['tasmax'] = xc.core.units.convert_units_to(tasmax_ds['tasmax'], 'degC')
    hursmin_ds = xr.open_dataset(args.hursmin_zarr, engine='zarr')
    sfcWindmax_ds = xr.open_dataset(args.sfcWindmax_zarr, engine='zarr')
    ffdi_da = xc.indices.mcarthur_forest_fire_danger_index(
        df_da,
        tasmax_ds['tasmax'],
        hursmin_ds['hursmin'],
        sfcWindmax_ds['sfcWindmax']
    )
    ffdi_ds = ffdi_da.to_dataset(name='FFDI')
    ffdi_ds = fix_metadata(ffdi_ds, tasmax_ds)
#    ffdi_ds.to_netcdf(args.outfile)

    # Metrics
    FFDIx_da = ffdi_ds['FFDI'].resample({'time': 'YE'}).max('time', keep_attrs=True)
    FFDIx_ds = FFDIx_da.to_dataset(name='FFDIx')
    FFDIx_ds.to_netcdf(args.FFDIx_outfile)

    FFDI99p_da = ffdi_ds['FFDI'].sel(time=slice('1950-01-01', '2014-12-31')).quantile(0.99, dim='time')
    FFDIgt99p_da = ffdi_ds['FFDI'] > FFDI99p_da
    FFDIgt99p_da = FFDIgt99p.resample({'time': 'YE'}).sum('time', keep_attrs=True)
    FFDIgt99p_ds = FFDIgt99p_da.to_dataset(name='FFDIgt99p')
    FFDIgt99p_ds.to_netcdf(args.FFDIgt99p_outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("FFDIx_outfile", type=str, help="FFDIx output file name")
    parser.add_argument("FFDIgt99p_outfile", type=str, help="FFDIgt99p output file name")
    parser.add_argument("--pr_zarr", type=str, help="input daily precipitation zarr collection")
    parser.add_argument("--tasmax_zarr", type=str, help="input daily maximum temperature zarr collection")
    parser.add_argument("--hursmin_zarr", type=str, help="input daily minimum relative humidity zarr collection")
    parser.add_argument("--sfcWindmax_zarr", type=str, help="input daily maximum surface wind speed zarr collection")
    parser.add_argument("--kbdi_files", type=str, nargs='*', help="input daily Keetch-Byram Drought Index files")
    args = parser.parse_args()
    main(args)
