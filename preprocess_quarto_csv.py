import argparse
import os
import pandas


def process_quarto():
    NUM_CSV = 1295
    FSQ_COL = 'Formal System Query'
    NLQ_COL = 'NL System Query'
    CSV_DIR = 'quarto' + os.path.sep + 'csv' + os.path.sep
    MR_OUT = 'quarto_queries_mr.csv'
    REF_OUT = 'quarto_queries_ref.csv'
    BOTH_OUT = 'quarto_queries_collection.csv'
    OUT_DIR = 'quarto' + os.path.sep

    # If the files exists, then delete them and rebuild them (small enough that we can do that)
    if os.path.isfile(OUT_DIR + MR_OUT):
        os.remove(OUT_DIR + MR_OUT)
    if os.path.isfile(OUT_DIR + REF_OUT):
        os.remove(OUT_DIR + REF_OUT)
    if os.path.isfile(OUT_DIR + BOTH_OUT):
        os.remove(OUT_DIR + BOTH_OUT)

    for i in range(1, NUM_CSV + 1):
        file_name = CSV_DIR + f'Quarto_dialog{i}.csv'
        try:
            data = pandas.read_csv(file_name)
            queries_both = data[[FSQ_COL, NLQ_COL]]
            queries_mr = data[[FSQ_COL]]
            queries_ref = data[[NLQ_COL]]

            queries_both.rename(columns={NLQ_COL: 'ref', FSQ_COL: 'mr'})
            queries_ref.rename(columns={NLQ_COL: 'ref'})
            queries_ref.rename(columns={FSQ_COL: 'mr'})

            queries_both.to_csv(OUT_DIR + BOTH_OUT,
                                mode='a',
                                index=False,
                                header=False)
            queries_ref.to_csv(OUT_DIR + REF_OUT,
                               mode='a',
                               index=False,
                               header=False)
            queries_mr.to_csv(OUT_DIR + MR_OUT,
                              mode='a',
                              index=False,
                              header=False)
        except FileNotFoundError:
            print(f"File not found {file_name}")


if __name__ == '__main__':
    process_quarto()
