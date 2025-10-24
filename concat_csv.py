"""Command line program for concatenating CSV files"""

import argparse

import pandas as pd


def main(args):
    """Run the program."""

    df_list = []   
    for infile in args.infiles:
        df = pd.read_csv(infile)
        df_list.append(df)
    df = pd.concat(df_list, ignore_index=True)
    df = df.sort_values(by=[df.columns[0], 'run'], ignore_index=True)
    df.to_csv(args.outfile, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("infiles", type=str, nargs='*', help="input CSV files")
    parser.add_argument("outfile", type=str, help="output file name")
    args = parser.parse_args()
    main(args)
