import logging
import os
from dataclasses import dataclass

from nf_rnaseq.api_schema import APIClient

logger = logging.getLogger(__name__)


@dataclass
class UniProt(APIClient):
    """Class to interact with UniProt API."""

    identifier: str
    """str: UniProt ID."""
    search_term: str
    """str: Term on which to search."""
    url_base: str = "https://rest.uniprot.org/uniprotkb"
    """str: URL base for UniProtKB API."""
    url_query: str = None
    """str: URL query for UniProt API."""
    headers = None
    """str: headers for UniProt API (use ast.as_literal for dict)."""
    json: dict = None
    """dict: JSON response from UniProt API."""
    text: str = None
    """str: Text response from UniProt API (if no json)."""
    gene_names: list[str] = None
    """list[str]: Gene name(s)."""

    def __post_init__(self):
        self.create_query_url()
        self.query_api()
        self.maybe_get_gene_names()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = os.path.join(self.url_base, self.identifier + ".json")

    def maybe_get_gene_names(self):
        """Get list of gene names from UniProt ID and add as gene_name attr."""
        try:
            list_genes = [str(gene["geneName"]["value"]) for gene in self.json["genes"]]
            self.gene_names = list_genes
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
