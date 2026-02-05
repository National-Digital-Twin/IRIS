# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""Converts liccheck_report.txt into liccheck_report.csv

Usage:
    liccheck -R liccheck_report.txt
    python -m convert_liccheck_report
"""

from __future__ import annotations

import logging as log
import os
from pathlib import Path

import pandas as pd

ROOT = Path()
TXT_FILENAME = "liccheck_report.txt"
CSV_FILENAME = "license_report.csv"


def main():
    """Convert liccheck report from txt to csv."""
    try:
        log.info(f"Reading {TXT_FILENAME}")
        with open(ROOT / TXT_FILENAME, encoding="utf8") as f:
            data = [line.replace("\n", "") for line in f.readlines()]

        df_list = []
        for line in data:
            package_name = line.split(" ")[0]
            package_version = line.split(" ")[1]
            status = line.split(" ")[-1]
            license_name = (
                line.replace(package_name, "")
                .replace(package_version, "")
                .replace(status, "")
                .strip()
            )
            df_list.append(
                {
                    "Package": package_name,
                    "Version": package_version,
                    "License": license_name,
                    "Status": status,
                },
            )
        df = pd.DataFrame(df_list)
        df.to_csv(ROOT / CSV_FILENAME, index=False)
        log.info(f"✅  Successfully exported to {CSV_FILENAME}")

        os.remove(ROOT / TXT_FILENAME)
        log.info(f"🗑️  Deleted {TXT_FILENAME}")
    except Exception:  # pylint: disable=broad-except
        log.exception("Unknown error occurred")


if __name__ == "__main__":
    main()
