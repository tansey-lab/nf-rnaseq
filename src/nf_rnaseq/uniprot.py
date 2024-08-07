import logging
import os
from dataclasses import dataclass

import requests

from nf_rnaseq.api_schema import APIClientGET, APIClientPOST

logger = logging.getLogger(__name__)


@dataclass
class UniProt(APIClientGET):
    """Class to interact with UniProt API for single identifier."""

    def __post_init__(self):
        super().__post_init__()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = os.path.join(self.url_base, self.identifier + ".json")

    def check_if_job_ready(self, res: requests.Response):
        """Check if the job is ready."""
        pass

    def maybe_get_gene_names(self):
        """Get list of gene names from UniProt ID and add as list_gene_names attr."""
        try:
            list_genes = [str(gene["geneName"]["value"]) for gene in self.json["genes"]]
            self.list_gene_names = list_genes
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)


@dataclass
class UniProtGET(APIClientGET):
    """Class to interact with UniProt API bulk download for list of identifiers via GET."""

    jobId: str
    """str: Job ID for UniProt bulk download."""

    def __post_init__(self):
        super().__post_init__()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = os.path.join(self.url_base, self.job)

    def maybe_get_gene_names(self):
        """Get list of gene names from UniProt ID and add as list_gene_names attr."""
        try:
            list_genes = [str(gene["geneName"]["value"]) for gene in self.json["genes"]]
            self.list_gene_names = list_genes
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)

    def check_if_job_ready(self, res: requests.Response):
        """Check if the job is ready."""
        pass


@dataclass
class UniProtPOST(APIClientPOST):
    """Class to interact with UniProt API bulk download for list of identifiers via POST."""

    def __post_init__(self):
        super().__post_init__()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = self.url_base

    def maybe_get_job_id(self):
        """Get job ID from UniProt and add as job attr."""
        try:
            self.jobId = self.json["jobId"]
        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
