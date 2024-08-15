import logging
from dataclasses import dataclass
from io import StringIO

import pandas as pd

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

    def check_if_job_ready(self):
        """Check if the job is ready; only necessary for POST + GET otherwise return False."""
        return False

    def maybe_get_gene_names(self):
        """Get dataframe of transcript IDs and gene names from transcript IDs and add as list_gene_names attr."""
        try:
            df = pd.read_csv(StringIO(self.text), sep="\t", header=None)
            df.columns = ["in", "out"]
            df_agg = df.groupby("in", sort=False).agg(list).reset_index()

            # some input IDs are not in the output dataframe, so add back as [None] to the output
            list_missing = [i for i in self.list_identifier if i not in df_agg["in"].tolist()]
            df_missing = pd.DataFrame(
                {
                    "in": list_missing,
                    "out": [[None] for i in range(len(list_missing))],
                }
            )
            df_agg = pd.concat([df_agg, df_missing], axis=0)

            list_check = [i for i in self.list_identifier if i in df_agg["in"].tolist()]
            assert len(list_check) == len(self.list_identifier)

            self.list_identifier = df_agg["in"].tolist()
            self.list_gene_names = df_agg["out"].tolist()

        except (KeyError, AttributeError) as e:
            logging.error("Error at %s", "division", exc_info=e)
