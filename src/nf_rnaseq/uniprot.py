import logging
import os
from dataclasses import dataclass

from nf_rnaseq import APIClient

logger = logging.getLogger(__name__)


@dataclass
class UniProt(APIClient):
    """Class to interact with UniProt API."""

    uniprot_id: str
    """str: UniProt ID."""
    url_base: str = "https://rest.uniprot.org/uniprotkb"
    """str: URL base for UniProtKB API."""
    url_query: str = None
    """str: URL query for UniProt API."""
    json: dict = None
    """dict: JSON response from UniProt API."""
    text: str = None
    """str: Text response from UniProt API (if no json)."""
    hgnc_gene_name: str = None
    """str: HGNC gene name."""

    def __post_init__(self):
        self.create_query_url()
        self.query_api()
        self.maybe_set_json_properties()
        self.maybe_get_hgnc_gene_name()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = os.path.join(self.url_base, self.uniprot_id, ".json")

    def maybe_set_json_properties(self):
        """If self.json is not None, set properties of UniProt object using self.json."""
        if self.json is not None:
            UniProt(**self.json)

    def maybe_get_hgnc_gene_name(self):
        """Get list of gene names from UniProt ID and add as hgnc_gene_name attr."""
        try:
            list_genes = [str(gene["geneName"]["value"]) for gene in self.genes]
            self.hgnc_gene_name = list_genes
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
