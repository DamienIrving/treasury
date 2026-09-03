"""Command line program for calculating likelihoods"""

import argparse

import numpy as np
import pandas as pd
import cmdline_provenance as cmdprov


def prep_data(df):
    """Prepare data for percentile and likelihood calculations."""

    ref_start = 1950
    ref_end = 2014
    if args.metric == 'SPEI':
        df = df.drop(['month', 'model', 'experiment'], axis=1).groupby(['year', 'run']).mean().reset_index()
    else:
        df = df.drop(['model', 'experiment'], axis=1) 
    df_ref = df[(df['year'] >= ref_start) & (df['year'] <= ref_end)]
    df_data = df.drop(['year', 'run'], axis=1)
    df_ref_data = df_ref.drop(['year', 'run'], axis=1)

    return df_data, df_ref_data


def main(args):
    """Run the program."""

    df = pd.read_csv(args.infile)
    df_data, df_ref_data = prep_data(df)
    nruns = len(df['run'].unique())
    window = nruns * 20
    model = df['model'].unique()[0]
    experiment = df['experiment'].unique()[-1]
    runs = ' '.join(list(df['run'].unique()))
    history = cmdprov.new_log()
    metric_label = args.metric.lower()
    locations = 'aus-states-cities' if args.metric in ['WSDI', 'Rx1day', 'Rx5day'] else 'aus-states'

    if args.metric == "SPEI":
        quantiles = np.array([0.01, 0.02, 0.025, 0.03, 0.033, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1])
    else:
        quantiles = np.array([0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.967, 0.97, 0.975, 0.98, 0.99])
    thresholds = df_ref_data.quantile(quantiles)

    # write out likelihoods
    for quantile in quantiles:
        percentile = round(quantile * 100, 1)
        plabel = str(percentile).zfill(4).replace('.', '-')
        if quantile > 0.5:
            df_threshold_test = df_data > thresholds.loc[quantile]
        else:
            df_threshold_test = df_data < thresholds.loc[quantile]
        odds = df_threshold_test.rolling(window, step=nruns, center=True).apply(lambda s: (sum(s) / window) * 100)
        odds.index = df['year'].unique()
        odds = odds.dropna()
        odds.index.name = 'year'
        odds = odds.round(decimals=1)
        start_year = odds.index[0]
        end_year = odds.index[-1]

        pre_header_lines = [
            f"Metric: {args.metric}",
            f"Threshold: {percentile} percentile over the 1950-2014 period",
            f"Model: {model}",
            f"Experiment: {experiment}",
            f"Runs: {runs}",
            "Description: Probability (%) of exceeding the threshold calculated empirically across all model runs for a 20-year rolling window centered on each year",
            f"File history: {history}"
        ]
        outfile = f"{args.outdir}/{metric_label}_yr_{plabel}p-likelihood_{model}_{experiment}_{locations}_{start_year}-{end_year}.csv"
        with open(outfile, mode='w') as f:
            for line in pre_header_lines:
                f.write(line + '\n')
            odds.to_csv(f, mode='a', header=True, index=True)

    # write out thresholds
    thresholds.index = (thresholds.index * 100).round(decimals=1)
    thresholds.index.name = 'percentile'
    thresholds = thresholds.round(decimals=2)
    pre_header_lines = [
        f"Metric: {args.metric}",
        f"Threshold: Percentiles over the 1950-2014 period",
        f"Model: {model}",
        f"Experiment: {experiment}",
        f"Runs: {runs}",
        f"File history: {history}"
    ]
    outfile = f"{args.outdir}/{metric_label}_yr_percentiles_{model}_{experiment}_{locations}_1950-2014.csv"
    with open(outfile, mode='w') as f:
        for line in pre_header_lines:
            f.write(line + '\n')
        thresholds.to_csv(f, mode='a', header=True, index=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("infile", type=str, help="input csv file name (i.e. for a given model and experiment)")
    parser.add_argument("metric", type=str, choices=('WSDI', 'SPEI', 'FFDIx', 'FFDIgt99p', 'Rx1day', 'Rx5day'), help="input metric")
    parser.add_argument("outdir", type=str, help="output directory")
    args = parser.parse_args()
    main(args)
