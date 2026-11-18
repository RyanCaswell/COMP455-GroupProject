import pandas as pd
import argparse
import sys

DATA_FILE = "data/yellow_tripdata_2026-01.parquet"

CHUNK_SIZE=50000

COLUMNS = [
    "tpep_pickup_datetime",
    #"tpep_dropoff_datetime",
    #"passenger_count",
    #"trip_distance",
    "PULocationID",
    "DOLocationID",
    #"fare_amount",
    "tip_amount",
    "total_amount",
    #"Airport_fee",
]

def main( limit = None ):
    # Load data, requested columns only
    data = pd.read_parquet( DATA_FILE, columns=COLUMNS )

    if limit is not None:
        data = data.head( limit )

    chunk = []

    for i, row in enumerate( data.itertuples( index=False ) ):
        text = f"{row.tpep_pickup_datetime},{row.PULocationID},{row.DOLocationID},{row.tip_amount},{row.total_amount}\n"

        chunk.append( text )

        if i + 1 % CHUNK_SIZE == 0:
            sys.stdout.write( "".join( chunk ) )
            chunk = []

    if chunk:
        sys.stdout.write( "".join( chunk ) )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( "--limit", "-n", type=int, default=None, help="Max records to ingest (default is all)" )
    args = parser.parse_args()

    main( args.limit )