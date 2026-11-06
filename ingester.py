import tracker
tracker.track( "ingester" )

import pandas as pd
import json
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

    # Send each record to standard output
    # for record in data.to_dict( orient="records" ):
    #     print( json.dumps( record, default=str ) )

    for i in range( 0, len( data ), CHUNK_SIZE ):
        chunk = data.iloc[ i : i + CHUNK_SIZE ]
        text = chunk.to_json( orient="records", lines=True, date_format="iso" )
        if not text.endswith( "\n" ):
            text += "\n"
        sys.stdout.write( text )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( "--limit", "-n", type=int, default=None, help="Max records to ingest (default is all)" )
    args = parser.parse_args()

    main( args.limit )