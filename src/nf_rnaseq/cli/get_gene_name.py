#!/usr/bin/env python

import argparse

from nf_rnaseq import biomart, config, hgnc, uniprot

DICT_DATABASES = {
    "BioMart": {
        "api_object": biomart.BioMart,
        "search_term": "ensembl_transcript_id_version",
    },
    "HGNC": {
        "api_object": hgnc.HGNC,
        "search_term": "mane_select",
    },
    "UniProt": {
        "api_object": uniprot.UniProt,
        "search_term": None,
    },
}


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

    try:
        api_obj = DICT_DATABASES[args.database]["api_object"](
            identifier=inputs_ids,
            search_term=DICT_DATABASES[args.database]["search_term"],
        )
        id_out = api_obj.gene_names
    except KeyError as e:
        raise UserWarning(f"Database {args.database} not in DICT_DATABASES.keys()") from e

    # set delimiter depending on tsv flag
    if args.tsv:
        delim = "\t"
    else:
        delim = ","

    # if inputs are a list, split and iterate
    list_inputs = inputs_ids.split(", ")
    str_out = ""
    if len(list_inputs) > 1:
        for idx, input_id in enumerate(list_inputs):
            str1 = f"{input_id.ljust(20)}"
            str2 = f"{str(id_out[idx]).ljust(20)}"
            str3 = f"{args.database}"
            str_out += f"{str1}{delim}{str2}{delim}{str3}\n"
    else:
        str1 = f"{args.input.ljust(20)}"
        str2 = f"{str(id_out).ljust(20)}"
        str3 = f"{args.database}"
        str_out = f"{str1}{delim}{str2}{delim}{str3}\n"

    print(str_out)
