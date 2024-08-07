import logging
from dataclasses import dataclass
from io import StringIO

import pandas as pd
import requests

from nf_rnaseq.api_schema import APIClientGET

logger = logging.getLogger(__name__)


@dataclass
class BioMart(APIClientGET):
    """Class to interact with Ensembl BioMart API."""

    def __post_init__(self):
        self.process_identifier()
        self.create_query_url()
        self.query_api()
        self.maybe_get_gene_names()

    def create_query_url(self):
        """Create URL for BioMart API query."""
        self.url_query = (
            self.url_base.replace("<IDS>", self.identifier)
            .replace("<TERM_IN>", self.term_in)
            .replace("<TERM_OUT>", self.term_out)
        )

    def check_if_job_ready(self, res: requests.Response):
        """Check if the job is ready."""
        pass

    def maybe_get_gene_names(self):
        """Get dataframe of transcript IDs and gene names from transcript IDs and add as list_gene_names attr."""
        try:
            df = pd.read_csv(StringIO(self.text), sep="\t", header=None)
            df.columns = ["in", "out"]
            df_agg = df.groupby("in", sort=False).agg(list)

            # check that all input IDs are in the output dataframe
            assert len([i for i in self.list_identifier if i in df_agg["in"].tolist()]) == len(self.list_identifier)

            self.list_identifier = df_agg["in"].tolist()
            self.list_gene_names = df_agg["out"].tolist()

        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
