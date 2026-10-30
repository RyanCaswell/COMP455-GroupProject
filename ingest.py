import pandas as pd
import json

DATA_FILE = "data/yellow_tripdata_2026-01.parquet"

COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "fare_amount",
    "tip_amount",
    "total_amount",
    "Airport_fee",
]

def main():
    # Load data, requested columns only
    data = pd.read_parquet( DATA_FILE, columns=COLUMNS )

    # Send each record to standard output
    count = 0               # Testing only
    for record in data.to_dict( orient="records" ):
        print( json.dumps( record, default=str ) )
        count += 1          # Testing only
        if count > 1000:    # Testing only
            break           # Testing only

if __name__ == "__main__":
    main()