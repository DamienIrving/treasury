"""Command line program for converting from netCDF to csv with spatial aggregation"""

import argparse

import numpy as np
import xarray as xr
import geopandas as gp
import regionmask
import xesmf as xe


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


def add_cities(da, df):
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
        city_series.index = city_series.index.year
        city_series = city_series.round(decimals=2)
        city_series.name = city
        df[city] = city_series

    return df


def main(args):
    """Run the program."""

    regions = get_regions()
    ds = xr.open_dataset(args.infile, decode_timedelta=False)
    frac = regions.mask_3D_frac_approx(ds)
    if args.mask_arid:
        frac = mask_arid(frac)
    weights = np.cos(np.deg2rad(ds['lat']))

    spatial_means = ds[args.var].weighted(frac * weights).mean(dim=("lat", "lon"))
    df = spatial_means.to_pandas()
    df.columns = spatial_means['abbrevs']
    if args.var == 'SPEI':
        index = df.index.strftime('%Y-%m')
    else:
        index = df.index.year
    df.index = index
    df = df.round(decimals=2)

    if args.cities:
        df = add_cities(ds[args.var], df, index)

    df.to_csv(args.outfile)


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
