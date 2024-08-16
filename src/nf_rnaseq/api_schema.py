import ast
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

import requests

from nf_rnaseq import requests_wrapper

logger = logging.getLogger(__name__)


@dataclass
class APIClient(ABC):
    """Abstract class for API clients."""

    identifier: str
    """str: Identifier or comma delimited list of identifiers from which to map."""
    term_in: str | None
    """str: Term on which from which to map."""
    term_out: str | None
    """str: Term on which to which to map, if needed."""
    url_base: str
    """str: URL base for API."""

    def __post_init__(self):
        self.process_identifier()

    @staticmethod
    def check_response(res: requests.Response) -> None:
        """Check the response status code for errors."""
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error("Error at %s", "division", exc_info=e)

    def process_identifier(self):
        """Process identifier string input to standardize, overwrite, and add as list."""
        # remove "[" and "]" added by NextFlow
        self.identifier = self.identifier.replace("[", "").replace("]", "")
        # split on ", ", trim, and
        self.list_identifier = [id.strip() for id in self.identifier.split(",")]
        # join with "," to ensure no spaces
        self.identifier = ",".join(self.list_identifier)

    @abstractmethod
    def query_api(self):
        """Query the API."""
        ...


@dataclass
class APIClientGET(APIClient):
    """Abstract class for API clients GET."""

    headers: str | None = None
    """str: Headers for API (use ast.as_literal to convert to dict)."""
    polling_interval: int = 5
    """int: Interval in seconds to poll API for job status."""

    def __post_init__(self):
        super().__post_init__()
        self.create_query_url()
        self.query_api()
        self.maybe_get_gene_names()

    def query_api(self):
        """Get response from API which tries to save as json in instance; otherwise saves as text."""
        session = requests_wrapper.get_cached_session()

        if self.headers is None:
            response = session.get(self.url_query)
        else:
            response = session.get(self.url_query, headers=ast.literal_eval(self.headers))

        self.check_response(response)
        if self.check_if_job_ready():
            logger.info(f"\n{self.identifier}\n{self.json}\n")
        else:
            try:
                self.json = response.json()
                logger.info(f"\n{self.identifier}\n{self.json}\n")
            except requests.exceptions.JSONDecodeError as e:
                logging.error("Error at %s", "division", exc_info=e)
                self.text = response.text
                logger.info(f"\n{self.identifier}\n{self.text}\n")

    @abstractmethod
    def create_query_url(self):
        """Create the URL to query the API (e.g., add search term or ID)."""
        ...

    @abstractmethod
    def check_if_job_ready(self):
        """Check if the job is ready."""
        ...

    @abstractmethod
    def maybe_get_gene_names(self):
        """Get the gene name from the request response."""
        ...


@dataclass
class APIClientPOST(APIClient):
    """Abstract class for API clients POST."""

    def __post_init__(self):
        super().__post_init__()
        self.create_query_url()
        self.query_api()
        self.maybe_get_job_id()

    def query_api(self):
        """Get response from API which tries to save as json in instance; otherwise saves as text."""
        response = requests.post(
            self.url_query,
            data={
                "from": self.term_in,
                "to": self.term_out,
                "ids": self.identifier,
            },
        )

        self.check_response(response)

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
    def maybe_get_job_id(self):
        """Get the job ID from the request response."""
        ...
