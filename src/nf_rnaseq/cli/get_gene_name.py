#!/usr/bin/env python

import argparse

from nf_rnaseq import config, variables


def parsearg_utils():
    """

    Argparser to get HGNC gene name from string input.

    Returns
    -------
    args: argparse.Namespace
        Namespace object containing featureCounts files

    """
    parser = argparse.ArgumentParser(description="Parser for get_hgnc_gene_name.py.")

    parser.add_argument(
        "-c",
        "--cachePath",
        help="Path to requests cache (type: str, default: '')",
        type=str,
        default="",
    )

    parser.add_argument(
        "-d",
        "--database",
        help="Database to use including BioMart, HGNC, and UniProt (type: str, no default)",
        type=str,
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Input string (type: str)",
        type=str,
    )

    parser.add_argument(
        "-t",
        "--tsv",
        help="If flag included tsv format out otherwise csv",
        action="store_true",
    )

    args = parser.parse_args()

    return args


def main():
    """Get HGNC gene name from string input."""
    args = parsearg_utils()
    inputs_ids = args.input.replace("[", "").replace("]", "")

    if args.cachePath != "":
        config.set_request_cache(args.cachePath)

    DICT_DATABASES = variables.DICT_DATABASES
    try:
        if "POST" in DICT_DATABASES[args.database].keys():
            dict_post = DICT_DATABASES[args.database]["POST"]
            post_obj = dict_post["api_object"](
                identifier=inputs_ids,
                term_in=dict_post["term_in"],
                term_out=dict_post["term_out"],
                url_base=dict_post["url_base"],
            )
            dict_get = DICT_DATABASES[args.database]["GET"]
            api_obj = dict_get["api_object"](
                identifier=inputs_ids,
                term_in=dict_get["term_in"],
                term_out=dict_get["term_out"],
                url_base=dict_get["url_base"],
                jobId=post_obj.jobId,
                headers=dict_get["headers"],
            )
        else:
            dict_get = DICT_DATABASES[args.database]["GET"]
            api_obj = dict_get["api_object"](
                identifier=inputs_ids,
                term_in=dict_get["term_in"],
                term_out=dict_get["term_out"],
                url_base=dict_get["url_base"],
                headers=dict_get["headers"],
            )
    except KeyError as e:
        raise UserWarning(f"Database {args.database} not in DICT_DATABASES.keys()") from e

    if args.tsv:
        delim = "\t"
    else:
        delim = ","

    str_out = ""
    for id_in, id_out in zip(
        api_obj.list_identifier,
        api_obj.list_gene_names,
        strict=False,
    ):
        str1 = f"{id_in.ljust(20)}"
        str2 = f"{str(id_out).ljust(20)}"
        str_out += f"{str1}{delim}{str2}{delim}{args.database}\n"

    print(str_out)
