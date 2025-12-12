# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Run from dbt:
    dbt run --select os_ngd_buildings --threads 8
"""

# logger
import json
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from logging_config import setup_logger

# extras
from pandarallel import pandarallel
from tqdm import tqdm

# load credentials from .env
load_dotenv(".env", verbose=True)

DEBUG = os.environ.get("DEBUG", True)


logger = setup_logger(DEBUG)
pandarallel.initialize(progress_bar=True)
tqdm.pandas()


def model(dbt, fal):
    """dbt-fal model."""

    # get validated EPC data
    ngd = dbt.ref("stg_os_ngd_buildings")
    try:
        logger.info("OS NGD Buildings columns: %s", list(ngd.columns))
        logger.info("OS NGD Buildings shape: %s", getattr(ngd, "shape", None))
    except Exception:
        # Be defensive: logging should never break the model
        pass

    return ngd
