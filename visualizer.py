import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import math

def sanitize_dataframe(df):
    for column in df.columns[1:]:
        last_known_element = None
        for index, element in enumerate(df[column]):
            if np.isnan(element):
                if last_known_element is not None:
                    df.loc[index, column] = last_known_element
                else:
                    cur_index = index
                    while np.isnan(df.loc[cur_index, column]):
                        cur_index += 1

                    df.loc[index:cur_index, column] = df.loc[cur_index, column]
            else:
                last_known_element = element

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description = 'Summarize csv data to create charts.')
    parser.add_argument('--filepath', type = str, help = 'Filepath to csv.', required = True)
    parser.add_argument('--debug', action = 'store_true', help = 'Debug issues with visusalizer.')
    parser.add_argument('--baseline', help = 'One of [zero, wiggle, weighted_wiggle, sym]')

    args = parser.parse_args()
    df = None
    with open(args.filepath, 'r') as f:
        df = pd.read_csv(f, parse_dates = ['Date'])

    assert df is not None, "Data must be provided for visualization to occur."
    sanitize_dataframe(df)

    #plot data
    fig, ax = plt.subplots(figsize=(15,7))
    fig.autofmt_xdate()
    plt.grid(True)
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, p: '$' + format(int(x / 100), ',')))
    dates = [pd.Timestamp(date).to_pydatetime() for date in df['Date']]
    columns = [[float(element) for element in df[column]] for column in df.columns if column != 'Date']
    baseline = args.baseline # 'zero' 'wiggle' 'weighted_wiggle' 'sym'
    plot = plt.stackplot(dates, *columns, baseline=baseline, labels = [column for column in df.columns if column != 'Date'])
    plt.legend(loc = 'upper left')
    plt.title('Net worth')
    plt.show(plot)