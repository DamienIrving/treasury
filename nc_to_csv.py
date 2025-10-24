"""Command line program for converting from netCDF to csv with spatial aggregation"""
import pdb
import argparse

import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gp
import regionmask
import xesmf as xe


def subset_lat(ds, lat_bnds, lat_dim="lat"):
    """Select grid points that fall within latitude bounds.

    Parameters
    ----------
    ds : Union[xarray.DataArray, xarray.Dataset]
        Input data
    lat_bnds : list
        Latitude bounds: [south bound, north bound]
    lat_dim: str, default 'lat'
        Name of the latitude dimension in ds

    Returns
    -------
    Union[xarray.DataArray, xarray.Dataset]
        Subsetted xarray.DataArray or xarray.Dataset
    """

    south_bound, north_bound = lat_bnds
    assert -90 <= south_bound <= 90, "Valid latitude range is [-90, 90]"
    assert -90 <= north_bound <= 90, "Valid latitude range is [-90, 90]"

    selection = (ds[lat_dim] <= north_bound) & (ds[lat_dim] >= south_bound)
    ds = ds.where(selection, drop=True)

    return ds


def subset_lon(ds, lon_bnds, lon_dim="lon"):
    """Select grid points that fall within longitude bounds.

    Parameters
    ----------
    ds : Union[xarray.DataArray, xarray.Dataset]
        Input data
    lon_bnds : list
        Longitude bounds: [west bound, east bound]
    lon_dim: str, default 'lon'
        Name of the longitude dimension in ds

    Returns
    -------
    Union[xarray.DataArray, xarray.Dataset]
        Subsetted xarray.DataArray or xarray.Dataset
    """

    west_bound, east_bound = lon_bnds
    assert west_bound >= ds[lon_dim].values.min()
    assert west_bound <= ds[lon_dim].values.max()
    assert east_bound >= ds[lon_dim].values.min()
    assert east_bound <= ds[lon_dim].values.max()

    if east_bound > west_bound:
        selection = (ds[lon_dim] <= east_bound) & (ds[lon_dim] >= west_bound)
    else:
        selection = (ds[lon_dim] <= east_bound) | (ds[lon_dim] >= west_bound)
    ds = ds.where(selection, drop=True)

    return ds


def xesmf_regrid(ds, ds_grid, variable):
    """Regrid data using xesmf.
    
    Parameters
    ----------
    ds : xarray Dataset
        Dataset to be regridded
    ds_grid : xarray Dataset
        Dataset containing target horizontal grid
    variable : str
        Variable to restore attributes for
    
    Returns
    -------
    ds : xarray Dataset
    
    """
    
    global_attrs = ds.attrs
    var_attrs = ds[variable].attrs
    regridder = xe.Regridder(ds, ds_grid, 'nearest_s2d')
    ds = regridder(ds)
    ds.attrs = global_attrs
    ds[variable].attrs = var_attrs

    return ds


def get_regions():
    """Define the regions of interest."""

    states_gp = gp.read_file('/g/data/ia39/aus-ref-clim-data-nci/shapefiles/data/aus_states_territories/aus_states_territories.shp')
    states_gp = states_gp.drop(columns=['AREASQKM21', 'LOCI_URI21'])
    states_gp = states_gp[:-2]  # remove ACT and other territories
   
    aus_gp = states_gp.dissolve()
    aus_gp['STE_NAME21'] = 'Australia'
    aus_gp['ABBREV'] = 'AUS'

    regions_gp = pd.concat([states_gp, aus_gp], ignore_index=True)

    regions_rm = regionmask.from_geopandas(
        regions_gp,
        names="STE_NAME21",
        abbrevs="ABBREV",
        name="states",
    )

    return regions_rm


def mask_arid(frac):
    """Mask arid areas."""

    ds_koppen_1p0 = xr.open_dataset('/g/data/xv83/dbi599/treasury/koppen/koppen_geiger_1p0_1991-2020.nc')
    ds_koppen = xesmf_regrid(ds_koppen_1p0, frac, variable='kg_class')
    ds_koppen = ds_koppen.compute()
    arid = (ds_koppen['kg_class'] > 3.5) & (ds_koppen['kg_class'] < 7.5)
    frac_masked = ~arid * frac    

    return frac_masked


def add_cities(da, df, index):
    """Add city values to a dataframe"""

    city_coords = {
        'Melbourne': (-37.81, 144.96),
        'Sydney': (-33.87, 151.21),
        'Brisbane': (-27.47, 153.03),
        'Darwin': (-12.44, 130.84),
        'Perth': (-31.95, 115.86),
        'Adelaide': (-34.93, 138.60),
        'Hobart': (-42.88, 147.33)
    }

    for city, coords in city_coords.items():
        lat, lon = coords
        city_da = da.sel({'lat': lat, 'lon': lon}, method='nearest')
        city_series = city_da.to_pandas()
        city_series.index = index
        city_series = city_series.round(decimals=2)
        city_series.name = city
        df[city] = city_series

    return df


def model_fixes(ds):
    """Model specific fixes to input data."""

    model = ds.attrs['source_id']
    if model == 'CanESM5':
        ds = subset_lat(ds, [-48, -5])
        ds = subset_lon(ds, [105, 160])
        ds['lat'] = np.round(ds['lat'], 2)

    return ds


def main(args):
    """Run the program."""

    regions = get_regions()
    ds = xr.open_dataset(args.infile, decode_timedelta=False)
    ds = model_fixes(ds)

    frac = regions.mask_3D_frac_approx(ds)
    if args.mask_arid:
        frac = mask_arid(frac)
    weights = np.cos(np.deg2rad(ds['lat']))

    spatial_means = ds[args.var].weighted(frac * weights).mean(dim=("lat", "lon"))
    df = spatial_means.to_pandas()
    df.columns = spatial_means['abbrevs']
    if args.var == 'SPEI':
        index = df.index.strftime('%Y-%m')
        index_label = 'year-month'
    else:
        index = df.index.year
        index_label = 'year'
    df.index = index
    df = df.round(decimals=2)
    if args.add_cities:
        df = add_cities(ds[args.var], df, index)
    
    df.insert(loc=0, column='experiment', value=np.where(df.index > 2014, ds.attrs['experiment_id'], 'historical'))
    df.insert(loc=0, column='run', value=ds.attrs['variant_label'])
    df.insert(loc=0, column='model', value=ds.attrs['source_id'])
    df.to_csv(args.outfile, index=True, index_label=index_label)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("infile", type=str, help="input file name")
    parser.add_argument("var", type=str, help="input file name")
    parser.add_argument("outfile", type=str, help="output file name")
    parser.add_argument("--mask_arid", action="store_true", default=False, help="mask arid areas")
    parser.add_argument("--add_cities", action="store_true", default=False, help="add cities to the output file")
    args = parser.parse_args()
    main(args)
