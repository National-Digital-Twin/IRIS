**Repository:** `IRIS-data-cleanser`

**Description:** `Details steps to set up an RDS instance to support a deployment of the pipeline`

**SPDX-License-Identifier:** OGL-UK-3.0


# RDS Initial Setup
# 	https://eu-west-2.console.aws.amazon.com/
# 	Sign in via root or IAM user
#   Go to https://eu-west-2.console.aws.amazon.com/rds/home?region=eu-west-2
# 	RDS > Dashboard > Create Database > Standard create > PostgreSQL

#   Specify DB Details:
#       - Engine Version        `PostgreSQL 15.3-R2`
#       - Template              `Dev/Test`
#       - Multi-AZ Deployment   `No` or `Single DB instance` (not needed for now, backups will be fine)
#       - Instance Identifier   `euwest2-postgres-iris-data-cleanser`
#       - Master Username       `postgres`
#       - Master Password       [8-41 ASCII chars, not /"@]
#       - DB Instance Class     Either `db.t3.small` (2 vCPU, 2 GiB Memory, $0.041/hr, ~£24/mo)
#       - Storage Type          `General Purpose SSD (gp3)`
#                               (SSD = $0.127/GB-mo or ~£0.85/mo for 10GB)
#       - Allocated Storage     `20GB`

#   Configure Advanced Settings:
#       - VPC                   `Default`
#       - Subnet Group          `Default`
#       - Publicly Accessible   `Yes`
#       - Security Group        `default`
#       - Availability Zone     `No Preference`
#       - RDS Proxy             `Unchecked`
#       - Certificate Authority `Default`
#       - Database port         `5432`
#       - Authentication        `Password authentication`
#       - Monitoring            `Turn on performance insights (7 days)`
#       - Enhanced Monitoring   `Turn on Enhanced monitoring`
#       - Initial database name `dbt`
#       - Automated backups     `Enabled`
#           - Retention Period  `7 days`
#           - Backup Window     `No Preference`
#           - Replication to another region = `No`
#       - Enable Encryption     `Yes`
#       - Log exports           `Disabled`
#       - Maintenance
#           - Auto Minor...     `Yes`
#           - M. Window         `No Preference`
#       - Deletion protection   `No`


# Launch DB Instance

# LIST USERS
SELECT rolname FROM pg_roles;
# or in psql
psql -h hostname -p port -U username -W
\du

# ADDING USERS
CREATE ROLE new_username WITH LOGIN PASSWORD 'password';
# Give new user permission to create databases?
CREATE ROLE new_username WITH LOGIN PASSWORD 'password' CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO new_username;

# CREATE DATABASE SCHEMA
# Terminate any active connections first
SELECT
    pg_terminate_backend(pg_stat_activity.pid)
FROM
    pg_stat_activity
WHERE
    pg_stat_activity.datname = 'production'
  AND pid <> pg_backend_pid();

# Then create the new database
CREATE DATABASE <database_name> OWNER postgres;
# Or to clone an existing database
CREATE DATABASE <database_name> WITH TEMPLATE production OWNER postgres;
