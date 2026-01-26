import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import osdatahub
from osdatahub import PlacesAPI
import time
import logging
import datetime

# Load environment variables
load_dotenv(".env")

logging.basicConfig(
     level=os.getenv("LOG_LEVEL", "INFO"),
     format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

OS_PLACES_API_KEY = os.environ.get("OS_PLACES_API_KEY")

if not OS_PLACES_API_KEY:
    logger.error("OS_PLACES_KEY not found. Please set it in your .env file.")
    raise RuntimeError("OS_PLACES_KEY not found. Please set it in your .env file.")
else:
    logger.info("OS Places API Key loaded.")

# Database Connection Details
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", default=5432)
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
MATCH_THRESHOLD=float(os.getenv("MATCH_THRESHOLD", default=0.8))
LOG_INTERVAL = int(os.getenv("LOG_INTERVAL", default=1000))
SLEEP_DURATION = float(os.getenv("SLEEP_DURATION", default=0.1))
COMMIT_INTERVAL = int(os.getenv("COMMIT_INTERVAL", default=100))
TIMEOUT_WAIT_TIME = int(os.getenv("TIMEOUT_WAIT_TIME", default=60))

_original_get = osdatahub.get

def get_with_timeout(*args, **kwargs):
    kwargs.setdefault("timeout", TIMEOUT_WAIT_TIME)
    return _original_get(*args, **kwargs)

osdatahub.get = get_with_timeout

BACKOFF_WAIT_TIME = float(os.getenv("BACKOFF_WAIT_TIME", default=15))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", default=3))


def get_db_connection(db_host, db_port, db_name, db_user, db_password):
    """Creates a SQLAlchemy engine for the Postgres database.
    
    Args:
        db_host (str): database host
        db_port (str): database port
        db_name (str): database name
        db_user (str): database user
        db_password (str): database password
    
    Returns:
        sqlalchemy.engine.Engine: postgres database engine"""
    
    connection_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_str)

    logger.info("Database configuration loaded.")

    return engine

def is_crossref_exists(engine, db_schema):
    """Determines whether the epc_address_uprn_crossref already exists.
    
    Args:
        engine: postgres database engine
        db_schema (str): database schema
    
    Returns:
        boolean: True if the table exists else False
        """

    query = text("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE  table_schema = :schema and
        table_name = 'epc_address_uprn_crossref'
    );
    """)

    with engine.connect() as conn:
        return conn.execute(query, {"schema": db_schema}).scalar()

def get_certificates(engine, db_schema, crossref_exists=False):
    """Given a database engine, retrieve a certificates table containing records without a UPRN.
    
    Args:
        engine: postgres database engine
        db_schema (str): database schema
        crossref_exists (bool): boolean on whether the cross reference table already exists 
    
    Returns:
        pd.DataFrame: Pandas dataframe containing certificate records without a UPRN whose LMK_KEY has not already been matched in the cross reference table
    """

    if crossref_exists:
        query = f"""
            WITH latest AS (
                SELECT
                    lmk_key,
                    MAX(match_date) AS last_match_date,
                    MAX(uprn) FILTER (WHERE uprn IS NOT NULL) AS uprn
                FROM {db_schema}.epc_address_uprn_crossref
                GROUP BY lmk_key
            )
            SELECT 
                c."LMK_KEY",
                concat_ws(', ', UPPER(c."ADDRESS"), UPPER(c."POSTTOWN"), UPPER(c."POSTCODE")) as query_address,
                c."LODGEMENT_DATE"
            FROM {db_schema}.certificates c
            left join latest eauc on eauc.lmk_key=c."LMK_KEY"
                WHERE NULLIF(TRIM(c."UPRN"), '') IS NULL
                AND (
                    eauc.lmk_key IS NULL
                    OR (
                        eauc.uprn IS NULL
                        AND (eauc.last_match_date IS NULL OR eauc.last_match_date < CURRENT_DATE - INTERVAL '1 year')
                    )
                );
        """

    else:
        query = f"""
            SELECT 
                "LMK_KEY",
                concat_ws(', ', UPPER("ADDRESS"), UPPER("POSTTOWN"), UPPER("POSTCODE")) as query_address,
                "LODGEMENT_DATE"
            FROM {db_schema}.certificates 
            WHERE NULLIF(TRIM("UPRN"), '') IS NULL;
        """

    return pd.read_sql(query, engine)

def find_with_retry(api_client, address, threshold, limit):
    """_summary_

    Args:
        api_client (_type_): _description_
        address (_type_): _description_
        threshold (_type_): _description_
        retries (int, optional): _description_. Defaults to 3.
        backoff (float, optional): _description_. Defaults to 0.5.
    """

    for attempt in range(1, MAX_RETRIES+1):
        try:
            return api_client.find(
                text=address, 
                minmatch=threshold, 
                limit=limit,
            )
        except Exception as e:
            logger.warning(f"Exception: {e} encoutered for record: {address}.")
            if attempt == MAX_RETRIES:
                logger.warning(f"No more attempts planned for record {address}. This record will be recorded as unmatched.")
                return None
            else:
                sleep_for = BACKOFF_WAIT_TIME * (2**(attempt-1))
                logger.warning(f"Retrying matching for {address} after {sleep_for} seconds.")
                time.sleep(sleep_for)
            
 
def match_address(api_client, address, threshold):
    """
    Given a EPC record with no UPRN, use the OS Places API to find a UPRN value with the highest match score which is above the threshold.
    
    Args:
        address (str): the address to be passed to the OS Places API
        threshold (float): a threshold (between 0.1 and 1) above which match scores must be
    
    Returns:
        uprn (str): a matched uprn value
        match_score (float): a match score value
    """

    results = find_with_retry(
                api_client=api_client,
                address=address, 
                threshold=threshold, 
                limit=1
            )
    if results and results.get("features"):
        props = results["features"][0].get("properties", {})
        return props.get("UPRN"), float(props.get("MATCH")), props.get("MATCH_DESCRIPTION") 
    else:
        return None, None, None

def main():

    engine = get_db_connection(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

    crossref_exists = is_crossref_exists(engine, DB_SCHEMA)
    certificates = get_certificates(engine, DB_SCHEMA, crossref_exists=crossref_exists)

    places_api = PlacesAPI(OS_PLACES_API_KEY)

    matched = 0
    unmatched = 0

    logger.info(f"Matching threshold set at {MATCH_THRESHOLD}.")
    logger.info(f"Sleep duration between matches set at: {SLEEP_DURATION}.")
    logger.info(f"Commit interval set at: {COMMIT_INTERVAL}.")
    logger.info(f"API timeout time set at: {TIMEOUT_WAIT_TIME}.")
    logger.info(f"Backoff wait time set at: {BACKOFF_WAIT_TIME}.")
    logger.info(f"Max retries set at: {MAX_RETRIES}.")
    
    crossref_rows = []
    for _, record in certificates.iterrows():

        uprn, match_score, match_description = match_address(places_api, record["query_address"], MATCH_THRESHOLD)

        time.sleep(SLEEP_DURATION)

        match_date = datetime.date.today()
        
        if uprn is not None and match_score is not None and match_description is not None:
            record_matched = {
                "lmk_key": record["LMK_KEY"],
                "query_address": record["query_address"],
                "uprn": uprn,
                "match_score": match_score,
                "match_date": match_date
            }
            crossref_rows.append(record_matched)
            matched += 1

        else:
            record_unmatched = {
                "lmk_key": record["LMK_KEY"],
                "query_address": record["query_address"],
                "uprn": None,
                "match_score": None,
                "match_date": match_date
            }
            crossref_rows.append(record_unmatched)
            unmatched += 1
        
        
        if (matched+unmatched) == 10:
            logger.debug(f"UPRN found for {matched} records so far.")
            logger.debug(f"A UPRN could not be found for {unmatched} records so far.")

        if (matched+unmatched) % LOG_INTERVAL == 0:
            logger.info(f"UPRN found for {matched} records so far.")
            logger.info(f"A UPRN could not be found for {unmatched} records so far.")

        if (matched+unmatched) % COMMIT_INTERVAL == 0:
            epc_address_uprn_crossref = pd.DataFrame(
                crossref_rows,
                columns=["lmk_key", "query_address", "uprn", "match_score", "match_date"]
            )
            epc_address_uprn_crossref.to_sql("epc_address_uprn_crossref", schema=DB_SCHEMA, con=engine, index=False, if_exists='append')
            crossref_rows = []
            logger.info(f"Committing {COMMIT_INTERVAL} records to the cross reference table.")
    
    if len(crossref_rows) != 0:
        epc_address_uprn_crossref = pd.DataFrame(
            crossref_rows,
            columns=["lmk_key", "query_address", "uprn", "match_score", "match_date"]
        )
        epc_address_uprn_crossref.to_sql("epc_address_uprn_crossref", schema=DB_SCHEMA, con=engine, index=False, if_exists='append')
        crossref_rows = []

    logger.info(f"A total of {matched} records were successfully matched.")
    logger.info(f"A total of {unmatched} records were not able to be matched.")

if __name__ == "__main__":
     main()



