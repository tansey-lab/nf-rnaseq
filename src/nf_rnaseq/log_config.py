import logging


def add_logging_flags(parser):
    """Add logging flags to the parser."""
    parser.add_argument(
        "--verbose",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level.",
    )
    return parser


def configure_logging(verbose: bool = False):
    """Configure logging for the package."""
    loggers = [
        logging.getLogger("nf_rnaseq"),
    ]

    for logger in loggers:
        ch = logging.StreamHandler()

        if verbose:
            logger.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            ch.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
