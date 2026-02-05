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

    # Avoid duplicate handlers if called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG if debug else logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        # Update level on existing handlers to reflect debug flag
        for h in logger.handlers:
            h.setLevel(logging.DEBUG if debug else logging.ERROR)

    return logger
