import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from osdatahub import PlacesAPI
import time
import logging

# Load environment variables
load_dotenv(".env")

logging.basicConfig(
     level=os.getenv("LOG_LEVEL", "INFO"),
     format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

OS_PLACES_KEY = os.environ.get("OS_PLACES_KEY")

if not OS_PLACES_KEY:
    logger.error("OS_PLACES_KEY not found. Please set it in your .env file.")
    raise RuntimeError("OS_PLACES_KEY not found. Please set it in your .env file.")
else:
    logger.info("OS Places API Key loaded.")

# Database Connection Details
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
MATCH_THRESHOLD=float(os.getenv("MATCH_THRESHOLD"))


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
        select
            "LMK_KEY",
            query_address, 
            "LODGEMENT_DATE"
        from (
            SELECT 
                c."LMK_KEY",
                concat_ws(', ', UPPER(c."ADDRESS"), UPPER(c."POSTTOWN"), UPPER(c."POSTCODE")) as query_address,
                c."LODGEMENT_DATE",
                eauc.lmk_key
            FROM {db_schema}.certificates c
            left join {db_schema}.epc_address_uprn_crossref eauc on eauc.lmk_key=c."LMK_KEY"
                WHERE NULLIF(TRIM(c."UPRN"), '') IS NULL
                and eauc.lmk_key is null) t;
    """

    else:
        query = f"""
        select
            "LMK_KEY",
            query_address, 
            "LODGEMENT_DATE"
        from (
            SELECT 
                "LMK_KEY",
                concat_ws(', ', UPPER("ADDRESS"), UPPER("POSTTOWN"), UPPER("POSTCODE")) as query_address,
                "LODGEMENT_DATE"
            FROM {db_schema}.certificates 
            WHERE NULLIF(TRIM("UPRN"), '') IS NULL) t;
        """

    return pd.read_sql(query, engine)
    
def match_address(api_client, address, threshold=0.8):
    """
    Given a EPC record with no UPRN, use the OS Places API to find a UPRN value with the highest match score which is above the threshold.
    
    Args:
        address (str): the address to be passed to the OS Places API
        threshold (float): a threshold (between 0.1 and 1) above which match scores must be
    
    Returns:
        uprn (str): a matched uprn value
        match_score (float): a match score value
    """

    results = api_client.find(text=address, minmatch=threshold, limit=1)
    if results and results.get("features"):
                props = results["features"][0].get("properties", {})
                return props.get("UPRN"), float(props.get("MATCH")), props.get("MATCH_DESCRIPTION") 
    else:
        return None, None, None

def main():

    engine = get_db_connection(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

    crossref_exists = is_crossref_exists(engine, DB_SCHEMA)
    certificates = get_certificates(engine, DB_SCHEMA, crossref_exists=crossref_exists)

    certificates_matched_dict = []
    places_api = PlacesAPI(OS_PLACES_KEY)

    matched = 0
    unmatched = 0

    logger.info(f"Matching threshold set at {MATCH_THRESHOLD}")

    for _, record in certificates.iterrows():

        uprn, match_score, match_description = match_address(places_api, record["query_address"], MATCH_THRESHOLD)

        time.sleep(0.1)
        
        if uprn is not None and match_score is not None and match_description is not None:
            record_matched = {
                "lmk_key": record["LMK_KEY"],
                "query_address": record["query_address"],
                "uprn": uprn,
                "match_score": match_score
            }
            certificates_matched_dict.append(record_matched)
            matched += 1

            if matched==10 or matched % 1000 == 0:
                 logger.info(f"Matched {matched} records.")
                 logger.info(f"Could find a UPRN at or above the threshold for {unmatched} records")
        else:
            unmatched += 1
            continue
    
    logger.info(f"{matched} records successfully matched.")

    epc_address_uprn_crossref = pd.DataFrame(
        certificates_matched_dict,
        columns=["lmk_key", "query_address", "uprn", "match_score"]
    )

    logger.info(f"{matched} records loading into postgres.")

    epc_address_uprn_crossref.to_sql("epc_address_uprn_crossref", schema=DB_SCHEMA, con=engine, index=False, if_exists='append')

    logger.info(f"{matched} records successfully loaded into postgres.")

if __name__ == "__main__":
     main()




