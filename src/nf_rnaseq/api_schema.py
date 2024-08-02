import ast
import logging
from abc import ABC, abstractmethod

import requests

from nf_rnaseq import requests_wrapper


class APIClient(ABC):
    """Abstract class for API clients."""

    def query_api(self):
        """Get response from API which tries to save as json in instance; otherwise saves as text."""
        session = requests_wrapper.get_cached_session()
        if self.headers is None:
            response = session.get(self.url_query)
        else:
            response = session.get(self.url_query, ast.literal_eval(self.header))

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error("Error at %s", "division", exc_info=e)

        try:
            self.json = response.json()
        except requests.exceptions.JSONDecodeError as e:
            logging.error("Error at %s", "division", exc_info=e)
            self.text = response.text

    @abstractmethod
    def create_query_url(self):
        """Create the URL to query the API (e.g., add search term or ID)."""
        ...

    @abstractmethod
    def maybe_set_attr_from_json(self):
        """Set attributes in the object from the json response."""
        ...

    @abstractmethod
    def maybe_get_hgnc_gene_name(self):
        """Get the HGNC gene name from the json response."""
        ...
