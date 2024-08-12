import logging
import os
import time
from dataclasses import dataclass

import numpy as np
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
        """Check if the job is ready; only necessary for POST + GET otherwise return True."""
        return True

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

    jobId: str | None = None
    """str: Job ID for bulk download; applies to UniProt bulk downloading."""

    def __post_init__(self):
        super().__post_init__()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = os.path.join(self.url_base, self.jobId)

    def check_if_job_ready(self):
        """Check if the job is ready."""
        while True:
            response = requests.get(self.url_query)
            self.check_response(response)
            if "jobStatus" in response.json():
                if response.json()["jobStatus"] == "RUNNING":
                    print(f"Retrying in {self.polling_interval}s")
                    time.sleep(self.polling_interval)
                else:
                    raise Exception(response.json()["jobStatus"])
            else:
                return bool(response.json()["results"] or response.json()["failedIds"])

    def maybe_get_gene_names(self):
        """Get list of gene names from UniProt ID and add as list_gene_names attr."""
        list_identifier = []
        list_gene_names = []

        str_results = "results"
        if str_results in self.json:
            list_results = self.json[str_results]
            list_identifier.extend([i["from"] for i in list_results])
            list_gene_names.extend([i["to"] for i in list_results])

        str_failedIds = "failedIds"
        if str_failedIds in self.json:
            list_failed = self.json[str_failedIds]
            list_identifier.extend(list_failed)
            list_gene_names.extend(list(np.repeat(np.nan, len(list_failed))))

        self.list_identifier = list_identifier
        self.list_gene_names = list_gene_names


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
