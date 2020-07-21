

from tabulate import tabulate
import imp
import pandas as pd
import argparse

def make_table(metadata, recall_file):

    parse = imp.load_source('parse_data', 'utils/parse_data.py')

    lin_obj_dict = parse.make_objects(metadata)[0]

    lin_obj_dict = parse.get_recall_value(lin_obj_dict, recall_file)

    df = parse.make_dataframe(lin_obj_dict)

    df.to_csv("summary_files/lineage_summary.tsv", sep="\t")

def main():
    
    parser = argparse.ArgumentParser(description="Table generator script")

    parser.add_argument("-m","--metadata", required=True, help="metadata", dest = "metadata")
    parser.add_argument("-r", "--recall-file", required=True, help="recall file", dest="recall")

    args = parser.parse_args()

    make_table(args.metadata, args.recall)

if __name__ == "__main__":
    main()

