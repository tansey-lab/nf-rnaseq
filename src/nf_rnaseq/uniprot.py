import logging
import os
import re
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests

from nf_rnaseq.api_schema import APIClientGET, APIClientPOST

logger = logging.getLogger(__name__)

re_next_link = re.compile(r'<(.+)>; rel="next"')


@dataclass
class UniProt(APIClientGET):
    """Class to interact with UniProt API for single identifier."""

    def __post_init__(self):
        super().__post_init__()

    def create_query_url(self):
        """Create URL for UniProt API query."""
        self.url_query = os.path.join(self.url_base, self.identifier + ".json")

    def check_if_job_ready(self):
        """Check if the job is ready; only necessary for POST + GET otherwise return False."""
        return False

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

    @staticmethod
    def get_next_link(headers):
        """Get next link from headers."""
        if "Link" in headers:
            # re_next_link set as a global variable
            match = re_next_link.match(headers["Link"])
            if match:
                return match.group(1)

    def get_batch(self):
        """Get batches of json from UniProt API."""
        batch_url = self.url_query
        while batch_url:
            response = requests.get(batch_url)
            self.check_response(response)
            yield response
            batch_url = self.get_next_link(response.headers)

    def concatenate_json_batches(self):
        """Concatenate json from batches and return as dictionary."""
        list_results = []
        # failedIds occur on each page so need to use a set instead of list
        set_failedIds = set()
        for batch in self.get_batch():
            batch_json = batch.json()
            if "results" in batch_json:
                list_results.extend(batch_json["results"])
            if "failedIds" in batch_json:
                set_failedIds.update(batch_json["failedIds"])
        dict_temp = {"results": list_results, "failedIds": list(set_failedIds)}
        return dict_temp

    def check_if_job_ready(self):
        """Check if the job is ready and add json if so."""
        i = 0
        while True:
            response = requests.get(self.url_query)
            self.check_response(response)
            j = response.json()
            if "results" in j or "failedIds" in j:
                self.json = self.concatenate_json_batches()
                logger.info(f"\n{self.jobId}\n{self.json}")
                return True
            else:
                i += 1
                if i >= 10:
                    raise Exception(f"{self.jobId}: {j['jobStatus']}")
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
        df_agg = df.groupby("in", sort=False).agg(set).reset_index()
        df_agg["out"] = df_agg["out"].apply(lambda x: list(x))

        # list_check = [i for i in self.list_identifier if i in df_agg["in"].tolist()]
        # assert len(list_check) == len(self.list_identifier)

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
