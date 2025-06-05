# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import logging


def setup_logger(debug=False):
    """
    Set up a console logger with debug mode control.

    Args:
        debug (bool): If True, sets logging level to DEBUG; otherwise ERROR

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.ERROR)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if debug else logging.ERROR)

    # Create formatter with fixed format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
