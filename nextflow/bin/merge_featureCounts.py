#!/usr/bin/env python

import argparse
import glob

import pandas as pd


def parsearg_utils():
    """

    Argparser to collect featureCounts.txt files.

    Returns
    -------
    args: argparse.Namespace
        Namespace object containing featureCounts files

    """
    parser = argparse.ArgumentParser(description="Parser for merge_featureCounts.py.")

    parser.add_argument(
        "-f",
        "--featureCounts",
        help="Path to featureCount *.txt files",
        nargs="+",
    )

    parser.add_argument(
        "-p",
        "--prefixFile",
        help="Path to featureCount *.txt files",
        type=str,
    )

    args = parser.parse_args()

    return args


def convert_files2list(
    featureCounts: list[str],
):
    """

    Convert featureCounts files to a list.

    Parameters
    ----------
    featureCounts: list
        List of featureCounts files to merge

    """
    list_files = []
    for file in featureCounts:
        if glob.escape(file) != file:
            list_files.extend(glob.glob(file))
        else:
            list_files.append(file)
    return list_files


# https://github.com/reneshbedre/bioinfokit/blob/master/bioinfokit/analys.py
def merge_featureCounts(
    list_files: list[str],
    prefix: str,
    gene_column_name: str = "Geneid",
):
    """

    Merge multiple featureCounts outputs into a single CSV.

    Parameters
    ----------
    list_files: list[str]
        List of featureCounts files to merge
    prefix: str
        Prefix for the output file
    gene_column_name: str
        Column name to merge on; default is "Geneid"

    """
    iter = 0
    for f in list_files:
        df = pd.read_csv(f, sep="\t", comment="#")
        if iter == 0:
            df_count_mat = df.iloc[:, [0, 6]]
            iter += 1
        elif iter > 0:
            df_temp = df.iloc[:, [0, 6]]
            df_count_mat = pd.merge(df_count_mat, df_temp, how="left", on=gene_column_name)
    df_count_mat.to_csv(f"{prefix}_featureCounts.csv", index=False)


def main():
    """Main function to merge featureCounts files."""
    arguments = parsearg_utils()
    file_list = convert_files2list(arguments.featureCounts)
    merge_featureCounts(file_list, arguments.prefixFile)


if __name__ == "__main__":
    main()
