import logging
import os
from dataclasses import dataclass

from nf_rnaseq.api_schema import APIClientGET

logger = logging.getLogger(__name__)


@dataclass
class HGNC(APIClientGET):
    """Class to interact with HGNC API."""

    def __post_init__(self):
        self.process_identifier()
        self.create_query_url()
        self.query_api()
        self.maybe_get_gene_names()

    def create_query_url(self):
        """Create URL for HGNC API query."""
        self.url_query = os.path.join(self.url_base, self.term_in, self.identifier)

    def check_if_job_ready(self):
        """Check if the job is ready; only necessary for POST + GET otherwise return False."""
        return False

    def maybe_get_gene_names(self):
        """Get list of gene names from mane_select term and add as list_gene_names attr."""
        try:
            list_genes = self.maybe_extract_list_from_hgnc_response_docs(self.term_out)
            self.list_gene_names = list_genes
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
            if self.json["response"]["numFound"] >= 1:
                list_output = [doc[str_to_extract] for doc in self.json["response"]["docs"]]
            else:
                list_output = []
            return list_output
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
