"""Take a dataset and produce a chunked zarr collection."""

import os
import argparse
import logging

import xarray as xr
from rechunker import rechunk
import dask.diagnostics
import zarr
import cmdline_provenance as cmdprov


dask.diagnostics.ProgressBar().register()
logging.basicConfig(level=logging.INFO)


def define_target_chunks(ds, var):
    """Create a target chunks dictionary."""

    chunks = {'time': len(ds['time']), 'lat': 1, 'lon': 1}
    target_chunks_dict = {var: chunks}
    variables = list(ds.keys())
    variables.remove(var)
    coords = list(ds.coords.keys())
    for name in coords + variables:
        target_chunks_dict[name] = None

    return target_chunks_dict


def drop_vars(ds):
    """Drop unwanted variables"""

    for var in ['height', 'lat_bnds', 'lon_bnds']:
        try:
            ds = ds.drop_vars(var)
        except ValueError:
            pass

    return ds


def main(args):
    """Run the command line program."""

    assert not os.path.isdir(args.output_zarr), f"Output Zarr collection already exists: {args.output_zarr}"
    ds = xr.open_mfdataset(args.infiles, preprocess=drop_vars)
    coords = list(ds.coords)
    chunks = ds[args.var].encoding['chunksizes']
    input_chunks = {}
    for coord, chunk in zip(coords, chunks):
        input_chunks[coord] = chunk
    ds = ds.chunk(input_chunks)
    ds.attrs['history'] = cmdprov.new_log(
        infile_logs={args.infiles[0]: ds.attrs['history']}
    )
    for var in ds.variables:
        ds[var].encoding = {}
    target_chunks_dict = define_target_chunks(ds, args.var)
    group_plan = rechunk(
        ds,
        target_chunks_dict,
        args.max_mem,
        args.output_zarr,
        temp_store=args.temp_zarr
    )
    group_plan.execute()
    zarr.consolidate_metadata(args.output_zarr)

    clean_up_command = f'rm -r {args.temp_zarr}'
    logging.info(clean_up_command)
    os.system(clean_up_command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)        
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("output_zarr", type=str, help="Path to output chunked zarr collection")
    parser.add_argument("temp_zarr", type=str, help="Temporary zarr collection")
    parser.add_argument("--max_mem", type=str, default='5GB', help="Maximum memory that workers can use")
    args = parser.parse_args()
    main(args)
    
