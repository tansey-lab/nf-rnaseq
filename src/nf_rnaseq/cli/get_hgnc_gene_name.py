#!/bin/usr/env python

import argparse

from nf_rnaseq import config, hgnc, uniprot


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
        "-i",
        "--input",
        help="Input string (type: str)",
        type="str",
    )

    parser.add_argument(
        "-s",
        "--searchTerm",
        help="Search term for HGNC Fetch; if UniProt, not in use (type: str)",
        type="str",
        default="mane_select",
    )

    parser.add_argument(
        "-t",
        "--tsv",
        help="If flag included tsv format out otherwise csv",
        action="store_true",
    )

    parser.add_argument(
        "-u",
        "--uniProt",
        help="If flag included UniProt should be queried otherwise HGNC database used",
        action="store_true",
    )

    args = parser.parse_args()

    return args


def main():
    """Get HGNC gene name from string input."""
    args = parsearg_utils()

    if args.cachePath != "":
        config.set_request_cache(args.cachePath)

    if args.uniProt:
        source = "UniProt"
        uniprot_obj = uniprot.UniProt(uniprot_id=args.input)
        uniprot_obj.query_api()
        uniprot_obj.maybe_set_attr_from_json()
        # id_out = uniprot_obj.hgnc_gene_name
    else:
        source = "HGNC"
        hgnc_obj = hgnc.HGNC(search_id=args.input, search_term=args.searchTerm)
        # hgnc_obj.query_api()
        # hgnc_obj.maybe_set_attr_from_json()
        id_out = hgnc_obj.hgnc_gene_name

    str1 = f"{args.input.ljust(20)}"
    str2 = f"{str(id_out).ljust(20)}"
    str3 = f"{source}"

    if args.tsv:
        print(f"{str1}\t{str2}\t{str3}")
    else:
        print(f"{str1},{str2},{str3}")
