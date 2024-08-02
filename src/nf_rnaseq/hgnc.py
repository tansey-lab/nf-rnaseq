import logging
import os
from dataclasses import dataclass

from nf_rnaseq.api_schema import APIClient

logger = logging.getLogger(__name__)


@dataclass
class HGNC(APIClient):
    """Class to interact with HGNC API."""

    search_id: str
    """str: ID on which to search."""
    search_term: str
    """str: Term from, https://www.genenames.org/help/rest/ on which to search."""
    url_base: str = "https://rest.genenames.org/fetch"
    """str: URL base for HGNC API."""
    header: str = "{'Accept': 'application/json'}"
    """str: Header for HGNC API (use ast.as_literal for dict)."""
    # url_query: str = None
    # """str: URL query for HGNC API."""
    # json: dict = None
    # """dict: JSON response from UniProt API."""
    # text: str = None
    # """str: Text response from UniProt API (if no json)."""
    # hgnc_gene_name: list[str] = None
    # """str: HGNC gene name."""

    def __post_init__(self):
        self.create_query_url()
        self.query_api()
        self.maybe_set_json_properties()
        self.maybe_get_hgnc_gene_name()

    def create_query_url(self):
        """Create URL for HGNC API query."""
        self.url_query = os.path.join(self.url_base, self.search_term, self.search_id)

    def maybe_set_json_properties(self):
        """If self.json is not None, set properties of UniProt object using self.json."""
        if self.json is not None:
            HGNC(**self.json)

    def maybe_get_hgnc_gene_name(self, str_symbol: str = "symbol") -> list[str]:
        """Get list of gene names from UniProt ID and add as hgnc_gene_name attr."""
        try:
            list_genes = self.maybe_extract_list_from_hgnc_response_docs(str_symbol)
            self.hgnc_gene_name = list_genes
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)

    def maybe_extract_list_from_hgnc_response_docs(
        self,
        str_to_extract: str,
    ) -> list[str] | None:
        """Extract a list of values from the response documents of an HGNC REST API request.

        Parameters
        ----------
        str_to_extract : str
            Key to extract from the response documents

        Returns
        -------
        list[str]
            List of values extracted from the response documents

        """
        try:
            if self.response["numFound"] >= 1:
                list_output = [doc[str_to_extract] for doc in self.response["docs"]]
            else:
                list_output = []
            return list_output
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
