import logging
from dataclasses import dataclass
from io import StringIO

import pandas as pd

from nf_rnaseq.api_schema import APIClient

logger = logging.getLogger(__name__)


@dataclass
class BioMart(APIClient):
    """Class to interact with Ensembl BioMart API."""

    identifier: str
    """str: Ensembl transcript ID(s); either one or a  list of comma separated values (<=500 total)."""
    search_term: str
    """str: Term on which to search."""
    url_base: str = 'http://www.ensembl.org/biomart/martservice?query=<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE Query><Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" ><Dataset name = "hsapiens_gene_ensembl" interface = "default" ><Filter name = "<SEARCH_TERM>" value = "<IDS>"/><Attribute name = "ensembl_transcript_id" /><Attribute name = "external_gene_name" /></Dataset></Query>'
    """str: URL base for Ensembl BioMart API."""
    url_query: str = None
    """str: URL query for BioMart API."""
    headers = None
    """str: headers for BioMart API (use ast.as_literal for dict)."""
    json: dict = None
    """dict: JSON response from BioMart API."""
    text: str = None
    """str: Text response from BioMart API (if no json)."""
    gene_names: list[str] = None
    """str: Gene name(s)."""

    def __post_init__(self):
        self.create_query_url()
        self.query_api()
        self.maybe_get_gene_names()

    def create_query_url(self):
        """Create URL for BioMart API query."""
        # split on ", ", trim, and join with "," to ensure no spaces
        self.identifier = ",".join([id.strip() for id in self.identifier.replace("[", "").replace("]", "").split(",")])
        self.url_query = self.url_base.replace("<IDS>", self.identifier).replace("<SEARCH_TERM>", self.search_term)

    def maybe_get_gene_names(self):
        """Get dataframe of transcript IDs and gene names from transcript IDs and add as hgnc_gene_name attr."""
        try:
            df = pd.read_csv(StringIO(self.text), sep="\t", header=None)
            df.columns = ["in", "out"]
            # in case multiple gene names for one transcript ID
            df_agg = df.groupby("in", sort=False).agg(list)
            self.gene_names = df_agg["out"].tolist()
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
