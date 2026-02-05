import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import osdatahub
from osdatahub import PlacesAPI
import time
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty

# Load environment variables
load_dotenv(".env")

logging.basicConfig(
     level=os.getenv("LOG_LEVEL", "INFO"),
     format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

OS_PLACES_API_KEY1 = os.environ.get("OS_PLACES_API_KEY1")
OS_PLACES_API_KEY2 = os.environ.get("OS_PLACES_API_KEY2")
OS_PLACES_API_KEY3 = os.environ.get("OS_PLACES_API_KEY3")
OS_PLACES_API_KEY4 = os.environ.get("OS_PLACES_API_KEY4")

api_keys = [key for key in [
    OS_PLACES_API_KEY1, 
    OS_PLACES_API_KEY2, 
    OS_PLACES_API_KEY3, 
    OS_PLACES_API_KEY4
] if key not in [None, '']]

num_api_keys = len(api_keys)
if num_api_keys < 1:
    logger.error("No OS Places API key found. Please add one or more keys to you .env file.")
    raise RuntimeError("OS_PLACES_KEY not found. Please add one or more to your .env file.")
else:
    logger.info(f"{num_api_keys} OS Places API keys loaded.")

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

def worker(api_key, in_q, out_q):
    
    try:
        api = PlacesAPI(api_key)
    except Exception:
        logger.error(f"Failed to create api class using key ending in {api_key[:-3]}")
        return
    
    while True:
        record = in_q.get()
        if record is None:
            in_q.task_done()
            break
        
        try:
            uprn, match_score, match_description = match_address(api, record["query_address"], MATCH_THRESHOLD)
            if uprn is not None and match_score is not None and match_description is not None:
                record_out = {
                    "lmk_key": record["LMK_KEY"],
                    "query_address": record["query_address"],
                    "uprn": uprn,
                    "match_score": match_score,
                    "match_date": datetime.date.today()
                }
            else:
                record_out = {
                    "lmk_key": record["LMK_KEY"],
                    "query_address": record["query_address"],
                    "uprn": None,
                    "match_score": None,
                    "match_date": datetime.date.today()
                }
        except Exception:
            logger.exception("Worker failed to process record; marking as unmatched.")
            record_out = {
                "lmk_key": record.get("LMK_KEY"),
                "query_address": record.get("query_address"),
                "uprn": None,
                "match_score": None,
                "match_date": datetime.date.today()
            }
        finally:
            out_q.put(record_out)
            in_q.task_done()
            
            # wait before using this API key again
            time.sleep(SLEEP_DURATION)

def write_records(engine, records):
    matching_results_df = pd.DataFrame(
        records,
        columns=["lmk_key", "query_address", "uprn", "match_score", "match_date"]
    )
    matching_results_df.to_sql("epc_address_uprn_crossref", schema=DB_SCHEMA, con=engine, index=False, if_exists='append')
    logger.info(f"Committing {len(records)} records to the cross reference table.")


def main():

    engine = get_db_connection(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

    crossref_exists = is_crossref_exists(engine, DB_SCHEMA)
    certificates = get_certificates(engine, DB_SCHEMA, crossref_exists=crossref_exists)

    matched = 0
    unmatched = 0

    logger.info(f"Matching threshold set at {MATCH_THRESHOLD}.")
    logger.info(f"Sleep duration between matches set at: {SLEEP_DURATION}.")
    logger.info(f"Commit interval set at: {COMMIT_INTERVAL}.")
    logger.info(f"API timeout time set at: {TIMEOUT_WAIT_TIME}.")
    logger.info(f"Backoff wait time set at: {BACKOFF_WAIT_TIME}.")
    logger.info(f"Max retries set at: {MAX_RETRIES}.")
    
    # build an in- and out- queue
    in_q = Queue()
    out_q = Queue()

    # populate queue with all records which require matching
    for _, record in certificates.iterrows():
        in_q.put(record)

    # append Nones to the queue to act as a finish line
    for _ in api_keys:
        in_q.put(None)
    
    # initiate workers to start address matching records in the queue
    with ThreadPoolExecutor(max_workers=num_api_keys) as executor:
        for key in api_keys:
            executor.submit(worker, key, in_q, out_q)
        logger.info(f"Instantiated {len(api_keys)} workers in parallel with one API key each.")

        # as the out queue begins populating, organise records into batches that are written to the DB
        batch = []
        matched = 0
        unmatched = 0
        written = 0

        while written < certificates.shape[0]:
            
            # get a record from the out queue
            try: 
                record = out_q.get(timeout=1)
            except Empty:
                continue # wait for more records to be added to the out queue by the workers

            if record["uprn"] is None and record["match_score"] is None:
                unmatched += 1
            else:
                matched += 1

            batch.append(record)
            written += 1

            if (matched+unmatched) == 10:
                logger.debug(f"UPRN found for {matched} records so far.")
                logger.debug(f"A UPRN could not be found for {unmatched} records so far.")

            if (matched+unmatched) % LOG_INTERVAL == 0:
                logger.info(f"UPRN found for {matched} records so far.")
                logger.info(f"A UPRN could not be found for {unmatched} records so far.")
            
            # write to DB 
            if len(batch) == COMMIT_INTERVAL:
                write_records(engine, batch)
                batch = []

        # write any leftover records
        if batch:
            write_records(engine, batch)
            batch = []

    logger.info(f"A total of {matched} records were successfully matched.")
    logger.info(f"A total of {unmatched} records were not able to be matched.")
    logger.info(f"In total, {written} records were written to the cross reference table.")

if __name__ == "__main__":
     main()



