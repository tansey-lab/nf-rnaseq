import logging
import os
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests

# from nf_rnaseq import requests_wrapper
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

    def check_if_job_ready(self):
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
        # session = requests_wrapper.get_cached_session()
        i = 0
        while True:
            # response = session.get(self.url_query)
            response = requests.get(self.url_query)
            self.check_response(response)
            j = response.json()
            if "results" in j or "failedIds" in j:
                return bool(j["results"] or j["failedIds"])
            else:
                i += 1
                if i >= 10:
                    raise Exception(f"{self.jobId}: {response.json()['jobStatus']}")
                else:
                    time.sleep(self.polling_interval)

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

        df = pd.DataFrame({"in": list_identifier, "out": list_gene_names})
        df_agg = df.groupby("in", sort=False).agg(list).reset_index()

        self.list_identifier = df_agg["in"].tolist()
        self.list_gene_names = df_agg["out"].tolist()


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
