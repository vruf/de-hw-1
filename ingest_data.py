import os
from pathlib import Path
from time import time

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

TRIP_DATA_FILE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"
ZONES_DATA_FILE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
TRIPDATA_FILEPATH = "green_tripdata_2019-10.csv.gz"
TAXI_ZONES_FILEPATH = "taxi_zone_lookup.csv"
DTYPE_SPEC = {TRIPDATA_FILEPATH: {"store_and_fwd_flag": "string"}}
PARSE_DATES_SPEC = {
    TRIPDATA_FILEPATH: ["lpep_pickup_datetime", "lpep_dropoff_datetime"]
}
PATH_TO_DATA = "./data/"

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")


engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")


def load_data() -> None:
    if not os.path.exists(PATH_TO_DATA):
        os.makedirs(PATH_TO_DATA)

    if any(Path(PATH_TO_DATA).iterdir()):
        return

    _load_file(TRIP_DATA_FILE_URL)
    _load_file(ZONES_DATA_FILE_URL)


def _load_file(url: str) -> None:
    # don't works in windows
    # os.system(f"wget {url} -P {PATH_TO_DATA}")

    response = requests.get(url)
    if not response.status_code == 200:
        return

    filename = url.split("/")[-1]
    local_path = os.path.join(PATH_TO_DATA, filename)

    with open(local_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=10240):  # 10 KB chunks
            if chunk:
                f.write(chunk)


def ingest_data(
    file_path: str,
    table_name: str,
    dtype_spec: dict | None = None,
    parse_dates: list[str] | None = None,
) -> None:
    df_iter = pd.read_csv(
        file_path,
        iterator=True,
        chunksize=100000,
        dtype=dtype_spec,
        parse_dates=parse_dates,
    )
    df = next(df_iter)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")
    df.to_sql(name=table_name, con=engine, if_exists="append")

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.to_sql(name=table_name, con=engine, if_exists="append")
            t_end = time()
            print("inserted another chunk, took %.3f second" % (t_end - t_start))

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break


if __name__ == "__main__":
    load_data()
    ingest_data(
        f"data/{TRIPDATA_FILEPATH}",
        "tripdata",
        DTYPE_SPEC.get(TRIPDATA_FILEPATH),
        PARSE_DATES_SPEC.get(TRIPDATA_FILEPATH),
    )
    ingest_data(f"data/{TAXI_ZONES_FILEPATH}", "taxi_zone_lookup")
