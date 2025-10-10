# EPC Data Backfill

Bulk backfill SAP ratings and expiry date EPC data from CSV files (local or S3) into PostgreSQL `iris.epc_assessment`.

The CSV files used are from a previous import, they require the columns:

| Column          | Description                             | Example       |
| --------------- | --------------------------------------- | ------------- |
| `UPRN`          | Unique Property Reference Number        | `10033219288` |
| `SAPBand`       | EPC rating band (A-G)                   | `C`           |
| `SAPScore`      | SAP numeric score                       | `72`          |
| `LodgementDate` | Certificate lodgement date (YYYY-MM-DD) | `2008-10-01`  |

**Note:** Rows with missing or empty values for `SAPBand`, `SAPScore`, `UPRN`, or `LodgementDate` will be skipped.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### From S3

```bash
CSV_PATH=s3://bucket/prefix/ python update_from_csv.py
```

### From Local Folder

```bash
CSV_PATH=/path/to/csv/files/ python update_from_csv.py
```

### From Local File

```bash
CSV_PATH=/path/to/file.csv python update_from_csv.py
```

## Environment Variables

| Variable            | Required | Default     | Description                                                   |
| ------------------- | -------- | ----------- | ------------------------------------------------------------- |
| `CSV_PATH`          | Yes      | -           | S3 path (s3://bucket/prefix), local directory, or single file |
| `DB_HOST`           | No       | `localhost` | PostgreSQL host                                               |
| `DB_USERNAME`       | No       | `postgres`  | PostgreSQL username                                           |
| `DB_PASSWORD`       | No       | `postgres`  | PostgreSQL password                                           |
| `DB_NAME`           | No       | `iris`      | Database name                                                 |
| `DB_PORT`           | No       | `5432`      | PostgreSQL port                                               |
| `DISABLE_FK_CHECKS` | No       | `false`     | Set to `true` to disable foreign key checks (testing only)    |

### AWS Credentials

For S3 access, configure [AWS environment variables for boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).
